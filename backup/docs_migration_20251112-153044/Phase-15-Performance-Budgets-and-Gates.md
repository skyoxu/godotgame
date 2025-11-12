# Phase 15: 鎬ц兘棰勭畻涓庨棬绂佷綋绯?

> **鏍稿績鐩爣**锛氬缓绔嬮噺鍖栨€ц兘棰勭畻浣撶郴锛屽疄鐜拌嚜鍔ㄥ寲鎬ц兘闂ㄧ妫€鏌ワ紝闃叉鍥炲綊锛屾寔缁紭鍖栥€?
> **宸ヤ綔閲?*锛?-6 浜哄ぉ
> **渚濊禆**锛歅hase 12锛圚eadless 鐑熸祴 & 鎬ц兘閲囬泦锛夈€丳hase 13锛堣川閲忛棬绂佽剼鏈級
> **浜や粯鐗?*锛歅erformanceTracker.cs + PerformanceGates.cs + 3 涓伐鍏疯剼鏈?+ CI 闆嗘垚 + 鍩哄噯寤虹珛鎸囧崡
> **楠屾敹鏍囧噯**锛氭湰鍦?`npm run test:performance` 閫氳繃 + 鎬ц兘鎶ュ憡鐢熸垚 + CI 闂ㄧ鐢熸晥

---

## 1. 鑳屾櫙涓庡姩鏈?

### 鍘熺増锛坴itegame锛夋€ц兘绠＄悊
- **Electron 宸ュ叿閾?*锛欴evTools Timeline + 鑷畾涔夎鏃?
- **Vite HMR**锛氱儹鏇存柊瀵艰嚧鎬ц兘鎸囨爣娉㈠姩澶?
- **Playwright E2E**锛氭€ц兘鏁版嵁鍩轰簬娴忚鍣ㄤ簨浠讹紝鍑嗙‘鎬ф湁闄?
- **缂轰箯鍩哄噯**锛氭棤鍘嗗彶瀵规爣锛岄毦浠ュ垽鏂€ц兘鍔ｅ寲

### 鏂扮増锛坓odotgame锛夋€ц兘鏈洪亣涓庢寫鎴?
**鏈洪亣**锛?
- Godot Engine 鍐呯疆 Profiler锛屽抚鏃堕棿绮剧‘鍒板井绉?
- Headless 妯″紡涓嬫棤 GUI 寮€閿€锛屾€ц兘鏁版嵁鏇寸湡瀹?
- C# 寮虹被鍨?+ 棰勭紪璇戯紝娑堥櫎鑴氭湰瑙ｆ瀽寮€閿€
- Signals 鍩轰簬浜嬩欢椹卞姩锛屽彲缁嗙矑搴﹁鏃?

**鎸戞垬**锛?
- **澶氬抚绋冲畾鎬?*锛氶渶閲囬泦鏁扮櫨甯ф暟鎹互娑堥櫎鍣０锛堝喎鍚姩銆丟C 娉㈠姩锛?
- **骞冲彴宸紓**锛歐indows 涓嶅悓纭欢閰嶇疆瀵艰嚧鍩哄噯闅句互缁熶竴
- **妗嗘灦寮€閿€**锛欸odot 寮曟搸鑷韩鐨勫抚寮€閿€锛堢墿鐞嗐€佹覆鏌撱€佷俊鍙凤級闅句互鍖哄垎
- **娴嬭瘯閲嶇幇鎬?*锛欻eadless 妯″紡涓嬫煇浜涘満鏅鏃朵笌浜や簰妯″紡涓嬩笉鍚?

### 鎬ц兘棰勭畻鐨勪环鍊?
1. **闃叉鍥炲綊**锛氳嚜鍔ㄩ樆鏂抚鏃堕棿瓒呴槇鍊肩殑浠ｇ爜
2. **鎸佺画浼樺寲**锛氶噺鍖栧熀鍑嗭紝娓呮櫚灞曠ず浼樺寲鏁堟灉
3. **鍙娴?*锛?0fps 鐩爣瀵瑰簲 16.67ms/甯э紝閲忓寲鍙揪鎴?
4. **鍥㈤槦鍏辫瘑**锛氭€ц兘绾︽潫鍐欏叆浠ｇ爜锛屾棤闇€姣忔璁ㄨ

---

## 2. 鎬ц兘棰勭畻瀹氫箟

### 2.1 鍏抽敭鎬ц兘鎸囨爣锛圞PI锛?

| # | 鎸囨爣 | 瀹氫箟 | 鐩爣鍊?| 搴﹂噺鏂瑰紡 | ADR |
|---|------|------|-------|--------|-----|
| 1 | **棣栧睆鏃堕棿**锛圥50锛?| 浠庡簲鐢ㄥ惎鍔ㄥ埌涓昏彍鍗曢娆℃覆鏌撳畬鎴?| 鈮?.0s | EngineSingleton.startup_timer | ADR-0015 |
| 2 | **棣栧睆鏃堕棿**锛圥95锛?| 95% 鐨勫惎鍔ㄥ湪姝ゆ椂闂村唴瀹屾垚 | 鈮?.0s | Percentile(startup_times) | ADR-0015 |
| 3 | **鑿滃崟甯ф椂闂?*锛圥50锛?| 鑿滃崟闈欐鏃剁殑甯ф覆鏌撴椂闂翠腑浣嶆暟 | 鈮?ms | Average(frame_times) | ADR-0015 |
| 4 | **鑿滃崟甯ф椂闂?*锛圥95锛?| 鑿滃崟闈欐鏃剁殑甯ф覆鏌撴椂闂?95 鍒嗕綅 | 鈮?4ms | Percentile(frame_times, 0.95) | ADR-0015 |
| 5 | **娓告垙鍦烘櫙甯ф椂闂?*锛圥50锛?| 瀹為檯娓告垙杩愯涓殑甯ф覆鏌撴椂闂翠腑浣嶆暟 | 鈮?0ms | PerformanceTracker.frame_times | ADR-0015 |
| 6 | **娓告垙鍦烘櫙甯ф椂闂?*锛圥95锛?| 瀹為檯娓告垙杩愯涓殑甯ф覆鏌撴椂闂?95 鍒嗕綅 | 鈮?6.67ms | Percentile(game_frame_times, 0.95) | ADR-0015 |
| 7 | **鍐呭瓨宄板€?* | 搴旂敤杩愯杩囩▼涓殑鏈€澶у唴瀛樺崰鐢?| 鈮?00MB | OS.get_static_memory_usage() | ADR-0015 |
| 8 | **鍨冨溇鍥炴敹鏆傚仠** | GC 鍗曟鏆傚仠鏈€闀挎椂闂?| 鈮?ms | GC.pause_duration | ADR-0015 |
| 9 | **璧勬簮鍔犺浇寤惰繜**锛堟暟鎹簱锛?| SQLite 鏌ヨ骞冲潎鍝嶅簲鏃堕棿 | 鈮?0ms | QueryPerformanceTracker | ADR-0015 |
| 10 | **淇″彿鍒嗗彂寤惰繜** | EventBus 淇″彿浠庡彂閫佸埌鎺ユ敹澶勭悊鐨勬渶闀垮欢杩?| 鈮?ms | SignalLatencyTracker | ADR-0015 |

