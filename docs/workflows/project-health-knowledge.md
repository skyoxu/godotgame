# Project Health: Knowledge + Impact

`serve-project-health` 现在在同一 `127.0.0.1` 服务上提供 `/knowledge/`，不是第二个常驻服务。

## 使用

```powershell
py -3 scripts/python/dev_cli.py serve-project-health
```

打开命令输出的 URL，然后访问同一端口的 `/knowledge/`。

页面能力：

1. `Fetch latest main + scan`：尝试抓取 `origin/main`，失败时保留并明确标注可用的本地主线引用；扫描事实绑定具体 commit。
2. Knowledge search：按 `repository-session | chapter4 | chapter5 | chapter6 | review` consumer 查询仓库文本，返回任务、配置、代码、测试和其他知识位置。
3. Impact preview：仅对扫描快照中的文件做确定性引用探索，始终 `handoff_eligible=false`。
4. Configuration：编辑仓库相对 source paths、GDD paths、query aliases 和经过人工审查的 task/scene bindings；模板默认没有业务别名或任务绑定。
5. Tasks：读取 `.taskmaster/tasks/tasks.json.master.tasks[]`；文件不存在或为空时显示未初始化，不注入伪任务。

## 正式交接边界

网页是探索入口，不生成正式 Chapter handoff。正式流程使用：

```powershell
py -3 scripts/python/prepare_knowledge_context.py --consumer chapter6 --task-id <id> --query "<intent>" --out <candidate.json>
py -3 scripts/python/freeze_knowledge_context.py --bundle <candidate.json> --decisions <decisions.json> --out <frozen.json>
py -3 scripts/python/build_impact_index.py --out <impact-index.json>
py -3 scripts/python/analyze_impact.py --target <repo-relative-file> --frozen <frozen.json> --out <impact-report.json>
```

Freeze 会验证 candidate bundle hash；正式 Impact 在提供 frozen context 时要求 revision 完全一致。

## 安全边界

- HTTP 只绑定 `127.0.0.1`。
- API 只暴露固定操作，不接收任意 shell 命令。
- 写操作要求同源请求和进程级 session token，并限制 JSON body 大小。
- 配置只允许仓库相对路径。
- 页面不提供任意文件系统下载、编辑器命令或自动 LLM 执行。

## 模板空态

`godotgame` 本身可以没有真实任务。此时 Knowledge/Impact 仍可检索模板代码和文档；任务区域显示 `uninitialized`。只有业务仓出现真实 `.taskmaster/tasks` 后，任务搜索和 Chapter task context 才产生数据。
