[![Windows Export Slim](https://github.com/skyoxu/godotgame/actions/workflows/windows-export-slim.yml/badge.svg)](https://github.com/skyoxu/godotgame/actions/workflows/windows-export-slim.yml) [![Windows Release](https://github.com/skyoxu/godotgame/actions/workflows/windows-release.yml/badge.svg)](https://github.com/skyoxu/godotgame/actions/workflows/windows-release.yml) [![Windows Quality Gate](https://github.com/skyoxu/godotgame/actions/workflows/windows-quality-gate.yml/badge.svg)](https://github.com/skyoxu/godotgame/actions/workflows/windows-quality-gate.yml)

# Godot Windows-only Template (C#)

即开即用，可复制的 Godot 4 + .NET（Windows-only）项目模板。

## About This Template

Production-ready Godot 4.5 + C# game template with enterprise-grade tooling.

### Why This Template
- **Historical lineage**: this repository was originally bootstrapped from a legacy stack and is now fully standardized on Godot 4.5 + C# .NET 8 (Windows-only).
- **Purpose**: Eliminate setup overhead with pre-configured best practices
- **For**: Windows desktop games (simulation, management, strategy)

### Key Features
- **AI-Friendly**: Optimized for BMAD, SuperClaude, Claude Code workflows
- **Quality Gates**: Coverage (≥90%), Performance (P95≤20ms), Security baseline
- **Testable Architecture**: Ports & Adapters + 80% xUnit + 15% GdUnit4
- **Complete Stack**: Godot 4.5, C# .NET 8, xUnit, GdUnit4, godot-sqlite, Sentry

**Full technical details**: See `CLAUDE.md`

---

## 3‑Minute From Zero to Export（3 分钟从 0 到导出）

1) 安装 Godot .NET（mono）并设置环境：
   - `setx GODOT_BIN C:\Godot\Godot_v4.5.1-stable_mono_win64.exe`
2) 运行最小测试与冒烟（可选示例）：
   - `./scripts/test.ps1 -GodotBin "$env:GODOT_BIN"`（默认不含示例；`-IncludeDemo` 可启用）
   - `./scripts/ci/smoke_headless.ps1 -GodotBin "$env:GODOT_BIN"`
3) 在 Godot Editor 安装 Export Templates（Windows Desktop）。
4) 导出与运行 EXE：
   - `./scripts/ci/export_windows.ps1 -GodotBin "$env:GODOT_BIN" -Output build\Game.exe`
   - `./scripts/ci/smoke_exe.ps1 -ExePath build\Game.exe`

One‑liner（已在 Editor 安装 Export Templates 后）：
- PowerShell：`$env:GODOT_BIN='C:\\Godot\\Godot_v4.5.1-stable_mono_win64.exe'; ./scripts/ci/export_windows.ps1 -GodotBin "$env:GODOT_BIN" -Output build\Game.exe; ./scripts/ci/smoke_exe.ps1 -ExePath build\Game.exe`

## What You Get（模板内容）
- 适配层 Autoload：EventBus/DataStore/Logger/Audio/Time/Input/SqlDb
- 场景分层：ScreenRoot + Overlays；ScreenNavigator（淡入淡出 + Enter/Exit 钩子）
- 安全基线：仅允许 `res://`/`user://` 读取，启动审计 JSONL，HTTP 验证示例
- 可观测性：本地 JSONL（Security/Sentry 占位），性能指标（[PERF] + perf.json）
- 测试体系：xUnit + GdUnit4（示例默认关闭），一键脚本
- 导出与冒烟：Windows-only 脚本与文档

## Delivery Profiles
- `DELIVERY_PROFILE=playable-ea`：最快的可玩性校验档位；覆盖率、语义审查、验收硬门尽量止损，安全默认派生到 `host-safe`。
- `DELIVERY_PROFILE=fast-ship`：模板默认档位；保留基本主机安全、核心测试和发版前的必要约束，适合日常开发。
- `DELIVERY_PROFILE=standard`：收口档位；ADR、验收、语义门禁更严格，安全默认派生到 `strict`。
- 生效优先级：CLI `--delivery-profile` > 环境变量 `DELIVERY_PROFILE` > 仓库默认 `fast-ship`。
- CI 工作流 `windows-quality-gate.yml` / `ci-windows.yml` 已接入 `delivery_profile` 输入，并会在 Step Summary 固化 `DeliveryProfile:` 与 `SecurityProfile:`。