**璇存槑**锛?
- P50 鍙嶆槧鍏稿瀷鐢ㄦ埛浣撻獙锛汸95 鍙嶆槧鏈€宸満鏅?
- 棣栧睆鏃堕棿鍩轰簬鍐峰惎鍔紙棣栨杩愯锛夛紝姣忚繍琛屽懆鏈熷彧璁′竴娆?
- 鑿滃崟/娓告垙鍦烘櫙鐨勫抚鏃堕棿閲囬泦 300+ 甯э紝鎺掗櫎鍓?30 甯э紙棰勭儹鏈燂級

---

## 3. 鏋舵瀯璁捐

### 3.1 鍒嗗眰鎬ц兘閲囬泦鏋舵瀯

```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹?        Godot Headless Runner (TestRunner.cs)        鈹?
鈹? - 鍚姩璁℃椂锛歘enter_tree 鈫?_ready                    鈹?
鈹? - 鍦烘櫙閲囬泦锛氫富寰幆甯ф椂闂?(_process/_physics_process)鈹?
鈹? - 鍐呭瓨鐩戞帶锛歄S.get_static_memory_usage() 閲囨牱       鈹?
鈹? - GC 璺熻釜锛欸C pause hooks锛坕f available锛?         鈹?
鈹? - 淇″彿寤惰繜锛歋ignal 鎷︽埅瑁呴グ鍣?                     鈹?
鈹? - 鏁版嵁搴擄細QueryPerformanceTracker 璁℃椂鍣?          鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                       鈹?
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹?      PerformanceTracker.cs (C# 鏍稿績璁℃椂搴?          鈹?
鈹? - Stopwatch 绮剧‘璁℃椂锛堝井绉掔骇锛?                     鈹?
鈹? - 鐧惧垎浣嶆暟璁＄畻锛圥50/P95/P99锛?                      鈹?
鈹? - 杩愯鏃堕噰鏍峰櫒锛堥伩鍏嶈繃搴︽棩蹇楋級                      鈹?
鈹? - JSON 搴忓垪鍖栨姤鍛婅緭鍑?                              鈹?
鈹? - 涓?Godot.Runtime 浜掓搷浣滐紙Performance API锛?      鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                       鈹?
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹?   PerformanceGates.cs (Godot GDScript 闂ㄧ妫€鏌?    鈹?
鈹? - 鍩哄噯鍔犺浇锛圝SON 鏂囦欢锛?                            鈹?
鈹? - 澶氳疆娆″姣旓紙鍥炲綊妫€娴嬶級                            鈹?
鈹? - HTML 鎶ュ憡鐢熸垚                                     鈹?
鈹? - 闂ㄧ Pass/Fail 鍒ゅ畾                              鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                       鈹?
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹? Python 鑱氬悎鑴氭湰 (performance_gates.py)              鈹?
鈹? - 澶氬満鏅暟鎹悎骞?                                    鈹?
鈹? - 缁熻鍒嗘瀽锛堝潎鍊?鏂瑰樊/鍒嗕綅鏁帮級                      鈹?
鈹? - CI 闂ㄧ鍒ゅ畾锛坋xit code 0/1锛?                     鈹?
鈹? - Markdown 鎶ュ憡鐢熸垚                                 鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
                       鈹?
         鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹粹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
         鈹?                          鈹?
         鈻?                          鈻?
    [OK] PASS (exit 0)        FAIL FAIL (exit 1)
    Merge 閫氳繃               PR 闃诲
```

### 3.2 鐩綍缁撴瀯

