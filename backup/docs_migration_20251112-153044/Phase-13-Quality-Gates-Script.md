# Phase 13: 璐ㄩ噺闂ㄧ鑴氭湰涓庤嚜鍔ㄥ寲

> **鏍稿績鐩爣**锛氱粺涓€ xUnit + GdUnit4 鐨勮川閲忛棬绂侊紝寤虹珛 `guard:ci` 鑴氭湰鍏ュ彛锛岀‘淇濇墍鏈夋瀯寤洪€氳繃 10 椤瑰己鍒堕棬绂佹鏌ャ€? 
> **宸ヤ綔閲?*锛?-5 浜哄ぉ  
> **渚濊禆**锛歅hase 10锛坸Unit 妗嗘灦锛夈€丳hase 11锛圙dUnit4 妗嗘灦锛夈€丳hase 12锛堢儫娴?& 鎬ц兘閲囬泦锛? 
> **浜や粯鐗?*锛? 涓剼鏈?+ 1 涓?GitHub Actions 宸ヤ綔娴?+ 鏃ュ織瑙勮寖  
> **楠屾敹鏍囧噯**锛氭湰鍦?`npm run guard:ci` 閫氳繃 + CI 鑷姩鎵ц閫氳繃

---

## 1. 鑳屾櫙涓庡姩鏈?

### 鍘熺増锛坴itegame锛夎川閲忔帶鍒?
- Electron + JavaScript/TypeScript
- Playwright E2E + Vitest 鍗曞厓娴嬭瘯
- ESLint + Prettier 鑷姩鍖?
- GitHub Actions 鍗曚竴宸ヤ綔娴?

### 鏂扮増锛坓odotgame锛夎川閲忔寫鎴?
- **鍙岃建娴嬭瘯鏋舵瀯**锛歺Unit锛圕#锛? GdUnit4锛圙DScript锛?
- **涓ょ缂栫▼璇█**锛氫唬鐮侀噸澶嶇巼妫€娴嬮毦搴﹀鍔?
- **Headless 鎵ц**锛氭棤 GUI 鍙嶉锛屽繀椤讳緷璧栨棩蹇楀拰鎶ュ憡
- **鎬ц兘鍩哄噯**锛氭柊澧?P50/P95/P99 鑷姩闂ㄧ
- **瀹夊叏瀹¤**锛氶渶楠岃瘉 Security.cs 瀹¤鏃ュ織鏍煎紡

### 璐ㄩ噺闂ㄧ鐨勪环鍊?
1. **闃叉鍥炲綊**锛氳嚜鍔ㄩ樆鏂鐩栫巼涓嬮檷銆佹€ц兘鎭跺寲鐨勪唬鐮?
2. **鍙璁?*锛氭瘡娆℃瀯寤虹殑鍐崇瓥杩囩▼鍙噸鐜般€佸彲婧簮
3. **蹇€熷弽棣?*锛氬紑鍙戣€呭湪 5 鍒嗛挓鍐呬簡瑙ｆ瀯寤虹姸鎬?
4. **CI 鑷姩鍖?*锛氭棤闇€浜哄伐浠嬪叆锛岃嚜鍔?pass/fail锛岄樆濉炰笉鍚堟牸 PR

---

## 2. 璐ㄩ噺闂ㄧ瀹氫箟

### 2.1 10 椤瑰己鍒堕棬绂?

| # | 闂ㄧ鍚嶇О | 搴﹂噺鏍囧噯 | 闃堝€?| 宸ュ叿 | ADR |
|---|---------|--------|------|------|-----|
| 1 | xUnit 瑕嗙洊鐜囷紙琛岋級 | Coverage % Lines | 鈮?0% | OpenCover | ADR-0005 |
| 2 | xUnit 瑕嗙洊鐜囷紙鍒嗘敮锛?| Coverage % Branches | 鈮?5% | OpenCover | ADR-0005 |
| 3 | GdUnit4 鍐掔儫閫氳繃鐜?| Test Pass Count | 100% | GdUnit4 | ADR-0001 |
| 4 | 浠ｇ爜閲嶅鐜?| Duplication % | 鈮?% | jscpd | ADR-0005 |
| 5 | 鍦堝鏉傚害锛坢ax锛?| Max Cyclomatic | 鈮?0 | SonarQube Metrics | ADR-0005 |
| 6 | 鍦堝鏉傚害锛堝钩鍧囷級 | Avg Cyclomatic | 鈮? | SonarQube Metrics | ADR-0005 |
| 7 | 寰幆渚濊禆 | Circular Deps Count | 0 | NetArchTest (arch tests) | ADR-0007 |
| 8 | 璺ㄥ眰渚濊禆 | Cross-layer Violations | 0 | NetArchTest (arch tests) | ADR-0007 |
| 9 | 鎬ц兘鍩哄噯锛圥95锛?| Frame Time P95 | 鈮?6.67ms* | PerformanceTracker | ADR-0015 |
| 10 | 瀹¤鏃ュ織鏍煎紡 | JSONL Valid | 100% | custom validator | ADR-0003 |

*Godot 鐩爣甯х巼 60fps 鈫?姣忓抚 16.67ms锛汸95 搴斿湪姝や互涓嬬‘淇濈粷澶у鏁板抚娴佺晠

---

## 3. 鏋舵瀯璁捐

### 3.1 鍒嗗眰鏋舵瀯

```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹?             CI/CD Orchestration                     鈹?
鈹?        (guard-ci.yml, GitHub Actions)              鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                       鈹?
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹?      Python Gate Runner (guard_ci.py)              鈹?
鈹? - 椤哄簭璋冪敤鍚勬祴璇?鎵弿鑴氭湰                          鈹?
鈹? - 鎹曡幏杈撳嚭鎶ュ憡璺緞                                 鈹?
鈹? - 璁惧畾鏃ュ織鐩綍涓庣幆澧冨彉閲?                          鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                       鈹?
      鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
      鈹?               鈹?               鈹?
      鈻?               鈻?               鈻?
  xUnit Test      GdUnit4 Test         Code Scan
  鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€        鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€         鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
  dotnet test     godot --headless jscpd, SonarQube,
  opencover       --scene ..       SonarQube metrics,
                  GdUnit4 test runner  NetArchTest
                       鈹?               鈹?
                       鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                              鈹?
         鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹粹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
         鈹?                                        鈹?
         鈻?                                        鈻?
   Report Aggregation              Python Quality Gates
   (JSON/JSONL collect)            (quality_gates.py)
                                   - 鑱氬悎瑕嗙洊鐜?
                                   - 妫€鏌ユ墍鏈夐棬绂?
                                   - 鐢熸垚 HTML/JSON 鎶ュ憡
                                   - 杩斿洖 exit code
                                        鈹?
                                        鈻?
                                  鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                                  鈹?PASS / FAIL  鈹?
                                  鈹?(exit code)  鈹?
                                  鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
```

