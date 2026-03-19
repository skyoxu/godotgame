# DELIVERY_PROFILE

## 1. 它是什么

`DELIVERY_PROFILE` 是本仓库的全局交付严格度开关。

它不是一个装饰性的标签，而是一组会真正影响仓库运行行为的参数包。它用于把以下内容统一到同一个模式下：

- CI 默认门禁
- 本地脚本默认参数
- `acceptance_check` 的严格度
- `test.py` 的覆盖率与 smoke 行为
- `run_gate_bundle.py` 的预算与硬门/软门倾向
- LLM 相关脚本的门槛、提示词强度和容错策略
- 默认安全姿态，也就是派生出来的 `SECURITY_PROFILE`
- `agent-review` 后置 sidecar 的执行/退出策略

一句话说清楚：

- `DELIVERY_PROFILE` 决定“当前阶段到底要多严”。

当前配置文件入口：

- `scripts/sc/config/delivery_profiles.json`

当前模板仓默认档位：

- `fast-ship`

## 2. 为什么要有它

这个机制是为了解决一个很容易反复出现的问题：

- 原型期需要先验证可玩性，不需要被重治理拖死。
- 日常开发需要基本质量和主机安全，但不该天天按发版级标准自虐。
- 发版前又必须收紧，不能继续用“差不多能跑”的口径糊过去。

如果没有 `DELIVERY_PROFILE`，团队通常会掉进两个坑：

- 到处手工加参数，最后每个脚本都是不同口径，CI 和本地也不一致。
- 整个仓库永远用一个过严默认值，日常开发速度被门禁长期拖慢。

所以 `DELIVERY_PROFILE` 的初衷就是止损：

- 用一个顶层开关，把“速度”和“治理”之间的平衡显式化。

## 3. 设计原则

这套机制的设计原则是：

- 只保留少量、清晰、可理解的档位。
- 由一个总开关驱动多个脚本，而不是每个脚本各搞一套默认值。
- 复制模板到新项目后，先改配置，不是先满仓库打补丁。
- `SECURITY_PROFILE` 默认从 `DELIVERY_PROFILE` 派生，避免双开关长期漂移。

这也意味着一条重要约束：

- 不要把 `DELIVERY_PROFILE` 变成失控的业务枚举表。

如果未来每个项目都开始新增一堆自定义 profile 名称，这套机制很快就会从“统一入口”退化成“新的复杂度来源”。

## 4. 当前三种模式

### 4.1 `playable-ea`

这是最轻的档位，核心目标是尽快验证“游戏能不能玩”。

适用场景：

- 非常早期的 EA 原型
- 主循环 spike
- 玩法试错分支
- 需要快速确认是否存在明显阻塞问题的阶段

当前口径概览：

- 默认派生 `security_profile = host-safe`
- `build.warn_as_error = false`
- 覆盖率硬门默认关闭
- 验收门禁大部分放宽
- LLM 语义类门禁大部分降级或跳过
- `task_links` 预警预算最高
- `agent_review.mode = skip`，默认不自动执行 reviewer sidecar

你可以把它理解为：

- 优先回答“能不能跑、能不能玩、有没有明显 blocker”。

它不适合作为长期发版默认档位。

### 4.2 `fast-ship`

这是模板当前默认档位，也是最适合日常开发的档位。

适用场景：

- 日常开发
- 功能集成
- 小团队快速商业化推进
- 需要基本质量，但不能被重治理压垮的项目阶段

当前口径概览：

- 默认派生 `security_profile = host-safe`
- `build.warn_as_error = true`
- 覆盖率门禁开启，但阈值低于 `standard`
- 验收门禁保留基础要求，但不过度苛刻
- LLM 审查以告警为主，不是高压强硬门
- `task_links` 预算处于中间值
- `agent_review.mode = warn`，会生成 reviewer sidecar，但 `needs-fix` 不会让主入口失败

你可以把它理解为：

- 优先回答“能不能较快交付，同时不把仓库搞烂”。

### 4.3 `standard`

这是最严的档位，核心目标是收口与发布前硬化。

