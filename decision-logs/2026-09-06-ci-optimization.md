# 单人 AI 游戏模板 CI 优化

- Branch: codex/ci-reliability-and-solo-workflow
- Git Head: c6e43552cfa5b95661385edd2f89b59e945d5d82
- Related ADRs: ADR-0005, ADR-0011, ADR-0018
- Related task id(s): n/a - user-authorized repository CI optimization, not a generated game task
- Related run id: GitHub Actions 34017601552; PR 74
- Related latest.json: n/a - GitHub Actions provides run state, no local task pipeline
- Related pipeline artifacts: `logs/ci/`
- Title: 单人 AI 游戏模板 CI 优化
- Date: 2026-09-06
- Status: accepted
- Supersedes: n/a - additive refinement of current CI
- Superseded by: n/a - current decision
- Why now: 用户明确授权执行前一轮 CI 审查建议
- Context: 日常验证存在无用环境安装，启动与发布存在假绿路径
- Decision: 保留 fast-ship 与核心硬门禁，按范围减少昂贵步骤，并验证完整 Release ZIP
- Consequences: 首次缓存填充仍有成本，后续文档与常规开发减少运行成本；错误会真实暴露
- Recovery impact: 保持 required check 名称，沿用 GitHub 日志与工件定位失败
- Validation: 本地 9 个 Python 测试与静态检查通过，Windows PowerShell 回归已通过；真实运行验证进行中
- Related execution plans: execution-plans/2026-09-06-ci-optimization.md


用户授权优化后，采用“减少重复成本、提高成功信号可信度”的方案。原有静态硬门禁一次样本仅约 10 秒，因此先保留；删除的是无导出 CI 的模板准备和 main 上第二套场景重复执行。

没有读取到传统分支保护设置，因此保持 `quality`、`smoke`、`build-test-export` 名称。工作流不会因纯文档变更整体消失。

发布仍由用户推标签或手动触发；本次优化不创建版本、不发布游戏。

实际验证结果见 PR。PowerShell 和 Godot 的真实环境验证以 Windows Actions 结果为准。
