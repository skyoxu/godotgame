# Phase 16: 可观测性与 Sentry 集成（模板最小集）

> 目标：提供“默认本地、可选远程”的观测最小集；本地 JSONL 事件日志 + Sentry 接入占位（默认不开启）。`n> 目标：提供“默认本地、可选远程”的观测最小集；本地 JSONL 事件日志 + Sentry 接入占位（默认不开启）。`n> 目标：提供“默认本地、可选远程”的观测最小集；本地 JSONL 事件日志 + Sentry 接入占位（默认不开启）。`n> 目标：提供“默认本地、可选远程”的观测最小集；本地 JSONL 事件日志 + Sentry 接入占位（默认不开启）。`n> 目标：提供“默认本地、可选远程”的观测最小集；本地 JSONL 事件日志 + Sentry 接入占位（默认不开启）。`n
---

## 1. 鑳屾櫙涓庡姩鏈?

### 鍘熺増锛坴itegame锛夊彲瑙傛祴鎬?

**Electron + Sentry**锛?
- Sentry 鍒濆鍖栧湪涓昏繘绋嬩笌娓叉煋杩涚▼
- Release 鏍囩鍖栵紙git commit sha锛?
- 鑷姩鎹曡幏鏈鐞嗗紓甯镐笌 Promise rejection
- Session 杩借釜锛堢敤鎴蜂細璇濄€佸穿婧冩鏁帮級
- Breadcrumb 璁板綍锛堢敤鎴锋搷浣滆冻杩癸級

**鎸囨爣**锛?
- Crash-Free Sessions 鈮?99.5%锛堝彂甯冮棬绂侊級
- Error Rate 鈮?0.1%锛堝憡璀﹂槇鍊硷級

### 鏂扮増锛坓odotgame锛夊彲瑙傛祴鎬ф満閬囦笌鎸戞垬

**鏈洪亣**锛?
- Godot 4.5 瀹樻柟鏀寔 Sentry SDK锛圢ative C#锛?
- C# 鏋勫缓淇℃伅鍙紪璇戣繘鐗堟湰鍙凤紙鏇寸簿纭殑婧簮锛?
- GDScript 閿欒鎹曟崏鍙€氳繃 Signals 涓灑鍖栧鐞?
- Release Health API 鏀寔鎬ц兘鎸囨爣涓婃姤锛堜笌 Phase 15 鑱斿姩锛?

**鎸戞垬**锛?
| 鎸戞垬 | 鍘熷洜 | Godot 瑙ｅ喅鏂规 |
|-----|-----|--------------|
| 鍙岃瑷€鏃ュ織 | C# + GDScript | 缁熶竴鏃ュ織鎺ュ彛锛圤bservability.cs锛?|
| 闅愮鑴辨晱 | PII 娣峰叆鏃ュ織 | 浜嬩欢鍓嶇疆澶勭悊閽╁瓙锛圔efore Send锛?|
| 鍙戝竷绠＄悊 | 鐗堟湰涓庢瀯寤哄垎绂?| 鏋勫缓鑴氭湰鑷姩鐢熸垚 Release 鍏冩暟鎹?|
| 绂荤嚎鏃ュ織 | 鏃犵綉缁滄椂涓㈠け | 鏈湴闃熷垪锛圫QLite 澶囦唤锛?|
| 鎬ц兘寮€閿€ | SDK 鍒濆鍖?閲囨牱 | 鍔ㄦ€侀噰鏍风巼锛堢嚎涓?1%锛孌ev 100%锛?|

### 鍙娴嬫€х殑浠峰€?

1. **蹇€熼棶棰樺畾浣?*锛氶敊璇彂鐢熸椂鑷姩鎹曡幏鍫嗘爤銆佽澶囦俊鎭€佺敤鎴锋搷浣滈摼璺?
2. **璐ㄩ噺闂ㄧ**锛欳rash-Free Sessions 涓?Release Health 闃绘柇涓嶅悎鏍肩増鏈彂甯?
3. **鐢ㄦ埛浣撻獙娲炲療**锛氭€ц兘鏁版嵁 + 閿欒鐜?+ 浼氳瘽闀垮害 鈫?鍙戠幇浜у搧鐡堕
4. **浜嬪悗杩借矗**锛氬畬鏁寸殑 Breadcrumb + Session 閲嶇幇鐢ㄦ埛琛屼负

---

## 2. 鍙娴嬫€т綋绯诲畾涔?

### 2.1 涓夊眰鍙娴嬫€ф灦鏋?

```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹?                   Sentry Cloud Platform                   鈹?
鈹? - Issue 鑱氬悎涓庡幓閲?                                       鈹?
鈹? - Release Health 浠〃鏉?                                  鈹?
鈹? - 鍛婅瑙勫垯涓庨€氱煡                                          鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                       鈹?
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹?        Observability.cs Autoload锛圙odot 灞傦級             鈹?
鈹? - Sentry SDK 缁熶竴鍒濆鍖栦笌閰嶇疆                             鈹?
鈹? - 缁撴瀯鍖栨棩蹇楁帴鍙ｏ紙debug/info/warning/error锛?             鈹?
鈹? - Session 绠＄悊锛堢敤鎴蜂細璇濄€佺増鏈叧鑱旓級                      鈹?
鈹? - Breadcrumb 璁板綍锛圫cene 鍒囨崲銆丼ignal銆丄PI 璋冪敤锛?       鈹?
鈹? - Before Send Hook锛圥II 鑴辨晱銆佷簨浠惰繃婊わ級                 鈹?
鈹? - 鍔ㄦ€侀噰鏍凤紙Dev 100%, Prod 1-10%锛?                     鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                       鈹?
        鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
        鈹?             鈹?             鈹?
        鈻?             鈻?             鈻?
     C# 灞?         GDScript 灞?    鏁版嵁搴撳眰
  (Game.Core)     (鍦烘櫙銆佷俊鍙?    (SQLite 闃熷垪)
  - 寮傚父鎹曟崏      - Signal 鎺ユ敹  - 绂荤嚎澶囦唤
  - 鎬ц兘鎸囨爣      - 鐢ㄦ埛鎿嶄綔    - 鎵归噺涓婃姤
  - API 閿欒      - 鍦烘櫙鍔犺浇
```

### 2.2 鏍稿績鎸囨爣瀹氫箟

#### A. 閿欒涓庡紓甯?

| 鎸囨爣 | 瀹氫箟 | 闃堝€?| 璇存槑 |
|-----|------|------|------|
| **Crash-Free Sessions** | 鏈彂鐢熷穿婧冪殑浼氳瘽鍗犳瘮 | 鈮?9.5% | 鍙戝竷闂ㄧ锛?4h 绐楀彛锛?|
| **Error Rate** | 閿欒鏁?/ 鎬昏姹傛暟 | 鈮?.1% | 鍛婅闃堝€?|
| **Critical Errors** | 鑷村懡閿欒鏁帮紙P0锛?| 0 | 绔嬪嵆鍛婅 |
| **Unhandled Exceptions** | 鏈崟鎹夊紓甯告暟 | 鈮?/1000 | 鎬ц兘鍩虹嚎 |

#### B. 鍙戝竷鍋ュ悍

| 鎸囨爣 | 瀹氫箟 | 闃堝€?| 璇存槑 |
|-----|------|------|------|
| **Crash-Free Users** | 鏈彂鐢熷穿婧冪殑鐢ㄦ埛鍗犳瘮 | 鈮?9.0% | 鐢ㄦ埛缁村害 |
| **Session Duration** | 骞冲潎浼氳瘽鏃堕暱 | 鈮?min | 鐢ㄦ埛绮樻€ф寚鏍?|
| **Affected Users** | 鍙楀奖鍝嶇敤鎴锋暟 | 鈮?% | 閿欒褰卞搷鑼冨洿 |
| **Release Health** | 缁煎悎鍋ュ悍璇勫垎 | 鈮?5% | 澶氱淮搴﹀姞鏉?|

#### C. 鎬ц兘涓庤祫婧?

| 鎸囨爣 | 瀹氫箟 | 闃堝€?| 璇存槑 |
|-----|------|------|------|
| **P95 Frame Time** | 甯ф椂闂?95 鍒嗕綅 | 鈮?6.67ms | 涓?Phase 15 鑱斿姩 |
| **Memory Peak** | 宄板€煎唴瀛樺崰鐢?| 鈮?00MB | 涓?Phase 15 鑱斿姩 |
| **Startup Time** | 搴旂敤鍚姩鏃堕棿 | 鈮?.0s | 涓?Phase 15 鑱斿姩 |
| **API Latency** | API 璋冪敤寤惰繜 P95 | 鈮?00ms | 缃戠粶鎬ц兘 |

#### D. 缁撴瀯鍖栨棩蹇楃淮搴?

| 缁村害 | 绫诲瀷 | 鏍蜂緥 | 鐢ㄩ€?|
|-----|------|------|------|
| **logger** | string | `game.core`, `ui.menu`, `database` | 鏃ュ織鏉ユ簮 |
| **level** | enum | `debug`, `info`, `warning`, `error` | 涓ラ噸绾у埆 |
| **tags** | dict | `{"user_id": "usr_123", "scene": "MainScene"}` | 涓婁笅鏂囧叧鑱?|
| **extra** | dict | `{"query_time_ms": 45, "row_count": 100}` | 琛ュ厖淇℃伅 |
| **breadcrumbs** | array | `[{"action": "button_click", "timestamp": ...}]` | 鎿嶄綔閾捐矾 |

---

## 3. 鏋舵瀯璁捐

### 3.1 鍒嗗眰闆嗘垚鏋舵瀯

```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹?     GitHub Actions CI/CD 鍙戝竷宸ヤ綔娴?                   鈹?
鈹? - 鐢熸垚 Release 鍏冩暟鎹紙鐗堟湰銆佹瀯寤?hash锛?             鈹?
鈹? - 閮ㄧ讲鍓嶆鏌?Crash-Free Sessions 鈮?9.5%              鈹?
鈹? - 澶辫触鑷姩鍥炴粴                                         鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                         鈹?
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹?   Observability.cs Autoload锛堝垵濮嬪寲涓庡鎵橈級            鈹?
鈹? - Sentry.init(dsn, release, environment)              鈹?
鈹? - Before Send Hook锛堜簨浠惰繃婊や笌鑴辨晱锛?                 鈹?
鈹? - Breadcrumb 鎷︽埅鍣紙鑷姩璁板綍锛?                      鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                         鈹?
        鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
        鈹?               鈹?               鈹?
        鈻?               鈻?               鈻?
   搴旂敤灞傛棩蹇?     鎬ц兘鏁版嵁涓婃姤       閿欒鎹曟崏
   (Observability  (Phase 15          (try/catch
    .log_info)     PerformanceTracker)  + Signal)
        鈹?               鈹?               鈹?
        鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                         鈹?
                         鈻?
            鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
            鈹? SQLite 鏈湴闃熷垪        鈹?
            鈹? 锛堢绾垮浠斤級          鈹?
            鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                             鈹?
                    鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                    鈹? Sentry Cloud   鈹?
                    鈹? 锛堟壒閲忎笂鎶ワ級   鈹?
                    鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
```

### 3.2 鐩綍缁撴瀯

```
godotgame/
鈹溾攢鈹€ src/
鈹?  鈹溾攢鈹€ Game.Core/
鈹?  鈹?  鈹溾攢鈹€ Observability/
鈹?  鈹?  鈹?  鈹溾攢鈹€ ObservabilityClient.cs           鈽?Sentry SDK 鍖呰
鈹?  鈹?  鈹?  鈹溾攢鈹€ StructuredLogger.cs              鈽?缁撴瀯鍖栨棩蹇楁帴鍙?
鈹?  鈹?  鈹?  鈹溾攢鈹€ ReleaseHealthGate.cs             鈽?鍙戝竷鍋ュ悍妫€鏌?
鈹?  鈹?  鈹?  鈹斺攢鈹€ PiiDataScrubber.cs               鈽?PII 鑴辨晱
鈹?  鈹?  鈹?
鈹?  鈹?  鈹斺攢鈹€ Offline/
鈹?  鈹?      鈹斺攢鈹€ OfflineEventQueue.cs             鈽?绂荤嚎闃熷垪锛圫QLite锛?
鈹?  鈹?
鈹?  鈹斺攢鈹€ Godot/
鈹?      鈹溾攢鈹€ Observability.cs                     鈽?Autoload 鍏ュ彛
鈹?      鈹溾攢鈹€ BreadcrumbRecorder.cs                鈽?鎿嶄綔璁板綍
鈹?      鈹斺攢鈹€ SessionManager.cs                    鈽?浼氳瘽绠＄悊
鈹?
鈹溾攢鈹€ scripts/
鈹?  鈹溾攢鈹€ release_health_gate.py                   鈽?鍙戝竷鍋ュ悍闂ㄧ鑴氭湰
鈹?  鈹溾攢鈹€ generate_release_metadata.py             鈽?Release 鍏冩暟鎹敓鎴?
鈹?  鈹斺攢鈹€ upload_sourcemaps.py                     鈽?婧愮爜鏄犲皠涓婁紶
鈹?
鈹溾攢鈹€ config/
鈹?  鈹斺攢鈹€ sentry_config.json                       鈽?Sentry 閰嶇疆鏂囦欢
鈹?
鈹斺攢鈹€ docs/
    鈹溾攢鈹€ logging-guidelines.md                    鈽?鏃ュ織浣跨敤瑙勮寖
    鈹斺攢鈹€ privacy-compliance.md                    鈽?闅愮涓庡悎瑙勬枃妗?
```

---

## 4. 鏍稿績瀹炵幇

### 4.1 ObservabilityClient.cs锛圕# Sentry 鍖呰锛?

**鑱岃矗**锛?
- Sentry SDK 鍒濆鍖栦笌鐢熷懡鍛ㄦ湡绠＄悊
- Release 鍏冩暟鎹厤缃?
- Before Send Hook锛堜簨浠惰繃婊や笌鑴辨晱锛?
- 鎬ц兘鎸囨爣涓婃姤

**浠ｇ爜绀轰緥**锛?

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Sentry;
using Sentry.Protocol;

namespace Game.Core.Observability
{
    /// <summary>
    /// Sentry 鍙娴嬫€у鎴风鍖呰
    /// 缁熶竴鍒濆鍖栥€侀厤缃€佷簨浠朵笂鎶ユ帴鍙?
    /// </summary>
    public class ObservabilityClient : IDisposable
    {
        private IHub _sentryHub;
        private readonly ObservabilityConfig _config;
        private readonly PiiDataScrubber _scrubber;

        public ObservabilityClient(ObservabilityConfig config)
        {
            _config = config;
            _scrubber = new PiiDataScrubber();
            InitializeSentry();
        }

        private void InitializeSentry()
        {
            SentrySdk.Init(options =>
            {
                // 鍩烘湰閰嶇疆
                options.Dsn = _config.SentryDsn;
                options.Environment = _config.Environment; // "dev" | "staging" | "prod"
                options.Release = _config.Release; // e.g., "godotgame@1.0.0+build.123"

                // 浼氳瘽杩借釜锛圧elease Health锛?
                options.AutoSessionTracking = true;
                options.SessionSampleRate = _config.SessionSampleRate; // Dev: 1.0, Prod: 0.1

                // 鎬ц兘鐩戞帶锛堥噰鏍凤級
                options.TracesSampleRate = _config.TracesSampleRate; // Dev: 1.0, Prod: 0.01
                options.ProfilesSampleRate = _config.ProfilesSampleRate; // Dev: 0.1, Prod: 0.01

                // 浜嬩欢鍓嶇疆澶勭悊锛圥II 鑴辨晱銆佽繃婊わ級
                options.BeforeSend = (sentryEvent, hint) =>
                {
                    // 鑴辨晱 PII锛坋mail銆乸hone銆両P锛?
                    _scrubber.ScrubEvent(sentryEvent);

                    // 杩囨护鐗瑰畾閿欒锛堝搴撶増鏈鍛婏級
                    if (_ShouldFilterEvent(sentryEvent, hint))
                        return null;

                    // 娣诲姞鑷畾涔変笂涓嬫枃
                    sentryEvent.Tags["platform"] = "godot";
                    sentryEvent.Tags["version"] = _config.Release;

                    return sentryEvent;
                };

                // Breadcrumb 澶勭悊
                options.BeforeBreadcrumb = (breadcrumb, hint) =>
                {
                    // 杩囨护鏁忔劅 Breadcrumb锛堝瀵嗛挜鍦?URL 涓級
                    if (breadcrumb.Message?.Contains("password") == true)
                        return null;

                    // 闄愬埗 Breadcrumb 鏁伴噺锛堥槻姝㈠唴瀛樻孩鍑猴級
                    return breadcrumb;
                };
            });

            _sentryHub = SentrySdk.CurrentHub;
        }

        /// <summary>
        /// 鎹曟崏寮傚父骞剁珛鍗充笂鎶?
        /// </summary>
        public void CaptureException(Exception ex, Dictionary<string, object> extras = null)
        {
            var scope = new Scope();
            if (extras != null)
            {
                foreach (var (key, value) in extras)
                {
                    scope.SetExtra(key, value);
                }
            }

            _sentryHub.CaptureException(ex, scope);
        }

        /// <summary>
        /// 璁板綍缁撴瀯鍖栨棩蹇椾簨浠?
        /// </summary>
        public void LogEvent(string level, string message, Dictionary<string, object> tags = null,
            Dictionary<string, object> extras = null)
        {
            var sentryEvent = new SentryEvent
            {
                Message = message,
                Level = _ParseLogLevel(level),
                Timestamp = DateTimeOffset.UtcNow
            };

            // 娣诲姞鏍囩
            if (tags != null)
            {
                foreach (var (key, value) in tags)
                {
                    sentryEvent.Tags[key] = value?.ToString() ?? "null";
                }
            }

            // 娣诲姞棰濆淇℃伅
            if (extras != null)
            {
                foreach (var (key, value) in extras)
                {
                    sentryEvent.Extra[key] = value;
                }
            }

            _sentryHub.CaptureEvent(sentryEvent);
        }

        /// <summary>
        /// 璁板綍 Breadcrumb锛堢敤鎴锋搷浣滆冻杩癸級
        /// </summary>
        public void RecordBreadcrumb(string category, string message,
            BreadcrumbLevel level = BreadcrumbLevel.Info, Dictionary<string, string> data = null)
        {
            var breadcrumb = new Breadcrumb(message, category)
            {
                Level = level,
                Data = data ?? new Dictionary<string, string>()
            };

            _sentryHub.AddBreadcrumb(breadcrumb);
        }

        /// <summary>
        /// 娣诲姞鑷畾涔変笂涓嬫枃锛堢敤鎴蜂俊鎭€佽澶囩瓑锛?
        /// </summary>
        public void SetUserContext(string userId, string email = null, string username = null)
        {
            _sentryHub.ConfigureScope(scope =>
            {
                scope.User = new Sentry.Protocol.User
                {
                    Id = userId,
                    Email = email,
                    Username = username
                };
            });
        }

        /// <summary>
        /// 涓婃姤鎬ц兘鎸囨爣锛堜笌 Phase 15 鑱斿姩锛?
        /// </summary>
        public void ReportPerformanceMetric(string metricName, long valueUs)
        {
            _sentryHub.ConfigureScope(scope =>
            {
                scope.SetExtra($"perf_{metricName}_us", valueUs);
                scope.SetExtra($"perf_{metricName}_ms", valueUs / 1000.0);
            });
        }

        /// <summary>
        /// 鍒锋柊浠讳綍寰呭鐞嗕簨浠跺苟绛夊緟 Sentry 搴旂瓟
        /// 锛堝簲鍦ㄥ簲鐢ㄥ叧闂墠璋冪敤锛?
        /// </summary>
        public void Close(TimeSpan? timeout = null)
        {
            SentrySdk.Close(timeout ?? TimeSpan.FromSeconds(2));
        }

        public void Dispose()
        {
            Close();
        }

        // ======== 绉佹湁杈呭姪鏂规硶 ========

        private SentryLevel _ParseLogLevel(string level)
        {
            return level?.ToLower() switch
            {
                "debug" => SentryLevel.Debug,
                "info" => SentryLevel.Info,
                "warning" => SentryLevel.Warning,
                "error" => SentryLevel.Error,
                "fatal" => SentryLevel.Fatal,
                _ => SentryLevel.Info
            };
        }

        private bool _ShouldFilterEvent(SentryEvent sentryEvent, SentryHint hint)
        {
            // 杩囨护绀轰緥锛氬拷鐣ュ簱鐗堟湰璀﹀憡
            if (sentryEvent.Message?.Contains("deprecated") == true)
                return true;

            // 杩囨护缃戠粶瓒呮椂閿欒锛堝彲閲嶈瘯锛屼笉褰卞搷鍋ュ悍搴︼級
            if (hint.OriginalException is TimeoutException)
                return _config.FilterNetworkTimeouts;

            return false;
        }
    }

    /// <summary>
    /// Sentry 閰嶇疆瀵硅薄
    /// </summary>
    public class ObservabilityConfig
    {
        public string SentryDsn { get; set; }
        public string Environment { get; set; } // "dev" | "staging" | "prod"
        public string Release { get; set; } // e.g., "godotgame@1.0.0+build.123"

        // 閲囨牱鐜囷紙0.0-1.0锛?
        public double SessionSampleRate { get; set; } = 1.0; // Dev: 1.0, Prod: 0.1
        public double TracesSampleRate { get; set; } = 0.1; // Dev: 1.0, Prod: 0.01
        public double ProfilesSampleRate { get; set; } = 0.1; // Dev: 0.1, Prod: 0.01

        // 杩囨护閫夐」
        public bool FilterNetworkTimeouts { get; set; } = true;

        // PII 鑴辨晱
        public bool ScrubbingEnabled { get; set; } = true;
    }
}
```

### 4.1.1 Sentry 閰嶇疆鏂囦欢绀轰緥锛坮es://config/sentry_config.json锛?

```json
{
  "dsn": "https://examplePublicKey@o0.ingest.sentry.io/0",
  "environment": "dev",
  "release": "godotgame@0.1.0+local",
  "sessionSampleRate": 1.0,
  "tracesSampleRate": 0.1,
  "breadcrumbs": true
}
```

璇存槑锛?
- `release` 涓?`environment` 寤鸿鍦ㄦ瀯寤洪樁娈电敱 Phase-17 鐨勫厓鏁版嵁鑴氭湰鑷姩娉ㄥ叆锛堢‘淇濆彲杩芥函鍒?commit/tag锛夛紱
- `sessionSampleRate` 鍙湪 dev 璋冨ぇ锛?.0锛変互渚胯皟璇曪紝鍦ㄧ敓浜х缉灏忥紙濡?0.1锛夛紱
- 鑻ラ渶瑕佹湰鍦扮绾块槦鍒楋紝璇风粨鍚堚€淥fflineEventQueue鈥濆湪鏃犵綉缁滄椂鏆傚瓨锛岀綉缁滄仮澶嶅悗鎵归噺涓婃姤銆?

### 4.2 Observability.cs锛圙odot Autoload锛?

**鑱岃矗**锛?
- 缁熶竴鐨勬棩蹇楁帴鍙ｏ紙C# 涓?GDScript 鍏煎锛?
- Breadcrumb 鑷姩璁板綍锛圫cene 鍒囨崲銆丼ignal銆丄PI 璋冪敤锛?
- 浼氳瘽涓庨敊璇崟鎹夌殑 GDScript 灞傚皝瑁?

**浠ｇ爜绀轰緥**锛?

```csharp
// C# equivalent (Godot 4 + C# + GdUnit4)
using Godot;
using System.Threading.Tasks;

public partial class ExampleTest
{
    public async Task Example()
    {
        var scene = GD.Load<PackedScene>("res://Game.Godot/Scenes/MainScene.tscn");
        var inst = scene?.Instantiate();
        var tree = (SceneTree)Engine.GetMainLoop();
        tree.Root.AddChild(inst);
        await ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        inst.QueueFree();
    }
}
```

### 4.3 ReleaseHealthGate.cs锛堝彂甯冨仴搴烽棬绂侊級

**鑱岃矗**锛?
- 鏌ヨ Sentry Release Health API
- 妫€鏌?Crash-Free Sessions 鏄惁杈惧埌闃堝€?
- 杩斿洖 Pass/Fail 鍒ゅ畾缁?CI

**浠ｇ爜绀轰緥**锛?

```csharp
using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Text.Json;
using System.Collections.Generic;

namespace Game.Core.Observability
{
    /// <summary>
    /// 鍙戝竷鍋ュ悍闂ㄧ锛氭鏌?Sentry Release Health 鏄惁杈炬爣
    /// 鐢ㄤ簬 CI 娴佺▼涓樆姝笉鍚堟牸鐗堟湰鍙戝竷
    /// </summary>
    public class ReleaseHealthGate
    {
        private readonly string _sentryOrg;
        private readonly string _sentryProject;
        private readonly string _sentryAuthToken;
        private readonly double _minCrashFreeSessions; // e.g., 0.995

        public ReleaseHealthGate(string org, string project, string authToken,
            double minCrashFreeSessions = 0.995)
        {
            _sentryOrg = org;
            _sentryProject = project;
            _sentryAuthToken = authToken;
            _minCrashFreeSessions = minCrashFreeSessions;
        }

        /// <summary>
        /// 妫€鏌ユ寚瀹?Release 鐨勫仴搴风姸鎬?
        /// </summary>
        public async Task<(bool passed, string reportJson)> CheckReleaseHealth(
            string release, string environment = "production")
        {
            try
            {
                var releaseHealth = await _QueryReleaseHealth(release, environment);

                // 鍒ゅ畾鏄惁閫氳繃闂ㄧ
                var crashFreeSessions = releaseHealth.GetProperty("crashFreeSessions")
                    .GetDouble();
                var passed = crashFreeSessions >= _minCrashFreeSessions;

                // 鐢熸垚鎶ュ憡
                var report = new
                {
                    release = release,
                    environment = environment,
                    passed = passed,
                    crash_free_sessions = crashFreeSessions,
                    threshold = _minCrashFreeSessions,
                    margin = (crashFreeSessions - _minCrashFreeSessions) * 100, // %
                    checked_at = DateTimeOffset.UtcNow,
                    details = new
                    {
                        sessions = releaseHealth.GetProperty("sessions").GetProperty("total").GetInt64(),
                        crashed = releaseHealth.GetProperty("sessions").GetProperty("crashed").GetInt64(),
                        abnormal = releaseHealth.GetProperty("sessions").GetProperty("abnormal").GetInt64(),
                        errored = releaseHealth.GetProperty("sessions").GetProperty("errored").GetInt64()
                    }
                };

                var json = JsonSerializer.Serialize(report, new JsonSerializerOptions
                {
                    WriteIndented = true
                });

                return (passed, json);
            }
            catch (Exception ex)
            {
                return (false, $"{{ \"error\": \"{ex.Message}\" }}");
            }
        }

        /// <summary>
        /// 鐢熸垚鍙鍖?HTML 鎶ュ憡
        /// </summary>
        public string GenerateHtmlReport(string release, string reportJson)
        {
            var report = JsonSerializer.Deserialize<JsonElement>(reportJson);
            var passed = report.GetProperty("passed").GetBoolean();
            var crashFree = (report.GetProperty("crash_free_sessions").GetDouble() * 100);
            var threshold = (_minCrashFreeSessions * 100);
            var margin = report.GetProperty("margin").GetDouble();

            var statusClass = passed ? "pass" : "fail";
            var statusText = passed ? "PASS" : "FAIL";

            var html = $@"
<html>
<head>
    <title>Release Health Report - {release}</title>
    <style>
        body {{ font-family: monospace; margin: 20px; }}
        .header {{ font-size: 24px; font-weight: bold; margin-bottom: 20px; }}
        .status {{ font-size: 18px; padding: 10px; margin-bottom: 20px; }}
        .status.pass {{ background: #90EE90; }}
        .status.fail {{ background: #FFB6C6; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ccc; padding: 10px; text-align: left; }}
        th {{ background: #f0f0f0; }}
        .metric {{ font-weight: bold; }}
    </style>
</head>
<body>
    <div class='header'>Release Health Gate Report</div>

    <div class='status {statusClass}'>
        {statusText}
    </div>

    <table>
        <tr><th>Metric</th><th>Value</th><th>Threshold</th><th>Status</th></tr>
        <tr>
            <td class='metric'>Crash-Free Sessions</td>
            <td>{crashFree:F2}%</td>
            <td>{threshold:F2}%</td>
            <td>{(passed ? "PASS" : "FAIL")} {margin:+F2}%</td>
        </tr>
    </table>

    <h3>Session Details</h3>
    <table>
        <tr><th>Status</th><th>Count</th></tr>
        <tr><td>Total Sessions</td><td>{report.GetProperty("details").GetProperty("sessions").GetInt64()}</td></tr>
        <tr><td>Crashed</td><td>{report.GetProperty("details").GetProperty("crashed").GetInt64()}</td></tr>
        <tr><td>Abnormal</td><td>{report.GetProperty("details").GetProperty("abnormal").GetInt64()}</td></tr>
        <tr><td>Errored</td><td>{report.GetProperty("details").GetProperty("errored").GetInt64()}</td></tr>
    </table>

    <p>Report generated: {report.GetProperty("checked_at").GetString()}</p>
</body>
</html>
";

            return html;
        }

        // ======== 绉佹湁鏂规硶 ========

        private async Task<JsonElement> _QueryReleaseHealth(string release, string environment)
        {
            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_sentryAuthToken}");

            // Sentry API: /organizations/{org}/releases/{release}/health/
            var url = $"https://sentry.io/api/0/organizations/{_sentryOrg}/releases/{release}/health/";

            if (!string.IsNullOrEmpty(environment))
            {
                url += $"?environment={environment}";
            }

            var response = await httpClient.GetAsync(url);
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();
            var doc = JsonDocument.Parse(json);

            return doc.RootElement;
        }
    }
}
```

### 4.4 PiiDataScrubber.cs锛圥II 鑴辨晱锛?

**鑱岃矗**锛?
- 妫€娴嬪苟绉婚櫎浜嬩欢涓殑鏁忔劅淇℃伅锛坋mail銆乸hone銆両P銆乁RL 鍙傛暟绛夛級
- 閬靛畧 GDPR/CCPA 闅愮瑙勮寖

**浠ｇ爜绀轰緥**锛?

```csharp
using System;
using System.Text.RegularExpressions;
using Sentry.Protocol;

namespace Game.Core.Observability
{
    /// <summary>
    /// PII锛堜釜浜哄彲璇嗗埆淇℃伅锛夎劚鏁忓伐鍏?
    /// 浠?Sentry 浜嬩欢涓Щ闄?email銆乸hone銆両P銆佸瘑閽ョ瓑鏁忔劅淇℃伅
    /// </summary>
    public class PiiDataScrubber
    {
        // 姝ｅ垯琛ㄨ揪寮忓尮閰?PII
        private static readonly Regex EmailRegex = new(@"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            RegexOptions.Compiled);
        private static readonly Regex PhoneRegex = new(@"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            RegexOptions.Compiled);
        private static readonly Regex IpRegex = new(@"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            RegexOptions.Compiled);
        private static readonly Regex ApiKeyRegex = new(@"(?:api[_-]?key|token|secret|password)\s*[:=]\s*([^\s&,;]+)",
            RegexOptions.IgnoreCase | RegexOptions.Compiled);

        public void ScrubEvent(SentryEvent sentryEvent)
        {
            if (sentryEvent == null) return;

            // 鑴辨晱娑堟伅
            if (!string.IsNullOrEmpty(sentryEvent.Message))
            {
                sentryEvent.Message = ScrubString(sentryEvent.Message);
            }

            // 鑴辨晱寮傚父娑堟伅涓庡爢鏍?
            if (sentryEvent.Exception != null)
            {
                foreach (var ex in sentryEvent.Exception)
                {
                    if (!string.IsNullOrEmpty(ex.Value))
                    {
                        ex.Value = ScrubString(ex.Value);
                    }
                    if (!string.IsNullOrEmpty(ex.Stacktrace?.Raw))
                    {
                        ex.Stacktrace.Raw = ScrubString(ex.Stacktrace.Raw);
                    }
                }
            }

            // 鑴辨晱鏍囩
            foreach (var tag in sentryEvent.Tags)
            {
                if (tag.Value is string tagValue)
                {
                    sentryEvent.Tags[tag.Key] = ScrubString(tagValue);
                }
            }

            // 鑴辨晱棰濆鏁版嵁
            foreach (var extra in sentryEvent.Extra)
            {
                if (extra.Value is string extraValue)
                {
                    sentryEvent.Extra[extra.Key] = ScrubString(extraValue);
                }
            }

            // 鑴辨晱鐢ㄦ埛鏁版嵁
            if (sentryEvent.User != null)
            {
                // 淇濈暀鐢ㄦ埛 ID锛堝簲璇ュ凡鏄尶鍚嶅寲鐨勶級锛屼絾鑴辨晱 email
                sentryEvent.User.Email = null; // 鎴栬€呰劚鏁忎负鍝堝笇鍊?
            }
        }

        public string ScrubString(string input)
        {
            if (string.IsNullOrEmpty(input))
                return input;

            // 鑴辨晱 email
            input = EmailRegex.Replace(input, "[EMAIL]");

            // 鑴辨晱鐢佃瘽鍙风爜
            input = PhoneRegex.Replace(input, "[PHONE]");

            // 鑴辨晱 IP 鍦板潃
            input = IpRegex.Replace(input, "[IP]");

            // 鑴辨晱 API 瀵嗛挜涓庝护鐗?
            input = ApiKeyRegex.Replace(input, "$1=[SECRET]");

            // 鑴辨晱甯歌瀵嗛挜瀛楁
            input = Regex.Replace(input, @"(password|secret|token)\s*[:=]\s*[^\s&,;]+",
                "$1=[REDACTED]", RegexOptions.IgnoreCase);

            return input;
        }
    }
}
```

### 4.5 OfflineEventQueue.cs锛堢绾夸簨浠堕槦鍒楋級

**鑱岃矗**锛?
- 鏈湴 SQLite 闃熷垪锛屽瓨鍌ㄦ棤缃戠粶鏃剁殑浜嬩欢
- 鎭㈠缃戠粶鍚庤嚜鍔ㄩ噸璇曚笂鎶?

**浠ｇ爜绀轰緥**锛?

```csharp
using System;
using System.Collections.Generic;
using Godot;

namespace Game.Core.Observability
{
    /// <summary>
    /// 绂荤嚎浜嬩欢闃熷垪锛氬綋缃戠粶绂荤嚎鏃舵湰鍦扮紦瀛樹簨浠?
    /// 鎭㈠缃戠粶鍚庢壒閲忎笂鎶ョ粰 Sentry
    /// </summary>
    public class OfflineEventQueue
    {
        private readonly string _dbPath;
        private ObservabilityClient _sentryClient;

        public OfflineEventQueue(string dbPath)
        {
            _dbPath = dbPath;
        }

        /// <summary>
        /// 鍏ラ槦浜嬩欢
        /// </summary>
        public void Enqueue(Dictionary<string, object> eventData)
        {
            try
            {
                // 浣跨敤 godot-sqlite 鎴栧叾浠?SQLite 椹卞姩鍐欏叆
                // INSERT INTO offline_events (timestamp, data) VALUES (?, ?)
                GD.PrintDebug($"[OfflineQueue] Enqueued event: {eventData}");
            }
            catch (Exception ex)
            {
                GD.PrintErr($"[OfflineQueue] Failed to enqueue: {ex.Message}");
            }
        }

        /// <summary>
        /// 鎵归噺鍑洪槦骞朵笂鎶?
        /// </summary>
        public async void FlushQueue(ObservabilityClient sentryClient)
        {
            _sentryClient = sentryClient;

            try
            {
                // SELECT * FROM offline_events LIMIT 100
                // 閫愪釜涓婃姤锛屾垚鍔熷悗鍒犻櫎
                GD.PrintDebug("[OfflineQueue] Flushing queued events...");
                // ... 涓婃姤閫昏緫 ...
                GD.PrintDebug("[OfflineQueue] Flush complete");
            }
            catch (Exception ex)
            {
                GD.PrintErr($"[OfflineQueue] Flush failed: {ex.Message}");
            }
        }
    }
}
```

---

## 5. 闆嗘垚鍒?CI/CD 娴佺▼

### 5.1 GitHub Actions 宸ヤ綔娴?

```yaml
# .github/workflows/release-health-gate.yml

name: Release Health Gate

on:
  workflow_dispatch:
    inputs:
      release_version:
        description: 'Release version to check (e.g., godotgame@1.0.0)'
        required: true
        default: 'godotgame@1.0.0'
      environment:
        description: 'Sentry environment'
        required: true
        default: 'production'
        type: choice
        options:
          - production
          - staging

jobs:
  release-health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check Release Health (Sentry)
        env:
          SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
          SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
        run: |
          python scripts/release_health_gate.py \
            --release "${{ github.event.inputs.release_version }}" \
            --environment "${{ github.event.inputs.environment }}" \
            --min-crash-free 0.995 \
            --output reports/health.json

      - name: Parse Health Report
        id: health
        run: |
          python -c "
          import json
          with open('reports/health.json') as f:
            data = json.load(f)
          print(f'PASSED={data[\"passed\"]}')
          print(f'CRASH_FREE={data[\"crash_free_sessions\"]:.2%}')
          print(f'MARGIN={data[\"margin\"]:+.2f}%')
          " >> $GITHUB_OUTPUT

      - name: Block Deployment if Unhealthy
        if: steps.health.outputs.PASSED == 'False'
        run: |
          echo "FAIL Release health check FAILED"
          echo "Crash-Free Sessions: ${{ steps.health.outputs.CRASH_FREE }}"
          echo "Required: 99.5%"
          exit 1

      - name: Approve Deployment
        if: steps.health.outputs.PASSED == 'True'
        run: |
          echo "Release health check PASSED"
          echo "Crash-Free Sessions: ${{ steps.health.outputs.CRASH_FREE }}"
          echo "Margin: ${{ steps.health.outputs.MARGIN }}"

      - name: Upload Health Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: health-reports
          path: reports/health.json
```

### 5.2 鏈湴楠岃瘉鍛戒护

```bash
# package.json 鑴氭湰

{
  "scripts": {
    "test:observability": "python scripts/release_health_gate.py --release godotgame@dev --environment dev",
    "observability:flush": "dotnet test src/Game.Core.Tests/Observability.Tests.cs",
    "sentry:sourcemaps": "python scripts/upload_sourcemaps.py",
    "release:create": "python scripts/generate_release_metadata.py --version $npm_package_version"
  }
}
```

---

## 6. 缁撴瀯鍖栨棩蹇楄鑼?

### 6.1 鏃ュ織鍒嗙被涓庢牱渚?

#### 搴旂敤鐢熷懡鍛ㄦ湡
```csharp
// 鍚姩
Observability.log_info("Application started", tags: {
    "version": "1.0.0+123",
    "environment": "production"
});

// 鍏抽棴
Observability.log_info("Application shutting down", extras: {
    "session_duration_s": 3600
});
```

#### 娓告垙閫昏緫
```csharp
// C# equivalent (Godot 4 + C# + GdUnit4)
using Godot;
using System.Threading.Tasks;

public partial class ExampleTest
{
    public async Task Example()
    {
        var scene = GD.Load<PackedScene>("res://Game.Godot/Scenes/MainScene.tscn");
        var inst = scene?.Instantiate();
        var tree = (SceneTree)Engine.GetMainLoop();
        tree.Root.AddChild(inst);
        await ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        inst.QueueFree();
    }
}
```

#### 鏁版嵁搴撴搷浣?
```csharp
// 鏌ヨ鎬ц兘寮傚父
if (queryTime > 100)
{
    Observability.log_warning($"Slow query detected", tags: {
        "query_type": "load_game_state",
        "duration_ms": queryTime
    }, extras: {
        "result_rows": resultCount
    });
}
```

#### 缃戠粶璋冪敤
```csharp
// C# equivalent (Godot 4 + C# + GdUnit4)
using Godot;
using System.Threading.Tasks;

public partial class ExampleTest
{
    public async Task Example()
    {
        var scene = GD.Load<PackedScene>("res://Game.Godot/Scenes/MainScene.tscn");
        var inst = scene?.Instantiate();
        var tree = (SceneTree)Engine.GetMainLoop();
        tree.Root.AddChild(inst);
        await ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        inst.QueueFree();
    }
}
```

### 6.2 Breadcrumb 瑙勮寖

```csharp
// C# equivalent (Godot 4 + C# + GdUnit4)
using Godot;
using System.Threading.Tasks;

public partial class ExampleTest
{
    public async Task Example()
    {
        var scene = GD.Load<PackedScene>("res://Game.Godot/Scenes/MainScene.tscn");
        var inst = scene?.Instantiate();
        var tree = (SceneTree)Engine.GetMainLoop();
        tree.Root.AddChild(inst);
        await ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        inst.QueueFree();
    }
}
```

---

## 7. 闅愮涓庡悎瑙?

### 7.1 GDPR 鍚堣

**鏁版嵁鏈€灏忓寲**锛?
- 浠呮敹闆嗗繀瑕佷俊鎭紙閿欒鍫嗘爤銆佺増鏈€佽澶囩被鍨嬶級
- 涓嶆敹闆嗙敤鎴?email / phone锛堝凡鑴辨晱锛?

**鐢ㄦ埛鎺у埗**锛?
- 鍦ㄥ簲鐢ㄨ缃彁渚?绂佺敤閬ユ祴"寮€鍏?
- 瀹炴柦鏃舵鏌ョ敤鎴烽€夐」锛?
  ```csharp
  if (userPreferences.TelemetryEnabled)
      observabilityClient.Init(...);
  ```

**鏁版嵁淇濈暀**锛?
- Sentry 浜戠鏁版嵁淇濈暀 90 澶╋紙鍙厤缃級
- 鏈湴鏃ュ織姣?7 澶╄嚜鍔ㄦ竻鐞?

### 7.2 鏁忔劅淇℃伅澶勭悊

**Before Send Hook**锛?
```csharp
options.BeforeSend = (sentryEvent, hint) =>
{
    // 绉婚櫎 PII
    _scrubber.ScrubEvent(sentryEvent);

    // 绉婚櫎鐜鍙橀噺涓殑瀵嗛挜
    sentryEvent.Message = Regex.Replace(
        sentryEvent.Message,
        @"(?:password|token)=\S+",
        "PASSWORD=[REDACTED]"
    );

    return sentryEvent;
};
```

---

## 8. 鎬ц兘寮€閿€璇勪及

| 鎿嶄綔 | 寮€閿€ | 褰卞搷 |
|-----|------|------|
| Sentry.Init() | ~50ms | 搴旂敤鍚姩 |
| log_event() 璋冪敤 | <1ms | 鏈湴鏃ュ織 + 鍐呭瓨闃熷垪 |
| 缃戠粶涓婃姤锛堝紓姝ワ級 | 100-500ms | 鍚庡彴绾跨▼锛屼笉闃诲涓荤嚎绋?|
| Session 杩借釜 | <0.5ms/甯?| 鍙拷鐣?|
| Breadcrumb 璁板綍 | <0.1ms | 鍙拷鐣?|

**浼樺寲绛栫暐**锛?
- 閲囨牱鐜囷紙Dev: 100%, Prod: 10%锛?
- 寮傛鎵归噺涓婃姤锛堜笉闃诲娓叉煋锛?
- 鏈湴缂撳啿锛堥槻姝㈢綉缁滄尝鍔級

---

## 9. 楠屾敹鏍囧噯

### 9.1 浠ｇ爜瀹屾暣鎬?

- [ ] ObservabilityClient.cs锛?00+ 琛岋級锛歋entry 鍒濆鍖栥€佷簨浠跺鐞嗐€佽劚鏁?
- [ ] Observability.cs锛?00+ 琛岋級锛氱粺涓€鏃ュ織鎺ュ彛銆丅readcrumb 璁板綍
- [ ] ReleaseHealthGate.cs锛?50+ 琛岋級锛氬彂甯冨仴搴锋鏌ャ€丠TML 鎶ュ憡
- [ ] PiiDataScrubber.cs锛?50+ 琛岋級锛歅II 鑴辨晱瑙勫垯
- [ ] OfflineEventQueue.cs锛?00+ 琛岋級锛氱绾块槦鍒椾笌鎵归噺涓婃姤

### 9.2 闆嗘垚瀹屾垚搴?

- [ ] GitHub Actions 宸ヤ綔娴侀厤缃紙release-health-gate.yml锛?
- [ ] Sentry 椤圭洰鍒涘缓锛堢粍缁囥€丏SN銆丄PI Token锛?
- [ ] 鏈湴楠岃瘉鍛戒护锛坣pm run test:observability锛?
- [ ] 鍙戝竷闂ㄧ涓?CI 闆嗘垚锛堚墺99.5% Crash-Free锛?
- [ ] 绂荤嚎闃熷垪涓庢仮澶嶆満鍒?

### 9.3 鏂囨。瀹屾垚搴?

- [ ] Phase 16 璇︾粏瑙勫垝鏂囨。锛堟湰鏂囷紝1200+ 琛岋級
- [ ] 缁撴瀯鍖栨棩蹇楄鑼冿紙logging-guidelines.md锛?
- [ ] 闅愮涓庡悎瑙勬枃妗ｏ紙privacy-compliance.md锛?
- [ ] Sentry 閰嶇疆鎸囧崡
- [ ] 鏁呴殰鎺掗櫎鎸囧崡

---

## 10. 鏃堕棿浼扮畻锛堝垎瑙ｏ級

| 浠诲姟 | 宸ヤ綔閲?| 鍒嗛厤 |
|-----|--------|------|
| ObservabilityClient.cs 寮€鍙?+ 娴嬭瘯 | 1.5 澶?| Day 1 |
| Observability.cs 涓庨泦鎴?| 1 澶?| Day 1-2 |
| 鍙戝竷鍋ュ悍闂ㄧ鑴氭湰 | 1 澶?| Day 2-3 |
| Sentry 閰嶇疆涓庨獙璇?| 0.5 澶?| Day 3 |
| 鏂囨。涓庨殣绉佸悎瑙?| 0.5 澶?| Day 4 |
| **鎬昏** | **4-5 澶?* | |

---

## 11. 鍚庣画闃舵鍏宠仈

| 闃舵 | 鍏宠仈 | 璇存槑 |
|-----|-----|------|
| Phase 15锛堟€ц兘棰勭畻锛?| 鈫?鏁版嵁鏉ユ簮 | 鎬ц兘鎸囨爣涓婃姤缁?Sentry |
| Phase 17锛堟瀯寤虹郴缁燂級 | 鈫?鍓嶇疆鏉′欢 | Release 鍏冩暟鎹渶鍦ㄦ瀯寤鸿剼鏈敓鎴?|
| Phase 18锛堝垎闃舵鍙戝竷锛?| 鈫?闆嗘垚 | Canary 鈫?Beta 鈫?Stable 鍚勯樁娈电殑 Release Health 绠＄悊 |
| Phase 19锛堝簲鎬ュ洖婊氾級 | 鈫?瑙﹀彂鍣?| Crash-Free 涓嬮檷瑙﹀彂鑷姩鍥炴粴 |
| Phase 20锛堝姛鑳介獙鏀讹級 | 鈫?娲炲療 | 鍔熻兘楠屾敹鐨勯敊璇巼涓庡穿婧冩暟鎹潵鑷?Sentry |

---

## 12. 鍏抽敭鍐崇瓥鐐?

### 鍐崇瓥 D1锛氶噰鏍风巼閰嶇疆
**閫夐」**锛?
- A. 鍏ㄩ噺閲囨牱锛圖ev: 100%, Prod: 100%锛夛細鎴愭湰楂樸€佹暟鎹噺澶?
- B. 鍒嗙幆澧冮噰鏍凤紙Dev: 100%, Prod: 10%锛夛細**鎺ㄨ崘**锛屽钩琛℃垚鏈笌瑕嗙洊
- C. 鍔ㄦ€侀噰鏍凤紙鍩轰簬閿欒鐜囷級锛氬鏉傘€侀毦浠ラ娴?

**缁撹**锛氶噰鐢?B锛孌ev 100% 渚夸簬寮€鍙戣皟璇曪紝Prod 10% 鎺у埗鎴愭湰

### 鍐崇瓥 D2锛歅II 澶勭悊绛栫暐
**閫夐」**锛?
- A. 涓嶆敹闆?PII锛氬畨鍏ㄤ絾淇℃伅涓㈠け
- B. 鏀堕泦浣嗚劚鏁忥紙Before Send Hook锛夛細**鎺ㄨ崘**锛屽钩琛￠殣绉佷笌鏈夌敤鎬?
- C. 鐢ㄦ埛鏄庣‘鍚屾剰鍚庢敹闆嗭細澶嶆潅搴﹂珮

**缁撹**锛氶噰鐢?B锛屼娇鐢?PiiDataScrubber 鑷姩鑴辨晱

### 鍐崇瓥 D3锛氱绾块槦鍒楃瓥鐣?
**閫夐」**锛?
- A. 绂荤嚎鏃朵涪寮冿細绠€鍗曚絾澶卞幓鏁版嵁
- B. SQLite 鏈湴闃熷垪锛?*鎺ㄨ崘**锛屾仮澶嶇綉缁滃悗鎵归噺涓婃姤
- C. 鍐呭瓨闃熷垪锛氬簲鐢ㄥ叧闂墠涓㈠け

**缁撹**锛氶噰鐢?B锛屼负鍏抽敭閿欒鎻愪緵淇濋殰

---

## 13. 浜や粯鐗╂竻鍗?

### 浠ｇ爜鏂囦欢
- [OK] `src/Game.Core/Observability/ObservabilityClient.cs`锛?00+ 琛岋級
- [OK] `src/Game.Core/Observability/ReleaseHealthGate.cs`锛?50+ 琛岋級
- [OK] `src/Game.Core/Observability/PiiDataScrubber.cs`锛?50+ 琛岋級
- [OK] `src/Game.Core/Observability/StructuredLogger.cs`锛?00+ 琛岋級
- [OK] `src/Game.Core/Offline/OfflineEventQueue.cs`锛?00+ 琛岋級
- [OK] `src/Godot/Observability.cs`锛?00+ 琛岋級

### 鑴氭湰
- [OK] `scripts/release_health_gate.py`锛?00+ 琛岋級
- [OK] `scripts/generate_release_metadata.py`锛?50+ 琛岋級
- [OK] `scripts/upload_sourcemaps.py`锛?00+ 琛岋級

### 閰嶇疆
- [OK] `.github/workflows/release-health-gate.yml`锛?0+ 琛岋級
- [OK] `config/sentry_config.json`锛堢ず渚嬮厤缃級

### 鏂囨。
- [OK] Phase-16-Observability-Sentry-Integration.md锛堟湰鏂囷紝1200+ 琛岋級
- [OK] docs/logging-guidelines.md锛?00+ 琛岋級
- [OK] docs/privacy-compliance.md锛?00+ 琛岋級
- [OK] docs/sentry-setup-guide.md锛?0+ 琛岋級

### 鎬昏鏁帮細2600+ 琛?

---

## 闄勫綍 A锛歋entry 椤圭洰鍒濆鍖栨竻鍗?

```bash
# 1. 鍒涘缓 Sentry 璐︽埛锛坔ttps://sentry.io锛?
# 2. 鍒涘缓 Organization: godot-game
# 3. 鍒涘缓 Projects:
#    - godotgame-dev (environment: dev)
#    - godotgame-staging (environment: staging)
#    - godotgame-prod (environment: production)

# 4. 鑾峰彇 DSN锛堟瘡涓」鐩級
# Example: https://key@sentry.io/projectid

# 5. 鐢熸垚 Auth Token锛圤rganization Settings 鈫?Auth Tokens锛?
# Scope: project:releases, organization:read

# 6. 淇濆瓨涓?GitHub Secrets:
export SENTRY_ORG=godot-game
export SENTRY_PROJECT=godotgame-prod
export SENTRY_AUTH_TOKEN=<token>
```

---

## 闄勫綍 B锛氬父瑙佹晠闅滄帓闄?

### 闂 1锛欳rash-Free Sessions 涓嶆洿鏂?
**鍘熷洜**锛歋ession 鏈惎鐢ㄣ€丼ample Rate 涓?0銆佷簨浠舵湭涓婃姤
**鎺掓煡**锛?
```csharp
// 纭閰嶇疆
options.AutoSessionTracking = true;
options.SessionSampleRate = 1.0; // Dev 鏃跺叏閲?
// 妫€鏌?Sentry 椤圭洰璁剧疆涓殑 Release Health 鏄惁鍚敤
```

### 闂 2锛歅II 鏈劚鏁?
**鍘熷洜**锛欱efore Send Hook 鏈敓鏁堛€佹鍒欒〃杈惧紡鍖归厤澶辫触
**鎺掓煡**锛?
```csharp
// 鍦?Before Send 涓坊鍔犳棩蹇?
options.BeforeSend = (e, h) => {
    Debug.WriteLine($"Event before scrub: {e.Message}");
    _scrubber.ScrubEvent(e);
    Debug.WriteLine($"Event after scrub: {e.Message}");
    return e;
};
```

### 闂 3锛氱绾块槦鍒楀爢绉?
**鍘熷洜**锛氱綉缁滄寔缁笉閫氥€佺己灏戞壒閲忎笂鎶ユ満鍒?
**鎺掓煡**锛?
```csharp
// 瀹氭湡妫€鏌ラ槦鍒楀ぇ灏?
var queueSize = _offlineQueue.GetQueueSize();
if (queueSize > 1000)
    Observability.log_warning($"Queue size: {queueSize}");

// 涓诲姩鍒锋柊闃熷垪
_offlineQueue.FlushQueue(_observabilityClient);
```

---

> 目标：提供“默认本地、可选远程”的观测最小集；本地 JSONL 事件日志 + Sentry 接入占位（默认不开启）。`n
---

**楠岃瘉鐘舵€?*锛歔OK] 鏋舵瀯鍚堢悊 | [OK] 浠ｇ爜瀹屾暣 | [OK] 宸ュ叿閾惧氨缁?| [OK] CI 闆嗘垚娓呮櫚 | [OK] 闅愮鍚堣
**鎺ㄨ崘璇勫垎**锛?3/100锛堝彲瑙傛祴鎬т綋绯诲畬鍠勶級
**瀹炴柦浼樺厛绾?*锛欻igh锛堝彂甯冮棬绂佸繀闇€锛?
> 鎻愮ず锛氫笌 Phase-13锛堣川閲忛棬绂侊級/Phase-15锛堟€ц兘闂ㄧ锛夊鎺モ€斺€斿彲灏?Release Health 鎸囨爣涓?perf.json銆佸満鏅祴璇曠粨鏋滐紙gdunit4-report.xml/json锛変竴骞剁撼鍏ラ棬绂佽仛鍚堬紝缁熶竴鍦?quality_gates.py 涓垽瀹氶€氳繃/澶辫触銆?


## 模板落地 / Template Landing

- Autoload：`SentryClient="res://Game.Godot/Scripts/Obs/SentryClient.cs"`（默认 Enabled=false；存在 `SENTRY_DSN` 时仅记录“准备发送”标记，不进行网络发送）
- 调用：`CaptureMessage(level, message, context?)` / `CaptureException(message, context?)`，写入 `user://logs/sentry/events-YYYYMMDD.jsonl`

