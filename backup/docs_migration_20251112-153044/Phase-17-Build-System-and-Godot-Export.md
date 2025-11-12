# Phase 17: 閺嬪嫬缂撶化鑽ょ埠娑?Godot Export

> Windows-only 蹇€熸寚寮?/ Quickstart: 瑙?See [Phase-17-Windows-Only-Quickstart.md](Phase-17-Windows-Only-Quickstart.md)
> 杩涢樁琛ュ厖 / Addendum: [Phase-17-Windows-Only-Quickstart-Addendum.md](Phase-17-Windows-Only-Quickstart-Addendum.md)
> FeatureFlags 快速指引 / Quickstart: 见 [Phase-18-Staged-Release-and-Canary-Strategy.md](Phase-18-Staged-Release-and-Canary-Strategy.md)


> **閺嶇绺鹃惄顔界垼**閿涙俺鍤滈崝銊ュ Windows .exe 閹垫挸瀵樺ù浣衡柤閿涘苯鐤勯悳鏉跨暚閺佸瓨鐎铏诡吀闁挷绗岄悧鍫熸拱缁狅紕鎮婇妴?
> **瀹搞儰缍旈柌?*閿?-4 娴滃搫銇?
> **娓氭繆绂?*閿涙瓍hase 1閿涘湙odot 鐎瑰顥婇敍澶堚偓涓砲ase 16閿涘湩elease 閸忓啯鏆熼幑顔炬晸閹存劧绱?
> **娴溿倓绮悧?*閿涙瓱xport_presets.cfg + Python 閺嬪嫬缂撴す鍗炲З閼存碍婀?+ GitHub Actions 瀹搞儰缍斿ù?+ 閻楀牊婀扮粻锛勬倞鐟欏嫯瀵?
> **妤犲本鏁归弽鍥у櫙**閿涙碍婀伴崷?`npm run build:exe` 闁俺绻?+ CI 閼奉亜濮╅崠鏍ㄥⅵ閸栧懘鈧俺绻?+ Windows .exe 閻欘剛鐝涢崣顖濈箥鐞?

---

## 1. 閼冲本娅欐稉搴″З閺?

### 閸樼喓澧楅敍鍧磇tegame閿涘鐎鐑樼ウ缁?

