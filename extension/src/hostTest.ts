/* Native VS Code host integration, executed only by test/run-host.cjs. */
import * as vscode from 'vscode';
import * as assert from 'assert';
import * as http from 'http';
import * as fs from 'fs/promises';
import * as os from 'os';
import * as path from 'path';

export async function run(): Promise<void> {
  let hold = false;
  const requests: any[] = [];
  const server = http.createServer((req,res)=>{
    let body=''; req.on('data',chunk=>body+=chunk);
    req.on('end',()=>{
      if (req.url === '/api/tasks' && hold) return;
      let data: any;
      if (req.url === '/health') data={status:'ok',model_configured:true,model:'integration-fixture'};
      else if (req.url === '/api/history') data=[];
      else if (req.url === '/api/verify') data={status:'unavailable',output:'Docker unavailable fixture',tests_sha256:'fixed'};
      else {
        const payload=JSON.parse(body);requests.push(payload);
        data={id:'fixture',task:payload.task,language:payload.language,code:'def add(a, b):\n    return a + b\n',explanation:'集成测试模拟模型',issues:[],suggestions:[],documentation:'# API',verification:'未验证',model:'integration-fixture',usage:{},duration_ms:1};
      }
      res.setHeader('Content-Type','application/json');res.end(JSON.stringify(data));
    });
  });
  await new Promise<void>(resolve=>server.listen(0,'127.0.0.1',resolve));
  const dir=await fs.mkdtemp(path.join(os.tmpdir(),'codepilot-host-'));
  let passed=0;
  try {
    const port=(server.address() as any).port;
    await vscode.workspace.getConfiguration('codepilot').update('backendUrl',`http://127.0.0.1:${port}`,vscode.ConfigurationTarget.Global);
    const extension=vscode.extensions.getExtension('course-project.course-codepilot');
    assert.ok(extension,'extension is installed in development host');
    const api=await extension.activate();
    const assistant=api.assistant as any;
    const messages: any[]=[];
    assistant.send=(message:any)=>messages.push(message);
    const file=path.join(dir,'source.py');await fs.writeFile(file,'# existing\n');
    let doc=await vscode.workspace.openTextDocument(file);
    let editor=await vscode.window.showTextDocument(doc);
    editor.selection=new vscode.Selection(new vscode.Position(1,0),new vscode.Position(1,0));
    await assistant.handle({action:'run',task:'generate',language:'python',requirement:'加法',useContext:true});
    assert.equal(requests.at(-1).code,''); assert.equal(assistant.result.verification,'未验证');passed++;
    await assistant.handle({action:'preview'});passed++;
    // Restore the original editor after diff preview, then apply to captured location.
    editor=await vscode.window.showTextDocument(doc);
    await assistant.handle({action:'apply'});
    assert.equal(doc.getText(),'# existing\ndef add(a, b):\n    return a + b\n');passed++;
    editor.selection=new vscode.Selection(new vscode.Position(1,0),doc.positionAt(doc.getText().length));
    await assistant.handle({action:'run',task:'review',language:'python',requirement:'审查',useContext:true});
    await editor.edit(edit=>edit.insert(new vscode.Position(0,0),'# user change\n'));
    const changed=doc.getText();await assistant.handle({action:'apply'});
    assert.equal(doc.getText(),changed);assert.ok(messages.some(m=>m.type==='status' && /已经修改/.test(m.text)));passed++;
    await assistant.handle({action:'verify',tests:'def test_x(): assert True'});
    assert.ok(messages.some(m=>m.type==='validation' && /未验证/.test(m.status)));passed++;
    const old=assistant.result;
    hold=true;
    const pending=assistant.handle({action:'run',task:'generate',language:'python',requirement:'cancel',useContext:true});
    setTimeout(()=>void assistant.handle({action:'cancel'}),200);
    await pending;
    assert.equal(assistant.result,old);assert.equal(assistant.controller,undefined);passed++;
    assert.ok(messages.some(m=>m.type==='status' && /已取消/.test(m.text)));
    const output=process.env.CODEPILOT_HOST_RESULT;
    if(output)await fs.writeFile(output,JSON.stringify({passed,model:'mock local HTTP provider',native_vscode:true,scenarios:['generation context','diff preview','apply insertion','stale source protection','unavailable verification','request cancellation']},null,2));
  } finally {
    server.closeAllConnections();server.close();
    // Test files are in an OS-generated temporary directory, never the user's workspace.
  }
}