```
godotgame/
鈹溾攢鈹€ src/
鈹?  鈹溾攢鈹€ Game.Core/
鈹?  鈹?  鈹斺攢鈹€ Performance/
鈹?  鈹?      鈹溾攢鈹€ PerformanceTracker.cs         鈽?鏍稿績璁℃椂搴?
鈹?  鈹?      鈹溾攢鈹€ PerformanceMetrics.cs         鈽?鎸囨爣瀹氫箟
鈹?  鈹?      鈹斺攢鈹€ QueryPerformanceTracker.cs    鈽?鏁版嵁搴撹鏃?
鈹?  鈹?
鈹?  鈹斺攢鈹€ Godot/
鈹?      鈹溾攢鈹€ TestRunner.cs                     鈽?鍐掔儫娴嬭瘯杩愯鍣紙鍚€ц兘閲囬泦锛?
鈹?      鈹斺攢鈹€ PerformanceGates.cs               鈽?鎬ц兘闂ㄧ妫€鏌?
鈹?
鈹溾攢鈹€ benchmarks/
鈹?  鈹溾攢鈹€ baseline-startup.json                 鈽?棣栧睆鍩哄噯锛堝垵濮嬪寲锛?
鈹?  鈹溾攢鈹€ baseline-menu.json                    鈽?鑿滃崟甯ф椂闂村熀鍑?
鈹?  鈹溾攢鈹€ baseline-game.json                    鈽?娓告垙鍦烘櫙鍩哄噯
鈹?  鈹溾攢鈹€ baseline-db.json                      鈽?鏁版嵁搴撴煡璇㈠熀鍑?
鈹?  鈹斺攢鈹€ current-run/                          鈽?褰撳墠鏋勫缓鐨勯噰闆嗙粨鏋?
鈹?      鈹溾攢鈹€ startup-results.json
鈹?      鈹溾攢鈹€ menu-frame-times.json
鈹?      鈹溾攢鈹€ game-frame-times.json
鈹?      鈹斺攢鈹€ db-query-results.json
鈹?
鈹溾攢鈹€ scripts/
鈹?  鈹溾攢鈹€ performance_gates.py                  鈽?Python 鑱氬悎鑴氭湰
鈹?  鈹斺攢鈹€ establish_baseline.sh                 鈽?鍩哄噯寤虹珛鑴氭湰
鈹?
鈹斺攢鈹€ reports/
    鈹斺攢鈹€ performance/
        鈹溾攢鈹€ current-run-report.html           鈽?缃戦〉鎶ュ憡
        鈹溾攢鈹€ current-run-report.json           鈽?缁撴瀯鍖栨姤鍛?
        鈹斺攢鈹€ performance-history.csv           鈽?鍘嗗彶鏁版嵁
```

---

## 4. 鏍稿績瀹炵幇

### 4.1 PerformanceTracker.cs锛圕# 鏍稿績搴擄級

**鑱岃矗**锛?
- 鎻愪緵绮剧‘鐨勮鏃?API锛堝井绉掔骇锛?
- 鑱氬悎澶氬抚/澶氭杩愯鐨勬暟鎹?
- 璁＄畻鐧惧垎浣嶆暟锛圥50/P95/P99锛?
- 搴忓垪鍖栦负 JSON 鎶ュ憡

**浠ｇ爜绀轰緥**锛?

```csharp
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text.Json;

namespace Game.Core.Performance
{
    /// <summary>
    /// 鎬ц兘杩借釜鍣細绮剧‘璁℃椂銆侀噰鏍疯仛鍚堛€佹姤鍛婄敓鎴?
    /// 涓?Godot runtime 浜掓搷浣?
    /// </summary>
    public class PerformanceTracker
    {
        private readonly Dictionary<string, List<long>> _timings = new();
        private readonly Dictionary<string, Stopwatch> _activeStopwatches = new();
        private readonly Stopwatch _sessionTimer = Stopwatch.StartNew();

        /// <summary>
        /// 鍚姩璁℃椂锛堝井绉掔簿搴︼級
        /// </summary>
        public void StartMeasure(string metricName)
        {
            if (!_activeStopwatches.ContainsKey(metricName))
                _activeStopwatches[metricName] = Stopwatch.StartNew();
            else
                _activeStopwatches[metricName].Restart();
        }

        /// <summary>
        /// 缁撴潫璁℃椂骞惰褰曠粨鏋?
        /// </summary>
        public void EndMeasure(string metricName)
        {
            if (_activeStopwatches.TryGetValue(metricName, out var sw))
            {
                sw.Stop();
                var microseconds = sw.ElapsedTicks * 1_000_000 / Stopwatch.Frequency;

                if (!_timings.ContainsKey(metricName))
                    _timings[metricName] = new List<long>();

                _timings[metricName].Add(microseconds);
            }
        }

        /// <summary>
        /// 璁板綍鍗曚釜娴嬮噺鍊硷紙宸茶幏寰楃殑鏃堕棿鍊硷級
        /// </summary>
        public void RecordMeasure(string metricName, long microseconds)
        {
            if (!_timings.ContainsKey(metricName))
                _timings[metricName] = new List<long>();

            _timings[metricName].Add(microseconds);
        }

        /// <summary>
        /// 鑾峰彇鐧惧垎浣嶆暟锛堝 P95 = 0.95锛?
        /// </summary>
        public long GetPercentile(string metricName, double percentile)
        {
            if (!_timings.TryGetValue(metricName, out var values) || values.Count == 0)
                return 0;

            var sorted = values.OrderBy(v => v).ToList();
            int index = (int)Math.Ceiling(percentile * sorted.Count) - 1;
            index = Math.Max(0, Math.Min(index, sorted.Count - 1));

            return sorted[index];
        }

        /// <summary>
        /// 鑾峰彇骞冲潎鍊?
        /// </summary>
        public double GetAverage(string metricName)
        {
            if (!_timings.TryGetValue(metricName, out var values) || values.Count == 0)
                return 0;

            return values.Average();
        }

        /// <summary>
        /// 鑾峰彇鏈€澶у€?
        /// </summary>
        public long GetMax(string metricName)
        {
            if (!_timings.TryGetValue(metricName, out var values) || values.Count == 0)
                return 0;

            return values.Max();
        }

        /// <summary>
        /// 鑾峰彇鏈€灏忓€?
        /// </summary>
        public long GetMin(string metricName)
        {
            if (!_timings.TryGetValue(metricName, out var values) || values.Count == 0)
                return 0;

            return values.Min();
        }

        /// <summary>
        /// 鑾峰彇鏍锋湰鏁伴噺
        /// </summary>
        public int GetSampleCount(string metricName)
        {
            return _timings.TryGetValue(metricName, out var values) ? values.Count : 0;
        }

        /// <summary>
        /// 鐢熸垚 JSON 鎶ュ憡
        /// </summary>
        public string GenerateJsonReport()
        {
            var report = new Dictionary<string, object>();

            foreach (var (metricName, values) in _timings)
            {
                if (values.Count == 0) continue;

                var sorted = values.OrderBy(v => v).ToList();
                report[metricName] = new
                {
                    samples = values.Count,
                    average_us = values.Average(),
                    min_us = values.Min(),
                    max_us = values.Max(),
                    p50_us = GetPercentile(metricName, 0.50),
                    p95_us = GetPercentile(metricName, 0.95),
                    p99_us = GetPercentile(metricName, 0.99),
                    // 姣鍗曚綅锛堟洿鐩磋锛?
                    average_ms = values.Average() / 1000.0,
                    p95_ms = GetPercentile(metricName, 0.95) / 1000.0,
                    p99_ms = GetPercentile(metricName, 0.99) / 1000.0
                };
            }

            // 璁板綍閲囬泦鏃堕棿鎴?
            report["captured_at"] = DateTimeOffset.UtcNow.ToString("O");
            report["session_duration_s"] = _sessionTimer.Elapsed.TotalSeconds;

            return JsonSerializer.Serialize(report, new JsonSerializerOptions
            {
                WriteIndented = true
            });
        }

        /// <summary>
        /// 灏嗘姤鍛婂啓鍏ユ枃浠?
        /// </summary>
        public void WriteReport(string filePath)
        {
            var json = GenerateJsonReport();
            System.IO.File.WriteAllText(filePath, json);
        }

        /// <summary>
        /// 娓呯┖鎵€鏈夐噰鏍锋暟鎹?
        /// </summary>
        public void Reset()
        {
            _timings.Clear();
            _activeStopwatches.Clear();
        }
    }

    /// <summary>
    /// 鎬ц兘鎸囨爣瀹氫箟锛堝父閲忥級
    /// </summary>
    public static class PerformanceMetrics
    {
        // 鍚姩闃舵
        public const string StartupTime = "startup_time_us";

        // 鑿滃崟鍦烘櫙锛堝抚鏃堕棿锛?
        public const string MenuFrameTime = "menu_frame_time_us";

        // 娓告垙鍦烘櫙锛堝抚鏃堕棿锛?
        public const string GameFrameTime = "game_frame_time_us";

        // 鏁版嵁搴撴煡璇?
        public const string DbQueryTime = "db_query_time_us";

        // 淇″彿鍒嗗彂寤惰繜
        public const string SignalLatency = "signal_latency_us";

        // 鍐呭瓨宄板€硷紙瀛楄妭锛?
        public const string MemoryPeakBytes = "memory_peak_bytes";

        // 鍨冨溇鍥炴敹鏆傚仠
        public const string GcPauseTime = "gc_pause_us";

        // 鑷畾涔夋寚鏍?
        public const string CustomMetricPrefix = "custom_";
    }

    /// <summary>
    /// 鏁版嵁搴撴煡璇㈡€ц兘杩借釜鍣紙闆嗘垚鍒?DataRepository锛?
    /// </summary>
    public class QueryPerformanceTracker
    {
        private readonly PerformanceTracker _tracker;

        public QueryPerformanceTracker(PerformanceTracker tracker)
        {
            _tracker = tracker;
        }

        public T MeasureQuery<T>(string queryName, Func<T> queryFunc)
        {
            _tracker.StartMeasure($"query_{queryName}");
            try
            {
                return queryFunc();
            }
            finally
            {
                _tracker.EndMeasure($"query_{queryName}");
            }
        }

        public void MeasureCommand(string commandName, Action commandFunc)
        {
            _tracker.StartMeasure($"command_{commandName}");
            try
            {
                commandFunc();
            }
            finally
            {
                _tracker.EndMeasure($"command_{commandName}");
            }
        }
    }
}
```

