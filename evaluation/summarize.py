import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean


def summarize(path):
    groups=defaultdict(list)
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():
            row=json.loads(line);groups[(row['kind'],row['mode'])].append(row)
    for (kind,mode),rows in sorted(groups.items()):
        yield {'kind':kind,'mode':mode,'count':len(rows),
               'first_pass_rate':sum(r.get('first_validation',{}).get('status')=='passed' for r in rows)/len(rows),
               'final_pass_rate':sum(r.get('final_status')=='passed' for r in rows)/len(rows),
               'error_count':sum(r.get('final_status')=='error' for r in rows),
               'mean_duration_ms':round(mean(r['duration_ms'] for r in rows)),
               'total_tokens':sum(r.get('usage',{}).get('total_tokens',0) for r in rows)}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('input',type=Path);parser.add_argument('--csv',type=Path)
    args=parser.parse_args();rows=list(summarize(args.input));print(json.dumps(rows,ensure_ascii=False,indent=2))
    if args.csv and rows:
        with args.csv.open('w',newline='',encoding='utf-8-sig') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
