# Godot+C# 模板快速开始（AI 协作视角）

> 目标读者：BMAD 游戏专家代理、task-master-ai、SuperClaude/Claude Code、Codex CLI，以及需要理解本模板“技术前提 + 命令入口”的人类开发者。

本项目是 **Windows-only 的 Godot 4.5.1 + C# 游戏模板**，用于支撑 ARC42/C4 + ADR 的 AI 驱动开发工作流。这里只描述 Godot 变体相关的约束与入口，不再展开 Electron/vitegame 细节。

---

## 1. 技术前提 SSoT（供 BMAD/PRD 使用）

- 平台与运行环境
  - 仅支持 Windows 桌面环境；CI 目标为 `windows-latest`。
  - 引擎：Godot 4.5.1 .NET（mono）控制台版，环境变量/参数统一命名为 `GODOT_BIN`。
  - .NET：8.x，用于 `Game.Core` 与 Godot C# 脚本编译与单元测试。

- 架构分层（Godot 变体）
  - `Game.Core`：纯 C# 域模型与服务，不引用 Godot API，可通过 xUnit 快速测试。
  - `Game.Godot`：适配层与场景脚本，仅在这里使用 Godot API（Nodes/Signals/Autoload）。
  - `Tests.Godot`：GdUnit4 场景集成测试项目（headless，禁用真实 UI 输入事件）。

- 持久化与配置
  - Settings 单一事实来源（SSoT）：`ConfigFile` → `user://settings.cfg`（ADR-0023）。
  - 领域数据：SQLite，通过 `SqliteDataStore` 适配器访问，仅允许 `user://` 路径，禁止 `..` 穿越，失败写审计 JSONL（ADR-0006）。

- 事件系统
  - Core 事件：`DomainEvent` + `EventBus` + `EventBusAdapter`（C#），在 Godot 中以 `DomainEventEmitted` Signal 暴露。
  - 命名规范：
    - UI 菜单：`ui.menu.<action>`（如 `ui.menu.start`, `ui.menu.settings`, `ui.menu.quit`）。
    - Screen 生命周期：`screen.<name>.<action>`（如 `screen.start.loaded`, `screen.settings.saved`）。
    - 领域事件（推荐）：`core.<entity>.<action>`（如 `core.score.updated`, `core.health.updated`, `core.game.started`）。
    - Demo 示例：`demo.*` 仅用于模板演示，不建议出现在真实业务事件中。
  - 历史事件名：`game.started` / `score.changed` / `player.health.changed` 仅保留在部分测试与兼容路径中，新 Story/任务必须使用 `core.*.*` / `ui.menu.*` / `screen.*.*`。

> 对 BMAD：生成 PRD 时，凡涉及事件/持久化/安全/测试的条目，应优先遵循上述约束，并在 CH05/CH06/CH07/Phase-9 文档中查找 Godot 变体说明，不要默认 Web/Electron 模式。

---

## 2. 从 PRD 到 tasks.json 的约束（供 task-master-ai 使用）

当 task-master-ai 将 PRD 转换为 `tasks.json` 时，建议遵守以下结构与回链规则：

- 任务元数据结构（建议模板）

```jsonc
{
  "id": "PH8-SCORE-001",
  "title": "Add core score service and events",
  "layer": "core", // core | adapter | scene | test | doc
  "adr_refs": ["ADR-0004", "ADR-0006"],
  "chapter_refs": ["CH05", "CH06", "Phase-8-Scene-Design"],
  "overlay_refs": ["PRD-<PRODUCT>/08/..."],
  "depends_on": ["PH4-DOMAIN-BASE"],
  "description": "Implement score domain model and publish core.score.updated events."
}
```

- layer 建议
  - `core`：只改 `Game.Core/**` 与 `Game.Core.Tests/**`。
  - `adapter`：只改 `Game.Godot/Adapters/**`（含 Db/Config/Security/EventBus 等）。
  - `scene`：改 `Game.Godot/Scenes/**` 与 `Game.Godot/Scripts/**` 中的 UI/Glue/Navigation。
  - `test`：改 `Game.Core.Tests/**` 或 `Tests.Godot/tests/**`。
  - `doc`：改 `docs/adr/**`, `docs/architecture/base/**`, `docs/migration/**` 等。

- 回链要求
  - 每个任务必须至少引用 1 条 **已接受的 ADR**（如 ADR-0004/0005/0006/0023），确保技术决策来源唯一。
  - 若任务修改安全/观察性/质量门禁口径，应在任务描述中指明需新增或 Supersede 的 ADR（并由人类/AI 另起 ADR 草案）。
  - 若任务落在 Phase-8 之后（Scene/Glue/E2E 等），应引用相应 Phase 文档与 overlays 中的 08 章节。

> 对 task-master-ai：生成 `tasks.json` 时，请将 Godot 特有任务类型（scene glue、GdUnit tests、ConfigFile/SQLite 适配）显式标记为对应 layer，并保持 ADR/Phase 回链，不要创造“无来源的技术决策”。

---

## 3. 常用命令入口（供 AI 工具与人类共用）

