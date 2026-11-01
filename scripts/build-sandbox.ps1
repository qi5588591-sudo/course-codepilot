$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw '请安装并启动 Docker Desktop（Linux containers）' }
docker build -t course-codepilot-sandbox:0.1 sandbox
if ($LASTEXITCODE -ne 0) { throw '容器镜像构建失败' }
