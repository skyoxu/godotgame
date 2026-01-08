param(
  [string]$ProjectPath = 'Tests.Godot',
  [string]$RuntimeDir = 'Game.Godot'
)

$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$proj = Join-Path $root $ProjectPath
$runtime = Join-Path $root $RuntimeDir
if (-not (Test-Path $proj)) { Write-Error "Test project path not found: $proj" }
if (-not (Test-Path $runtime)) { Write-Error "Runtime dir not found: $runtime" }

# Audit log (UTF-8)
$date = Get-Date -Format 'yyyy-MM-dd'
$logDir = Join-Path $root ("logs\\ci\\$date")
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "prepare-gd-tests.log"
function Write-Log([string]$Message) {
  $ts = (Get-Date).ToString("s")
  $line = "[$ts] $Message"
  Write-Host $line
  try { Add-Content -LiteralPath $logPath -Value $line -Encoding utf8 } catch { }
}

# Create a junction inside Tests.Godot to expose runtime under res://
$link = Join-Path $proj $RuntimeDir
if (Test-Path $link) {
  try {
    $item = Get-Item -LiteralPath $link -Force
    $isReparse = (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)
    if ($isReparse) {
      $resolved = (Resolve-Path -LiteralPath $link).Path
      $expected = (Resolve-Path -LiteralPath $runtime).Path
      if ($resolved -eq $expected) {
        Write-Log "Test runtime Junction already OK: $link -> $resolved"
        exit 0
      }
      Write-Log "Test runtime Junction points elsewhere: $link -> $resolved (expected: $expected)"
      # Safe to remove junction link itself (not target)
      cmd /c rmdir "$link" | Out-Null
    } else {
      # Refuse to auto-delete a normal directory unless it's a prior copy marker or we're in CI.
      $marker = Join-Path $link '._copied'
      $isCI = ($null -ne $env:CI -and $env:CI -ne '')
      if (Test-Path -LiteralPath $marker -or $isCI) {
        Write-Log "Test runtime is a normal directory; removing to recreate Junction (ci=$isCI, marker=$(Test-Path -LiteralPath $marker))"
        Remove-Item -LiteralPath $link -Recurse -Force
      } else {
        Write-Log "Refuse to delete non-Junction directory at: $link"
        Write-Error "Expected a Junction at $link, but found a normal directory. Delete it manually and re-run prepare_gd_tests.ps1."
      }
    }
  } catch {
    Write-Log "Failed to inspect existing link dir: $link error=$($_.Exception.Message)"
    Write-Error $_
  }
}

Write-Log "Creating junction: $link -> $runtime"
$mkArgs = @("/c","mklink","/J","`"$link`"","`"$runtime`"")
# NOTE: -NoNewWindow and -WindowStyle cannot be used together. Use -NoNewWindow for CI.
$mk = Start-Process -FilePath "cmd" -ArgumentList $mkArgs -PassThru -NoNewWindow
$ok = $mk.WaitForExit(10000)
if (-not $ok -or $mk.ExitCode -ne 0 -or -not (Test-Path $link)) {
  $fallbackCopy = ($null -ne $env:GD_TEST_RUNTIME_FALLBACK_COPY -and $env:GD_TEST_RUNTIME_FALLBACK_COPY -eq '1')
  if (-not $fallbackCopy) {
    Write-Log "mklink failed or not available (exit=$($mk.ExitCode)); fallback copy disabled; failing."
    Write-Error "Failed to create Junction for test runtime. Set GD_TEST_RUNTIME_FALLBACK_COPY=1 to allow fallback copy (not recommended)."
  }

  Write-Log "mklink failed or not available (exit=$($mk.ExitCode)); falling back to copy (GD_TEST_RUNTIME_FALLBACK_COPY=1)."
  # Fallback copy (exclude bin/obj/.import/.godot/logs)
  $exclude = @('bin','obj','.import','.godot','logs')
  New-Item -ItemType Directory -Force -Path $link | Out-Null
  Get-ChildItem -Force -LiteralPath $runtime | ForEach-Object {
    if ($exclude -contains $_.Name) { return }
    Copy-Item -Recurse -Force -LiteralPath $_.FullName -Destination (Join-Path $link $_.Name)
  }
  New-Item -ItemType File -Force -Path (Join-Path $link '._copied') | Out-Null
  if (-not (Test-Path $link)) { Write-Error "Failed to prepare test runtime at $link" }
  Write-Log "Copied runtime to $link"
} else {
  Write-Log "Junction created."
}
