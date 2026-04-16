# Prototype 7天可玩 Godot 原型执行模板（中文）

本文档用于指导新仓在仍处于玩法验证阶段时，不进入 `workflow.md` 第五章和第六章，而是通过 prototype lane 和 prototype TDD 尽快做出一个能玩、能判断是否值得继续的 Godot 原型。

## 1. 适用前提

适用于以下情况：

- 还在验证玩法本身是否值得做
- 还不想启用 `.taskmaster/tasks/*.json` 正式跟踪
- 还不想填 acceptance refs / overlay refs / semantic review
- 目标是先做出“可实际操作”的 Godot 原型，再决定是否 promote

不适用于以下情况：

- 已经是正式交付任务
- 已经需要正式 acceptance / review 门禁
- 已经需要作为 Chapter 6 证据链的一部分

## 2. 核心原则

这个阶段要做的不是“做正式产品”，而是“快速验证这个想法值不值得继续”。

因此优先级是：

1. 可玩
2. 可验证
3. 可做出 discard / archive / promote 决策
4. 可以在后续 promote 时迁移回正式流程
5. 最后才是架构优雅性

## 3. 推荐目录结构

建议先把 prototype 与正式模块分开，不要一开始就把实验代码放进长期模块。

```text
Game.Godot/Prototypes/<slug>/
  <SlugPascalCase>Prototype.tscn
  Scripts/
  Assets/
Tests.Godot/tests/Prototype/<Slug>/
docs/prototypes/
```

例子：

```text
Game.Godot/Prototypes/combat-loop/
  CombatLoopPrototype.tscn
  Scripts/
    CombatLoopPrototype.cs
    EnemyDummy.cs
Tests.Godot/tests/Prototype/CombatLoop/
docs/prototypes/2026-04-15-combat-loop.md
```

## 4. 命名建议

- slug：`combat-loop`、`hud-flow`、`target-selection` 这种短横线命名
- 场景名：`<SlugPascalCase>Prototype.tscn`
- 脚本名：`<SlugPascalCase>Prototype.cs`、`EnemyDummy.cs` 等
- C# 测试名仍建议遵循 `ShouldX_WhenY`

## 5. 7天执行节奏

### Day 1：建原型记录，明确假设

目标：先写明要验证什么，而不是盲目写代码。

```powershell
py -3 scripts/python/dev_cli.py run-prototype-tdd --slug combat-loop --create-record-only --hypothesis "核心战斗循环值得继续做" --scope-in "移动、攻击、受击反馈、简单敌人" --scope-out "正式 task refs、acceptance refs、overlay refs、正式 review" --success-criteria "玩家可以完成一次完整战斗循环" --success-criteria "试玩后仍认为值得继续做" --next-step "先做最小可操作场景"
```

产物：

- `docs/prototypes/<date>-combat-loop.md`

### Day 2：做出最小可操作场景

目标：在 Godot 中做出一个可进入、可操作、可完成最小玩法循环的 prototype scene。

建议最少包含：

- 玩家节点
- 一个敌人假体
- 最简单的输入
- 最简单的反馈

这一天的验证以 Godot Editor 实际运行场景为主，不追求完整体系。

### Day 3：补最关键的 C# 小测试，跑 red

适合先钉住的内容：

- 状态切换
- 攻击 cooldown
- 目标选择
- 伤害结果

```powershell
py -3 scripts/python/dev_cli.py run-prototype-tdd --slug combat-loop --stage red --dotnet-target Game.Core.Tests/Game.Core.Tests.csproj --filter CombatLoop
```

成功标准：

- 至少一条验证失败
- prototype red 是有效的，而不是 `unexpected_green`

### Day 4：做最小实现，跑 green

```powershell
py -3 scripts/python/dev_cli.py run-prototype-tdd --slug combat-loop --stage green --dotnet-target Game.Core.Tests/Game.Core.Tests.csproj --filter CombatLoop
```

成功标准：

- 关键测试通过
- 在 Godot 场景中可以完成一个最小玩法循环

### Day 5：如果重点是交互，补 Godot / GdUnit 验证

如果这个原型重点是 HUD、UI、节奏或场景交互，可以单独补一小组 Godot 验证路径：

```text
Tests.Godot/tests/Prototype/CombatLoop/
```

red:

```powershell
py -3 scripts/python/dev_cli.py run-prototype-tdd --slug combat-loop --stage red --godot-bin "$env:GODOT_BIN" --gdunit-path tests/Prototype/CombatLoop
```

green:

```powershell
py -3 scripts/python/dev_cli.py run-prototype-tdd --slug combat-loop --stage green --godot-bin "$env:GODOT_BIN" --gdunit-path tests/Prototype/CombatLoop
```

这一天适合验证：

- HUD 是否出现
- 交互输入后 UI 是否更新
- 最小场景操作流是否成立

### Day 6：实际试玩，记录证据

这一天不再优先增加功能，而是进入“这个方向值不值得继续做”的判断阶段。

建议收集：

- 实际试玩视频
- 截图
- prototype summary / report
- 自己的观察笔记

重点读取产物：

- `docs/prototypes/<date>-<slug>.md`
- `logs/ci/<date>/prototype-tdd-<slug>-red/summary.json`
- `logs/ci/<date>/prototype-tdd-<slug>-green/summary.json`
- `logs/ci/<date>/prototype-tdd-<slug>-*/report.md`

### Day 7：做出退出决策

只允许三种结果：

- `discard`：方向不成立，停止
- `archive`：保留证据，但暂不进入正式交付
- `promote`：这个想法已经准备好转为正式任务

如果结果是 `promote`，后续再进入正式流程：

1. 创建正式 task
2. 补 task refs / acceptance refs / overlay refs
3. 需要时补 execution-plan / decision-log
4. 再切入 Chapter 6

## 6. 这个阶段不需要做的事

既然目标是“先做出可玩原型”，那么先不要做这些：

- 不建 `.taskmaster/tasks/*.json`
- 不补 acceptance refs
- 不补 overlay refs
- 不跑 `run_review_pipeline.py`
- 不跑 `llm_review_needs_fix_fast.py`
- 不把 prototype red/green 当成 Chapter 6 正式证据

## 7. 常用命令模板

### Day 1

```powershell
py -3 scripts/python/dev_cli.py run-prototype-tdd --slug combat-loop --create-record-only --hypothesis "核心战斗循环值得继续做"
```

### Day 3 red

```powershell
py -3 scripts/python/dev_cli.py run-prototype-tdd --slug combat-loop --stage red --dotnet-target Game.Core.Tests/Game.Core.Tests.csproj --filter CombatLoop
```

### Day 4 green

```powershell
py -3 scripts/python/dev_cli.py run-prototype-tdd --slug combat-loop --stage green --dotnet-target Game.Core.Tests/Game.Core.Tests.csproj --filter CombatLoop
```

### Day 5 Godot red

```powershell
py -3 scripts/python/dev_cli.py run-prototype-tdd --slug combat-loop --stage red --godot-bin "$env:GODOT_BIN" --gdunit-path tests/Prototype/CombatLoop
```

### Day 5 Godot green

```powershell
py -3 scripts/python/dev_cli.py run-prototype-tdd --slug combat-loop --stage green --godot-bin "$env:GODOT_BIN" --gdunit-path tests/Prototype/CombatLoop
```

## 8. 一句话总结

如果你的目标只是“先做出一个能玩的 Godot 原型”，那么正确做法是：用 prototype lane 管边界，用 `run-prototype-tdd` 做最小 red/green 闭环，用 Godot 场景实际试玩，并尽快做出 `discard | archive | promote` 决策。
