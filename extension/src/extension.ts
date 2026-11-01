import * as vscode from 'vscode';
import { randomUUID } from 'crypto';
import { html } from './webview';
import { languageFor, modelText, shouldSendFile, taskNames, validSource } from './core';

type Snapshot = { uri: vscode.Uri; version: number; range: vscode.Range; fullText: string; code: string; language: string };
type ContextFile = { path: string; content: string };
const statuses: Record<string, string> = { passed: '测试通过', failed: '测试失败', syntax_error: '语法错误',
  timeout: '执行超时', unavailable: '执行环境不可用，未验证', no_tests: '缺少有效测试，未验证', error: '执行失败，未验证' };

export function backendUrl(): string {
  const raw = vscode.workspace.getConfiguration('codepilot').get<string>('backendUrl', 'http://127.0.0.1:8765');
  const url = new URL(raw);
  if (!['http:', 'https:'].includes(url.protocol)) throw new Error('后端地址必须是 HTTP 或 HTTPS');
  if (url.protocol !== 'https:' && !['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname)) throw new Error('远程后端请使用 HTTPS');
  return raw.replace(/\/$/, '');
}

async function api(context: vscode.ExtensionContext, path: string, body?: unknown, signal?: AbortSignal): Promise<any> {
  const token = await context.secrets.get('backendToken');
  const timeout = vscode.workspace.getConfiguration('codepilot').get<number>('requestTimeoutSeconds', 120);
  const controller = new AbortController();
  const abort = () => controller.abort();
  signal?.addEventListener('abort', abort);
  if (signal?.aborted) controller.abort();
  const timer = setTimeout(abort, timeout * 1000);
  try {
    const response = await fetch(backendUrl() + path, { method: body === undefined ? 'GET' : 'POST',
      headers: { 'Content-Type': 'application/json', ...(token ? {Authorization: `Bearer ${token}`} : {}) },
      body: body === undefined ? undefined : JSON.stringify(body), signal: controller.signal });
    const result: any = await response.json();
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : `请求失败 HTTP ${response.status}，请检查输入长度与格式`);
    return result;
  } finally { clearTimeout(timer); signal?.removeEventListener('abort', abort); }
}

function capture(task: string): Snapshot | undefined {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.uri.scheme !== 'file') return undefined;
  if (!shouldSendFile(editor.document.uri.fsPath)) throw new Error('请勿发送密钥或凭据文件');
  const doc = editor.document;
  const full = new vscode.Range(doc.positionAt(0), doc.positionAt(doc.getText().length));
  const range = editor.selection.isEmpty ? (task === 'generate' ? new vscode.Range(editor.selection.active, editor.selection.active) : full) : editor.selection;
  return { uri: doc.uri, version: doc.version, range, fullText: doc.getText(), code: doc.getText(editor.selection.isEmpty ? full : editor.selection), language: doc.languageId };
}

