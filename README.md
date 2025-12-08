[![Windows Export Slim](https://github.com/skyoxu/godotgame/actions/workflows/windows-export-slim.yml/badge.svg)](https://github.com/skyoxu/godotgame/actions/workflows/windows-export-slim.yml) [![Windows Release](https://github.com/skyoxu/godotgame/actions/workflows/windows-release.yml/badge.svg)](https://github.com/skyoxu/godotgame/actions/workflows/windows-release.yml) [![Windows Quality Gate](https://github.com/skyoxu/godotgame/actions/workflows/windows-quality-gate.yml/badge.svg)](https://github.com/skyoxu/godotgame/actions/workflows/windows-quality-gate.yml)

# Godot Windows-only Template (C#)

即开即用，可复制的 Godot 4 + .NET（Windows-only）项目模板。

## About This Template

Production-ready Godot 4.5 + C# game template with enterprise-grade tooling.

### Why This Template
- **Migrated from**: vitegame (Electron + Phaser) → Godot 4.5 + C# .NET 8
- **Purpose**: Eliminate setup overhead with pre-configured best practices
- **For**: Windows desktop games (simulation, management, strategy)

### Key Features
- **AI-Friendly**: Optimized for BMAD, SuperClaude, Claude Code workflows
- **Quality Gates**: Coverage (≥90%), Performance (P95≤20ms), Security baseline
- **Testable Architecture**: Ports & Adapters + 80% xUnit + 15% GdUnit4
- **Complete Stack**: Godot 4.5, C# .NET 8, xUnit, GdUnit4, godot-sqlite, Sentry

📖 **Full technical details**: See `CLAUDE.md`

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

## Quick Links
- 文档索引：`docs/PROJECT_DOCUMENTATION_INDEX.md`
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
