$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
& '.venv/Scripts/python.exe' -m pytest -q --junitxml=artifacts/backend-tests.xml
if ($LASTEXITCODE -ne 0) { throw '后端测试失败' }
Push-Location extension
try {
    node node_modules/typescript/bin/tsc -p ./
    if ($LASTEXITCODE -ne 0) { throw '插件编译失败' }
    node --test test/core.test.cjs
    if ($LASTEXITCODE -ne 0) { throw '插件测试失败' }
} finally { Pop-Location }
