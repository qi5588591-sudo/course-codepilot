const test = require('node:test');
const assert = require('node:assert/strict');
const {languageFor, validSource, modelText, shouldSendFile} = require('../out/core');
test('maps supported editor languages', () => {
  assert.equal(languageFor('python'),'python'); assert.equal(languageFor('cpp'),'cpp'); assert.equal(languageFor('markdown'),undefined);
});
test('rejects edits based on stale or different documents', () => {
  assert.equal(validSource(2,3,'a','a'),false); assert.equal(validSource(2,2,'a','b'),false); assert.equal(validSource(2,2,'a','a'),true);
});
test('blocks common credential files without blocking normal source code', () => {
  for (const path of ['a/.env','a/.env.local','C:\\x\\secret.key','credentials.json']) assert.equal(shouldSendFile(path),false);
  assert.equal(shouldSendFile('a/main.py'),true);
});
test('formats issue positions and suggestions without HTML interpretation', () => {
  const text = modelText({explanation:'<script>text</script>',issues:[{severity:'warning',line:3,message:'边界',suggestion:'修复'}],suggestions:['rename']});
  assert.match(text,/第 3 行/); assert.match(text,/<script>/); assert.match(text,/rename/);
});
