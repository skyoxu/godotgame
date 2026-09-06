---
ADR-ID: ADR-0005
title: 质量门禁（Windows-only）- Godot + C# 统一入口
status: Accepted
decision-time: '2025-12-16'
deciders: [架构团队, 开发团队]
archRefs: [CH07, CH09]
verification:
  - path: scripts/ci/quality_gate.ps1
    assert: Single entrypoint runs hard gates and writes artifacts under logs/**
  - path: scripts/python/quality_gates.py
    assert: CI-aligned orchestration (dotnet + selfcheck + encoding; optional gdunit/smoke)
  - path: scripts/ci/check_perf_budget.ps1
    assert: Parses [PERF] p95_ms from headless.log and enforces threshold when enabled
  - path: scripts/sc/acceptance_check.py
    assert: Task-scoped deterministic acceptance gate supports security-profile aware controls
  - path: .github/workflows/windows-quality-gate.yml
    assert: Writes `SecurityProfile: <host-safe|strict>` to Step Summary
impact-scope:
  - Game.Core/
  - Game.Godot/
  - Tests.Godot/
  - scripts/
  - .github/workflows/
tech-tags: [quality-gates, windows, godot, csharp, dotnet, xunit, gdunit4, perf, encoding, security-profile]
depends-on: [ADR-0011, ADR-0018, ADR-0019, ADR-0031, ADR-0003, ADR-0015, ADR-0025, ADR-0020]
depended-by: [ADR-0008]
supersedes: []
---

# ADR-0005: 质量门禁（Godot + C#）

## Context

模板必须做到“复制即可跑 CI”：一旦门禁分散在多个脚本和工作流里，就会出现“本地通过、CI 失败”或“同一问题重复审查”。
当前项目采用 Godot + C#，门禁应默认对齐模板可复制场景，并允许按项目阶段切换强度。

## Decision

### 1) 单入口优先

- CI 与本地统一入口优先使用 Python 脚本编排（Windows 兼容）。
- 所有门禁必须写入 `logs/**` 工件，保证可追溯与可审计。

### 2) 最小硬门禁集合（默认）

- dotnet：编译与单元测试（xUnit）。
- Godot：headless self-check（启动 + 关键 Autoload 兜底）。
- 编码：UTF-8 / 无 BOM / 无语义级乱码（文档与工作流关键目录）。

### 3) 可选硬门禁（按需启用）

- GdUnit4 小集（安全/关键装配）。
- Headless smoke（严格模式 marker/DB）。
- 性能 P95 门禁（阈值口径见 ADR-0015）。

### 4) 软门禁（不阻断，但必须产出工件）

- 契约引用对齐：`scripts/python/validate_contracts.py`。
- 其他质量/可观测补充扫描。

### 5) Security Profile 驱动门禁强度

- 统一配置：`SECURITY_PROFILE=host-safe|strict`，默认 `host-safe`。
- `host-safe`（模板默认）：
  - `security-path-gate=require`
  - `security-sql-gate=require`
  - `security-audit-schema-gate=warn`
  - `ui-event-json-guards=skip`
  - `ui-event-source-verify=skip`
  - `security-audit-evidence=skip`
- `strict`（项目可选）：
  - 上述安全门禁全部 `require`。
- 安全 profile 语义来源见 ADR-0031；安全边界来源见 ADR-0019。

### 6) 工件（统一落盘）

- 单元测试：`logs/unit/<YYYY-MM-DD>/`
- 引擎/场景：`logs/e2e/<YYYY-MM-DD>/`
- CI 汇总与扫描：`logs/ci/<YYYY-MM-DD>/`

## Verification

本地最小验收（Windows）：

```powershell
pwsh -File scripts/ci/quality_gate.ps1 -GodotBin "$env:GODOT_BIN"
```

CI 侧应能在 `logs/**` 中找到对应摘要与日志文件；失败时可直接定位到具体 gate 输出。

## Consequences

- 正向：门禁入口统一、Windows 兼容、失败可定位、产物可回溯。
- 代价：需要保持“单入口优先”的纪律，避免把门禁逻辑散落到示例脚本或临时 workflow 里。

## Addendum (2026-02 Security profile + 5 scripts)

- `scripts/sc/acceptance_check.py` remains the blocking decision source for task delivery.
- `scripts/sc/llm_review.py`, `scripts/sc/llm_extract_task_obligations.py`, `scripts/sc/llm_check_subtasks_coverage.py`, and `scripts/sc/llm_semantic_gate_all.py` are advisory/diagnostic by default.
- CI must expose one explicit line in Step Summary: `SecurityProfile: <host-safe|strict>`.
- Default profile stays `host-safe`; `strict` is opt-in per project phase.

## Addendum (2026-09-06 Single-maintainer CI)

- 保持 `fast-ship` 默认档位和原有硬门禁集合；本次不通过降低覆盖率或取消安全检查来提速。
- 已知纯文档变更仅跳过昂贵运行时步骤，工作流与原有 required check 名称仍回报结果。未知路径、代码、配置变更和手动运行必须执行运行时检查。
- PR 执行 Quality 与场景 Smoke；main push 保留 Quality，避免重复运行第二套场景 Smoke。发布包另有独立启动验证。
- 无导出行为的 CI 不安装导出模板。运行环境准备收敛到 `.github/actions/setup-godot-windows/action.yml`，保留既有 SDK 8.0.401 / Runtime 8.0.21 / Godot 4.5.1 版本并增加缓存。
- 同一 PR 的新提交取消旧运行；发布流程不取消。
- `build-test-export` 暂保留为既有分支保护兼容名称，汇总 Quality 与按需导出验证结果。工作流、发布脚本或工程配置变更增加一次完整打包验证，普通玩法和纯文档变更不付出该成本。此兼容例外只用于避免未知现有分支保护被破坏。
- Self-check 必须成功退出，且六个必需端口全部为 true。发布包 smoke 必须出现 `[TEMPLATE_SMOKE_READY]`，无引擎错误，且未异常退出；仅 DB 日志或任意输出不算通过。日常源树 smoke 在模板存在已知引擎基线问题时保留为告警并上传完整日志，不阻断单人玩法迭代；发布包 smoke 永远是硬门禁。观察窗口到期后的主动终止，只有已满足上述条件时才允许成功。
- GdUnit 清理旧报告，要求本轮报告至少执行一个测试且无失败；超时和解析错误不可归一化为成功。静默进程也必须服从超时。
- 回归验证入口：`py -3 -m unittest discover -s scripts/ci/tests -p "test_*.py" -v`。Windows CI 同时运行 PowerShell 成功、异常退出、无标记、错误日志、超时及陈旧导出产物案例。