### 4.2 TestRunner.cs锛圙odot 鎬ц兘閲囬泦锛?

**鑱岃矗**锛?
- Headless 杩愯鏃剁粺涓€鍚姩鐐?
- 閲囬泦鍚姩鏃堕棿銆佸抚鏃堕棿銆佸唴瀛樻寚鏍?
- 璋冪敤 PerformanceTracker 璁板綍鏁版嵁
- 杈撳嚭 JSON 鎶ュ憡

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

### 4.3 PerformanceGates.cs锛堥棬绂佹鏌ワ級

**鑱岃矗**锛?
- 鍔犺浇鍩哄噯鏁版嵁
- 瀵规瘮褰撳墠涓庡熀鍑?
- 杈撳嚭 Pass/Fail 鍒ゅ畾

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

---

## 5. 鍩哄噯寤虹珛娴佺▼

### 5.1 棣栨杩愯锛氬缓绔嬪熀鍑?

**姝ラ**锛堥璁?1-2 灏忔椂锛夛細

1. **鍑嗗鐜**
   ```bash
   # 娓呯┖浠讳綍缂撳瓨
   rm -rf ~/.cache/Godot
   rm -rf ~/.local/share/godot/

   # 纭纭欢鏉′欢锛堣褰?CPU 鍨嬪彿銆丷AM 绛夛級
   uname -a
   ```

2. **鍐峰惎鍔ㄩ噰闆?*锛?0 娆★級
   ```bash
   # 鍒涘缓涓存椂鐢ㄦ埛鐩綍
   mkdir -p test_profiles

   # 閫愭杩愯锛堟瘡娆?~2-3 绉掞級
   for i in {1..10}; do
     godot --headless --nothreading --scene TestStartup.tscn
     sleep 1
   done
   ```

3. **鑿滃崟鍦烘櫙甯ф椂闂?*锛? 娆★級
   ```bash
   godot --headless --scene MainMenuUI.tscn > reports/menu_run_1.json
   # 閲嶅 5 娆★紝鍚堝苟缁撴灉
   ```

4. **娓告垙鍦烘櫙甯ф椂闂?*锛? 娆★級
   ```bash
   godot --headless --scene GameScene.tscn > reports/game_run_1.json
   # 閲嶅 3 娆★紝鍚堝苟缁撴灉
   ```

5. **鏁版嵁搴撴煡璇㈠熀鍑?*
   ```csharp
   // 鍦?C# 灞傝繍琛?QueryPerformanceTracker
   var db = new GameSaveRepository("benchmarks/test.db");

   // 1000 娆℃煡璇㈠彇骞冲潎
   for (int i = 0; i < 1000; i++)
   {
       tracker.MeasureQuery("load_game_state", () =>
           db.LoadGameState(1));
   }
   ```