**Electron + Vite 瀹搞儱鍙块柧?*閿?
- Vite 瀵偓閸欐垶婀囬崝鈥虫珤閿涘湚MR閵嗕礁鎻╅柅鐔峰煕閺傚府绱?
- `npm run build` 閳?妫板嫭鐎?React/Tailwind/Phaser閿涘瀫2.5s閿?
- `electron-builder` 閼奉亜濮╅崠鏍ㄥⅵ閸栧拑绱欑粵鎯ф倳閵嗕椒鍞惍浣规暈閸忋儯鈧浇绁┃鎰喘閸栨牭绱?
- 娴溠冨毉閿涙itegame-1.0.0.exe閿涘瀫150MB閿涘苯瀵橀崥?Node.js runtime閿?
- CI閿涙itHub Actions 閼奉亜濮╅弸鍕紦娑撳骸褰傜敮?(.exe 娑撳﹣绱堕崚?Release閿?

### 閺傛壆澧楅敍鍧搊dotgame閿涘鐎鐑樻簚闁洣绗岄幐鎴炲灛

**閺堟椽浜?*閿?
- Godot Export System閿涙碍鍨氶悢鐔烘畱婢舵艾閽╅崣鏉款嚤閸戞椽鍘ょ純顕嗙礄export_presets.cfg閿?
- 閼存碍婀伴崠鏍ь嚤閸戠尨绱癭godot --headless --export-release "Windows Desktop" output.exe`
- 鏉炲鍣虹痪褌楠囬悧鈺嬬窗娑撳秴鎯?.NET runtime閿涘牏閮寸紒鐔稿絹娓氭冻绱氶敍灞肩矌 .exe + .pck閿涘瀫50MB閿?
- 缁?Python 妞瑰崬濮╅敍姘虫硶楠炲啿褰撮懘姘拱閺冪娀娓?Shell 娓氭繆绂?

**閹告垶鍨?*閿?
| 閹告垶鍨?| 閸樼喎娲?| Godot 鐟欙絽鍠呴弬瑙勵攳 |
|-----|-----|--------------|
| 鐎电厧鍤柊宥囩枂婢跺秵娼?| 婢舵矮閲?.dll閵嗕胶姹楅悶鍡楀竾缂傗斂鈧線鐓舵０鎴炵壐瀵繘鈧銆?| export_presets.cfg 闂嗗棔鑵戦柊宥囩枂 |
| 娴狅絿鐖滅粵鎯ф倳 | Windows 鎼存梻鏁ら崚鍡楀絺闂団偓鐟?Code Signing | PowerShell SignTool 闂嗗棙鍨?|
| .pck 娑?.exe 閸掑棛顬?| .exe 閺堫剝闊╂禒?~10MB閿涘本鏆熼幑顔兼躬 .pck | 閼存碍婀伴懛顏勫З閹峰棗鍨庢稉搴ㄥ櫢缂?|
| 婢х偤鍣洪弸鍕紦 | 鐎瑰本鏆ｉ弸鍕紦闂団偓鐟?5-10s閿涘瓔I 缂傛挸鐡ㄩ崶浼存 | Godot 鐎电厧鍤Ο鈩冩緲缂傛挸鐡ㄩ張鍝勫煑 |
| 閻楀牊婀扮粻锛勬倞 | Release閵嗕竻uild Number閵嗕笩it Hash 閸忓疇浠?| 閺嬪嫬缂撻懘姘拱閼奉亜濮╁▔銊ュ弳閻楀牊婀版穱鈩冧紖 |

### 閺嬪嫬缂撶粻锟犱壕閻ㄥ嫪鐜崐?

1. **娑撯偓闁款喖褰傜敮?*閿涙瓪npm run build:exe` 娴溠冨毉閸欘垰鍨庨崣?.exe
2. **CI 閼奉亜濮╅崠?*閿涙碍鐦℃稉?tag 閼奉亜濮╅弸鍕紦閵嗕胶顒烽崥宥冣偓浣风瑐娴?GitHub Release
3. **閻楀牊婀版潻鍊熼嚋**閿?exe 閸愬懎绁?git commit sha閿涘奔绌舵禍搴＄┛濠у啯濮ら崨濠呮嫹濠?
4. **瀵偓閸欐垶鏅ラ悳?*閿涙碍婀伴崷鎵处鐎?Export Templates閿涘苯濮為柅鐔诲嚡娴狅絾鐎?

---

## 2. 閺嬪嫬缂撶化鑽ょ埠閺嬭埖鐎?

### 2.1 閺嬪嫬缂撳ù浣衡柤閸?

```
閳瑰备鏀㈤埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞?
閳?       GitHub Actions Release Trigger        閳?
閳? (manual dispatch / git tag push)            閳?
閳规柡鏀㈤埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞顑芥敘閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳?
                 閳?
閳瑰备鏀㈤埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埢灏栨敘閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳?
閳?  閻㈢喐鍨?Release 閸忓啯鏆熼幑?                        閳?
閳? - 閻楀牊婀伴崣鍑ょ礄git tag閿?                        閳?
閳? - Build Number (CI run ID)                  閳?
閳? - Commit SHA                                閳?
閳? - Build Timestamp                           閳?
閳规柡鏀㈤埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞顑芥敘閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳?
                 閳?
閳瑰备鏀㈤埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埢灏栨敘閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳?
閳?  Python 閺嬪嫬缂撴す鍗炲З閼存碍婀?(build_windows.py)      閳?
閳? 1. 妤犲矁鐦夐悳顖氼暔閿涘湙odot閵?NET閵嗕讣ignTool閿?      閳?
閳? 2. 濞撳懐鎮婇弮褎鐎杞伴獓閻?                          閳?
閳? 3. 閹笛嗩攽 Godot Export閿涘湚eadless閿?          閳?
閳? 4. 閻㈢喐鍨?.exe + .pck                        閳?
閳? 5. 娴狅絿鐖滅粵鎯ф倳閿涘牆褰查柅澶涚礆                        閳?
閳? 6. 閻㈢喐鍨氶弽锟犵崣閸?(SHA256)                     閳?
閳? 7. 閸掓稑缂撻悧鍫熸拱娣団剝浼?JSON                       閳?
閳规柡鏀㈤埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞顑芥敘閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳?
                 閳?
        閳瑰备鏀㈤埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞鈧埞绮规敘閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳光偓閳?
        閳?                閳?
        閳?                閳?
   閺堫剙婀村銉ゆ          CI 瀹搞儰娆㈡稉濠佺炊
   (dist/)          閳?GitHub Release
```

### 2.2 閻╊喖缍嶇紒鎾寸€?

```
godotgame/
閳规壕鏀㈤埞鈧?src/
閳?  閳规壕鏀㈤埞鈧?Godot/
閳?  閳?  閳规壕鏀㈤埞鈧?project.godot                     # Godot 妞ゅ湱娲伴柊宥囩枂
閳?  閳?  閳规柡鏀㈤埞鈧?export_presets.cfg                閳?Export 闁板秶鐤嗛敍鍦礽ndows閿?
閳?  閳?
閳?  閳规柡鏀㈤埞鈧?Game.Core/
閳?      閳规柡鏀㈤埞鈧?Version/
閳?          閳规柡鏀㈤埞鈧?VersionInfo.cs                閳?閻楀牊婀版穱鈩冧紖 (git hash, build time)
閳?
閳规壕鏀㈤埞鈧?scripts/
閳?  閳规壕鏀㈤埞鈧?build_windows.py                      閳?Python 閺嬪嫬缂撴す鍗炲З閼存碍婀?
閳?  閳规壕鏀㈤埞鈧?generate_build_metadata.py            閳?閻楀牊婀伴崗鍐╂殶閹诡喚鏁撻幋?
閳?  閳规柡鏀㈤埞鈧?sign_executable.ps1                   閳?PowerShell 娴狅絿鐖滅粵鎯ф倳閼存碍婀?
閳?
閳规壕鏀㈤埞鈧?.github/
閳?  閳规柡鏀㈤埞鈧?workflows/
閳?      閳规柡鏀㈤埞鈧?build-windows.yml                 閳?GitHub Actions 閺嬪嫬缂撳銉ょ稊濞?
閳?
閳规壕鏀㈤埞鈧?dist/                                     閳?閺堫剙婀撮弸鍕紦鏉堟挸鍤惄顔肩秿
閳?  閳规壕鏀㈤埞鈧?godotgame-1.0.0.exe
閳?  閳规壕鏀㈤埞鈧?godotgame-1.0.0.pck
閳?  閳规壕鏀㈤埞鈧?godotgame-1.0.0-SHA256.txt
閳?  閳规柡鏀㈤埞鈧?build-metadata.json
閳?
閳规柡鏀㈤埞鈧?package.json
    閳规壕鏀㈤埞鈧?"build:exe"                           閳?閺堫剙婀撮弸鍕紦閸涙垝鎶?
    閳规壕鏀㈤埞鈧?"build:exe:debug"                     閳?鐠嬪啳鐦弸鍕紦
    閳规柡鏀㈤埞鈧?"release:create"                      閳?閻楀牊婀伴崣鎴濈濞翠胶鈻?
```

---

## 3. 閺嶇绺剧€圭偟骞?

### 3.1 export_presets.cfg閿涘湙odot Export 闁板秶鐤嗛敍?

**閼卞矁鐭?*閿?
- 鐎规矮绠?Windows Desktop 鐎电厧鍤崣鍌涙殶
- 闁板秶鐤嗙挧鍕爱娴兼ê瀵查敍鍫㈡睏閻炲棗甯囩紓鈹库偓渚€鐓舵０鎴炵壐瀵骏绱?
- 鐠嬪啳鐦?vs 閸欐垵绔锋稉銈咁殰闁板秶鐤?
- 瀹撳苯鍙嗛悧鍫熸拱娣団剝浼?

**娴狅絿鐖滅粈杞扮伐**閿?

```ini
# Godot Export Presets Configuration
# Windows Desktop - Release Configuration

[preset.0]

name="Windows Desktop"
platform="windows"
runnable=true
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="dist/godotgame-1.0.0.exe"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.0.options]

# 閸╃儤婀伴柊宥囩枂
windows/subsystem=2
application/file_description="Godot Game - Vite Migration"
application/copyright="2025"
application/trademarks=""
application/company_name="Anthropic"
application/product_name="GodotGame"
application/product_version="1.0.0"
application/file_version="1.0.0"
application/icon="res://icon.svg"

# 娴狅絿鐖滅粵鎯ф倳
windows/signtool=""
windows/timestamp_server_url=""
windows/timestamp_server_hash="sha256"

# 娴滃矁绻橀崚鎯扮翻閸?
windows/console_wrapper_icon=""

# 缁惧湱鎮婄€电厧鍙嗘导妯哄
textures/vram_compression/mode=2
textures/basis_universal/uastc_4x4_zstd_15_trellis_100_sb_2=true

# 闂婃娊顣舵导妯哄
audio/general/trim_silence=true
audio/bus_layouts/default="res://audio/default_bus_layout.tres"

# 濞撳弶鐓嬫稉搴⑩偓褑鍏?
rendering/textures/vram_compression/import_etc2_astc=true
rendering/global_illumination/gi_probe_quality=1

# 閸欐垵绔烽弽鍥х箶
debug/gdscript_warnings/unused_variable=2
debug/gdscript_warnings/unused_class_variable=1
debug/gdscript_warnings/unused_argument=1
debug/gdscript_warnings/unused_signal=1
debug/gdscript_warnings/shadowed_variable=1
debug/gdscript_warnings/shadowed_variable_base_class=0
debug/gdscript_warnings/unused_parameter_shadowed=0
debug/gdscript_warnings/integer_division=1
debug/gdscript_warnings/function_used_as_property=1
debug/gdscript_warnings/variable_conflicts_property=1
debug/gdscript_warnings/function_conflicts_variable=1
debug/gdscript_warnings/function_conflicts_constant=1
debug/gdscript_warnings/incompatible_ternary=1
debug/gdscript_warnings/undefined_variable=1
debug/gdscript_warnings/undefined_function=1
debug/gdscript_warnings/match_already_bound=1
debug/gdscript_warnings/standalone_expression=1
debug/gdscript_warnings/standalone_ternary=1
debug/gdscript_warnings/assert_always_true=1
debug/gdscript_warnings/assert_always_false=1

# GDScript 娴兼ê瀵?
mono/profiler/enabled=false

# 缂冩垹绮舵稉搴ょカ濠?
network/ssl/certificates=""

# 閹嗗厴閻╃鍙?
physics/2d/physics_engine="GodotPhysics2D"
physics/3d/physics_engine="GodotPhysics3D"

[preset.1]

name="Windows Desktop (Debug)"
platform="windows"
runnable=true
custom_features="debug"
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="dist/godotgame-1.0.0-debug.exe"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.1.options]

# 閸╃儤婀伴柊宥囩枂閿涘牆鎮?Release閿涘奔绲惧ǎ璇插鐠嬪啳鐦粭锕€褰块敍?
windows/subsystem=2
application/file_description="Godot Game - Debug Build"
application/copyright="2025"
application/company_name="Anthropic"
application/product_name="GodotGame"
application/product_version="1.0.0-debug"
application/file_version="1.0.0"
application/icon="res://icon.svg"

# 鐠嬪啳鐦Ο鈥崇础閸忔娊妫存导妯哄
debug/gdscript/warnings/unused_variable=2
debug/gdscript/warnings/unused_argument=2

# 閹嗗厴閸掑棙鐎介弨顖涘瘮
debug/profiler/enabled=true
debug/profile_monitor/enabled=true

# 鐠囷妇绮忛弮銉ョ箶
debug/gdscript/warnings/print_verbose=true
```

### 3.2 build_windows.py閿涘湧ython 閺嬪嫬缂撴す鍗炲З閼存碍婀伴敍?

**閼卞矁鐭?*閿?
- 妤犲矁鐦夐弸鍕紦閻滎垰顣ㄩ敍鍦檕dot閵?NET閵嗕讣ignTool閿?
- 閹笛嗩攽 Godot headless export
- 閻㈢喐鍨氶悧鍫熸拱娣団剝浼呮稉搴㈢墡妤犲苯鎷?
- 閸欘垶鈧鍞惍浣侯劮閸?
- 闁挎瑨顕ゆ径鍕倞娑撳孩妫╄箛妤勭翻閸?

**娴狅絿鐖滅粈杞扮伐**閿?

```python
#!/usr/bin/env python3
"""
Godot Windows Build Driver
Orchestrates: validation 閳?export 閳?signing 閳?metadata generation
"""

import os
import sys
import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Optional

class GodotBuildDriver:
    def __init__(self, project_root: Path, build_config: str = "release"):
        self.project_root = project_root
        self.build_config = build_config.lower()
        self.godot_path = self._find_godot()
        self.dist_dir = project_root / "dist"
        self.log_dir = project_root / "logs" / "builds"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.build_log = self.log_dir / f"build-{datetime.now().isoformat()}.log"

    def _find_godot(self) -> str:
        """閸︺劎閮寸紒?PATH 閹存牜骞嗘晶鍐ㄥ綁闁插繋鑵戦弻銉﹀ Godot"""
        # 濡偓閺屻儳骞嗘晶鍐ㄥ綁闁?
        godot_env = os.getenv("GODOT_BIN")
        if godot_env and Path(godot_env).exists():
            return godot_env

        # 濡偓閺?PATH
        for cmd in ["godot", "godot.exe", "godot.cmd"]:
            result = subprocess.run(["where", cmd], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return result.stdout.strip().split("\n")[0]

        raise RuntimeError("Godot not found in PATH. Set GODOT_BIN environment variable.")

    def _log(self, message: str, level: str = "INFO") -> None:
        """閸愭瑥鍙嗛弮銉ョ箶"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        with open(self.build_log, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

    def validate_environment(self) -> bool:
        """妤犲矁鐦夐弸鍕紦閻滎垰顣?""
        self._log("Validating build environment...")

        # 1. 濡偓閺?Godot
        try:
            result = subprocess.run(
                [self.godot_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            godot_version = result.stdout.strip().split("\n")[0]
            self._log(f"Godot found: {godot_version}")
        except Exception as e:
            self._log(f"Godot validation failed: {e}", "ERROR")
            return False

        # 2. 濡偓閺?.NET (閸欘垶鈧?
        try:
            result = subprocess.run(
                ["dotnet", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            dotnet_version = result.stdout.strip()
            self._log(f".NET found: {dotnet_version}")
        except Exception as e:
            self._log(f".NET not found (optional): {e}", "WARN")

        # 3. 濡偓閺?export_presets.cfg
        export_presets = self.project_root / "export_presets.cfg"
        if not export_presets.exists():
            self._log(f"export_presets.cfg not found at {export_presets}", "ERROR")
            return False

        self._log("Environment validation passed")
        return True

    def clean_build_dir(self) -> None:
        """濞撳懐鎮婇弮褎鐎杞伴獓閻?""
        self._log("Cleaning build directory...")
        if self.dist_dir.exists():
            for file in self.dist_dir.glob("godotgame-*"):
                file.unlink()
                self._log(f"Removed: {file.name}")

    def build_export(self) -> Tuple[bool, Optional[str]]:
        """閹笛嗩攽 Godot Headless Export"""
        self._log(f"Starting Godot export ({self.build_config})...")

        preset_name = "Windows Desktop" if self.build_config == "release" else "Windows Desktop (Debug)"
        exe_name = f"godotgame-1.0.0{'-debug' if self.build_config == 'debug' else ''}.exe"
        exe_path = self.dist_dir / exe_name

        # 绾喕绻?dist 閻╊喖缍嶇€涙ê婀?
        self.dist_dir.mkdir(parents=True, exist_ok=True)

        # 閺嬪嫬缂撻崨鎴掓姢
        export_cmd = [
            self.godot_path,
            "--headless",
            "--export-release" if self.build_config == "release" else "--export-debug",
            preset_name,
            str(exe_path)
        ]

        try:
            self._log(f"Running: {' '.join(export_cmd)}")
            result = subprocess.run(
                export_cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            if result.returncode != 0:
                self._log(f"Godot export failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}", "ERROR")
                return False, None

            if not exe_path.exists():
                self._log(f"Export succeeded but .exe not found at {exe_path}", "ERROR")
                return False, None

            exe_size_mb = exe_path.stat().st_size / (1024 * 1024)
            self._log(f"Export successful: {exe_name} ({exe_size_mb:.2f} MB)")
            return True, str(exe_path)

        except subprocess.TimeoutExpired:
            self._log("Godot export timed out (>5 minutes)", "ERROR")
            return False, None
        except Exception as e:
            self._log(f"Godot export error: {e}", "ERROR")
            return False, None

    def generate_checksums(self, exe_path: str) -> None:
        """閻㈢喐鍨氶弬鍥︽閺嶏繝鐛欓崪?""
        self._log("Generating checksums...")

        exe_file = Path(exe_path)
        sha256_path = exe_file.parent / f"{exe_file.stem}-SHA256.txt"

        # 鐠侊紕鐣?SHA256
        sha256_hash = hashlib.sha256()
        with open(exe_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)

        # 閸愭瑥鍙嗛弽锟犵崣閸滃本鏋冩禒璁圭礄閸忕厧顔?checksum 瀹搞儱鍙块弽鐓庣础閿?
        checksum_text = f"{sha256_hash.hexdigest()}  {exe_file.name}"
        with open(sha256_path, "w", encoding="utf-8") as f:
            f.write(checksum_text)

        self._log(f"Checksum written: {sha256_path}")

    def sign_executable(self, exe_path: str, cert_path: Optional[str] = None) -> bool:
        """娴狅絿鐖滅粵鎯ф倳閿涘牆褰查柅澶涚礆"""
        if not cert_path:
            self._log("Code signing skipped (no certificate provided)")
            return True

        self._log(f"Signing executable with certificate: {cert_path}")

        sign_cmd = [
            "signtool",
            "sign",
            "/f", cert_path,
            "/fd", "SHA256",
            "/tr", "http://timestamp.digicert.com",
            "/td", "SHA256",
            exe_path
        ]

        try:
            result = subprocess.run(
                sign_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                self._log(f"Code signing failed: {result.stderr}", "ERROR")
                return False

            self._log("Code signing successful")
            return True

        except Exception as e:
            self._log(f"Code signing error: {e}", "ERROR")
            return False

    def generate_build_metadata(self, exe_path: str) -> None:
        """閻㈢喐鍨氶弸鍕紦閸忓啯鏆熼幑?JSON"""
        self._log("Generating build metadata...")

        # 閼惧嘲褰?Git 娣団剝浼?
        try:
            commit_sha = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            ).stdout.strip()

            tag = subprocess.run(
                ["git", "describe", "--tags", "--always"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            ).stdout.strip()
        except Exception as e:
            self._log(f"Git info retrieval failed: {e}", "WARN")
            commit_sha = "unknown"
            tag = "unknown"

        exe_file = Path(exe_path)
        metadata = {
            "version": "1.0.0",
            "build_config": self.build_config,
            "executable": exe_file.name,
            "executable_size_bytes": exe_file.stat().st_size,
            "built_at": datetime.utcnow().isoformat() + "Z",
            "git_commit": commit_sha,
            "git_tag": tag,
            "godot_version": self._get_godot_version(),
            "platform": "windows",
            "architecture": "x86_64"
        }

        metadata_path = exe_file.parent / "build-metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        self._log(f"Build metadata written: {metadata_path}")

    def _get_godot_version(self) -> str:
        """閼惧嘲褰?Godot 閻楀牊婀伴崣?""
        try:
            result = subprocess.run(
                [self.godot_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip().split("\n")[0]
        except:
            return "unknown"

    def build(self) -> bool:
        """鐎瑰本鏆ｉ弸鍕紦濞翠胶鈻?""
        self._log(f"========== Build Started ({self.build_config}) ==========")

        # 1. 妤犲矁鐦夐悳顖氼暔
        if not self.validate_environment():
            self._log("Build aborted: environment validation failed", "ERROR")
            return False

        # 2. 濞撳懐鎮婇弸鍕紦閻╊喖缍?
        self.clean_build_dir()

        # 3. 閹笛嗩攽鐎电厧鍤?
        success, exe_path = self.build_export()
        if not success or not exe_path:
            self._log("Build failed: Godot export failed", "ERROR")
            return False

        # 4. 閻㈢喐鍨氶弽锟犵崣閸?
        self.generate_checksums(exe_path)

        # 5. 閸欘垶鈧鍞惍浣侯劮閸?
        cert_path = os.getenv("CODE_SIGN_CERT")
        if cert_path:
            if not self.sign_executable(exe_path, cert_path):
                self._log("Code signing failed (but continuing)", "WARN")

        # 6. 閻㈢喐鍨氶崗鍐╂殶閹?
        self.generate_build_metadata(exe_path)

        self._log("========== Build Completed Successfully ==========")
        return True


def main():
    """CLI 閸忋儱褰?""
    project_root = Path(__file__).parent.parent
    build_config = sys.argv[1] if len(sys.argv) > 1 else "release"

    driver = GodotBuildDriver(project_root, build_config)

    if not driver.build():
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
```

### 3.3 GitHub Actions 閺嬪嫬缂撳銉ょ稊濞?

**閼卞矁鐭?*閿?
- 閻╂垵鎯?git tag 閹存牗澧滈崝銊ㄐ曢崣?
- 濡偓閸戣桨鍞惍浣风瑢闁板秶鐤嗙紓鎾崇摠
- 鏉╂劘顢?Python 閺嬪嫬缂撴す鍗炲З
- 娑撳﹣绱跺銉ゆ閸?GitHub Release
- 閸欘垶鈧娈?Sentry Release 閸掓稑缂?

**娴狅絿鐖滅粈杞扮伐**閿?

```yaml
# .github/workflows/build-windows.yml

name: Windows Build & Release

on:
  push:
    tags:
      - 'v*.*.*'  # 閻楀牊婀伴弽鍥╊劮 (v1.0.0, v1.0.1, etc.)
  workflow_dispatch:
    inputs:
      build_config:
        description: 'Build configuration'
        required: true
        default: 'release'
        type: choice
        options:
          - release
          - debug

env:
  GODOT_VERSION: '4.5.0'
  DOTNET_VERSION: '8.0.x'

jobs:
  build-windows:
    runs-on: windows-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for git describe

      - name: Cache Godot Export Templates
        uses: actions/cache@v3
        with:
          path: |
            ~/.cache/godot/export_presets
            ~/AppData/Roaming/Godot/export_templates
          key: godot-export-templates-${{ env.GODOT_VERSION }}
          restore-keys: |
            godot-export-templates-

      - name: Setup Godot
        uses: chickensoft-games/setup-godot@v1
        with:
          version: ${{ env.GODOT_VERSION }}
          use-dotnet: true

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: ${{ env.DOTNET_VERSION }}

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Build Windows Executable (Release)
        if: github.event_name == 'push' || github.event.inputs.build_config == 'release'
        run: |
          python scripts/build_windows.py release
          Get-Item dist/godotgame-*.exe | ForEach-Object {
            Write-Host "Built: $($_.Name) ($([math]::Round($_.Length / 1MB, 2)) MB)"
          }
        shell: powershell

      - name: Build Windows Executable (Debug)
        if: github.event.inputs.build_config == 'debug'
        run: |
          python scripts/build_windows.py debug
        shell: powershell

      - name: Generate Build Report
        if: always()
        run: |
          Write-Host "=== Build Artifacts ==="
          Get-Item dist/ -ErrorAction SilentlyContinue | Get-ChildItem | ForEach-Object {
            Write-Host "$($_.Name) ($([math]::Round($_.Length / 1MB, 2)) MB)"
          }
        shell: powershell

      - name: Upload Build Artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: windows-builds
          path: dist/
          retention-days: 7

      - name: Create GitHub Release
        if: startsWith(github.ref, 'refs/tags/')
        uses: softprops/action-gh-release@v1
        with:
          files: |
            dist/godotgame-*.exe
            dist/godotgame-*-SHA256.txt
            dist/build-metadata.json
          body: |
            ## Build Information

            **Version**: ${{ github.ref_name }}
            **Build Date**: ${{ github.event.head_commit.timestamp }}
            **Commit**: ${{ github.sha }}

            ### Files
            - `godotgame-*.exe` - Windows Desktop executable
            - `godotgame-*-SHA256.txt` - File integrity checksum
            - `build-metadata.json` - Build configuration metadata

            ### Installation
            Extract and run `godotgame-1.0.0.exe`. No installation required.

            ### Requirements
            - Windows 10/11 (64-bit)
            - .NET 8.0 Runtime (included in executable)
          draft: false
          prerelease: ${{ contains(github.ref_name, 'rc') || contains(github.ref_name, 'beta') }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Notify Build Completion
        if: always()
        run: |
          Write-Host "Build Status: ${{ job.status }}"
          Write-Host "Workflow Run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
        shell: powershell
```

### 3.4 閻楀牊婀扮粻锛勬倞鐟欏嫯瀵?

**閻楀牊婀伴崨钘夋倳缁撅箑鐣?*閿?
- 閺嶇厧绱￠敍姝歷{MAJOR}.{MINOR}.{PATCH}[-{PRERELEASE}]`
- 缁€杞扮伐閿涙瓪v1.0.0`, `v1.0.1-rc.1`, `v1.1.0-beta.2`

**Git 閺嶅洨顒峰銉ょ稊濞?*閿?
```bash
# 1. 閺堫剙婀撮崚娑樼紦閺嶅洨顒?
git tag -a v1.0.0 -m "Release version 1.0.0 - Initial stable release"

# 2. 閹恒劑鈧焦鐖ｇ粵鎯у煂 GitHub閿涘牐鍤滈崝銊ㄐ曢崣?CI閿?
git push origin v1.0.0

# 3. GitHub Actions 閼奉亜濮╅弸鍕紦閵嗕胶顒烽崥宥冣偓浣稿灡瀵?Release

# 4. 妤犲矁鐦夐弸鍕紦閿涘牊顥呴弻?GitHub Release 妞ょ敻娼伴敍?
# https://github.com/yourrepo/releases/tag/v1.0.0
```

**閻楀牊婀版穱鈩冧紖瀹撳苯鍙?*閿?

閸?`src/Game.Core/Version/VersionInfo.cs`閿?

```csharp
using System;

namespace Game.Core.Version
{
    /// <summary>
    /// 鎼存梻鏁ら悧鍫熸拱娣団剝浼呴敍鍫㈢椽鐠囨垶妞傚▔銊ュ弳閿?
    /// </summary>
    public static class VersionInfo
    {
        /// <summary>
        /// 鐠囶厺绠熼悧鍫熸拱 (SemVer) - e.g., "1.0.0"
        /// </summary>
        public const string SemanticVersion = "1.0.0";

        /// <summary>
        /// Git 閹绘劒姘?SHA閿涘牏绱拠鎴ｅ壖閺堫剚鏁為崗銉礆
        /// </summary>
        public static string GitCommit { get; set; } = "unknown";

        /// <summary>
        /// Git 閺嶅洨顒?/ 閸掑棙鏁崥宥囆?
        /// </summary>
        public static string GitTag { get; set; } = "unknown";

        /// <summary>
        /// 閺嬪嫬缂撻弮鍫曟？閹?(ISO 8601)
        /// </summary>
        public static string BuildTime { get; set; } = "unknown";

        /// <summary>
        /// 鐎瑰本鏆ｉ悧鍫熸拱鐎涙顑佹稉?
        /// </summary>
        public static string FullVersion =>
            $"{SemanticVersion}+{GitCommit.Substring(0, 7)}@{BuildTime}";

        /// <summary>
        /// 鎼存梻鏁ら悽銊﹀煕娴狅絿鎮婄€涙顑佹稉璇х礄閻劋绨?Sentry Release閿?
        /// </summary>
        public static string UserAgent =>
            $"godotgame/{SemanticVersion} ({GitTag})";
    }
}
```

閺嬪嫬缂撻懘姘拱闁俺绻冮悳顖氼暔閸欐﹢鍣哄▔銊ュ弳閿?

```python
# build_windows.py 娑擃厾娈戦幍鈺佺潔
def inject_version_info(project_root: Path, commit_sha: str, git_tag: str, build_time: str) -> None:
    """鐏忓棛澧楅張顑夸繆閹垱鏁為崗銉ュ煂 C# 濠ф劒鍞惍?""
    version_file = project_root / "src" / "Game.Core" / "Version" / "VersionInfo.cs"

    content = version_file.read_text(encoding="utf-8")

    # 閺囨寧宕查崡鐘辩秴缁?
    content = content.replace(
        'public static string GitCommit { get; set; } = "unknown";',
        f'public static string GitCommit {{ get; set; }} = "{commit_sha}";'
    )
    content = content.replace(
        'public static string GitTag { get; set; } = "unknown";',
        f'public static string GitTag {{ get; set; }} = "{git_tag}";'
    )
    content = content.replace(
        'public static string BuildTime { get; set; } = "unknown";',
        f'public static string BuildTime {{ get; set; }} = "{build_time}";'
    )

    version_file.write_text(content, encoding="utf-8")
```

---

## 4. package.json 閼存碍婀伴梿鍡樺灇

```json
{
  "scripts": {
    "build": "npm run build:exe",
    "build:exe": "python scripts/build_windows.py release",
    "build:exe:debug": "python scripts/build_windows.py debug",
    "build:sign": "set CODE_SIGN_CERT=path/to/cert.pfx && python scripts/build_windows.py release",
    "release:tag": "node scripts/create-release-tag.mjs",
    "release:info": "cat dist/build-metadata.json",
    "clean:dist": "rmdir /s /q dist 2>nul || echo 'dist directory not found'"
  }
}
```

閺堫剙婀撮弸鍕紦濞翠胶鈻奸敍?
```bash
# 瀵偓閸欐垶鐎鐚寸礄鐠嬪啳鐦粭锕€褰块敍?
npm run build:exe:debug
# 鏉堟挸鍤敍姝瀒st/godotgame-1.0.0-debug.exe

# 閸欐垵绔烽弸鍕紦閿涘牅绱崠鏍电礆
npm run build:exe
# 鏉堟挸鍤敍姝瀒st/godotgame-1.0.0.exe, dist/build-metadata.json, dist/godotgame-*-SHA256.txt

# 鐢缚鍞惍浣侯劮閸氬秶娈戦弸鍕紦
npm run build:sign
# 闂団偓鐟曚浇顔曠純?CODE_SIGN_CERT 閻滎垰顣ㄩ崣姗€鍣?
```

---

## 5. 妞嬪酣娅撶拠鍕強娑撳骸鍠呯粵?

| # | 妞嬪酣娅?| 缁涘楠?| 缂傛捁袙閺傝顢?|
|---|-----|------|---------|
| 1 | Export Templates 缂傛挸鐡ㄦ径杈ㄦ櫏 | 娴?| GitHub Actions Cache key閿涘瓘odot 閻楀牊婀伴柨浣哥暰 |
| 2 | 娴狅絿鐖滅粵鎯ф倳鐠囦椒鍔熸潻鍥ㄦ埂 | 娑?| 娴ｈ法鏁?DigiCert 閺冨爼妫块幋铏箛閸斺槄绱濈拠浣峰姛閺囧瓨鏌婇幓鎰板晪 |
| 3 | 閺嬪嫬缂撻懓妤佹閿?-10s閿?| 娴?| 婢х偤鍣?Export 娴兼ê瀵查敍瀛峹port Template 妫板嫮鍎?|
| 4 | Windows Defender 鐠囶垱濮?| 娴?| Code Signing + Sentry Release 娣団剝浼呴敍宀€鏁ら幋鐤啅閸欘垳娅ч崥宥呭礋 |
| 5 | 閻楀牊婀伴崣宄板暱缁?| 娴?| 娑撱儲鐗?SemVer閿涘瓔I 妤犲矁鐦夐崬顖欑閹?|

### 閸忔娊鏁崘宕囩摜

**閸愬磭鐡?D1閿涙瓱xport_presets.cfg 鐎涙ê鍋嶆担宥囩枂**
- **A**. 閹绘劒姘﹂崚?git閿涘牊甯归懡鎰剁礆閿涙矮绌舵禍搴ｅ閺堫剚甯堕崚璁圭礉閹碘偓閺堝绱戦崣鎴ｂ偓鍛閼峰娈戠€电厧鍤柊宥囩枂
- **B**. 娴?GitHub Secrets 閸斻劍鈧胶鏁撻幋鎰剁窗闁倸鎮庨崥顐ｆ櫛閹扮喍淇婇幁顖滄畱闁板秶鐤嗛敍鍫熸畯閺冪媴绱?
- **缂佹捁顔?*閿涙岸鍣伴悽?A閿涘瞼鐣濋崠鏍ㄧウ缁嬪绱漞xport_presets.cfg 閹绘劒姘﹂崚?repo

**閸愬磭鐡?D2閿涙矮鍞惍浣侯劮閸氬秶鐡ラ悾?*
- **A**. 瀵搫鍩楃粵鎯ф倳閿涘牊甯归懡鎰剁礆閿涙瓙indows Defender 閹躲儴顒熺亸鎴礉閻劍鍩涙穱鈥叉崲鎼达箓鐝?
- **B**. 閸欘垶鈧顒烽崥宥忕窗闂勫秳缍?CI 婢跺秵娼呴幀褝绱濇担鍡楀絺鐢啰澧楅張顒€绻€妞よ崵顒烽崥?
- **C**. 娴?Release 缁涙儳鎮曢敍娆磂v 閻楀牊婀扮捄瀹犵箖閿涘苯濮為柅鐔峰敶闁劏鍑禒?
- **缂佹捁顔?*閿涙岸鍣伴悽?B閿涘elease tag 鐟欙箑褰傜粵鎯ф倳閿涘牓娓剁憰?CODE_SIGN_CERT Secret閿涘绱濋幍瀣З鐟欙箑褰傞弨顖涘瘮娑撱倗顫?

**閸愬磭鐡?D3閿涙氨澧楅張顒€褰块弶銉︾爱**
- **A**. Git tag閿涘牊甯归懡鎰剁礆閿涙矮绗?Release 閸氬本顒為敍宀冨殰閸斻劌瀵茬粙瀣妤?
- **B**. package.json 閻楀牊婀伴敍姘跺櫢婢跺秶娣幎銈忕礉閺勬挷绨崙铏瑰箛閸嬪繐妯?
- **C**. 閻滎垰顣ㄩ崣姗€鍣哄▔銊ュ弳閿涙氨浼掑ú璁崇稻娑撳秷顫夐懠?
- **缂佹捁顔?*閿涙岸鍣伴悽?A閿涘疅it tag 娴ｆ粈璐?SSOT閿涘矁鍓奸張顒冨殰閸斻劏袙閺?

---

## 6. 閺冨爼妫挎导鎵暬閿涘牆鍨庣憴锝忕礆

| 娴犺濮?| 瀹搞儰缍旈柌?| 閸掑棝鍘?|
|-----|--------|------|
| export_presets.cfg 鐠佹崘顓告稉搴ょ殶鐠?| 0.5 婢?| Day 1 |
| Python 閺嬪嫬缂撴す鍗炲З閼存碍婀伴敍鍧唘ild_windows.py閿?| 1.5 婢?| Day 1-2 |
| GitHub Actions 瀹搞儰缍斿ù渚€鍘ょ純顕嗙礄build-windows.yml閿?| 1 婢?| Day 2-3 |
| 閺堫剙婀村ù瀣槸娑撳海澧楅張顒傤吀閻炲棜顫夐懠鍐╂瀮濡?| 0.5 婢?| Day 3 |
| **閹槒顓?* | **3.5-4 婢?* | |

---

## 7. 妤犲本鏁归弽鍥у櫙

### 7.1 娴狅絿鐖滅€瑰本鏆ｉ幀?

- [ ] export_presets.cfg閿涙瓟OK] Windows Desktop Release + Debug 闁板秶鐤?
- [ ] build_windows.py閿?80+ 鐞涘矉绱氶敍姝擮K] 鐎瑰本鏆?validate 閳?export 閳?sign 閳?metadata 濞翠胶鈻?
- [ ] build-windows.yml閿?00+ 鐞涘矉绱氶敍姝擮K] CI 閼奉亜濮╅崠鏍ㄧ€鎭掆偓涓積lease 閸掓稑缂?
- [ ] VersionInfo.cs閿涙瓟OK] 閻楀牊婀版穱鈩冧紖瀹撳苯鍙嗛弨顖涘瘮