## Quick Links
- Delivery Profile 说明：`DELIVERY_PROFILE.md`
- 文档索引：`docs/PROJECT_DOCUMENTATION_INDEX.md`
- Persistent Harness: `docs/agents/03-persistent-harness.md`
- Harness Marathon: `docs/agents/06-harness-marathon.md`
- AGENTS 构建原则：`docs/agents/11-agents-construction-principles.md`
- Godot+C# 快速开始（godotgame 项目）：`docs/TEMPLATE_GODOT_GETTING_STARTED.md`
- Windows-only 快速指引：`docs/migration/Phase-17-Windows-Only-Quickstart.md`
- FeatureFlags 快速指引：`docs/migration/Phase-18-Staged-Release-and-Canary-Strategy.md`
- 导出清单：`docs/migration/Phase-17-Export-Checklist.md`
- Headless 冒烟：`docs/migration/Phase-12-Headless-Smoke-Tests.md`
- Actions 快速链路验证（Dry Run）：`.github/workflows/windows-smoke-dry-run.yml`
- 场景设计：`docs/migration/Phase-8-Scene-Design.md`
- 测试体系：`docs/migration/Phase-10-Unit-Tests.md`
- 安全基线：`docs/migration/Phase-14-Godot-Security-Baseline.md`
- 手动发布指引：`docs/release/WINDOWS_MANUAL_RELEASE.md`
- Release/Sentry 软门禁与工作流说明：`docs/workflows/GM-NG-T2-playable-guide.md`

## Task / ADR / PRD 工具
- `scripts/python/task_links_validate.py` —— 检查 NG/GM 任务与 ADR / 章节 / Overlay 的回链完整性（CI 已在用，作为门禁）。
- `scripts/python/verify_task_mapping.py` —— 抽样检查 NG/GM → tasks.json 的元数据完整度（owner / layer / adr_refs / chapter_refs 等）。
- `scripts/python/validate_task_master_triplet.py` —— 全面校验三份任务文件之间的结构一致性（link + layer + depends_on + 映射），适合作为本地或后续 CI 的结构总检。
- `scripts/python/prd_coverage_report.py` —— 生成 PRD → 任务的覆盖报表（软检查，不参与门禁，用于观察覆盖程度）。
- `scripts/python/run_obligations_jitter_batch5x3.py` —— 本地批量运行 `scripts/sc/llm_extract_task_obligations.py`，按 5x3 轮次收集 obligations 抖动原始数据；支持 `--delivery-profile`，模板仓在缺少真实 `.taskmaster/tasks/*.json` 时自动回退到 `examples/taskmaster/tasks.json`。
- `scripts/python/build_obligations_jitter_summary.py` —— 将 5x3 原始运行结果汇总为 jitter summary / markdown report，用于判断稳定通过、稳定失败和抖动任务。
- `scripts/python/refresh_obligations_jitter_summary_with_overrides.py` —— 将补跑结果覆盖回原 summary，生成 refreshed summary / report，适合局部重跑后的收敛分析。
- `scripts/python/generate_obligations_freeze_whitelist_draft.py` —— 基于 jitter summary 生成 obligations freeze whitelist 草案，供人工审阅，不直接放进 CI 硬门。
- `scripts/python/evaluate_obligations_freeze_whitelist.py` —— 评估 whitelist 草案或 current baseline 对当前 jitter summary 的适配度，输出 judgable / freeze_gate_pass 等汇总结果。
- `scripts/python/promote_obligations_freeze_baseline.py` —— 将审阅通过的 draft 提升为带日期/标签的 immutable baseline，并更新 current pointer。
- `scripts/python/run_obligations_freeze_pipeline.py` —— 串起 jitter batch、summary、override refresh、draft、evaluate、promote 的本地编排入口；默认作为人工分析工具链，不作为模板仓 CI 必跑项。


<!-- BEGIN:NEW_PROJECT_SANGUO_ALIGNMENT -->

## Script Portability Tags (Template Use)

- `template-core` (directly reusable)
  - `scripts/python/sync_task_overlay_refs.py` - Sync overlay refs across task triplet; supports `.taskmaster/tasks` and `examples/taskmaster` fallback.
  - `scripts/python/validate_overlay_execution.py` - Validate overlay execution docs (structure, front matter, and referenced paths).
  - `scripts/python/validate_docs_utf8_no_bom.py` - Enforce UTF-8 without BOM on `docs/.github/.taskmaster/AGENTS.md` scope.

