/* Only textContent renders model output. No remote scripts or raw model HTML. */
const vscode = acquireVsCodeApi();
const $ = id => document.getElementById(id);
let result;
let canApply = false;
const previous = vscode.getState() || {};
for (const id of ['task','language','requirement','errorLog','testCode']) {
  if (typeof previous[id] === 'string') $(id).value = previous[id];
  $(id).addEventListener('input', () => vscode.setState(Object.fromEntries(['task','language','requirement','errorLog','testCode'].map(k => [k,$(k).value]))));
}
function send(action, extra = {}) { vscode.postMessage({ action, task: $('task').value, language: $('language').value, requirement: $('requirement').value, errorLog: $('errorLog').value, useContext: $('useContext').checked, tests: $('testCode').value, ...extra }); }
for (const id of ['run','cancel','addContext','preview','apply','newFile','save','verify','repair','history']) $(id).addEventListener('click', () => send(id));
$('useAsTests').addEventListener('click', () => { if (result?.code) { $('testCode').value = result.code; vscode.setState({...vscode.getState(),testCode: result.code}); } });
window.addEventListener('message', ({data}) => {
  if (data.type === 'busy') {
    for (const id of ['run','verify','repair','apply','preview','newFile','save']) $(id).disabled = data.value;
    $('cancel').disabled = !data.value;
    if (!data.value) { $('apply').disabled = !canApply; $('preview').disabled = !canApply; }
  }
  if (data.type === 'status') { $('status').textContent = data.text; $('status').classList.toggle('error', !!data.error); }
  if (data.type === 'health') $('health').textContent = data.text;
  if (data.type === 'context') $('contextCount').textContent = `${data.count} 个文件`;
  if (data.type === 'task') $('task').value = data.task;
  if (data.type === 'result') {
    result = data.result; $('resultSection').hidden = false;
    $('code').textContent = result.code || ''; $('explanation').textContent = data.text;
    $('verification').textContent = result.verification || '未验证';
    $('meta').textContent = `${result.model || ''}  ${result.duration_ms || 0} ms  ${JSON.stringify(result.usage || {})}`;
    canApply = data.canApply;
    $('apply').disabled = !canApply; $('preview').disabled = !canApply;
    if (result.task === 'tests') $('testCode').value = result.code || '';
    $('validation').textContent = '';
  }
  if (data.type === 'validation') {
    $('validation').textContent = data.text; $('verification').textContent = data.status;
    if (data.code !== undefined && result) { result.code = data.code; $('code').textContent = data.code; }
  }
  if (data.type === 'history') {
    $('historyList').replaceChildren();
    for (const row of data.rows) { const b = document.createElement('button'); b.className = 'historyItem'; b.textContent = `${row.kind} · ${row.language}\n${row.requirement || row.created_at}`; b.addEventListener('click', () => send('loadHistory', {id: row.id})); $('historyList').appendChild(b); }
  }
});
send('ready');
