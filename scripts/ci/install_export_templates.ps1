param([string]$Version = '4.5.1')
$ErrorActionPreference = 'Stop'
$archive = 'godot/mono_export_templates.tpz'
New-Item -ItemType Directory -Force godot | Out-Null
if (-not (Test-Path $archive)) {
  $url = "https://github.com/godotengine/godot/releases/download/${Version}-stable/Godot_v${Version}-stable_mono_export_templates.tpz"
  & curl.exe -fL --retry 3 --connect-timeout 30 --max-time 1200 -o $archive $url
  if ($LASTEXITCODE -ne 0) { throw 'Failed to download .NET export templates.' }
}
$unpacked = Join-Path $env:RUNNER_TEMP 'godot-mono-templates'
Expand-Archive -LiteralPath $archive -DestinationPath $unpacked -Force
$destination = Join-Path $env:APPDATA "Godot/export_templates/${Version}.stable.mono"
New-Item -ItemType Directory -Force $destination | Out-Null
Copy-Item -Recurse -Force "$unpacked/templates/*" $destination
if (-not (Test-Path "$destination/windows_release_x86_64.exe")) {
  throw 'Windows .NET release template is missing.'
}
