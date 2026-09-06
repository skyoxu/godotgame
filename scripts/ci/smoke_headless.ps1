param(
  [string]$GodotBin = $env:GODOT_BIN,
  [string]$Scene = 'res://Game.Godot/Scenes/Main.tscn',
  [int]$TimeoutSec = 15,
  [string]$ProjectPath = '.'
)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/smoke_process.ps1"
Invoke-SmokeProcess -Executable $GodotBin -TimeoutSec $TimeoutSec `
  -Arguments @('--headless', '--path', (Resolve-Path $ProjectPath).Path, '--scene', $Scene)
