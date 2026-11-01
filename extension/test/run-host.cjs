const path=require('node:path');
const fs=require('node:fs');
const os=require('node:os');
const {runTests}=require('@vscode/test-electron');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'codepilot-vscode-profile-'));
const root=path.resolve(__dirname,'../..');
runTests({
  vscodeExecutablePath:process.env.CODEPILOT_VSCODE_PATH,
  extensionDevelopmentPath:path.join(root,'extension'),
  extensionTestsPath:path.join(root,'extension/out/hostTest.js'),
  extensionTestsEnv:{CODEPILOT_HOST_RESULT:path.join(root,'artifacts/extension-host-tests.json')},
  launchArgs:['--user-data-dir='+profile,'--extensions-dir='+path.join(profile,'extensions'),'--disable-extensions','--disable-gpu','--skip-welcome','--skip-release-notes','--disable-workspace-trust']
}).catch(error=>{console.error(error);process.exitCode=1;});