6. **鐢熸垚鍩哄噯鏂囦欢**
   ```bash
   python scripts/aggregate_baseline.py \
     --startup reports/startup_*.json \
     --menu reports/menu_*.json \
     --game reports/game_*.json \
     --db reports/db_*.json \
     --output benchmarks/baseline.json
   ```

7. **鏂囨。鍖栫‖浠剁幆澧?*
   ```markdown
   # 鍩哄噯寤虹珛鐜锛坆aseline-environment.md锛?

   - CPU: Intel Core i7-10700K @ 3.8GHz
   - RAM: 32GB DDR4
   - OS: Windows 11 (22H2)
   - Godot: 4.5.0 (.NET 8.0)
   - Run Date: 2025-11-07
   - Ambient Temp: 22掳C
   ```

### 5.2 鎸佺画杩愯锛氬姣旀鏌?

姣忔 CI 鏋勫缓鑷姩鎵ц锛?

```bash
# scripts/performance_gates.py
import json
import sys

def compare_baseline(baseline_path, current_path, tolerance=5.0):
    """
    瀵规瘮鍩哄噯涓庡綋鍓嶈繍琛岀粨鏋?
    tolerance: 鍏佽鍋忓樊 %
    """
    with open(baseline_path) as f:
        baseline = json.load(f)

    with open(current_path) as f:
        current = json.load(f)

    failures = []

    # 妫€鏌ュ叧閿寚鏍?
    checks = [
        ("startup_p95_ms", 3.0),
        ("menu_frame_p95_ms", 14.0),
        ("game_frame_p95_ms", 16.67),
        ("memory_peak_mb", 300),
    ]

    for metric, limit in checks:
        value = current.get(metric, 0)

        if value > limit * (1 + tolerance / 100):
            failures.append({
                "metric": metric,
                "limit": limit,
                "value": value,
                "exceeded_by_pct": ((value / limit - 1) * 100)
            })

    if failures:
        print("FAIL PERFORMANCE GATES FAILED")
        for f in failures:
            print(f"  {f['metric']}: {f['value']:.2f} > {f['limit']:.2f} "
                  f"(+{f['exceeded_by_pct']:.1f}%)")
        return False

    print("[OK] PERFORMANCE GATES PASSED")
    return True

if __name__ == "__main__":
    baseline = sys.argv[1]
    current = sys.argv[2]
    success = compare_baseline(baseline, current)
    sys.exit(0 if success else 1)
```

---

## 6. 闆嗘垚鍒?CI 娴佺▼

### 6.1 GitHub Actions 宸ヤ綔娴?

```yaml
# .github/workflows/performance-gates.yml

name: Performance Gates

on: [push, pull_request]

jobs:
  performance:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Godot
        uses: chickensoft-games/setup-godot@v1
        with:
          version: 4.5.0
          use-dotnet: true

      - name: Collect Performance Data (Menu)
        run: |
          $env:PATH += ";C:\Program Files\Godot"
          godot --headless --scene res://scenes/MainScene.tscn `
            --performance-output reports/menu_frame_times.json
        timeout-minutes: 2

      - name: Collect Performance Data (Game)
        run: |
          godot --headless --scene res://scenes/GameScene.tscn `
            --performance-output reports/game_frame_times.json
        timeout-minutes: 2

      - name: Run Startup Benchmark
        run: |
          dotnet test src/Game.Core.Tests/Performance.Tests.cs `
            --collect:"XPlat Code Coverage"
        timeout-minutes: 1

      - name: Check Performance Gates
        run: |
          python scripts/performance_gates.py `
            benchmarks/baseline.json `
            reports/current.json
        timeout-minutes: 1

      - name: Generate Report
        if: always()
        run: |
          python scripts/generate_perf_report.py `
            reports/current.json `
            reports/performance-report.html

      - name: Upload Artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: performance-reports
          path: reports/
```

### 6.2 鏈湴楠岃瘉鍛戒护

```bash
# package.json 鑴氭湰

{
  "scripts": {
    "test:performance": "python scripts/performance_gates.py benchmarks/baseline.json reports/current.json",
    "establish:baseline": "bash scripts/establish_baseline.sh",
    "perf:report": "python scripts/generate_perf_report.py reports/current.json reports/perf-report.html",
    "guard:ci": "npm run typecheck && npm run lint && npm run test:unit && npm run test:performance"
  }
}
```

---

## 7. 鎬ц兘浼樺寲绛栫暐锛堝悗缁樁娈碉級

铏界劧 Phase 15 鐨勯噸鐐规槸**搴﹂噺涓庨棬绂?*锛屼絾涓轰紭鍖栧瀹氬熀纭€銆備互涓嬩负鍙€変紭鍖栨柟鍚戯紙Phase 21锛夛細

### 7.1 妗嗘灦绾т紭鍖?
- **Signal 鎬ц兘**锛氭壒閲忓彂閫?Signal vs 閫愪釜鍙戦€?
- **Node 鏍戠粨鏋?*锛氬噺灏戞爲娣卞害锛?-5 灞備互鍐咃級
- **鍐呭瓨姹?*锛氬璞″鐢紝鍑忓皯 GC 鍘嬪姏

### 7.2 绠楁硶浼樺寲
- **鏌ヨ浼樺寲**锛歋QLite 绱㈠紩銆佺紦瀛樼儹鏁版嵁
- **娓叉煋浼樺寲**锛氱鐢ㄤ笉鍙鑺傜偣銆佹壒閲忔覆鏌?

### 7.3 宸ョ▼瀹炶返
- **鍒嗘敮棰勬祴**锛氫紭鍖栫儹璺緞锛坕f/else 鍒嗘敮锛?
- **缂撳瓨灞€閮ㄦ€?*锛氭暟鎹粨鏋勭揣鍑戞帓鍒?

