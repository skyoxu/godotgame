# 单维护者 CI 优化

- Branch: codex/ci-reliability-and-solo-workflow
- Git Head: c6e43552cfa5b95661385edd2f89b59e945d5d82
- Related ADRs: ADR-0005, ADR-0011, ADR-0018
- Related task id(s): n/a - user-authorized repository CI optimization, not a generated game task
- Related run id: GitHub Actions 34017601552; PR 74
- Related latest.json: n/a - GitHub Actions provides run state, no local task pipeline
- Related pipeline artifacts: `logs/ci/`
- Title: 单维护者 CI 优化
- Status: active
- Goal: 降低重复 CI 成本并消除运行与发布假绿
- Scope: 工作流、CI 脚本、回归测试和相关 ADR
- Current step: Windows Actions 与真实导出验证
- Last completed step: Python 回归、actionlint 与 Windows PowerShell 回归通过
- Stop-loss: 失败时修复实际原因，不降低硬门禁或吞掉失败
- Next action: 修复恢复文档格式后继续 Windows 验证
- Recovery command: git fetch origin codex/ci-reliability-and-solo-workflow
- Open questions: 真实 Godot 与打包验证结果待 Actions 完成
- Exit criteria: PR 的 Quality、Smoke 和按需发布包验证通过
- Related decision logs: decision-logs/2026-09-06-ci-optimization.md


状态：实现完成，验证与 PR 中。

授权：用户在 CI 审查后明确授权优化。
依据：ADR-0005、ADR-0011、ADR-0018。

1. 修复 self-check、严格 smoke 和 Release 导出的假绿判定。
2. 移除无用模板安装，缓存共享环境，纯文档跳过昂贵运行时步骤。
3. 保留现有 required check 名称，减少合并后重复场景检查。
4. 共用发布流程，验证完整 ZIP 中的游戏。
5. 添加针对失败模式的回归案例，运行确定性检查并提交 PR。

不改动运行时安全姿态、覆盖率阈值或 GitHub 分支保护设置。
