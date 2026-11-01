param([int]$Port = 8765)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$pythonPath = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 虚拟环境创建失败' }
}
& $pythonPath -c 'import fastapi, uvicorn, httpx, pydantic_settings' 2>$null
if ($LASTEXITCODE -ne 0) {
    & $pythonPath -m pip install --index-url https://pypi.org/simple -e '.[dev]'
    if ($LASTEXITCODE -ne 0) { throw '依赖安装失败' }
}
if (-not (Test-Path -LiteralPath '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
& $pythonPath -m uvicorn backend.main:app --host 127.0.0.1 --port $Port
