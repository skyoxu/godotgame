# Phase 17 闄勫綍锛歐indows-only 蹇€熸寚寮曪紙鏈粨搴撴ā鏉匡級

1) 鏈湴杩愯涓庢祴璇?- 璁剧疆 PATH锛堝綋鍓嶄細璇濓級: `$env:Path = "$env:USERPROFILE\.dotnet;" + $env:Path`锛圙odot .NET 鏋勫缓闇€瑕侊級
- 杩愯 GdUnit4 娴嬭瘯: `./scripts/ci/run_gdunit_tests.ps1 -GodotBin "$env:GODOT_BIN"`
- 杩愯婕旂ず鍦烘櫙锛堥潪 headless锛? `"$env:GODOT_BIN" --path . --scene "res://Game.Godot/Scenes/Main.tscn"`

2) 瀵煎嚭 Windows 鍙墽琛?- 棰勮: `export_presets.cfg` 宸插寘鍚?鈥淲indows Desktop鈥濓紝杈撳嚭鍒?`build/Game.exe`
- 鍛戒护: `./scripts/ci/export_windows.ps1 -GodotBin "$env:GODOT_BIN" -Output build\Game.exe`
- 鎻愮ず: 闇€鍦?Godot Editor 涓畨瑁?Windows 瀵煎嚭妯℃澘锛圗ditor 鈫?Export 鈫?Manage Export Templates锛?
3) CI锛圙itHub Actions / Windows锛?- 宸ヤ綔娴? `.github/workflows/windows-ci.yml`
- 姝ラ: 瀹夎 .NET 鈫?涓嬭浇 Godot .NET 鈫?杩愯 GdUnit4 鈫?瀵煎嚭 .exe 鈫?涓婁紶 `build/Game.exe` 涓?`logs/ci/**`

4) 璺緞涓庢敞鎰忎簨椤?- `user://` 鏄犲皠: `%APPDATA%\Godot\app_userdata\<椤圭洰鍚?`锛堥」鐩悕鍙栬嚜 `project.godot` 鐨?`application/config/name`锛?- Headless 鎻愮ず: UI/闊抽鍦?headless 涓嬩笉绋冲畾锛岄€傞厤灞傛祴璇曚紭鍏?DataStore/ResourceLoader/浜嬩欢淇″彿
- Autoload 鍗曚緥: 宸插湪 `project.godot` 娉ㄥ唽 `EventBus/DataStore/Logger/Audio/Time/Input`锛屽満鏅腑鍙€氳繃 `/root/<Name>` 璁块棶

Commands (Windows-only):
- Test: `.\\scripts\\test.ps1 -GodotBin "$env:GODOT_BIN"`
- Export: `.\\scripts\\ci\\export_windows.ps1 -GodotBin "$env:GODOT_BIN" -Output build\\Game.exe`
- Smoke (headless): `.\\scripts\\ci\\smoke_headless.ps1 -GodotBin "$env:GODOT_BIN"`
- Smoke (exe): `.\\scripts\\ci\\smoke_exe.ps1 -ExePath build\\Game.exe`