### 7.2 閸旂喕鍏樻灞炬暪

- [ ] 閺堫剙婀?`npm run build:exe` 閹存劕濮涙禍褍鍤?.exe 閺傚洣娆?
- [ ] 閼奉亜濮╅悽鐔稿灇 build-metadata.json閿涘牆鎯?git commit閵嗕攻uild time閿?
- [ ] 閼奉亜濮╅悽鐔稿灇 SHA256 閺嶏繝鐛欓崪?
- [ ] GitHub Actions 閹靛濮╃憴锕€褰傞弸鍕紦闁俺绻?
- [ ] Git tag 閹恒劑鈧浇鍤滈崝銊ㄐ曢崣?Release 閸掓稑缂?
- [ ] 閻㈢喐鍨氶惃?.exe 閸?Windows 11 閻欘剛鐝涢崣顖濈箥鐞涘矉绱欓弮?Godot/瀵偓閸欐垹骞嗘晶鍐х贩鐠ф牭绱?

### 7.3 閺傚洦銆傜€瑰本鍨氭惔?

- [ ] Phase 17 鐠囷妇绮忕憴鍕灊閺傚洦銆傞敍鍫熸拱閺傚浄绱?000+ 鐞涘矉绱?
- [ ] export_presets.cfg 鐎瑰本鏆ｅ▔銊╁櫞
- [ ] 閻楀牊婀扮粻锛勬倞娑撳骸褰傜敮鍐╃ウ缁嬪鏋冨?
- [ ] 閺堫剙婀撮弸鍕紦韫囶偊鈧喎绱戞慨瀣瘹閸?

