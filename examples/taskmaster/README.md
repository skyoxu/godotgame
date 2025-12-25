# Taskmaster 示例文件（模板）

本目录提供 **示例** 的 Taskmaster triplet 文件结构，用于演示/迁移脚本与 CI 工作流如何读取字段，不代表本仓库已经启用真实的 `.taskmaster/tasks/*.json`。

注意：

- 这些示例文件不会被 CI 自动读取（避免模板仓在未启用 Taskmaster 时被门禁误伤）。
- 如果你把这些文件复制到 `.taskmaster/tasks/`，则需要同步创建对应的 overlay 文档与测试文件，否则 refactor 阶段的确定性门禁会失败。

包含：

- `examples/taskmaster/tasks.json`
- `examples/taskmaster/tasks_back.json`
- `examples/taskmaster/tasks_gameplay.json`
- `examples/taskmaster/taskdoc/11.md`

