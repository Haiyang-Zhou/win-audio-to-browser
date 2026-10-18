param([Parameter(Mandatory = $true)][string]$InterfaceAlias)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Run setup.cmd first.' }
Get-NetAdapter -Name $InterfaceAlias -ErrorAction Stop | Out-Null
# Explicit opt-in, administrator-only, private networks and local subnet only.
foreach ($protocol in @('TCP', 'UDP')) {
    $name = "AudioLink-$protocol-$InterfaceAlias"
    if (-not (Get-NetFirewallRule -Name $name -ErrorAction SilentlyContinue)) {
        $port = if ($protocol -eq 'TCP') { '8787' } else { 'Any' }
        New-NetFirewallRule -Name $name -DisplayName $name -Direction Inbound -Action Allow -Program $python -Protocol $protocol -LocalPort $port -RemoteAddress LocalSubnet -InterfaceAlias $InterfaceAlias -Profile Private | Out-Null
    }
}
