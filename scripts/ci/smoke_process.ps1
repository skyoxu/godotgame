# ADR-0005 / ADR-0018: require readiness and reject runtime errors.
function Invoke-SmokeProcess {
  param(
    [Parameter(Mandatory=$true)][string]$Executable,
    [string[]]$Arguments = @(),
    [int]$TimeoutSec = 15,
    [string]$WorkingDirectory = (Get-Location).Path,
    [string]$LogName = 'headless'
  )
  $ErrorActionPreference = 'Stop'
  if ($TimeoutSec -le 0) { throw 'TimeoutSec must be positive.' }
  $exe = (Resolve-Path -LiteralPath $Executable).Path
  $dest = Join-Path $PSScriptRoot ("../../logs/ci/" + (Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '/smoke')
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  $out = Join-Path $dest "$LogName.out.log"
  $err = Join-Path $dest "$LogName.err.log"
  $runtimeLog = Join-Path $dest 'runtime.log'
  $Arguments = @($Arguments) + @('--log-file', $runtimeLog)
  $start = @{
    FilePath = $exe; WorkingDirectory = $WorkingDirectory; PassThru = $true
    RedirectStandardOutput = $out; RedirectStandardError = $err
  }
  if ($Arguments.Count -gt 0) {
    $start.ArgumentList = ($Arguments | ForEach-Object { '"' + ($_ -replace '"', '\"') + '"' }) -join ' '
  }
  $p = Start-Process @start
  $null = $p.Handle
  $timedOut = -not $p.WaitForExit($TimeoutSec * 1000)
  $processExit = $null
  if ($timedOut) {
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    $p.WaitForExit()
  } else {
    $p.WaitForExit()
    $processExit = $p.ExitCode
  }
  $content = [System.IO.File]::ReadAllText($out) + "`n" + [System.IO.File]::ReadAllText($err)
  if (Test-Path $runtimeLog) { $content += "`n" + [System.IO.File]::ReadAllText($runtimeLog) }
  [System.IO.File]::WriteAllText((Join-Path $dest "$LogName.log"), $content)
  $ready = $content.Contains('[TEMPLATE_SMOKE_READY]')
  $runtimeError = $content -match '(?im)^\s*(?:SCRIPT ERROR:|ERROR:|Unhandled exception|Parser Error)'
  $passed = $ready -and -not $runtimeError -and ($timedOut -or $processExit -eq 0)
  $summary = @{
    ready = $ready; runtime_error = $runtimeError; timed_out = $timedOut
    process_exit = $processExit; passed = $passed; executable = $exe
  }
  $summary | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $dest 'summary.json')
  Write-Host "SMOKE ready=$ready runtime_error=$runtimeError process_exit=$processExit logs=$dest"
  if (-not $passed) { throw 'Smoke failed: readiness, exit code, or runtime log check failed.' }
}