class AssistantView implements vscode.WebviewViewProvider {
  private view?: vscode.WebviewView;
  private controller?: AbortController;
  private source?: Snapshot;
  private result: any;
  private contextFiles: ContextFile[] = [];
  private previews = new Map<string, string>();
  constructor(private context: vscode.ExtensionContext) {
    context.subscriptions.push(vscode.workspace.registerTextDocumentContentProvider('codepilot-preview', {
      provideTextDocumentContent: uri => this.previews.get(uri.toString()) || ''
    }));
  }
  resolveWebviewView(view: vscode.WebviewView) {
    this.view = view;
    view.webview.options = { enableScripts: true, localResourceRoots: [vscode.Uri.joinPath(this.context.extensionUri, 'media')] };
    view.webview.html = html(view.webview, this.context.extensionUri);
    view.webview.onDidReceiveMessage(message => { void this.handle(message); }, undefined, this.context.subscriptions);
    view.onDidDispose(() => this.controller?.abort(), undefined, this.context.subscriptions);
  }
  private send(message: any) { void this.view?.webview.postMessage(message); }
  async open(task?: string) {
    await vscode.commands.executeCommand('workbench.view.extension.codepilot');
    if (task) this.send({type: 'task', task});
  }
  private display(canApply = !!this.source) {
    this.send({ type: 'result', result: this.result, text: modelText(this.result),
      canApply: canApply && !!this.result.code && ['generate','review','fix','complete'].includes(this.result.task) });
  }
  private async history() { this.send({type: 'history', rows: await api(this.context, '/api/history')}); }
  private async freshSource(): Promise<vscode.TextDocument> {
    if (!this.source) throw new Error('历史记录没有原位置，请打开为新文件');
    const doc = await vscode.workspace.openTextDocument(this.source.uri);
    if (!validSource(this.source.version, doc.version, this.source.uri.toString(), doc.uri.toString()) || doc.getText() !== this.source.fullText) {
      throw new Error('原文件已经修改，请重新生成或打开结果为新文件，避免覆盖新内容');
    }
    return doc;
  }
  private async handle(message: any) {
    if (!message || typeof message.action !== 'string') return;
    const action = message.action;
    if (action === 'cancel') { this.controller?.abort(); return; }
    const network = ['run','verify','repair'].includes(action);
    if (network && this.controller) { this.send({type:'status',text:'请先等待当前任务完成或取消'}); return; }
    if (network) { this.controller = new AbortController(); this.send({type:'busy',value:true}); this.send({type:'status',text: action === 'run' ? '模型正在处理…' : '正在验证，请等待容器执行…'}); }
    try {
      if (!vscode.workspace.isTrusted) throw new Error('请先信任当前工作区');
      if (action === 'ready') {
        try { const health = await api(this.context, '/health'); this.send({type:'health',text: health.model_configured ? `已连接 · ${health.model}` : '后端已连接 · 请配置模型 API'}); await this.history(); }
        catch { this.send({type:'health',text:'后端未连接 · 请先运行启动脚本'}); }
      } else if (action === 'history') await this.history();
      else if (action === 'addContext') {
        const uris = await vscode.window.showOpenDialog({canSelectMany:true, filters:{'代码文件':['py','java','js','cpp','h','hpp','txt','md']}});
        if (uris) {
          if (uris.length > 4) throw new Error('最多选择 4 个相关文件');
          const files: ContextFile[] = [];
          for (const uri of uris) {
            if (!shouldSendFile(uri.fsPath)) throw new Error('不能添加凭据文件');
            const bytes = await vscode.workspace.fs.readFile(uri);
            const content = Buffer.from(bytes).toString('utf8');
            if (content.length > 12000) throw new Error(`${vscode.workspace.asRelativePath(uri)} 超过 12000 字符，请选择更小的上下文文件`);
            files.push({path: vscode.workspace.asRelativePath(uri), content});
          }
          this.contextFiles = files; this.send({type:'context',count:files.length});
        }
      } else if (action === 'run') {
        if (!taskNames[message.task] || !['python','java','javascript','cpp'].includes(message.language)) throw new Error('不支持的任务或语言');
        const source = capture(message.task);
        const editor = vscode.window.activeTextEditor;
        const position = editor && source ? editor.document.offsetAt(editor.selection.active) : 0;
        const full = source?.fullText || '';
        const code = source?.code || '';
        if (code.length > 60000) throw new Error('代码超过 60000 字符，请选中需要处理的函数');
        const result = await api(this.context, '/api/tasks', {
          task: message.task, language: message.language, requirement: String(message.requirement || ''),
          code: message.task === 'generate' && source?.range.isEmpty ? '' : code,
          prefix: full.slice(Math.max(0,position-16000),position), suffix: full.slice(position,position+8000),
          context_files: this.contextFiles, use_context: !!message.useContext, error_log: String(message.errorLog || '')
        }, this.controller?.signal);
        if (this.controller?.signal.aborted) return;
        this.source = source && languageFor(source.language) === message.language ? source : undefined;
        this.result = result; this.display(); this.send({type:'status',text:'处理完成 · 生成内容尚未执行验证'}); await this.history();
      } else if (action === 'loadHistory') {
        if (this.controller) throw new Error('请先取消当前任务');
        const row = await api(this.context, '/api/history/' + encodeURIComponent(String(message.id)));
        this.source = undefined;
        this.result = row.final_code !== undefined ? {code:row.final_code,task:'fix',language:'python',model:row.model,usage:row.usage,explanation:JSON.stringify(row.rounds,null,2),verification:statuses[row.status]} : row;
        this.display(false); this.send({type:'status',text:'已读取历史记录，可打开为新文件'});
      } else if (action === 'preview' || action === 'apply') {
        if (!this.result?.code || !['generate','review','fix','complete'].includes(this.result.task)) throw new Error('该结果请打开为新文件');
        const doc = await this.freshSource();
        const source = this.source!;
        if (action === 'preview') {
          this.previews.clear();
          const uri = vscode.Uri.parse(`codepilot-preview:/${randomUUID()}/${source.uri.path.split('/').pop()}`);
          this.previews.set(uri.toString(), source.fullText.slice(0,doc.offsetAt(source.range.start)) + this.result.code + source.fullText.slice(doc.offsetAt(source.range.end)));
          await vscode.commands.executeCommand('vscode.diff',source.uri,uri,'CodePilot 修改预览');
        } else {
          const edit = new vscode.WorkspaceEdit(); edit.replace(source.uri,source.range,this.result.code);
          if (!await vscode.workspace.applyEdit(edit)) throw new Error('编辑未成功应用');
          this.source = undefined; this.display(false); this.send({type:'status',text:'已应用，可通过编辑器撤销'});
        }
      } else if (action === 'newFile' || action === 'save') {
        if (!this.result) throw new Error('请先生成内容');
        const docs = this.result.task === 'docs';
        const text = docs ? this.result.documentation : this.result.code || modelText(this.result);
        if (action === 'newFile') {
          const document = await vscode.workspace.openTextDocument({content:text,language: docs ? 'markdown' : this.result.language});
          await vscode.window.showTextDocument(document,{preview:false});
        } else {
          const ext = docs ? 'md' : ({python:'py',java:'java',javascript:'js',cpp:'cpp'} as Record<string,string>)[this.result.language] || 'txt';
          const uri = await vscode.window.showSaveDialog({filters:{'结果文件':[ext]}});
          if (uri) await vscode.workspace.fs.writeFile(uri,Buffer.from(text,'utf8'));
        }
      } else if (action === 'verify' || action === 'repair') {
        if (!this.result || this.result.language !== 'python') throw new Error('首版仅支持 Python 自动执行验证');
        const code = this.result.task === 'tests' ? this.source?.code : this.result.code;
        if (!code) throw new Error('缺少待验证 Python 代码，请先生成或选中代码生成测试');
        if (!String(message.tests || '').trim()) throw new Error('请提供 pytest 测试');
        const response = await api(this.context, action === 'repair' ? '/api/repair' : '/api/verify',
          {code,tests:String(message.tests),...(action === 'repair' ? {requirement:String(message.requirement || ''),max_repairs:2} : {})},this.controller?.signal);
        if (this.controller?.signal.aborted) return;
        if (action === 'repair') {
          this.result = {...this.result, task:'fix', code:response.final_code, usage:response.usage};
          // A tests task originally captures its source code range, suitable for replacing with repaired code.
          this.display();
          this.send({type:'validation',status:statuses[response.status],code:response.final_code,
            text:response.rounds.map((r:any)=>`第 ${r.round} 轮 · ${statuses[r.validation.status]}\n${r.validation.output}\n测试 SHA256: ${r.validation.tests_sha256}\n${r.explanation || ''}`).join('\n\n') + (response.repair_error ? '\n修复中断：' + response.repair_error : '')});
          await this.history();
        } else this.send({type:'validation',status:statuses[response.status],text:response.output + '\n测试 SHA256: ' + response.tests_sha256});
        this.send({type:'status',text:'验证流程结束'});
      }
    } catch (error: any) {
      const canceled = this.controller?.signal.aborted;
      this.send({type:'status',text:canceled ? '已取消当前请求' : error.name === 'AbortError' ? '请求超时，请重试' : error.message || '操作失败',error:!canceled});
    } finally {
      if (network) { this.controller = undefined; this.send({type:'busy',value:false}); }
    }
  }
}