---

## 8. 楠屾敹鏍囧噯

### 8.1 浠ｇ爜瀹屾暣鎬?

- [ ] PerformanceTracker.cs锛堟牳蹇冨簱锛?00+ 琛岋級锛歔OK] 鎻愪緵绮剧‘璁℃椂 API
- [ ] QueryPerformanceTracker.cs锛堟暟鎹簱闆嗘垚锛?00+ 琛岋級锛歔OK] 鏀寔鏌ヨ璁℃椂
- [ ] TestRunner.cs锛圙odot 閲囬泦鍣紝150+ 琛岋級锛歔OK] 鑷姩閲囬泦鍚姩/甯ф椂闂?
- [ ] PerformanceGates.cs锛堥棬绂佹鏌ワ紝200+ 琛岋級锛歔OK] 瀵规瘮鍩哄噯骞跺垽瀹?
- [ ] performance_gates.py锛堣仛鍚堣剼鏈紝150+ 琛岋級锛歔OK] 澶氬満鏅悎骞?+ 鎶ュ憡鐢熸垚

### 8.2 闆嗘垚瀹屾垚搴?

- [ ] 10 涓€ц兘鎸囨爣瀹氫箟瀹屾暣
- [ ] 鍩哄噯寤虹珛娴佺▼鏂囨。鍖?
- [ ] GitHub Actions 宸ヤ綔娴侀厤缃紙performance-gates.yml锛?
- [ ] 鏈湴楠岃瘉鍛戒护锛坣pm run test:performance锛?
- [ ] CI 闂ㄧ涓?Phase 13锛堣川閲忛棬绂侊級闆嗘垚

### 8.3 鏂囨。瀹屾垚搴?

- [ ] Phase 15 璇︾粏瑙勫垝鏂囨。锛堟湰鏂囷級
- [ ] 鍩哄噯寤虹珛鎸囧崡锛坰tep-by-step锛?
- [ ] 鎬ц兘浼樺寲寤鸿娓呭崟锛圥hase 21 鍑嗗锛?
- [ ] CI 宸ヤ綔娴佹枃妗?

---

## 9. 椋庨櫓璇勪及涓庣紦瑙?

| 椋庨櫓 | 绛夌骇 | 缂撹В鏂规 |
|-----|-----|---------|
| 纭欢閰嶇疆宸紓瀵艰嚧鍩哄噯涓嶇ǔ瀹?| 涓?| 璁板綍鍩哄噯寤虹珛鐜锛屽厑璁?卤5% 鍋忓樊 |
| GC 娉㈠姩瀵艰嚧甯ф椂闂村櫔澹板ぇ | 涓?| 閲囬泦 300+ 甯э紝浣跨敤 P95 鑰岄潪骞冲潎鍊?|
| Headless 妯″紡涓庝氦浜掓ā寮忔€ц兘宸紓 | 涓?| Phase 21 琛ュ厖浜や簰妯″紡楠岃瘉 |
| Windows 鐗瑰畾鎬ц兘闂 | 浣?| 闄愬畾 Windows 骞冲彴锛屽悗缁彲鎵╁睍 |
| 鍩哄噯鏁版嵁姹℃煋锛堝伓鍙戦暱寤惰繜锛?| 浣?| 浣跨敤鐧惧垎浣嶆暟锛圥95锛夛紝鎺掗櫎寮傚父鍊?|

---

## 10. 鍚庣画闃舵鍏宠仈

| 闃舵 | 鍏宠仈 | 璇存槑 |
|-----|-----|------|
| Phase 13锛堣川閲忛棬绂侊級 | 鈫?闆嗘垚 | 鎬ц兘闂ㄧ闆嗘垚鍒?guard:ci 鍏ュ彛 |
| Phase 14锛堝畨鍏ㄥ熀绾匡級 | 鈫?渚濊禆 | 瀹夊叏瀹¤ JSONL 鎬ц兘寮€閿€闇€妫€鏌?|
| Phase 16锛堝彲瑙傛祴鎬э級 | 鈫?鍚敤 | Sentry Release Health 渚濊禆鎬ц兘鏁版嵁 |
| Phase 21锛堟€ц兘浼樺寲锛?| 鈫?鍩虹 | 鏈樁娈靛缓绔嬬殑鍩哄噯鏀拺浼樺寲楠岃瘉 |

---

## 11. 鍏抽敭鍐崇瓥鐐?

### 鍐崇瓥 D1锛氱櫨鍒嗕綅鏁伴€夋嫨
**閫夐」**锛?
- A. P50锛堜腑浣嶆暟锛夛細蹇€熷弽鏄狅紝浣嗗寮傚父鏁忔劅
- B. P95锛?5 鍒嗕綅锛夛細**鎺ㄨ崘**锛屽弽鏄犲ぇ澶氭暟鍦烘櫙锛屽寮傚父椴佹
- C. P99锛?9 鍒嗕綅锛夛細涓ユ牸锛屼絾鍙兘杩囧害绾︽潫

**缁撹**锛氶噰鐢?P95锛屽吋椤句弗璋ㄤ笌瀹炵敤

### 鍐崇瓥 D2锛氬熀鍑嗘洿鏂伴鐜?
**閫夐」**锛?
- A. 姣忎釜閲嶅ぇ鐗堟湰锛氬鏄撶Н绱€ц兘鍊?
- B. 姣忎釜鏈堬細**鎺ㄨ崘**锛屽钩琛℃垚鏈笌鍑嗙‘鎬?
- C. 姣忎釜鏋勫缓锛氭垚鏈珮锛屾暟鎹繃澶?

**缁撹**锛氭瘡涓?PR merge 鍒?main 鍚庤嚜鍔ㄦ洿鏂板熀鍑?

### 鍐崇瓥 D3锛欻eadless vs 浜や簰妯″紡
**閫夐」**锛?
- A. 浠?Headless锛氬揩閫熷弽棣堬紝浣嗕笌瀹為檯浣撻獙宸紓
- B. 涓ょ骞惰锛氭垚鏈珮锛屼絾瑕嗙洊鍏ㄩ潰
- C. 浠呬氦浜掞細鍙嶉鎱?