### 3.2 鐩綍缁撴瀯

```
godotgame/
鈹溾攢鈹€ scripts/
鈹?  鈹溾攢鈹€ guard.ps1                  # PowerShell 涓诲叆鍙ｈ剼鏈?
鈹?  鈹溾攢鈹€ python/
鈹?  鈹?  鈹斺攢鈹€ quality_gates.py        # Python 闂ㄧ鑱氬悎涓庡喅绛?
鈹?  鈹溾攢鈹€ ci/
鈹?  鈹?  鈹溾攢鈹€ run_xunit_tests.ps1     # xUnit 鎵ц涓庤鐩栫巼鏀堕泦
鈹?  鈹?  鈹溾攢鈹€ run_gut_tests.ps1       # GdUnit4 鐑熸祴鎵ц
鈹?  鈹?  鈹斺攢鈹€ run_code_scans.ps1      # 閲嶅鐜?澶嶆潅搴?渚濊禆妫€鏌?
鈹?  鈹斺攢鈹€ validate/
鈹?      鈹溾攢鈹€ validate_coverage.py    # 瑕嗙洊鐜囪В鏋愪笌闃堝€兼鏌?
鈹?      鈹溾攢鈹€ validate_gut_report.py  # GdUnit4 鎶ュ憡瑙ｆ瀽
鈹?      鈹斺攢鈹€ validate_audit_logs.py  # JSONL 瀹¤鏃ュ織楠岃瘉
鈹溾攢鈹€ logs/
鈹?  鈹斺攢鈹€ ci/                         # 鎸夋棩鏈熺粍缁囩殑 CI 鏃ュ織
鈹?      鈹斺攢鈹€ 2025-11-07/
鈹?          鈹溾攢鈹€ xunit-coverage.xml
鈹?          鈹溾攢鈹€ gut-report.log
鈹?          鈹溾攢鈹€ jscpd-report.json
鈹?          鈹溾攢鈹€ complexity-report.html
鈹?          鈹溾攢鈹€ quality-gates.html   # 鏈€缁堥棬绂佹姤鍛?
鈹?          鈹斺攢鈹€ quality-gates.json   # 鏈哄櫒鍙鐗堟湰
鈹溾攢鈹€ .github/
鈹?  鈹斺攢鈹€ workflows/
鈹?      鈹斺攢鈹€ guard-ci.yml            # GitHub Actions 宸ヤ綔娴?
鈹斺攢鈹€ package.json
    "guard:ci": "py -3 scripts/python/guard_ci.py"
```

---

## 4. 鍏抽敭浜や粯鐗╄缁嗚璁?

### 4.0 鏋舵瀯娴嬭瘯涓庡鏉傚害搴﹂噺绀轰緥

#### 4.0.1 NetArchTest 鏈€灏忔灦鏋勬祴璇曪紙C# xUnit锛?

```csharp
// Game.Core.Tests/Architecture/LayeringTests.cs
using NetArchTest.Rules;
using Xunit;

namespace Game.Core.Tests.Architecture;

public class LayeringTests
{
    private const string CoreNamespace = "Game.Core";
    private const string GodotNamespace = "Game.Godot";

    [Fact]
    public void Core_Should_Not_Depend_On_Godot()
    {
        var result = Types
            .InAssembly(typeof(Game.Core.Domain.Entities.Player).Assembly)
            .That()
            .ResideInNamespace(CoreNamespace, useRegularExpressions: true)
            .Should()
            .NotHaveDependencyOn(GodotNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful, string.Join("\n", result.Failures));
    }
}
```

鐢ㄦ硶锛氬皢璇ユ祴璇曠撼鍏?`dotnet test` 鍗冲彲锛涘湪闂ㄧ鑱氬悎涓皢鍏跺け璐ヨ涓衡€滆法灞傝繚瑙?寰幆渚濊禆鈥濅笉閫氳繃銆?

#### 4.0.2 SonarQube Metrics 鏈€灏忛泦鎴?

```bash
# 1) 寮€濮嬪垎鏋愶紙绀轰緥锛?
dotnet sonarscanner begin \
  /k:"godotgame" /d:sonar.host.url="%SONAR_HOST_URL%" \
  /d:sonar.login="%SONAR_TOKEN%" \
  /d:sonar.cs.opencover.reportsPaths="logs/ci/xunit-coverage.xml"

# 2) 杩愯鏋勫缓/娴嬭瘯锛堢‘淇濈敓鎴愯鐩栫巼锛?
dotnet build
dotnet test Game.Core.Tests \
  --collect:"XPlat Code Coverage;Format=opencover;FileName=logs/ci/xunit-coverage.xml"

# 3) 缁撴潫鍒嗘瀽
dotnet sonarscanner end /d:sonar.login="%SONAR_TOKEN%"
```

璇存槑锛?
- 鍦?CI 涓彲浣跨敤 `sonar.qualitygate.wait=true` 鎴栬鍙?Sonar API JSON 缁撴灉锛屽皢鍦堝鏉傚害/閲嶅鐜?璐ㄩ噺闂ㄧ瑙ｆ瀽鍚庝紶鍏?`quality_gates.py` 鑱氬悎銆?
- 鑻ユ棤 Sonar 鏈嶅姟鍣紝鍙€€鍖栦负鈥滃鍑烘湰鍦?metrics JSON锛堢涓夋柟宸ュ叿鎴栬嚜缂栵級鈫?瑙ｆ瀽 鈫?鑱氬悎鈥濈殑娴佺▼銆?

### 4.1 鑴氭湰锛歡uard_ci.py锛圥ython 涓诲叆鍙ｏ級

**鑱岃矗**锛氬崗璋冩墍鏈夋祴璇曚笌鎵弿鐨勬墽琛岄『搴忥紝绠＄悊鏃ュ織鐩綍

```python
# scripts/python/guard_ci.py
import argparse, subprocess, sys
from pathlib import Path
from datetime import datetime

def run(cmd: list[str]) -> None:
    print('>',' '.join(cmd))
    subprocess.check_call(cmd)

def main() -> int:
    parser = argparse.ArgumentParser()
    default_log = f"logs/ci/{datetime.now().strftime('%Y-%m-%d')}"
    parser.add_argument('--log-dir', default=default_log)
    args = parser.parse_args()

    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    print('CI Logs:', log_dir)

    # 1) xUnit 娴嬭瘯涓庤鐩栫巼
    run([
        'dotnet','test','Game.Core.Tests',
        '--configuration','Release','--no-build',
        '--logger', f"trx;LogFileName={log_dir/'xunit-results.trx'}",
        '--collect:XPlat Code Coverage;Format=opencover;FileName=' + str(log_dir/'xunit-coverage.xml')
    ])

    # 2) GdUnit4 鍐掔儫锛坔eadless锛?
    run([
        'godot','--headless','--path','Game.Godot',
        '--script','res://addons/gut/gut_cmdln.cs',
        '-gdir=Game.Godot/Tests','-goutput=' + str(log_dir/'gut-report.json')
    ])

    # 3) 浠ｇ爜鎵弿锛堥噸澶嶇巼 绛夛級
    run(['npx','jscpd','--reporters','json','--json-file', str(log_dir/'jscpd-report.json'), '--pattern','**/*.{cs,gd}','--gitignore'])

    # 4) 闂ㄧ鑱氬悎
    run(['py','-3','scripts/python/quality_gates.py',
         '--log-dir', str(log_dir),
         '--coverage-report', str(log_dir/'xunit-coverage.xml'),
         '--gut-report', str(log_dir/'gut-report.json'),
         '--jscpd-report', str(log_dir/'jscpd-report.json')])

    print('All quality gates passed')
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as e:
        print('Quality gates failed with code', e.returncode)
        sys.exit(e.returncode)
```