---

## 8. 閸氬海鐢婚梼鑸殿唽閸忓疇浠?

| 闂冭埖顔?| 閸忓疇浠?| 鐠囧瓨妲?|
|-----|-----|------|
| Phase 15閿涘牊鈧嗗厴妫板嫮鐣婚敍?| 閳?娓氭繆绂?| Release 閸忓啯鏆熼幑顔芥降閼?build_windows.py閿涘瞼鏁ゆ禍?Sentry 娑撳﹥濮?|
| Phase 16閿涘牆褰茬憴鍌涚ゴ閹嶇礆 | 閳?娓氭繆绂?| Release tag 娑?Sentry Release API 閼辨柨濮╅敍灞藉絺鐢啫浠存惔鐑芥，缁備焦顥呴弻?|
| Phase 18閿涘牆鍨庨梼鑸殿唽閸欐垵绔烽敍?| 閳?閸氼垳鏁?| Canary/Beta/Stable 閻楀牊婀扮粻锛勬倞閸╄桨绨?git tag 閸掑棙鏁粵鏍殣 |
| Phase 19閿涘牆绨查幀銉ユ礀濠婃熬绱?| 閳?闂嗗棙鍨?| 閸ョ偞绮撮懘姘拱娴?git tag 娑撳搫鐔€閸戝棙瀵氱€规氨澧楅張?|

