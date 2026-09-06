# ADR-0018: Godot Runtime and Distribution

- Status: Accepted
- Context: Migration Phase-2（docs/migration/Phase-2-ADR-Updates.md），对齐 CH01/CH03 基线；Windows-only 交付。原项目使用 LegacyDesktopShell + LegacyUIFramework + Legacy2DEngine + TypeScript 技术栈，本仓库迁移为 Godot 4.5 + C#/.NET 8 模板，需要统一运行时、发布与测试/门禁口径，避免契约与流程分叉。
- Decision:
  - 运行时：采用 Godot 4.5.1（.NET/mono）作为 UI/渲染/物理运行时；主语言为 C#（.NET 8 LTS）。
  - 架构与测试：领域层保持纯 C#（Game.Core，不依赖 Godot），适配层封装 Godot API 通过接口注入；单元测试使用 xUnit，场景/集成测试使用 GdUnit4；覆盖率使用 coverlet；质量门禁与可观测性沿用 ADR-0005/ADR-0003 统一口径。
  - 发布：Windows Desktop 导出为独立 `.exe`（嵌入或旁挂 `.pck`）；导出/发布流水线由 Godot Export Templates 驱动；CI 以 headless 模式运行冒烟/门禁，导出产物门禁作用于 `.exe/.pck`。
- Consequences:
  - LegacyDesktopShell/Chromium 运行时退役；安全基线从“LegacyDesktopShell 安全”切换为“Godot 安全”（见 ADR-0019）。
  - 契约/DTO/事件统一落盘到 `Game.Core/Contracts/**`（见 ADR-0020/ADR-0004），Overlay 08 章仅引用 CH01/02/03 口径，不复制阈值与策略。
  - CI/CD 转为 Windows 优先（见 ADR-0011），E2E/冒烟转为 Godot Headless 方案，相关日志与工件统一落 `logs/**`。
- Supersedes: ADR-0001-tech-stack
- References:
  - docs/migration/MIGRATION_INDEX.md
  - docs/migration/Phase-2-ADR-Updates.md
  - docs/migration/Phase-17-Build-System-and-Godot-Export.md
  - docs/architecture/base/07-dev-build-and-gates-v2.md
  - ADR-0011-windows-only-platform-and-ci
  - ADR-0005-quality-gates
  - ADR-0003-observability-release-health
  - ADR-0019-godot-security-baseline

## Addendum (2026-09-06 Verified Windows package)

- Follow-up: example scenes are covered by the required scene smoke suite, including loading their C# scripts and entering the scene tree. Godot text scenes must not carry a UTF-8 BOM.
- GdUnit prewarm imports resources to completion before building scripting solutions. Each stage has a bounded timeout and separate timing/log evidence; failure stops the run instead of retrying the same cold editor invocation or ignoring a fallback build failure.

- 三个已有发布/导出入口共用 `windows-release.yml` 的 reusable workflow，保留入口名称以兼容现有引用。
- `Game.Godot/` 是实际运行时资源目录，不得设置目录级 `.gdignore`；移除历史误放的该标记，保留 `docs/`、`_bmad/`、`logs/` 的非运行时导入边界。预设使用 `all_resources`，导出前构建编辑器需要的 Debug 程序集并完成资源导入。
- 使用与 Godot 版本匹配的 **mono export templates**。正式导出必须是 Release、退出码为零，并生成新的非空 EXE；不再接受 Debug/PCK 降级或“报错但文件存在”。
- 发布流程在所选提交运行 Release 单测，导出后将完整 `build/` 分发目录打包为 ZIP，保留 C# 运行所需的旁挂数据与依赖。
- ZIP 解压到仓库外的临时目录后运行 EXE smoke，通过后才上传分发工件。标签工作流只发布该已验证 ZIP，手动流程只生成可下载工件。
- 单机模板发布继续使用 `fast-ship` 和 `host-safe` 默认姿态；不把所有文档治理、LLM 意见或在线服务健康指标变成每次导出的硬门禁。