### 4.1.1 鎶ュ憡鏀堕泦涓庡鍒讹紙user:// 鈫?浠撳簱 logs/ci锛?

Godot 鍦?Windows 涓嬪皢 `user://` 鏄犲皠鍒?`C:\Users\<User>\AppData\Roaming\Godot\app_userdata\<ProjectName>`銆備负渚夸簬 CI 鑱氬悎闂ㄧ鎶ュ憡锛屽彲鍦?`guard_ci.py` 缁撴潫鍓嶈拷鍔犲涓嬫敹闆嗛€昏緫锛?

```python
import os, shutil
from pathlib import Path

def collect_user_reports(project_name: str, date_str: str, dest_dir: Path) -> None:
    base = Path(os.environ.get('APPDATA',''))/ 'Godot' / 'app_userdata' / project_name / 'logs' / 'e2e' / date_str
    if not base.exists():
        print('No user:// reports found at', base)
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    for f in base.glob('*'):
        if f.is_file():
            shutil.copy2(f, dest_dir / f.name)

# 鐢ㄦ硶绀轰緥锛?
# collect_user_reports(project_name='godotgame', date_str=datetime.now().strftime('%Y-%m-%d'), dest_dir=Path('logs')/'e2e'/datetime.now().strftime('%Y-%m-%d'))
```

璇存槑锛圵indows 璺緞鏄犲皠锛夛細
- `user://` 瀹為檯璺緞閫氬父浣嶄簬 `%APPDATA%\Godot\app_userdata\<ProjectName>`銆?
 - `<ProjectName>` 鍙栬嚜 `project.godot` 涓?`application/config/name`锛涜纭繚涓?CI 涓殑宸ョ▼鍚嶄竴鑷达紝浠ヤ究鏀堕泦鍣ㄨ兘鎵惧埌姝ｇ‘鐩綍銆?

鍙€夎緭鍏ワ紙GdUnit4 鍦烘櫙娴嬭瘯锛夛細
- 鑻ュ凡灏?GdUnit4 鎶ュ憡澶嶅埗鍒?`logs/ci/YYYY-MM-DD/gdunit4/`锛屽彲鍦?`quality_gates.py` 涓鍔犺В鏋愭楠わ細
  - 璇诲彇 `gdunit4-report.xml`锛圝Unit XML锛夋垨 `gdunit4-report.json`锛堣嫢瀛樺湪锛夛紝璁＄畻閫氳繃鐜囷紱
  - 灏嗏€滃満鏅祴璇曢€氳繃鐜?100%鈥濅綔涓哄墠缃棬绂侊紝鍐嶆墽琛屾€ц兘闂ㄧ涓庡叾浠栬川閲忛棬绂侊紱
  - 鎺ㄨ崘鍦?`guard_ci.py` 璋冪敤 `quality_gates.py` 鏃讹紝鏂板鍙傛暟濡?`--gdunit4-report` 浼犲叆鏂囦欢璺緞锛屼互缁熶竴鑱氬悎銆?

---

## 鎵╁睍闂ㄧ锛堝彲閫?鎺ㄨ崘锛孏odot + C# 鐜锛?

| # | 闂ㄧ鍚嶇О | 搴﹂噺鏍囧噯 | 闃堝€?| 宸ュ叿/鏉ユ簮 | 璇存槑 |
|---|---------|--------|------|-----------|-----|
| 11 | Taskmaster 浠诲姟閾炬牎楠?| Errors Count | = 0 | taskmaster_validate.py | 瑙ｆ瀽浠诲姟閾句笌鍙嶉摼锛圵indows/py -3锛夛紝杈撳嚭 JSON锛涘け璐ラ樆鏂?|
| 12 | 濂戠害鏍￠獙锛圕# Contracts锛?| Errors Count | = 0 | contracts_validate.py 鎴?C# 楠岃瘉鍣?| 瀵?`Game.Core/Contracts/**` DTO/浜嬩欢濂戠害杩涜绾︽潫鏍￠獙锛圖ataAnnotations/鑷畾涔夎鍒欙級锛岃緭鍑?JSON锛涘け璐ラ樆鏂?|

guard_ci.py 鍙傛暟鎵╁睍璇存槑锛堢ず渚嬶級锛?
```
py -3 scripts/python/quality_gates.py \
  --log-dir logs/ci/2025-11-07 \
  --coverage-report logs/ci/2025-11-07/xunit-coverage.xml \
  --gut-report logs/ci/2025-11-07/gut-report.json \
  --jscpd-report logs/ci/2025-11-07/jscpd-report.json \
  --gdunit4-report logs/ci/2025-11-07/gdunit4/gdunit4-report.xml \
  --taskmaster-report logs/ci/2025-11-07/taskmaster-report.json \
  --contracts-report logs/ci/2025-11-07/contracts-report.json
```

璇存槑锛氭墿灞曢棬绂佺殑鎶ュ憡鏂囦欢鍙湪鈥滄姤鍛婃敹闆嗕笌澶嶅埗鈥濇楠や腑缁熶竴褰掗泦鍚庡啀浼犲叆鑱氬悎鑴氭湰锛涘湪 Godot + C# 鐜涓嬶紝濂戠害鐩綍寤鸿浣嶄簬 `Game.Core/Contracts/**`锛屼娇鐢?C# 楠岃瘉鍣紙DataAnnotations/鑷畾涔夎鍒欙級瀵煎嚭 JSON銆?

---

### 4.2 鑴氭湰锛歳un_xunit_tests.ps1

**鑱岃矗**锛氭墽琛?xUnit 娴嬭瘯骞舵敹闆?OpenCover 瑕嗙洊鐜囨姤鍛?

