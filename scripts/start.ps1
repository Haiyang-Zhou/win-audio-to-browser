$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\pythonw.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Run setup.cmd first.' }
$data = Join-Path $root 'data'
New-Item -ItemType Directory -Force -Path $data | Out-Null
Start-Process -FilePath $python -ArgumentList ('"' + (Join-Path $root 'app\floating_control.py') + '"') -WorkingDirectory $root -WindowStyle Hidden
