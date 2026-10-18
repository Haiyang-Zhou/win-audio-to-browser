$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\pythonw.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Run setup.cmd first.' }
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'Audio Link.lnk'))
$link.TargetPath = $python
$link.Arguments = '"' + (Join-Path $root 'app\floating_control.py') + '"'
$link.WorkingDirectory = $root
$link.IconLocation = Join-Path $root 'assets\icons\audio-link.ico'
$link.Description = 'Audio Link - local audio streaming'
$link.Save()