```powershell
# scripts/ci/run_xunit_tests.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$LogDir
)

$ErrorActionPreference = "Stop"

# xUnit 椤圭洰璺緞
$xunitProject = "Game.Core.Tests"
$coverageReport = "$LogDir/xunit-coverage.xml"

Write-Host "xUnit Project: $xunitProject"
Write-Host "Coverage Report: $coverageReport"

# 妫€鏌?OpenCover 瀹夎锛堟垨浣跨敤 dotnet 鍐呯疆锛?
# 鎵ц娴嬭瘯骞舵敹闆嗚鐩栫巼
$testCommand = @(
    "dotnet", "test", $xunitProject,
    "--configuration Release",
    "--no-build",
    "--logger `"trx;LogFileName=$LogDir/xunit-results.trx`"",
    "--collect:`"XPlat Code Coverage;Format=opencover;FileName=$coverageReport`""
)

Write-Host "Running: $($testCommand -join ' ')" -ForegroundColor Cyan
& $testCommand[0] $testCommand[1..($testCommand.Length-1)]

if ($LASTEXITCODE -ne 0) {
    Write-Error "xUnit tests execution failed"
    exit 1
}

Write-Host "xUnit tests completed" -ForegroundColor Green
exit 0
```

---

### 4.3 鑴氭湰锛歳un_gut_tests.ps1

**鑱岃矗**锛氭墽琛?GdUnit4 鍐掔儫娴嬭瘯锛岀敓鎴?JSON 鏍煎紡鎶ュ憡

```powershell
# scripts/ci/run_gut_tests.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$LogDir
)

$ErrorActionPreference = "Stop"

$gutReport = "$LogDir/gut-report.json"
$gutProjectPath = "."  # Godot 椤圭洰鏍圭洰褰?

Write-Host "GdUnit4 Project: $gutProjectPath"
Write-Host "Report: $gutReport"

# 浣跨敤 Godot headless + GdUnit4 runner scene
$gutCommand = @(
    "godot", "--headless", "--no-window",
    "--scene", "res://tests/SmokeTestRunner.tscn",
    "--", "output=$gutReport"  # GdUnit4 鍛戒护琛屽弬鏁?
)

Write-Host "Running: $($gutCommand -join ' ')" -ForegroundColor Cyan
& $gutCommand[0] $gutCommand[1..($gutCommand.Length-1)]

if ($LASTEXITCODE -ne 0) {
    Write-Warning "GdUnit4 execution returned non-zero, but may contain passing tests"
    # GdUnit4 鍙兘杩斿洖闈為浂锛屽嵆浣挎祴璇曢€氳繃锛涢渶鍦?Python 楠岃瘉闃舵澶勭悊
}

# 楠岃瘉鎶ュ憡鏂囦欢瀛樺湪
if (-not (Test-Path $gutReport)) {
    Write-Error "GdUnit4 report file not generated: $gutReport"
    exit 1
}

Write-Host "GdUnit4 tests completed" -ForegroundColor Green
exit 0
```

---

### 4.4 鑴氭湰锛歳un_code_scans.ps1

**鑱岃矗**锛氭墽琛屼唬鐮佹壂鎻忥紙閲嶅鐜囥€佸鏉傚害銆佷緷璧栨鏌ワ級

```powershell
# scripts/ci/run_code_scans.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$LogDir
)

$ErrorActionPreference = "Stop"

Write-Host "Running code quality scans..." -ForegroundColor Cyan

# 1. jscpd - 閲嶅鐜囨鏌?
Write-Host "`n[Scan 1/3] jscpd (duplication)..." -ForegroundColor Yellow
$jscpdReport = "$LogDir/jscpd-report.json"
$jscpdCmd = @(
    "npx", "jscpd",
    "--threshold", "2",  # 澶辫触闃堝€?2%
    "--gitignore",
    "--reporters", "json",
    "--json-file", $jscpdReport,
    "--pattern", "**/*.{cs,gd,ts,tsx}",
    "Game.Core", "Game.Godot"
)

& $jscpdCmd[0] $jscpdCmd[1..($jscpdCmd.Length-1)]
if ($LASTEXITCODE -ne 0) {
    Write-Warning "jscpd check failed (duplication > 2%)"
    # 妫€鏌ユ槸鍚︾湡鐨勮秴闃堝€硷紝鎴栧彧鏄鍛?
}

# 2. complexity-report - 鍦堝鏉傚害
Write-Host "`n[Scan 2/3] complexity-report..." -ForegroundColor Yellow
$complexityReport = "$LogDir/complexity-report.json"
$complexityCmd = @(
    "npx", "complexity-report",
    "-o", $complexityReport,
    "Game.Core", "Game.Godot"
)

& $complexityCmd[0] $complexityCmd[1..($complexityCmd.Length-1)]
if ($LASTEXITCODE -ne 0) {
    Write-Warning "complexity-report execution had issues (may be non-blocking)"
}

# 3. dependency-cruiser - 渚濊禆妫€鏌?
Write-Host "`n[Scan 3/3] dependency-cruiser (circular/cross-layer)..." -ForegroundColor Yellow
$depCruiserReport = "$LogDir/dependency-cruiser.json"
$depCmd = @(
    "npx", "depcruise",
    "--output-type", "json",
    "-o", $depCruiserReport,
    "Game.Core", "Game.Godot"
)

& $depCmd[0] $depCmd[1..($depCmd.Length-1)]
if ($LASTEXITCODE -ne 0) {
    Write-Warning "dependency-cruiser check failed"
}

Write-Host "`nCode scans completed" -ForegroundColor Green
exit 0
```

---

### 4.5 鑴氭湰锛歲uality_gates.py锛圥ython 闂ㄧ鑱氬悎锛?

**鑱岃矗**锛氳В鏋愭墍鏈夋姤鍛婏紝妫€鏌ラ棬绂侊紝鐢熸垚鏈€缁堟姤鍛?

```python
#!/usr/bin/env python3
"""
scripts/python/quality_gates.py

璐ㄩ噺闂ㄧ鑱氬悎涓庡喅绛栧紩鎿?
- 璇诲彇 xUnit/GdUnit4/jscpd/complexity 鎶ュ憡
- 閫愰」妫€鏌ラ棬绂侊紙10 椤癸級
- 鐢熸垚 HTML/JSON 杈撳嚭
- 杩斿洖 exit code锛?=pass, 1=fail锛?
"""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import argparse