- `optional-llm` (advanced, requires obligations/SC toolchain)
  - `scripts/python/_obligations_freeze_pipeline_common.py` - Shared helpers for obligations freeze orchestration.
  - `scripts/python/_obligations_freeze_pipeline_runner.py` - End-to-end obligations freeze runner; depends on jitter/summary/draft/evaluate/promote scripts.
  - `scripts/python/rerun_obligations_hardgate_round3.py` - Multi-round rerun wrapper for `scripts/sc/llm_extract_task_obligations.py`.

- `domain-specific` (requires project-level evaluation)
  - `scripts/python/config_contract_sync_check.py` - Domain contract consistency checker; template mode defaults to `SKIPPED` when domain files are absent, `--strict-presence` makes it hard fail.
  - `scripts/python/guard_archived_overlays.py` - Archived overlay drift guard; recommended only when `_archived` overlay workflow is used.

## New project task-gate alignment

When you copy this template to create a new project, enable task-scoped gates after real Taskmaster files are ready:

1) Prepare triplet files:
- `.taskmaster/tasks/tasks.json`
- `.taskmaster/tasks/tasks_back.json`
- `.taskmaster/tasks/tasks_gameplay.json`

2) Pick one delivery profile and let scripts derive the default security posture:
- Playable EA posture:
  - `py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin "$env:GODOT_BIN" --delivery-profile playable-ea --skip-llm-review`
- Fast ship posture (template default):
  - `py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin "$env:GODOT_BIN" --delivery-profile fast-ship --skip-llm-review`
- Standard posture (release tightening):
  - `py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin "$env:GODOT_BIN" --delivery-profile standard --skip-llm-review`
- Remove `--skip-llm-review` only when you intentionally want the advisory LLM review stage as part of the unified pipeline.
- Only pass `--security-profile` when you intentionally need to break the default mapping.

3) Keep profile observability in CI:
- Step Summary should contain both `DeliveryProfile: <playable-ea|fast-ship|standard>` and `SecurityProfile: <host-safe|strict>`.
- LLM scripts are diagnostic only and do not replace hard gates.

4) Initialize `overlay_task_drift` only after real Taskmaster triplet files exist:
- `py -3 scripts/python/remind_overlay_task_drift.py --write --overlay-index docs/architecture/overlays/PRD-Guild-Manager/08/_index.md`
- Do not run `--write` in the bare template state; otherwise the baseline only records missing task files.

<!-- END:NEW_PROJECT_SANGUO_ALIGNMENT -->

## Notes
- DB 后端：默认插件优先；`GODOT_DB_BACKEND=plugin|managed` 可控。
- 示例 UI/测试：默认关闭；设置 `TEMPLATE_DEMO=1` 启用（Examples/**）。

## Feature Flags（特性旗标）
- Autoload：`/root/FeatureFlags`（文件：`Game.Godot/Scripts/Config/FeatureFlags.cs`）
- 环境变量优先生效：
  - 单项：`setx FEATURE_demo_screens 1`
  - 多项：`setx GAME_FEATURES "demo_screens,perf_overlay"`
- 文件配置：`user://config/features.json`（示例：`{"demo_screens": true}`）
- 代码示例：`if (FeatureFlags.IsEnabled("demo_screens")) { /* ... */ }`

## 如何发版（打 tag）
- 确认主分支已包含所需变更：`git status && git push`
- 创建版本标签：`git tag v0.1.1 -m "v0.1.1 release"`
- 推送标签触发发布：`git push origin v0.1.1`
- 工作流：`Windows Release (Tag)` 自动导出并将 `build/Game.exe` 附加到 GitHub Release。
- 如需手动导出：运行 `Windows Release (Manual)` 或 `Windows Export Slim`。

## 自定义应用元数据（图标/公司/描述）
- 文件：`export_presets.cfg` → `[preset.0.options]` 段。
- 关键字段：
  - `application/product_name`（产品名），`application/company_name`（公司名）
  - `application/file_description`（文件描述），`application/*_version`（版本）
  - 图标：`application/icon`（推荐 ICO：`res://icon.ico`；当前为 `res://icon.svg`）
- 修改后，运行 `Windows Export Slim` 或 `Windows Release (Manual)` 验证导出产物。
