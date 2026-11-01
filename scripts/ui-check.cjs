// Browser harness for the real webview assets; model output is explicitly simulated.
const fs=require('node:fs/promises');const path=require('node:path');const http=require('node:http');const Module=require('node:module');
const root=path.resolve(__dirname,'..');
const {chromium}=require(process.env.CODEPILOT_PLAYWRIGHT || path.join(root,'build/node_modules/playwright'));
const original=Module._load;
Module._load=function(id,...args){if(id==='vscode')return {Uri:{joinPath:(_uri,...parts)=>parts.join('/')}};return original.call(this,id,...args);};
const {html}=require(path.join(root,'extension/out/webview.js'));Module._load=original;
(async()=>{
 const server=http.createServer(async(req,res)=>{
  if(req.url==='/'){
   const port=server.address().port;
   const result=html({cspSource:`http://127.0.0.1:${port}`,asWebviewUri:p=>`http://127.0.0.1:${port}/${p}`},{});
   res.setHeader('Content-Type','text/html; charset=utf-8');res.end(result);
  }else{
   const file=path.join(root,'extension',req.url);
   res.setHeader('Content-Type',file.endsWith('.css')?'text/css':'application/javascript');
   res.end(await fs.readFile(file));
  }
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({executablePath:process.env.CODEPILOT_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:440,height:1100},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.addInitScript(()=>{let state={};window.posted=[];window.acquireVsCodeApi=()=>({postMessage:m=>window.posted.push(m),getState:()=>state,setState:s=>state=s});});
  await page.goto(`http://127.0.0.1:${server.address().port}/`);
  await page.evaluate(()=>window.dispatchEvent(new MessageEvent('message',{data:{type:'health',text:'离线界面预览 · 模型尚未配置'}})));
  await page.screenshot({path:path.join(root,'build/assistant.png'),fullPage:true});
  await page.locator('#requirement').fill('实现二分查找');await page.locator('#run').click();
  if(!await page.evaluate(()=>window.posted.some(m=>m.action==='run'&&m.requirement==='实现二分查找')))throw Error('request payload missing');
  await page.evaluate(()=>window.dispatchEvent(new MessageEvent('message',{data:{type:'result',canApply:false,result:{task:'review',language:'python',code:'<img src=x onerror="window.injected=true">'},text:'<script>window.injected=true</script>'}})));
  if(await page.evaluate(()=>!!window.injected || document.querySelector('#explanation script')!==null))throw Error('model HTML was interpreted');
  await page.evaluate(()=>window.dispatchEvent(new MessageEvent('message',{data:{type:'busy',value:false}})));
  if(!await page.locator('#apply').isDisabled())throw Error('stale apply became enabled after busy reset');
  await page.evaluate(()=>window.dispatchEvent(new MessageEvent('message',{data:{type:'history',rows:[{id:'<script>',kind:'review',language:'python',requirement:'<b>literal</b>'}]}})));
  if(await page.locator('#historyList b').count())throw Error('history HTML was interpreted');
  await page.locator('#historyList button').click();
  if(!await page.evaluate(()=>window.posted.some(m=>m.action==='loadHistory'&&m.id==='<script>')))throw Error('history action missing');
  if(errors.length)throw Error(errors.join('\n'));
  await fs.writeFile(path.join(root,'artifacts/webview-tests.json'),JSON.stringify({passed:5,checks:['request payload','model text escaping','stale apply button','history text escaping','history action'],model:'simulated browser messages'},null,2));
 }finally{await browser.close();server.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