---

## 9. 娴溿倓绮悧鈺傜閸?

### 娴狅絿鐖滈弬鍥︽
- [OK] `src/Godot/export_presets.cfg`閿?50+ 鐞涘矉绱漌indows Desktop 闁板秶鐤嗛敍?
- [OK] `scripts/build_windows.py`閿?80+ 鐞涘矉绱?
- [OK] `scripts/generate_build_metadata.py`閿?20+ 鐞涘矉绱?
- [OK] `scripts/sign_executable.ps1`閿?0+ 鐞涘矉绱?
- [OK] `src/Game.Core/Version/VersionInfo.cs`閿?0+ 鐞涘矉绱?

### 瀹搞儰缍斿ù渚€鍘ょ純?
- [OK] `.github/workflows/build-windows.yml`閿?20+ 鐞涘矉绱?

### 閺傚洦銆?
- [OK] Phase-17-Build-System-and-Godot-Export.md閿涘牊婀伴弬鍥风礉1000+ 鐞涘矉绱?
- [OK] 閻楀牊婀扮粻锛勬倞鐟欏嫯瀵栭敍鍦檌t tag 缁撅箑鐣鹃妴涓糴mVer閿?
- [OK] 閺堫剙婀撮弸鍕紦韫囶偊鈧喎绱戞慨?