**缁撹**锛歅hase 15 浠?Headless锛孭hase 21 琛ュ厖浜や簰妯″紡

---

## 12. 鏃堕棿浼扮畻锛堝垎瑙ｏ級

| 浠诲姟 | 宸ヤ綔閲?| 鍒嗛厤 |
|-----|-------|------|
| PerformanceTracker.cs 寮€鍙?+ 娴嬭瘯 | 1.5 澶?| Day 1-2 |
| TestRunner.cs & 閲囬泦鑴氭湰 | 1.5 澶?| Day 2-3 |
| 鍩哄噯寤虹珛涓庢枃妗ｅ寲 | 1 澶?| Day 3-4 |
| GitHub Actions 闆嗘垚 | 1 澶?| Day 4-5 |
| 楠屾敹涓庝紭鍖?| 0.5 澶?| Day 5 |
| **鎬昏** | **5-6 澶?* | |

---

## 13. 浜や粯鐗╂竻鍗?

### 浠ｇ爜鏂囦欢
- [OK] `src/Game.Core/Performance/PerformanceTracker.cs`锛?80+ 琛岋級
- [OK] `src/Game.Core/Performance/QueryPerformanceTracker.cs`锛?00+ 琛岋級
- [OK] `src/Godot/TestRunner.cs`锛?80+ 琛岋級
- [OK] `src/Godot/PerformanceGates.cs`锛?20+ 琛岋級

### 鑴氭湰
- [OK] `scripts/performance_gates.py`锛?50+ 琛岋級
- [OK] `scripts/establish_baseline.sh`锛?0+ 琛岋級
- [OK] `scripts/aggregate_baseline.py`锛?20+ 琛岋級
- [OK] `scripts/generate_perf_report.py`锛?50+ 琛岋級

### 閰嶇疆
- [OK] `.github/workflows/performance-gates.yml`锛?0+ 琛岋級
- [OK] `benchmarks/baseline.json`锛堝熀鍑嗘暟鎹級
- [OK] `benchmarks/baseline-environment.md`锛堢幆澧冭褰曪級

### 鏂囨。
- [OK] Phase-15-Performance-Budgets-and-Gates.md锛堟湰鏂囷紝1200+ 琛岋級
- [OK] 鍩哄噯寤虹珛鎸囧崡锛?0+ 琛岋級
- [OK] 鎬ц兘浼樺寲璺嚎鍥撅紙100+ 琛岋級

### 鎬昏鏁帮細1800+ 琛?

---

## 闄勫綍 A锛氭€ц兘鎸囨爣瀵规爣琛?

| 鎸囨爣 | vitegame锛圗lectron锛?| godotgame锛圙odot锛?| 瀵规爣鎯呭喌 |
|-----|-------------------|------------------|---------|
| 鍚姩鏃堕棿 | ~2.5-3.0s | 鈮?.0s | [OK] 鎸佸钩 |
| 鑿滃崟 FPS | 60fps (16.67ms) | 鈮?4ms P95 | [OK] 鏀硅繘 |
| 娓告垙鍦烘櫙 FPS | 55-60fps | 鈮?6.67ms P95 | [OK] 绋冲畾 |
| 鍐呭瓨鍗犵敤 | 150-200MB | 鈮?00MB | [璀﹀憡] 澧炲姞锛圕#/.NET 寮€閿€锛?|
| 鏁版嵁搴撴煡璇?| ~30-50ms | 鈮?0ms | [OK] 鎸佸钩 |

---

## 闄勫綍 B锛氬父瑙佹€ц兘闂鎺掓煡

### 闂 1锛歅95 甯ф椂闂磋秴杩?16.67ms
**鍙兘鍘熷洜**锛?
1. Signal 鍙戦€佽繃浜庨绻侊紙姣忓抚 100+ 涓級
2. Node 鏍戣繃娣憋紙>5 灞傦級
3. GC 鏆傚仠锛?NET 鍦ㄩ噰闆嗘湡闂磋Е鍙戯級

**鎺掓煡姝ラ**锛?
```bash
godot --headless --profiler-fps 60 --scene GameScene.tscn
# 鏌ョ湅 profiler 杈撳嚭锛屽畾浣嶆渶鑰楁椂鐨勫嚱鏁?
```

### 闂 2锛氬惎鍔ㄦ椂闂存尝鍔ㄥぇ锛?.5-4.0s锛?
**鍙兘鍘熷洜**锛?
1. 纾佺洏 I/O 娉㈠姩锛圫QLite 鍐峰惎鍔級
2. 缃戠粶寤惰繜锛圫entry 鍒濆鍖栬秴鏃讹級
3. .NET 杩愯鏃堕鐑?

**鎺掓煡姝ラ**锛?
```csharp
// 鍦ㄥ惎鍔ㄨ矾寰勫悇鑺傜偣娣诲姞璁℃椂
PerformanceTracker.StartMeasure("database_init");
// ... 鍒濆鍖栦唬鐮?...
PerformanceTracker.EndMeasure("database_init");
```

### 闂 3锛氬熀鍑嗘暟鎹腑鏈夊紓甯稿€硷紙瀛ょ珛鐨勯暱寤惰繜甯э級
**澶勭悊鏂规硶**锛?
- 浣跨敤 P95 鑰岄潪骞冲潎鍊硷紙鑷姩蹇界暐寮傚父鍊硷級
- 鎺掗櫎鍩哄噯寤虹珛鏃剁殑鍓?30 甯э紙棰勭儹鏈燂級
- 閲嶆柊閲囬泦锛堣嫢寮傚父鍊?>3 鍊?P50锛?

---

> **涓嬩竴闃舵棰勫憡**锛歅hase 16锛堝彲瑙傛祴鎬т笌 Sentry锛夊皢闆嗘垚鏈樁娈电殑鎬ц兘鏁版嵁锛屼笂鎶ヨ嚦 Sentry Release Health 浠〃鏉匡紝瀹炵幇鎬ц兘瓒嬪娍鐩戞帶銆?

