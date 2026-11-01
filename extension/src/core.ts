export type Language = 'python' | 'java' | 'javascript' | 'cpp';
export const taskNames: Record<string, string> = {
  generate: '生成代码', complete: '代码补全', explain: '解释代码', review: '审查与优化',
  tests: '生成测试', docs: 'API 文档', fix: '诊断与修复', naming: '命名建议', suggest: '函数建议'
};
export function languageFor(id: string): Language | undefined {
  return ({ python: 'python', java: 'java', javascript: 'javascript', javascriptreact: 'javascript', cpp: 'cpp', c: 'cpp' } as Record<string, Language>)[id];
}
export function validSource(version: number, currentVersion: number, uri: string, currentUri: string): boolean {
  return version === currentVersion && uri === currentUri;
}
export function modelText(result: any): string {
  return [result.explanation || '', result.documentation || '',
    ...(result.issues || []).map((i: any) => `[${i.severity}] ${i.line ? '第 ' + i.line + ' 行 ' : ''}${i.message}\n${i.suggestion || ''}`),
    ...(result.suggestions || [])].filter(Boolean).join('\n\n');
}
export function shouldSendFile(name: string): boolean {
  return !/(^|[\\/])(\.env(?:\..*)?|.*\.(pem|key|p12|pfx)|id_rsa|credentials(?:\..*)?)$/i.test(name);
}
