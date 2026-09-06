param(
  [Parameter(Mandatory=$true)][string]$ExePath,
  [int]$TimeoutSec = 15,
  [string[]]$Args = @('--headless')
)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/smoke_process.ps1"
$exe = (Resolve-Path -LiteralPath $ExePath).Path
Invoke-SmokeProcess -Executable $exe -Arguments $Args -TimeoutSec $TimeoutSec `
  -WorkingDirectory (Split-Path -Parent $exe) -LogName 'exe'
