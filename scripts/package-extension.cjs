const path = require('node:path');
const {execFileSync} = require('node:child_process');
const fs = require('node:fs');
const root = path.resolve(__dirname,'..');
const extension = path.join(root,'extension');
execFileSync(process.execPath,[path.join(extension,'node_modules/typescript/bin/tsc'),'-p',extension],{stdio:'inherit'});
fs.mkdirSync(path.join(root,'artifacts'),{recursive:true});
// Package through the official vsce API. Compilation above replaces the npm prepublish hook.
const {createVSIX} = require(path.join(extension,'node_modules/@vscode/vsce'));
createVSIX({cwd:extension,packagePath:path.join(root,'artifacts/course-codepilot-0.1.0.vsix'),
  dependencies:false,prepublish:false,allowMissingRepository:true}).catch(error=>{console.error(error);process.exitCode=1;});