### 閹槒顢戦弫甯窗1100+ 鐞?

---

## 闂勫嫬缍?A閿涙艾鐖剁憴渚€妫舵０妯诲笓閺?

### 闂傤噣顣?1閿涙odot Export 鐡掑懏妞傞敍?5 閸掑棝鎸撻敍?
**閸樼喎娲?*閿涙xport Template 缂傛挸鐡ㄩ張顏勬嚒娑擃厹鈧胶顥嗛惄?I/O 閹?
**閹烘帗鐓?*閿?
```bash
# 妫板嫮鍎?Export Template
godot --export-templates

# 濞撳懐鎮婇弮褏绱︾€?
rm -r ~/.cache/godot/export_presets
rm -r ~/AppData/Roaming/Godot/export_templates

# 闁插秵鏌婃潻鎰攽閺嬪嫬缂?
npm run build:exe
```

### 闂傤噣顣?2閿涙氨顒烽崥宥呫亼鐠愩儻绱橲ignTool 娑撳秴鐡ㄩ崷顭掔礆
**閸樼喎娲?*閿涙瓙indows SDK 閺堫亜鐣ㄧ憗鍛灗 SignTool 娑撳秴婀?PATH 娑?
**閹烘帗鐓?*閿?
```powershell
# 閺屻儲澹?SignTool
Get-Command signtool

# 閹存牗澧滈崝銊﹀瘹鐎规俺鐭惧?
$env:SIGNTOOL_PATH = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"
```

