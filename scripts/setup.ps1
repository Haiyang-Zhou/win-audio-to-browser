$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
if (-not (Test-Path -LiteralPath "$root\.venv\Scripts\python.exe")) {
    & py -3.12 -m venv "$root\.venv"
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12 (with the Windows py launcher) first.' }
}
& "$root\.venv\Scripts\python.exe" -m pip install -r "$root\requirements.txt"
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
Write-Host 'Setup complete. Run start.cmd to open Audio Link.'
