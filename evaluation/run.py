"""Real model evaluation only. No fabricated scores or host execution fallback."""
import argparse
import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time

import httpx

from evaluation.build_dataset import records


async def evaluate(args):
    cases = [r for r in records() if args.kind == 'all' or r['kind']==args.kind]
    if args.limit: cases=cases[:args.limit]
    modes = ['baseline','context','repair'] if args.mode=='all' else [args.mode]
    if args.dry_run:
        print(json.dumps({'case_count':len(cases),'modes':modes,'model_calls_at_least':len(cases)*len(modes),
                          'notice':'dry run: no model calls, no measured scores'},ensure_ascii=False,indent=2)); return
    headers = {'Authorization':'Bearer '+os.environ['CODEPILOT_BACKEND_TOKEN']} if os.environ.get('CODEPILOT_BACKEND_TOKEN') else {}
    async with httpx.AsyncClient(base_url=args.url,headers=headers,timeout=600) as client:
        health=(await client.get('/health')).raise_for_status().json()
        if not health['model_configured']: raise SystemExit('模型未配置，未执行实验')
        check=(await client.post('/api/verify',json={'code':'def add(a,b): return a+b','tests':'from solution import add\ndef test_add(): assert add(1,2)==3'})).raise_for_status().json()
        if check['status']!='passed': raise SystemExit('容器预检未通过，未执行实验：'+check['output'])
        args.output.parent.mkdir(parents=True,exist_ok=True)
        if args.output.exists(): raise SystemExit('输出文件已存在，请选择新文件名以保留原始实验记录')
        with args.output.open('x',encoding='utf-8') as out:
            for mode in modes:
                for case in cases:
                    started=time.perf_counter()
                    payload={'task':'generate' if case['kind']=='generate' else 'fix','language':'python',
                             'requirement':case['requirement'],'code':case.get('buggy',''),
                             'use_context':mode!='baseline','context_files':case['context_files'] if mode!='baseline' else []}
                    row={'id':case['id'],'kind':case['kind'],'mode':mode,'model':health['model'],
                         'timestamp':datetime.now(timezone.utc).isoformat()}
                    try:
                        if case['kind']=='fix':
                            original=(await client.post('/api/verify',json={'code':case['buggy'],'tests':case['tests']})).raise_for_status().json()
                            payload['error_log']=original['output']
                            row['original_validation']=original
                        generation=(await client.post('/api/tasks',json=payload)).raise_for_status().json()
                        row['generation']=generation
                        validation=(await client.post('/api/verify',json={'code':generation['code'],'tests':case['tests']})).raise_for_status().json()
                        row['first_validation']=validation
                        row['final_status']=validation['status']
                        row['usage']=dict(generation['usage'])
                        if mode=='repair' and validation['status'] in ('failed','syntax_error'):
                            repair=(await client.post('/api/repair',json={'code':generation['code'],'tests':case['tests'],'requirement':case['requirement'],'max_repairs':2})).raise_for_status().json()
                            row['repair']=repair;row['final_status']=repair['status']
                            for key,value in repair['usage'].items(): row['usage'][key]=row['usage'].get(key,0)+value
                    except (httpx.HTTPError,KeyError) as exc:
                        row['error']=f'{type(exc).__name__}: experiment request failed'
                        row['final_status']='error'
                    row['duration_ms']=int((time.perf_counter()-started)*1000)
                    out.write(json.dumps(row,ensure_ascii=False)+'\n');out.flush()
                    print(case['id'],mode,row['final_status'],row['duration_ms'],'ms')
        print('真实实验记录：',args.output)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8765')
    parser.add_argument('--kind',choices=['all','generate','fix'],default='all')
    parser.add_argument('--mode',choices=['all','baseline','context','repair'],default='all')
    parser.add_argument('--limit',type=int,default=0)
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--output',type=Path,default=Path('artifacts/evaluation-real.jsonl'))
    asyncio.run(evaluate(parser.parse_args()))