本模板优先通过 Python 脚本统一驱动 CI/测试/Smoke。推荐优先使用 `scripts/python/dev_cli.py` 暴露的子命令，而不是在上层工具重复拼接长命令行。

### 3.1 dev_cli 子命令（推荐调用方式）

```bash
py -3 scripts/python/dev_cli.py run-ci-basic \
  --godot-bin "C:\Godot\Godot_v4.5.1-stable_mono_win64_console.exe"

py -3 scripts/python/dev_cli.py run-quality-gates \
  --godot-bin "C:\Godot\Godot_v4.5.1-stable_mono_win64_console.exe" \
  --gdunit-hard --smoke

py -3 scripts/python/dev_cli.py run-gdunit-hard \
  --godot-bin "C:\Godot\Godot_v4.5.1-stable_mono_win64_console.exe"

py -3 scripts/python/dev_cli.py run-gdunit-full \
  --godot-bin "C:\Godot\Godot_v4.5.1-stable_mono_win64_console.exe"

py -3 scripts/python/dev_cli.py run-smoke-strict \
  --godot-bin "C:\Godot\Godot_v4.5.1-stable_mono_win64_console.exe" \
  --timeout-sec 5
```

- `run-ci-basic`
  - 调用 `ci_pipeline.py all`，执行：dotnet 测试 + 自检（CompositionRoot）+ 编码扫描。
  - 用于基础健康检查，不包含 GdUnit 与 Smoke。

- `run-quality-gates`
  - 调用 `quality_gates.py all`，可选 `--gdunit-hard` 与 `--smoke`：
    - `--gdunit-hard`：运行 Adapters/Config + Security GdUnit 小集（硬门禁）。
    - `--smoke`：运行严格 headless Smoke（需要检测到 `[TEMPLATE_SMOKE_READY]` 或 `[DB] opened`）。

- `run-gdunit-hard`
  - 直接调用 `run_gdunit.py`，只跑 `tests/Adapters/Config` 与 `tests/Security` 集合，报告输出到 `logs/e2e/dev-cli/gdunit-hard`。

- `run-gdunit-full`
  - 直接调用 `run_gdunit.py`，跑 Adapters + Security + Integration + UI 集合，报告输出到 `logs/e2e/dev-cli/gdunit-full`。

- `run-smoke-strict`
  - 调用 `smoke_headless.py`，以严格模式跑 Main 场景 Smoke，作为快速可玩性冒烟入口。

> 对 SuperClaude/Claude Code/Codex CLI：上层 MCP 工具可统一个接 dev_cli 的子命令，不需要重复维护脚本参数细节。

---

## 4. 最小“AI 驱动工作流”示例

### 4.1 BMAD → PRD（高层）

1. BMAD 游戏专家代理读取：
   - `CLAUDE.md`, `AGENTS.md`（协作规则）；
   - `docs/architecture/base/**`（CH01–CH07）；
   - `docs/adr/**`（特别是 ADR‑0004/0005/0006/0023）；
   - 本文件（Godot 技术前提）。
2. 生成 PRD 时：
   - 将输入/状态更新/存储/SLO 设计成适配 Godot+C#：Scene+Signal+ConfigFile+SQLite，而非浏览器 UI/HTTP API 为中心。

### 4.2 task-master-ai → tasks.json

1. 读取 PRD + ADR/Phase 文档，按本文件第 2 节的结构生成 `tasks.json`：
   - 每个任务指定 `layer`、`adr_refs`、`chapter_refs`、`overlay_refs`；
   - 明确哪些任务是 Core、哪些是 Adapter/Scene、哪些是 Tests/Docs。
2. 将 `tasks.json` 放入本仓库（例如 `docs/tasks/tasks.json`），供 SuperClaude/Claude Code 消费。

### 4.3 SuperClaude/Claude Code + Codex CLI 执行任务

- SuperClaude/Claude Code：
  - 逐条读取 `tasks.json`，根据 layer/refs 决定修改 `Game.Core`、`Game.Godot`、`Tests.Godot` 或文档；
  - 使用本模板已有的脚本和工作流（通过 dev_cli）进行单元测试和 GdUnit 场景测试；
  - 最终通过官方 subagents/skills 工具进行 code review 与测试结果汇总。

- Codex CLI（当前助手）：
  - 作为辅助代理，优先遵循 `AGENTS.md` 与本文件约束；
  - 在需要验证代码/测试/CI 时优先调用：
    - `py -3 scripts/python/dev_cli.py run-ci-basic ...`
    - `py -3 scripts/python/dev_cli.py run-quality-gates ...`。

---

## 5. 后续扩展建议（仅模板视角）

- 当某个项目准备上线时：
  - 优先从 Phase‑16/ADR‑0003 Backlog 中选择 Sentry Release Health 接入方案；
  - 结合 Phase‑15/Phase‑21 Backlog，收紧 Perf P95 门禁（按场景/用例维度细化）。

- 对模板本身，不建议继续在 Phase 文档细节上无限扩展，而是优先：
  - 保持本文件与 `PROJECT_CAPABILITIES_STATUS.md` 一致；
  - 保证 dev_cli 与现有脚本的行为稳定，为多代理协作提供清晰的“命令 SSoT”。