export function activate(context: vscode.ExtensionContext) {
  const provider = new AssistantView(context);
  context.subscriptions.push(vscode.window.registerWebviewViewProvider('codepilot.assistant',provider,{webviewOptions:{retainContextWhenHidden:true}}));
  context.subscriptions.push(vscode.commands.registerCommand('codepilot.open',()=>provider.open()));
  for (const task of Object.keys(taskNames).filter(t=>t!=='complete')) context.subscriptions.push(vscode.commands.registerCommand(`codepilot.${task}`,()=>provider.open(task)));
  context.subscriptions.push(vscode.commands.registerCommand('codepilot.setToken',async()=>{
    const token = await vscode.window.showInputBox({prompt:'本地后端令牌（不是模型 API 密钥），留空清除',password:true});
    if (token !== undefined) { if (token) await context.secrets.store('backendToken',token); else await context.secrets.delete('backendToken'); }
  }));
  let manualCompletion = false;
  context.subscriptions.push(vscode.commands.registerCommand('codepilot.complete',async()=>{
    manualCompletion = true;
    try { await vscode.commands.executeCommand('editor.action.inlineSuggest.trigger'); }
    finally { manualCompletion = false; }
  }));
  context.subscriptions.push(vscode.languages.registerInlineCompletionItemProvider(
    ['python','java','javascript','cpp'].map(language=>({language,scheme:'file'})), {
      async provideInlineCompletionItems(doc,position,_completionContext,cancellation) {
        if (!vscode.workspace.isTrusted || !shouldSendFile(doc.uri.fsPath)) return [];
        if (!manualCompletion && !vscode.workspace.getConfiguration('codepilot').get<boolean>('inlineCompletion',false)) return [];
        const controller = new AbortController();
        const listener = cancellation.onCancellationRequested(()=>controller.abort());
        try {
          if (cancellation.isCancellationRequested) return [];
          await new Promise(resolve=>setTimeout(resolve,450));
          if (cancellation.isCancellationRequested) return [];
          const version = doc.version, full = doc.getText(), offset = doc.offsetAt(position);
          const result = await api(context,'/api/tasks',{task:'complete',language:languageFor(doc.languageId),
            prefix:full.slice(Math.max(0,offset-12000),offset),suffix:full.slice(offset,offset+4000),requirement:'补全光标处代码'},controller.signal);
          if (doc.version !== version || cancellation.isCancellationRequested || !result.code) return [];
          return [new vscode.InlineCompletionItem(result.code,new vscode.Range(position,position))];
        } catch { return []; } finally { listener.dispose(); }
      }
    }
  ));
  return { assistant: provider };
}

export function deactivate() {}