适用场景：

- 发版前清账
- 重要里程碑前收口
- 合并到稳定主线前的强化检查
- 高风险改动后的严格回归

当前口径概览：

- 默认派生 `security_profile = strict`
- `build.warn_as_error = true`
- 覆盖率阈值最高
- 验收门禁最严格
- LLM 语义类门禁最严格
- `task_links` 预算最紧
- `agent_review.mode = require`，`needs-fix`/`block` 会让主入口返回非 0

你可以把它理解为：

- 优先回答“是否已经达到更稳定、更可发布的状态”。

它不适合作为每一次本地小改动的默认档位。

## 5. 三种模式与项目类型的建议映射

对于你前面提到的三类项目，可以这样映射：

- Windows only 的 PC 单机游戏 EA 简陋版 -> `playable-ea`
- Windows only 的 PC 单机游戏快速开发商业化版 -> `fast-ship`
- Windows only 的 PC 单机游戏正常版本 -> `standard`

但这里有一个容易误判的点：

- `fast-ship` 不是“最松”
- 真正最松的是 `playable-ea`
- `standard` 才是收口档

如果团队只看名字，不看定义，很容易切错档位。

## 6. 解析优先级

当前解析顺序应该理解为：

- CLI 参数 `--delivery-profile`
- 环境变量 `DELIVERY_PROFILE`
- `scripts/sc/config/delivery_profiles.json` 里的 `default_profile`

而 `SECURITY_PROFILE` 的正确定位是：

- 默认由 `DELIVERY_PROFILE` 派生
- 只有在你明确需要打破默认映射时，才手工覆写

这点非常重要。否则你会把一套总开关，又重新拆成两套长期漂移的开关。

## 7. 它当前会影响什么

在当前仓库里，`DELIVERY_PROFILE` 已经会影响或应当影响以下方面：

- 构建是否 `warn_as_error`
- 单测覆盖率门槛
- smoke 严格度
- acceptance 默认硬门/软门策略
- `task_test_refs` 与 `executed_refs` 是否要求非空
- 性能门禁默认阈值
- `task_links` 允许的 warning 预算
- LLM review 的严格度与预算
- obligations 提取脚本的运行强度
- semantic gate 的阈值
- `agent-review` 后置 sidecar 的执行与退出码策略
- CI summary 中的可观测性信息

所以这不是“文档概念”，而是“运行中的控制面”。

## 8. 如何使用

### 8.1 单次命令切换

适合你明确知道这一次要用什么档位。

示例：

```powershell
py -3 scripts/sc/run_review_pipeline.py --task-id 10 --godot-bin "$env:GODOT_BIN" --delivery-profile playable-ea
py -3 scripts/sc/run_review_pipeline.py --task-id 10 --godot-bin "$env:GODOT_BIN" --delivery-profile fast-ship
py -3 scripts/sc/run_review_pipeline.py --task-id 10 --godot-bin "$env:GODOT_BIN" --delivery-profile standard
```

### 8.2 当前终端会话切换

适合一个开发时段都想保持同一种口径。

```powershell
$env:DELIVERY_PROFILE='fast-ship'
py -3 scripts/sc/run_review_pipeline.py --task-id 10 --godot-bin "$env:GODOT_BIN" --skip-llm-review
```

### 8.3 CI 中切换

当前工作流已经接入了 `delivery_profile`：

- `.github/workflows/ci-windows.yml`
- `.github/workflows/windows-quality-gate.yml`

CI summary 应当固定输出：

- `DeliveryProfile: <playable-ea|fast-ship|standard>`
- `SecurityProfile: <host-safe|strict>`

原因很现实：

- 同一份门禁结果，如果没有 profile 上下文，其实是不可解释的。

## 9. 日常建议怎么切

建议直接采用这条团队规则：

- 本地日常开发默认用 `fast-ship`
- 玩法探索、快速试错、EA 验证用 `playable-ea`
- 发版前、里程碑前、准备合并稳定主线时用 `standard`

这条规则的好处是：