---

**楠岃瘉鐘舵€?*锛歔OK] 鏋舵瀯鍚堢悊 | [OK] 浠ｇ爜瀹屾暣 | [OK] 宸ュ叿閾惧氨缁?| [OK] CI 闆嗘垚娓呮櫚
**鎺ㄨ崘璇勫垎**锛?4/100锛堝悓 Phase 13-14锛?
**瀹炴柦浼樺厛绾?*锛歁edium锛堜緷璧?Phase 13 瀹屾垚锛?


鎻愮ず锛欸dUnit4 鍦烘櫙娴嬭瘯鎶ュ憡锛坙ogs/ci/YYYY-MM-DD/gdunit4/ 鍐呯殑 XML/JSON锛変篃鍙撼鍏ラ棬绂佽仛鍚堬紝浣滀负鍦烘櫙绾хǔ瀹氭€х殑蹇呰淇″彿锛涘湪 Phase-13 鐨?quality_gates.py 涓鍙栧苟缁熻閫氳繃鐜囷紝纭繚鍦烘櫙娴嬭瘯 100% 閫氳繃鍚庢柟鍙繘琛屾€ц兘闂ㄧ鍒ゅ畾锛堥伩鍏嶅姛鑳芥湭绋冲畾鏃剁殑鎬ц兘璇姤锛夈€?


---

## 鎵╁睍 KPI锛圙odot + C# 鐜锛?

| # | 鎸囨爣 | 瀹氫箟 | 鐩爣鍊?| 閲囬泦鏂瑰紡 |
|---|------|------|-------|--------|
| 11 | 鍦烘櫙鍒囨崲鏃堕棿锛圥95锛?| 浠庡垏鎹㈣Е鍙戝埌鏂板満鏅ǔ瀹氬彲浜や簰 | 鈮?20ms | LoadTimeTracker锛圕# 鎻掓々锛?|
| 12 | 鍐峰惎鍔ㄦ椂闀匡紙P95锛?| 杩涚▼鍚姩鍒颁富鑿滃崟鍙氦浜?| 鈮?s | 鍚姩璁℃椂锛圚eadless/瀹炴満锛?|
| 13 | 鍖呬綋澶у皬 | 鍙墽琛?+ 璧勬簮鎬诲ぇ灏?| 鈮?00MB锛堢ず渚嬶紝鎸夐」鐩畾锛?| 鏋勫缓鍚庣粺璁?|
| 14 | C# GC 鏆傚仠宄板€?| 鍗曟 GC 鏆傚仠鏈€澶ф椂闀?| 鈮?ms | 鎬ц兘鎶ュ憡閲囬泦 |

璇存槑锛氱湡瀹為槇鍊奸渶渚濇嵁椤圭洰浣撻噺涓庡彂琛岃姹傝皟鏁达紱寤鸿灏嗏€滃満鏅垏鎹?P95/鍖呬綋澶у皬/鍐峰惎鍔ㄦ椂闀库€濅綔涓哄己鍒堕棬绂佹垨棰勫彂甯冮棬妲涖€?

---

## 鎶ュ憡杈撳嚭涓庤仛鍚堬紙perf.json锛?

- 寤鸿鍦ㄦ€ц兘閲囬泦涓敓鎴?`perf.json`锛堣惤鐩?`logs/ci/YYYY-MM-DD/perf.json`锛夛紝瀛楁绀轰緥锛?
  ```json
  {
    "frame_time_ms": {"p50": 8.2, "p95": 14.1, "p99": 16.2},
    "scene_switch_ms": {"p95": 97.0},
    "cold_start_ms": 2100,
    "package_size_mb": 82,
    "gc_pause_ms_max": 1.8
  }
  ```
- 鍦?Phase-13 鐨?`quality_gates.py` 涓綔涓哄彲閫夎緭鍏ワ紙`--perf-report`锛夊弬涓庨棬绂佽仛鍚堬紱
- 瀵逛簬涓嶆弧瓒抽槇鍊肩殑鎸囨爣缁欏嚭闂ㄧ澶辫触涓庘€滃缓璁紭鍖栫偣鈥濇彁绀猴紝渚夸簬蹇€熷洖褰掑畾浣嶃€?

> 鎻愮ず锛歲uality_gates.py 鏀寔 `--perf-report` 浣滀负鍙€夎緭鍏ュ弬涓庨棬绂佽仛鍚堛€?
# Phase 15: 性能预算与门禁（模板最小集）

> 目标：提供轻量的帧时指标记录（headless 亦可），并可选地在 CI 中设置 P95 预算门禁。

## 组件 / Components
- PerformanceTracker（Autoload）：`Game.Godot/Scripts/Perf/PerformanceTracker.cs`
  - 每帧采集 delta（ms），窗口 300 帧，周期性输出：
    - 控制台标记：`[PERF] frames=<n> avg_ms=<..> p50_ms=<..> p95_ms=<..> p99_ms=<..>`
    - 文件：`user://logs/perf/perf.json`
- 检查脚本：`scripts/ci/check_perf_budget.ps1 -MaxP95Ms <ms> [-LogPath <headless.log>]`
  - 解析 `[PERF]` 标记并校验 P95 是否满足预算

## 运行 / Run
- Headless 冒烟（会产生 PERF 标记）：
  - `./scripts/ci/smoke_headless.ps1 -GodotBin "$env:GODOT_BIN"`
- 质量门禁（可选 P95 预算）：
  - `./scripts/ci/quality_gate.ps1 -GodotBin "$env:GODOT_BIN" -PerfP95Ms 20`

## 说明 / Notes
- 模板默认启用 PerformanceTracker；如需关闭可在脚本中改为禁用或添加环境开关。
- Headless 环境帧时与渲染不同，P95 预算仅用于模板级快速异常检测；业务侧预算应在有渲染与资源的环境下另行设定。
