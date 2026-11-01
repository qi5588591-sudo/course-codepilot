import * as vscode from 'vscode';
import { randomBytes } from 'crypto';

export function html(view: vscode.Webview, extension: vscode.Uri): string {
  const nonce = randomBytes(18).toString('base64');
  const script = view.asWebviewUri(vscode.Uri.joinPath(extension, 'media', 'main.js'));
  const style = view.asWebviewUri(vscode.Uri.joinPath(extension, 'media', 'style.css'));
  return `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${view.cspSource}; script-src 'nonce-${nonce}';">
  <link href="${style}" rel="stylesheet"><title>CodePilot</title></head><body>
  <header><span class="eyebrow">COURSE PROJECT 32</span><h1>CodePilot</h1><p>让代码有依据，让修复可验证。</p></header>
  <div id="health" role="status">正在连接后端…</div>
  <label for="task">开发任务</label><select id="task">
  <option value="generate">生成代码</option><option value="explain">解释代码</option><option value="review">审查与优化</option>
  <option value="tests">生成单元测试</option><option value="docs">生成 API 文档</option><option value="fix">诊断与修复</option>
  <option value="naming">命名建议</option><option value="suggest">函数建议</option></select>
  <label for="language">目标语言</label><select id="language"><option value="python">Python</option><option value="java">Java</option><option value="javascript">JavaScript</option><option value="cpp">C++</option></select>
  <label for="requirement">需求与约束</label><textarea id="requirement" rows="5" placeholder="例如：实现二分查找，未找到返回 -1，输入列表已经升序排列。"></textarea>
  <details><summary>上下文与错误日志</summary><p id="source">使用当前编辑器选中代码；无选区时使用当前文件。</p>
  <label class="check"><input id="useContext" type="checkbox" checked>结合光标附近代码与相关文件</label>
  <button id="addContext" class="secondary">选择相关文件</button><span id="contextCount">0 个文件</span>
  <label for="errorLog">编译错误或运行日志</label><textarea id="errorLog" rows="4" placeholder="粘贴 traceback 或编译错误"></textarea></details>
  <p class="hint">请求会将所选代码和上下文发送到你配置的模型服务。</p>
  <div class="actions"><button id="run">开始处理</button><button id="cancel" class="secondary" disabled>取消</button></div>
  <div id="status" role="status" aria-live="polite">就绪</div>
  <section id="resultSection" hidden><div class="sectionHeading"><h2>处理结果</h2><span id="verification">未验证</span></div>
  <div id="meta" class="hint"></div><pre id="code"></pre><pre id="explanation"></pre>
  <div class="actions wrap"><button id="preview" class="secondary">查看修改差异</button><button id="apply">应用到原位置</button>
  <button id="newFile" class="secondary">打开为新文件</button><button id="save" class="secondary">保存结果</button></div>
  <details><summary>Python 测试验证与修复</summary><p>测试固定导入 solution。自动修复最多两轮，测试保持不变。</p>
  <label for="testCode">pytest 测试代码</label><textarea id="testCode" rows="8" placeholder="from solution import binary_search&#10;&#10;def test_found():&#10;    assert binary_search([1, 3, 5], 3) == 1"></textarea>
  <div class="actions wrap"><button id="useAsTests" class="secondary">将本次结果用作测试</button><button id="verify">执行测试</button><button id="repair">验证并修复</button></div>
  <pre id="validation"></pre></details></section>
  <section><div class="sectionHeading"><h2>最近任务</h2><button id="history" class="secondary">刷新</button></div><div id="historyList"></div></section>
  <script nonce="${nonce}" src="${script}"></script></body></html>`;
}
