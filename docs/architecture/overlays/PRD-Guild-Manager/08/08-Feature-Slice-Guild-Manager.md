---
PRD-ID: PRD-Guild-Manager
Title: 功能纵切 — 公会管理器
Status: Active
Arch-Refs:
  - CH01
  - CH02
  - CH03
ADR-Refs:
  - ADR-0004
  - ADR-0005
  - ADR-0011
  - ADR-0019
Test-Refs:
  - Game.Core.Tests/Engine/GameEngineCoreEventTests.cs
  - Game.Core.Tests/Services/EventBusTests.cs
  - Tests.Godot/tests/UI/test_hud_updates_on_events.gd
  - Tests.Godot/tests/Scenes/Smoke/test_main_scene_smoke.gd
---

本页定义 `PRD-Guild-Manager` 在模板仓中的 08 章实现收口方式，只记录本功能纵切需要落地的契约、事件连线、测试入口与验收边界。

## 约束边界

- 跨切面阈值、安全基线、发布健康和 CI 门禁只引用 Base 与 ADR，不在本页复制。
- 事件、DTO、端口与常量的唯一事实源是 `Game.Core/Contracts/**`。
- 场景层只消费契约和事件，不得重新定义字符串事件名或复制契约结构。

## 契约落点

以下契约文件构成本纵切的最小闭环，必须保持与场景/UI 代码一致：

- `Game.Core/Contracts/DomainEvent.cs`：统一领域事件基类与元数据载体。
- `Game.Core/Contracts/EventTypes.cs`：集中定义事件类型常量，禁止 UI/场景硬编码 `core.*` 字符串。
- `Game.Core/Contracts/Guild/GuildMemberJoined.cs`：公会成员加入事件示例，作为模块事件契约基线。

## 运行时接线

- UI 或场景节点通过适配层发布/订阅 `DomainEvent` 派生事件。
- 事件类型字符串只能来自 `EventTypes` 或具体契约文件内的 `EventType` 常量。
- 如需新增公会纵切事件，应先在 `Game.Core/Contracts/Guild/` 目录新增具体契约文件，再更新对应 Overlay 文档与测试引用。

## 验收与测试

- 领域事件发布与事件总线行为由 `Game.Core.Tests/Engine/GameEngineCoreEventTests.cs` 和 `Game.Core.Tests/Services/EventBusTests.cs` 负责。
- HUD/UI 对事件消费的场景连线由 `Tests.Godot/tests/UI/test_hud_updates_on_events.gd` 覆盖。
- 主场景冒烟与基础信号连通由 `Tests.Godot/tests/Scenes/Smoke/test_main_scene_smoke.gd` 收口。

## 变更要求

- 任何新增/修改契约都必须同步更新 `Test-Refs` 与对应 08 合同页。
- 若改变安全口径、事件命名规则或质量门禁，必须同步新增或更新对应 ADR。