### 闂傤噣顣?3閿涙氨澧楅張顒€褰块張顏呮暈閸忋儱鍩?.exe
**閸樼喎娲?*閿涙瓘ersionInfo.cs 閺嬪嫬缂撻懘姘拱閺堫亝澧界悰灞惧灗 C# 妞ゅ湱娲伴張顏堝櫢閺傛壆绱拠?
**閹烘帗鐓?*閿?
```bash
# 閹靛濮╁▔銊ュ弳閻楀牊婀版穱鈩冧紖
python scripts/generate_build_metadata.py

# 瀵搫鍩楅柌宥嗘煀缂傛牞鐦?
dotnet clean src/Game.Core.csproj
dotnet build src/Game.Core.csproj

# 闁插秵鏌婇弸鍕紦
npm run build:exe
```

---

**妤犲矁鐦夐悩鑸碘偓?*閿涙瓟OK] 閺嬭埖鐎崥鍫㈡倞 | [OK] 閼存碍婀扮€瑰本鏆?| [OK] 瀹搞儰缍斿ù浣圭閺?| [OK] 閻楀牊婀扮粻锛勬倞鐏忚京鍗?
**閹恒劏宕樼拠鍕瀻**閿?2/100閿涘牊鐎楦垮殰閸斻劌瀵茬€瑰苯鏉介敍宀冧氦瀵邦喗鏁兼潻娑氣敄闂傝揪绱扮拠浣峰姛缁狅紕鎮婇妴浣割杻闁?Export閿?
**鐎圭偞鏌︽导妯哄帥缁?*閿涙igh閿涘湧hase 18-19 娓氭繆绂嗛張顒勬▉濞堝吀楠囬崙鐚寸礆