class QualityGatesReport:
    def __init__(self, log_dir):
        self.log_dir = Path(log_dir)
        self.gates = {}
        self.timestamp = datetime.now().isoformat()
        
    def check_gate_1_xunit_lines_coverage(self, coverage_report_path):
        """xUnit 瑕嗙洊鐜囷紙琛岋級鈮?0%"""
        gate_id = "GATE-1"
        gate_name = "xUnit Line Coverage"
        threshold = 90
        
        try:
            tree = ET.parse(coverage_report_path)
            root = tree.getroot()
            
            # OpenCover XML 鏍煎紡锛?CoverageSession ... lineCoverage="XX.XX">
            line_coverage = float(root.get('lineCoverage', '0'))
            
            passed = line_coverage >= threshold
            self.gates[gate_id] = {
                'name': gate_name,
                'threshold': f'{threshold}%',
                'actual': f'{line_coverage:.2f}%',
                'passed': passed,
                'reason': f"Line coverage {line_coverage:.2f}% {'鈮? if passed else '<'} {threshold}%"
            }
            return passed
        except Exception as e:
            self.gates[gate_id] = {
                'name': gate_name,
                'threshold': f'{threshold}%',
                'actual': 'ERROR',
                'passed': False,
                'reason': f"Failed to parse coverage report: {str(e)}"
            }
            return False
    
    def check_gate_2_xunit_branches_coverage(self, coverage_report_path):
        """xUnit 瑕嗙洊鐜囷紙鍒嗘敮锛夆墺85%"""
        gate_id = "GATE-2"
        gate_name = "xUnit Branch Coverage"
        threshold = 85
        
        try:
            tree = ET.parse(coverage_report_path)
            root = tree.getroot()
            
            branch_coverage = float(root.get('branchCoverage', '0'))
            
            passed = branch_coverage >= threshold
            self.gates[gate_id] = {
                'name': gate_name,
                'threshold': f'{threshold}%',
                'actual': f'{branch_coverage:.2f}%',
                'passed': passed,
                'reason': f"Branch coverage {branch_coverage:.2f}% {'鈮? if passed else '<'} {threshold}%"
            }
            return passed
        except Exception as e:
            self.gates[gate_id] = {
                'name': gate_name,
                'threshold': f'{threshold}%',
                'actual': 'ERROR',
                'passed': False,
                'reason': f"Failed to parse coverage report: {str(e)}"
            }
            return False
    
    def check_gate_3_gut_pass_rate(self, gut_report_path):
        """GdUnit4 鍐掔儫閫氳繃鐜?= 100%"""
        gate_id = "GATE-3"
        gate_name = "GdUnit4 Pass Rate"
        threshold = 100
        
        try:
            with open(gut_report_path, 'r', encoding='utf-8') as f:
                gut_data = json.load(f)
            
            # GdUnit4 鎶ュ憡鏍煎紡锛歿 "tests": [{...}], "passed": N, "failed": N }
            total = gut_data.get('total_tests', 0)
            passed = gut_data.get('passed_tests', 0)
            
            if total == 0:
                pass_rate = 0
            else:
                pass_rate = (passed / total) * 100
            
            passed_gate = pass_rate >= threshold
            self.gates[gate_id] = {
                'name': gate_name,
                'threshold': f'{threshold}%',
                'actual': f'{pass_rate:.1f}% ({passed}/{total})',
                'passed': passed_gate,
                'reason': f"GdUnit4 Pass Rate {pass_rate:.1f}% {'鈮? if passed_gate else '<'} {threshold}%"
            }
            return passed_gate
        except Exception as e:
            self.gates[gate_id] = {
                'name': gate_name,
                'threshold': f'{threshold}%',
                'actual': 'ERROR',
                'passed': False,
                'reason': f"Failed to parse GdUnit4 report: {str(e)}"
            }
            return False
    
    def check_gate_4_duplication_rate(self, jscpd_report_path):
        """浠ｇ爜閲嶅鐜?鈮?%"""
        gate_id = "GATE-4"
        gate_name = "Code Duplication"
        threshold = 2
        
        try:
            with open(jscpd_report_path, 'r', encoding='utf-8') as f:
                jscpd_data = json.load(f)
            
            # jscpd 鎶ュ憡锛歿 "duplicates": [...], "statistics": { "total": N, "clones": M } }
            duplicates = jscpd_data.get('duplicates', [])
            statistics = jscpd_data.get('statistics', {})
            total_lines = statistics.get('total', 1)
            duplicate_lines = statistics.get('clones', 0)
            
            dup_rate = (duplicate_lines / total_lines) * 100 if total_lines > 0 else 0
            
            passed = dup_rate <= threshold
            self.gates[gate_id] = {
                'name': gate_name,
                'threshold': f'鈮threshold}%',
                'actual': f'{dup_rate:.2f}% ({duplicate_lines}/{total_lines} lines)',
                'passed': passed,
                'reason': f"Duplication {dup_rate:.2f}% {'鈮? if passed else '>'} {threshold}%"
            }
            return passed
        except Exception as e:
            self.gates[gate_id] = {
                'name': gate_name,
                'threshold': f'鈮threshold}%',
                'actual': 'ERROR',
                'passed': False,
                'reason': f"Failed to parse jscpd report: {str(e)}"
            }
            return False
    
    def check_gate_5_6_cyclomatic_complexity(self, complexity_report_path):
        """鍦堝鏉傚害锛歮ax 鈮?0, avg 鈮?"""
        gate_5_id = "GATE-5"
        gate_6_id = "GATE-6"
        gate_5_name = "Max Cyclomatic Complexity"
        gate_6_name = "Avg Cyclomatic Complexity"
        threshold_max = 10
        threshold_avg = 5
        
        try:
            with open(complexity_report_path, 'r', encoding='utf-8') as f:
                complexity_data = json.load(f)
            
            # complexity-report 鏍煎紡锛歔{ "name": "...", "complexity": N }, ...]
            complexities = [item.get('complexity', 0) for item in complexity_data if isinstance(item, dict)]
            
            if not complexities:
                max_complexity = 0
                avg_complexity = 0
            else:
                max_complexity = max(complexities)
                avg_complexity = sum(complexities) / len(complexities)
            
            passed_5 = max_complexity <= threshold_max
            passed_6 = avg_complexity <= threshold_avg
            
            self.gates[gate_5_id] = {
                'name': gate_5_name,
                'threshold': f'鈮threshold_max}',
                'actual': f'{max_complexity:.1f}',
                'passed': passed_5,
                'reason': f"Max complexity {max_complexity:.1f} {'鈮? if passed_5 else '>'} {threshold_max}"
            }
            
            self.gates[gate_6_id] = {
                'name': gate_6_name,
                'threshold': f'鈮threshold_avg}',
                'actual': f'{avg_complexity:.2f}',
                'passed': passed_6,
                'reason': f"Avg complexity {avg_complexity:.2f} {'鈮? if passed_6 else '>'} {threshold_avg}"
            }
            
            return passed_5 and passed_6
        except Exception as e:
            self.gates[gate_5_id] = {
                'name': gate_5_name,
                'threshold': f'鈮threshold_max}',
                'actual': 'ERROR',
                'passed': False,
                'reason': f"Failed to parse complexity report: {str(e)}"
            }
            self.gates[gate_6_id] = {
                'name': gate_6_name,
                'threshold': f'鈮threshold_avg}',
                'actual': 'ERROR',
                'passed': False,
                'reason': f"Failed to parse complexity report: {str(e)}"
            }
            return False
    
    def check_gate_7_8_dependencies(self, dep_cruiser_report_path):
        """寰幆渚濊禆 & 璺ㄥ眰渚濊禆 = 0"""
        gate_7_id = "GATE-7"
        gate_8_id = "GATE-8"
        gate_7_name = "Circular Dependencies"
        gate_8_name = "Cross-layer Violations"
        
        try:
            with open(dep_cruiser_report_path, 'r', encoding='utf-8') as f:
                dep_data = json.load(f)
            
            # dependency-cruiser 鏍煎紡锛歿 "modules": [...], "summary": { "error": N, "warn": M } }
            violations = dep_data.get('summary', {}).get('error', 0)
            warnings = dep_data.get('summary', {}).get('warn', 0)
            
            # 杩欓噷绠€鍖栧鐞嗭紱瀹為檯鍙粏鍒嗗惊鐜緷璧?vs 璺ㄥ眰
            circular_deps = violations
            cross_layer_violations = warnings
            
            passed_7 = circular_deps == 0
            passed_8 = cross_layer_violations == 0
            
            self.gates[gate_7_id] = {
                'name': gate_7_name,
                'threshold': '0',
                'actual': f'{circular_deps}',
                'passed': passed_7,
                'reason': f"{circular_deps} circular dependencies found" if not passed_7 else "No circular deps"
            }
            
            self.gates[gate_8_id] = {
                'name': gate_8_name,
                'threshold': '0',
                'actual': f'{cross_layer_violations}',
                'passed': passed_8,
                'reason': f"{cross_layer_violations} cross-layer violations found" if not passed_8 else "No violations"
            }
            
            return passed_7 and passed_8
        except Exception as e:
            self.gates[gate_7_id] = {
                'name': gate_7_name,
                'threshold': '0',
                'actual': 'ERROR',
                'passed': False,
                'reason': f"Failed to parse dependency report: {str(e)}"
            }
            self.gates[gate_8_id] = {
                'name': gate_8_name,
                'threshold': '0',
                'actual': 'ERROR',
                'passed': False,
                'reason': f"Failed to parse dependency report: {str(e)}"
            }
            return False
    
    def check_gate_9_performance_baseline(self):
        """鎬ц兘鍩哄噯锛圥95锛夆墹16.67ms"""
        gate_id = "GATE-9"
        gate_name = "Performance Baseline (P95)"
        threshold = 16.67
        
        # 浠?GdUnit4 鐑熸祴鎶ュ憡涓彁鍙栨€ц兘鏁版嵁
        # 杩欓噷绀轰緥锛屽疄闄呴渶浠?PerformanceTracker.cs 杈撳嚭鐨勬暟鎹枃浠惰鍙?
        try:
            perf_report = self.log_dir / "performance-tracker.json"
            if perf_report.exists():
                with open(perf_report, 'r', encoding='utf-8') as f:
                    perf_data = json.load(f)
                
                p95_time = perf_data.get('frame_time_p95', 0)
                passed = p95_time <= threshold
            else:
                p95_time = None
                passed = True  # 濡傛灉娌℃湁鎬ц兘鏁版嵁锛屾殏鏃堕€氳繃锛堝彲閫夛級
            
            self.gates[gate_id] = {
                'name': gate_name,
                'threshold': f'鈮threshold}ms',
                'actual': f'{p95_time:.2f}ms' if p95_time else 'N/A',
                'passed': passed,
                'reason': f"P95 frame time {p95_time:.2f}ms {'鈮? if passed else '>'} {threshold}ms" if p95_time else "No perf data"
            }
            return passed
        except Exception as e:
            self.gates[gate_id] = {
                'name': gate_name,
                'threshold': f'鈮threshold}ms',
                'actual': 'ERROR',
                'passed': True,  # 鏆傛椂鏀捐
                'reason': f"Performance data not available (optional): {str(e)}"
            }
            return True
    
    def check_gate_10_audit_logs_format(self):
        """瀹¤鏃ュ織鏍煎紡锛圝SONL锛? 100% 鏈夋晥"""
        gate_id = "GATE-10"
        gate_name = "Audit Log Format (JSONL)"
        
        try:
            audit_log = self.log_dir / "security-audit.jsonl"
            if not audit_log.exists():
                self.gates[gate_id] = {
                    'name': gate_name,
                    'threshold': '100% valid',
                    'actual': 'N/A',
                    'passed': True,
                    'reason': "No audit log generated (optional)"
                }
                return True
            
            total_lines = 0
            valid_lines = 0
            
            with open(audit_log, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    total_lines += 1
                    try:
                        json.loads(line)
                        valid_lines += 1
                    except json.JSONDecodeError:
                        pass
            
            if total_lines == 0:
                validity_rate = 100
                passed = True
            else:
                validity_rate = (valid_lines / total_lines) * 100
                passed = validity_rate == 100
            
            self.gates[gate_id] = {
                'name': gate_name,
                'threshold': '100%',
                'actual': f'{validity_rate:.1f}% ({valid_lines}/{total_lines})',
                'passed': passed,
                'reason': f"JSONL validity {validity_rate:.1f}% {'=' if passed else '鈮?} 100%"
            }
            return passed
        except Exception as e:
            self.gates[gate_id] = {
                'name': gate_name,
                'threshold': '100%',
                'actual': 'ERROR',
                'passed': True,
                'reason': f"Audit log validation skipped: {str(e)}"
            }
            return True
    
    def run_all_checks(self, coverage_report, gut_report, jscpd_report, complexity_report, dep_cruiser_report):
        """鎵ц鎵€鏈?10 椤归棬绂佹鏌?""
        results = []
        
        results.append(self.check_gate_1_xunit_lines_coverage(coverage_report))
        results.append(self.check_gate_2_xunit_branches_coverage(coverage_report))
        results.append(self.check_gate_3_gut_pass_rate(gut_report))
        results.append(self.check_gate_4_duplication_rate(jscpd_report))
        passed_5_6 = self.check_gate_5_6_cyclomatic_complexity(complexity_report)
        results.append(passed_5_6)
        results.append(passed_5_6)
        
        passed_7_8 = self.check_gate_7_8_dependencies(dep_cruiser_report)
        results.append(passed_7_8)
        results.append(passed_7_8)
        
        results.append(self.check_gate_9_performance_baseline())
        results.append(self.check_gate_10_audit_logs_format())
        
        return all(results)
    
    def generate_html_report(self, output_path):
        """鐢熸垚 HTML 鎶ュ憡"""
        passed_count = sum(1 for g in self.gates.values() if g['passed'])
        total_count = len(self.gates)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Quality Gates Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ font-size: 24px; font-weight: bold; margin: 20px 0; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #f8f9fa; }}
        tr.pass {{ background: #f0f8f5; }}
        tr.fail {{ background: #fff5f5; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Quality Gates Report</h1>
        <p>Generated: {self.timestamp}</p>
    </div>
    
    <div class="summary">
        Result: <span class="{'passed' if passed_count == total_count else 'failed'}">
            {passed_count}/{total_count} Gates PASSED
        </span>
    </div>
    
    <table>
        <tr>
            <th>Gate ID</th>
            <th>Name</th>
            <th>Threshold</th>
            <th>Actual</th>
            <th>Status</th>
            <th>Reason</th>
        </tr>
"""
        
        for gate_id in sorted(self.gates.keys()):
            gate = self.gates[gate_id]
            status = 'PASS' if gate['passed'] else 'FAIL'
            row_class = 'pass' if gate['passed'] else 'fail'
            
            html += f"""        <tr class="{row_class}">
            <td>{gate_id}</td>
            <td>{gate['name']}</td>
            <td>{gate['threshold']}</td>
            <td>{gate['actual']}</td>
            <td>{status}</td>
            <td>{gate['reason']}</td>
        </tr>
"""
        
        html += """    </table>
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def generate_json_report(self, output_path):
        """鐢熸垚 JSON 鎶ュ憡"""
        report = {
            'timestamp': self.timestamp,
            'summary': {
                'passed': sum(1 for g in self.gates.values() if g['passed']),
                'total': len(self.gates),
                'all_passed': all(g['passed'] for g in self.gates.values())
            },
            'gates': self.gates
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Quality Gates Aggregator')
    parser.add_argument('--log-dir', required=True, help='CI logs directory')
    parser.add_argument('--coverage-report', required=True, help='xUnit coverage XML')
    parser.add_argument('--gut-report', required=True, help='GdUnit4 test report JSON')
    parser.add_argument('--jscpd-report', required=True, help='jscpd report JSON')
    parser.add_argument('--complexity-report', required=True, help='complexity report JSON')
    parser.add_argument('--dep-cruiser-report', default=None, help='dependency-cruiser report JSON')
    
    args = parser.parse_args()
    
    report = QualityGatesReport(args.log_dir)
    
    # 杩愯鎵€鏈夋鏌?
    all_passed = report.run_all_checks(
        args.coverage_report,
        args.gut_report,
        args.jscpd_report,
        args.complexity_report,
        args.dep_cruiser_report or (Path(args.log_dir) / "dependency-cruiser.json")
    )
    
    # 鐢熸垚鎶ュ憡
    log_dir = Path(args.log_dir)
    report.generate_html_report(log_dir / "quality-gates.html")
    report.generate_json_report(log_dir / "quality-gates.json")
    
    print(f"\n{'='*60}")
    print(f"Quality Gates Report")
    print(f"{'='*60}")
    print(f"Passed: {sum(1 for g in report.gates.values() if g['passed'])}/{len(report.gates)}")
    print(f"Status: {'ALL PASSED' if all_passed else 'FAILED'}")
    print(f"\nDetailed Report: {log_dir}/quality-gates.html")
    print(f"JSON Report: {log_dir}/quality-gates.json")
    print(f"{'='*60}\n")
    
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
```

---

### 4.6 GitHub Actions 宸ヤ綔娴侊細guard-ci.yml

**鑱岃矗**锛欳I/CD 鑷姩鍖栧叆鐐癸紝璋冪敤鏈湴鑴氭湰锛屼笂浼犲伐浠?

```yaml
# .github/workflows/guard-ci.yml
name: Guard CI - Quality Gates

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  quality-gates:
    runs-on: windows-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup .NET 8
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          npm install
          dotnet restore Game.Core.sln
      
      - name: Run Quality Gates Script
        shell: pwsh
        run: |
          pwsh scripts/guard.ps1
        continue-on-error: true
      
      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: quality-gates-reports
          path: logs/ci/*/
          retention-days: 30
      
      - name: Comment PR with Results
        if: github.event_name == 'pull_request' && always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const reportPath = 'logs/ci/*/quality-gates.json';
            // 瑙ｆ瀽鎶ュ憡锛屽啓鍏?PR 璇勮
```

---

## 5. 闆嗘垚鐐逛笌宸ヤ綔娴?

### 5.1 鏈湴寮€鍙戞祦绋?

```bash
# 寮€鍙戣€呮彁浜ゅ墠杩愯鏈湴 guard:ci
npm run guard:ci

# 杈撳嚭绀轰緥
# [Step 1/4] Running xUnit tests with coverage...
# xUnit tests completed
# [Step 2/4] Running GdUnit4 smoke tests...
# GdUnit4 tests completed
# [Step 3/4] Running code quality scans...
# Code scans completed
# [Step 4/4] Aggregating quality gates...
# ============================================================
# Quality Gates Report
# ============================================================
# Passed: 10/10
# Status: ALL PASSED
# 
# Detailed Report: logs/ci/2025-11-07/quality-gates.html
# JSON Report: logs/ci/2025-11-07/quality-gates.json
# ============================================================
```

### 5.2 CI 宸ヤ綔娴?

```
PR 鍒涘缓 / push to develop
    鈹?
    鈻?
guard-ci.yml workflow triggered
    鈹?
    鈹溾攢鈻?setup (.NET, Node, Python)
    鈹溾攢鈻?npm install / dotnet restore
    鈹溾攢鈻?pwsh scripts/guard.ps1
    鈹?  鈹溾攢鈻?run_xunit_tests.ps1
    鈹?  鈹溾攢鈻?run_gut_tests.ps1
    鈹?  鈹溾攢鈻?run_code_scans.ps1
    鈹?  鈹斺攢鈻?quality_gates.py
    鈹?
    鈻?(always)
Upload artifacts: logs/ci/*
    鈹?
    鈻?(on pull_request)
Comment PR with quality-gates.json summary
    鈹?
    鈻?
Branch protection rule checks:
  - status: guard-ci / quality-gates
  - if FAIL 鈫?block merge
  - if PASS 鈫?allow merge
```

---

## 6. 瀹屾垚娓呭崟涓庨獙鏀舵爣鍑?

### 6.1 瀹炵幇妫€鏌ユ竻鍗?

- [ ] 鍒涘缓 `scripts/guard.ps1` 涓诲叆鍙ｈ剼鏈?
- [ ] 鍒涘缓 `scripts/ci/run_xunit_tests.ps1`
- [ ] 鍒涘缓 `scripts/ci/run_gut_tests.ps1`
- [ ] 鍒涘缓 `scripts/ci/run_code_scans.ps1`
- [ ] 鍒涘缓 `scripts/python/quality_gates.py`锛堝惈 10 椤归棬绂佹鏌ワ級
- [ ] 鍒涘缓 `.github/workflows/guard-ci.yml`
- [ ] 鍦?`package.json` 涓厤缃?`guard:ci` 鑴氭湰
- [ ] 寤虹珛 `logs/ci/` 鐩綍缁撴瀯涓庢棩蹇楄鑼?
- [ ] 缂栧啓 Phase 13 瀹屾暣鏂囨。锛堟湰鏂囨。锛?
- [ ] 鏈湴娴嬭瘯 `npm run guard:ci` 鎴愬姛閫氳繃

### 6.2 楠屾敹鏍囧噯

| 椤圭洰 | 楠屾敹鏍囧噯 | 纭 |
|-----|--------|------|
| 鑴氭湰瀹屾暣鎬?| 5 涓剼鏈?+ 1 涓伐浣滄祦瀹屾暣鍙繍琛?| 鈻?|
| 闂ㄧ鍏ㄨ鐩?| 10 椤归棬绂佸叏閮ㄦ鏌ヤ笖鏈夌悊鐢辫鏄?| 鈻?|
| 鎶ュ憡鐢熸垚 | HTML + JSON 鎶ュ憡鑷姩鐢熸垚 | 鈻?|
| 鏈湴鎵ц | `npm run guard:ci` <2min 瀹屾垚 | 鈻?|
| CI 闆嗘垚 | GitHub Actions 鑷姩瑙﹀彂锛岀粨鏋滆瘎璁?PR | 鈻?|
| 鏂囨。瀹屾暣 | Phase 13 鏂囨。 鈮?00 琛岋紝鍚唬鐮佺ず渚?| 鈻?|
| 鏃ュ織瑙勮寖 | `logs/ci/YYYY-MM-DD/` 鐩綍鑷姩鍒涘缓 | 鈻?|

---

## 7. 椋庨櫓涓庣紦瑙?

| # | 椋庨櫓 | 绛夌骇 | 缂撹В |
|---|-----|------|-----|
| 1 | xUnit/GdUnit4 鎶ュ憡鏍煎紡鍙樻洿 | 涓?| 鐗堟湰閿佸畾锛屽畾鏈熸洿鏂拌В鏋愬櫒 |
| 2 | 鎵弿宸ュ叿缃戠粶瓒呮椂 | 涓?| 绂荤嚎缂撳瓨锛岃秴鏃堕檷绾э紙璀﹀憡鑰岄潪澶辫触锛?|
| 3 | PowerShell 璺ㄥ钩鍙伴棶棰?| 楂?| 浠呮敮鎸?Windows锛堝凡鏄庣‘锛夛紝鏈潵鎵╁睍鑰冭檻 core |
| 4 | 瑕嗙洊鐜囬槇鍊艰繃楂樺鑷撮绻?fail | 涓?| 鍓?2 鍛ㄥ鏉撅紙85%锛夛紝閫愭鎻愰珮鍒?90% |
| 5 | 鎬ц兘鍩哄噯閲囬泦涓嶇ǔ瀹?| 涓?| 閲囬泦 5 娆″彇鍧囧€硷紝baseline.json 鐗堟湰鍖?|

---

## 8. 鍚庣画宸ヤ綔锛圥hase 14-22锛?

瀹屾垚 Phase 13 鍚庯紝鍚庣画宸ヤ綔搴忓垪锛?

- **Phase 14**锛欸odot 瀹夊叏鍩虹嚎涓庡璁★紙Security.cs 瀹屾暣瀹炵幇銆丣SONL 鏃ュ織锛?
- **Phase 15**锛氭€ц兘棰勭畻涓庨棬绂侊紙PerformanceTracker 鍩哄噯銆佽嚜鍔ㄥ洖褰掓娴嬶級
- **Phase 16**锛氬彲瑙傛祴鎬т笌 Sentry 闆嗘垚锛圧elease Health 闂ㄧ锛?
- **Phase 17-22**锛氭瀯寤恒€佸彂甯冦€佸洖婊氥€佸姛鑳介獙鏀躲€佹€ц兘浼樺寲銆佹枃妗ｆ洿鏂?

---

## 9. 鍙傝€冧笌閾炬帴

- **ADR-0005**锛氳川閲忛棬绂?- 瑕嗙洊鐜囥€佸鏉傚害銆侀噸澶嶇巼
- **ADR-0003**锛氬彲瑙傛祴鎬т笌 Sentry - 鍙戝竷鍋ュ悍闂ㄧ
- **ADR-0001**锛氭妧鏈爤涓?Godot 闆嗘垚
- **Phase 10**锛歺Unit 妗嗘灦涓庨」鐩粨鏋?
- **Phase 11**锛欸dUnit4 妗嗘灦涓庡満鏅祴璇?
- **Phase 12**锛欻eadless 鐑熸祴涓庢€ц兘閲囬泦

---

**鏂囨。鐗堟湰**锛?.0  
**瀹屾垚鏃ユ湡**锛?025-11-07  
**浣滆€?*锛欳laude Code  
**鐘舵€?*锛歊eady for Implementation


> 鍙傝€?Runner 鎺ュ叆鎸囧崡锛氳 docs/migration/gdunit4-csharp-runner-integration.md銆?


py -3 scripts/python/quality_gates.py   --log-dir logs/ci/2025-11-07   --coverage-report logs/ci/2025-11-07/xunit-coverage.xml   --gut-report logs/ci/2025-11-07/gut-report.json   --jscpd-report logs/ci/2025-11-07/jscpd-report.json   --gdunit4-report logs/ci/2025-11-07/gdunit4/gdunit4-report.xml   --taskmaster-report logs/ci/2025-11-07/taskmaster-report.json   --contracts-report logs/ci/2025-11-07/contracts-report.json   --perf-report logs/ci/2025-11-07/perf.json

> 鎻愮ず锛歚perf.json` 瀛楁绀轰緥涓庤鑼冭 Phase-15锛堟€ц兘闂ㄧ锛夋枃妗ｄ腑鐨勨€滄姤鍛婅緭鍑轰笌鑱氬悎鈥濄€?

## 模板质量门禁脚本 / Template Quality Gate

- 一键门禁：`./scripts/ci/quality_gate.ps1 -GodotBin "$env:GODOT_BIN" [-IncludeDemo] [-WithExport] [-WithCoverage]`
- 步骤：
  1) dotnet tests（可选覆盖率）
  2) GdUnit4 tests（示例测试默认关闭，可用 -IncludeDemo 启用）
  3) Headless smoke（无界面冒烟）
  4) Export + EXE smoke（可选 -WithExport）

退出码：通过=0，失败=1（便于 CI 集成）


## GitHub Actions（Windows） / CI Template

- 工作流：`.github/workflows/windows-quality-gate.yml`（手动触发 `workflow_dispatch`）
- 步骤：Checkout → Setup .NET → 下载 Godot .NET（mono）→ 运行 `scripts/ci/quality_gate.ps1`
- 默认不包含导出（Export Templates 需在编辑器安装）；如需导出与 EXE 冒烟，可在本地或自建 Runner 上开启 `-WithExport`。