- 日志更有意义
- 团队沟通成本更低
- 不容易出现“我以为你用的是严格档，其实不是”的误判

## 10. 新项目复制后应该怎么调整

新项目从模板复制出来后，建议按这个顺序处理。

### Step 1：先定默认档位

编辑：

- `scripts/sc/config/delivery_profiles.json`

先改：

- `default_profile`

建议：

- 强玩法试错型新项目：`playable-ea` 或 `fast-ship`
- 普通快速商业化项目：`fast-ship`
- 已经成熟、强治理型项目：`standard`

不要一上来就为了“看起来正式”把默认值改成 `standard`。那通常会把团队重新拖回低效率状态。

### Step 2：改 profile 包，而不是散改脚本

仍然在 `scripts/sc/config/delivery_profiles.json` 中，优先调整 profile block 本身。

重点字段：

- `build.warn_as_error`
- `test.coverage_gate`
- `test.coverage_lines_min`
- `test.coverage_branches_min`
- `acceptance.strict_adr_status`
- `acceptance.require_task_test_refs`
- `acceptance.require_executed_refs`
- `acceptance.require_headless_e2e`
- `acceptance.subtasks_coverage`
- `acceptance.perf_p95_ms`
- `gate_bundle.task_links_max_warnings`
- `llm_review.semantic_gate`
- `llm_review.strict`
- `llm_obligations.consensus_runs`
- `llm_semantic_gate_all.max_needs_fix`
- `llm_semantic_gate_all.max_unknown`
- `agent_review.mode`

正确做法是：

- 先改 profile catalog
- 再让脚本继续从 catalog 派生

错误做法是：

- 新项目一有需求，就直接在单个脚本里硬编码特殊值

如果这么做，几轮之后这套总开关就名存实亡了。

### Step 3：保留有意识的安全映射

当前模板的默认映射是：

- `playable-ea` -> `host-safe`
- `fast-ship` -> `host-safe`
- `standard` -> `strict`

对于本地单机项目，即便你在“反篡改”和“本地数据不可改”方面采取降级策略，也不代表主机边界安全应该一起消失。

建议：

- 轻档位可以降级治理，不要顺手把主机边界也一起取消。

### Step 4：同步 CI 默认值

如果新项目修改了默认 profile，也要一起检查：

- `.github/workflows/ci-windows.yml`
- `.github/workflows/windows-quality-gate.yml`

否则会出现一种很糟糕的漂移：

- 配置文件说默认是 A
- CI 实际仍按 B 在跑

这种漂移比“没有 profile”还危险，因为它会制造假一致性。

### Step 5：同步项目说明文档

如果新项目把默认姿态改了，也应该同步修改：

- `README.md`
- `scripts/sc/README.md`
- `DELIVERY_PROFILE.md`

入口文档如果不改，后续开发者和 LLM 很容易继续按旧口径做事。

## 11. 不要这样用

以下做法不推荐：

- 不要因为 `standard` 看起来更专业，就把它当长期默认值
- 不要把 profile 之外的阈值散落硬编码到各个脚本里
- 不要长期到处显式传 `--security-profile` 去打破默认映射
- 不要过早引入太多项目特化 profile 名称
- 不要让 CI 输出缺少 `DeliveryProfile` / `SecurityProfile` 上下文

这些做法都会让这套机制失去价值。

## 12. 维护规则

以后每当你发现某个脚本开始需要“分阶段不同严格度”时，先问自己一个问题：

- 这个差异是不是应该并入 `DELIVERY_PROFILE`，而不是再增加一个零散 CLI 开关？

如果答案是“是”，那优先：

- 改 profile catalog
- 改统一 resolver
- 不要优先加孤立参数

只有这样，这套机制才会在模板仓和复制出来的新项目里保持长期可维护。

## 13. 一条最短操作建议

如果你不想每次都重新思考，直接记住这条：

- 日常开发：`fast-ship`
- 玩法试错：`playable-ea`
- 发版收口：`standard`

这就是当前模板仓对 `DELIVERY_PROFILE` 的预期使用方式。