---

## 8. Python 缁涘鏅ラ懘姘拱缁€杞扮伐閿涘牊娴涙禒?PowerShell 閸栧懓顥婇敍?
```python
# scripts/build_windows.py
import subprocess, pathlib
project = pathlib.Path('Game.Godot')
export_preset = 'Windows Desktop'
output = pathlib.Path('dist')/ 'godotgame.exe'
output.parent.mkdir(parents=True, exist_ok=True)

# 鐎电厧鍤崣顖涘⒔鐞涘本鏋冩禒?subprocess.check_call([
  'godot','--headless','--path', str(project),
  '--export-release', export_preset, str(output)
])

# 閿涘牆褰查柅澶涚礆缁涙儳鎮曢敍姘洤娴ｈ法鏁?signtool.exe閿涘苯褰查崷銊︻劃鐠嬪啰鏁?
# subprocess.check_call(['signtool','sign','/fd','SHA256','/a','/tr','http://timestamp.digicert.com','/td','SHA256', str(output)])

print('Build completed at', output)
```

## 9. Python 缁涙儳鎮曠粈杞扮伐閿涘澃igntool閿?
```python
# scripts/sign_executable.py
import argparse, subprocess, sys, shutil
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Path to exe to sign')
    parser.add_argument('--timestamp', default='http://timestamp.digicert.com')
    parser.add_argument('--thumbprint', help='Cert thumbprint (optional when using /a)')
    parser.add_argument('--pfx', help='Path to .pfx (optional)')
    parser.add_argument('--pfx-password', help='Password for .pfx (optional)')
    args = parser.parse_args()

    signtool = shutil.which('signtool') or r'C:\\Program Files (x86)\\Windows Kits\\10\\bin\\x64\\signtool.exe'
    exe = Path(args.file)
    if not Path(signtool).exists():
        print('signtool not found', file=sys.stderr); return 1
    if not exe.exists():
        print('file to sign not found:', exe, file=sys.stderr); return 1

    cmd = [signtool, 'sign', '/fd', 'SHA256', '/td', 'SHA256', '/tr', args.timestamp]
    if args.pfx:
        cmd += ['/f', args.pfx]
        if args.pfx_password:
            cmd += ['/p', args.pfx_password]
    elif args.thumbprint:
        cmd += ['/sha1', args.thumbprint]
    else:
        cmd += ['/a']
    cmd.append(str(exe))
    print('>', ' '.join(cmd))
    subprocess.check_call(cmd)
    print('Signed', exe)
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

閻劍纭堕敍?```
py -3 scripts/sign_executable.py --file dist\godotgame.exe --thumbprint <CERT_SHA1>
```

鐠囧瓨妲戦敍?- 婵″倹鐏夋担鐘卞▏閻?.pfx 閺傚洣娆㈤敍灞藉讲娴肩姴鍙?`--pfx` 娑?`--pfx-password`閵?- 閺冨爼妫块幋铏箛閸斺€冲讲闁俺绻?`--timestamp` 閹稿洤鐣鹃敍娑㈢帛鐠併倓濞囬悽?DigiCert閵?- 閸?CI 娑擃叏绱濆楦款唴鐏忓棜鐦夋稊锕€鎷扮€靛棛鐖滄禒銉︽簚鐎靛棙鏌熷蹇旀暈閸忋儳骞嗘晶鍐跨礄GitHub Actions Secrets閿涘鈧?
> 閹绘劗銇氶敍姘€杞扮瑢缁涙儳鎮曠€瑰本鍨氶崥搴礉瀵ら缚顔呯亸鍡樷偓褑鍏橀幎銉ユ啞閿涘潷erf.json閿涘鈧笩dUnit4 閸︾儤娅欏ù瀣槸閹躲儱鎲￠敍鍧揹unit4-report.xml/json閿涘鈧箑askmaster 娑?Contracts 閺嶏繝鐛欓幎銉ユ啞缂佺喍绔磋ぐ鎺撱€傞懛?logs/ci/YYYY-MM-DD/閿涘苯鑻熼崷?Phase-13 閻?quality_gates.py 娑擃厺浜?`--perf-report`閵嗕梗--gdunit4-report`閵嗕梗--taskmaster-report`閵嗕梗--contracts-report` 娴ｆ粈璐熼崣顖炩偓澶庣翻閸忋儱寮稉搴ㄦ，缁備浇浠涢崥鍫涒偓?
---

Windows-only 韫囶偊鈧喐瀵氬?/ Quickstart: 鐟?See [Phase-17-Windows-Only-Quickstart.md](Phase-17-Windows-Only-Quickstart.md)
鏉╂盯妯佺悰銉ュ帠 / Addendum: [Phase-17-Windows-Only-Quickstart-Addendum.md](Phase-17-Windows-Only-Quickstart-Addendum.md)

## Windows‑only 导出注意 / DB Backend

- 插件后端：检测到 `addons/godot-sqlite` 时优先使用；日志 `[DB] backend=plugin`。
- 托管后备：无插件时使用 Microsoft.Data.Sqlite；日志 `[DB] backend=managed`；工程已引入 `SQLitePCLRaw.bundle_e_sqlite3` 以便导出携带本机库。
- 失败排查：优先检查 Export Templates 安装、`GODOT_BIN` 路径、插件启用状态以及日志。

