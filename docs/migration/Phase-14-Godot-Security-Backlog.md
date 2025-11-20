# Phase 14 Backlog — Godot 安全基线增强

> 状态：Backlog（非当前模板 DoD，按需渐进启用）
> 目的：承接 Phase-14-Godot-Security-Baseline.md 中尚未在当前 Godot+C# 模板完全落地的安全规则，避免“蓝图要求”与“实际实现”脱节，同时为后续项目提供可选安全增强清单。
> 相关 ADR：ADR-0002（Electron 安全基线）、ADR-0003（审计与发布健康）、ADR-0006（数据存储）、ADR-0005（质量门禁）

---

## B1：网络白名单配置化与统一封装

- 现状：
  - `SecurityHttpClient` 当前通过 [Export] 暴露 `AllowedDomains`、`AllowedMethods`、`EnforceHttps` 等字段，默认值内联在 C# 中；
  - Phase‑14 文档中的 `OpenUrlSafe` 蓝图示例尚未作为统一入口对接 `OS.ShellOpen` 或 HTTPRequest 适配层。
- 目标：
  - 将“允许域名/协议/方法”从硬编码迁移到集中配置（例如项目设置、ConfigFile 或环境变量），并在文档中给出 SSoT。
  - 提供一个统一的 URL 打开入口（例如 `SecurityUrlAdapter` 或扩展 `SecurityHttpClient`），封装 `OS.ShellOpen()` 调用，强制执行 HTTPS + 域白名单。
- 建议实现方式：
  - 引入 `ALLOWED_EXTERNAL_HOSTS` 环境变量或 Config 节点，解析为安全白名单；
  - 在 UI/Glue 层禁止直接调用 `OS.ShellOpen`，改为调用统一的安全适配器；
  - 保持现有 `SecurityHttpClient.Validate` 作为 HTTP 通路的中心验证点。
- 优先级：P1–P2（适合在真实项目需要外链/外网访问时落实，模板阶段保留为 Backlog）。

---

## B2：文件系统保护统一封装

- 现状：
  - SqliteDataStore 已对 DB 路径实施 `user://` 前缀与 `..` 拒绝；
  - 其它文件访问（例如 ConfigFile、导出、临时文件）目前多处直接调用 Godot `FileAccess`/`DirAccess`，缺少统一守卫；
  - Phase‑14 蓝图中的 `OpenFileSecure` 示例尚未以运行时代码形式落地。
- 目标：
  - 提供统一的文件访问适配层（如 `SecurityFileAdapter` 或扩展现有组件），封装 `FileAccess` 与 `DirAccess` 调用：
    - 仅允许 `res://`（只读）与 `user://`（读写）；
    - 拒绝绝对路径与 `../` 路径穿越；
    - 失败路径写入审计日志。
- 建议实现方式：
  - 在 Phase‑14 蓝图的 `OpenFileSecure` 基础上，提炼为实际适配类，并逐步替换模板中的直连 FileAccess 调用；
  - 与 SqliteDataStore 的路径规则保持一致，避免出现多套标准。
- 优先级：P2（对安全基线有价值，但需要结合实际业务 I/O 规划节奏）。

---

## B3：OS.execute / 外部进程调用守卫

- 现状：
  - 当前模板中基本未使用 `OS.execute`，Phase‑5/AGENTS 中仅从文档层规定“默认禁用，或仅开发态开启并严审计”；
  - 没有统一的运行时守卫或审计实现。
- 目标：
  - 为后续可能引入的外部进程调用提供统一安全适配层：
    - 默认拒绝执行外部命令；
    - 若必须执行，需显式声明白名单命令/参数并写入安全审计 JSONL。
- 建议实现方式：
  - 引入 `SecurityProcessAdapter`，对 `OS.execute` 做统一封装，并在模板代码中禁止直接调用 `OS.execute`；
  - 在 Phase‑14 文档与 ADR‑0002 的 Godot 变体中记录该适配器的约束与审计口径。
- 优先级：P3（仅在确有需求时启用，模板阶段可不实现）。

---

## B4：审计 JSONL 校验脚本与门禁

- 现状：
  - SqliteDataStore 与 SecurityAudit/SecurityHttpClient 已分别写入：
    - `logs/ci/<date>/security-audit.jsonl`（DB 层）；
    - `user://logs/security/security-audit.jsonl`（启动基线）；
    - `user://logs/security/audit-http.jsonl`（HTTP 安全）；
  - Phase‑13 Backlog 中提出了“审计 JSONL 校验”的质量门禁，但尚未实现具体脚本。
- 目标：
  - 提供一个 Python 脚本（例如 `scripts/python/validate_audit_logs.py`），对关键审计文件进行结构校验：
    - 每行必须是合法 JSON；
    - 包含最小字段集合（例如 {ts, action, reason, target, caller} 或相应变体）；
    - 可选：校验 event_type/decision 等字段值是否在允许枚举内。
- 建议实现方式：
  - 将该脚本作为 Phase‑13 `quality_gates.py` 的可选软门禁接入；
  - 在 Phase‑14 文档与 ADR‑0006/0003 中引用该校验脚本作为“审计可验证”的一部分。
- 优先级：P2（对安全与可观测性有实际价值，但不强制模板阶段完成）。

---

## B5：Signal 契约验证与测试门禁

- 现状：
  - Phase‑14 蓝图中提出了“Signal 契约验证”（只允许预定义事件、参数类型匹配），但当前实现主要集中在 Phase‑9 的 EventBusAdapter + 测试层，尚未形成独立的安全门禁；
  - 没有专门的 CI 步骤检查“安全相关 Signal 是否具备 XML 注释、命名是否符合约定”等。
- 目标：
  - 将与安全相关的 Signal（例如 SecurityHttpClient.RequestBlocked）纳入一套统一的契约与门禁体系：
    - 命名/参数通过 xUnit/GdUnit4 测试或静态检查脚本验证；
    - 关键 Signal 补齐 XML 文档注释（见 Phase‑9 Backlog B2）。
- 建议实现方式：
  - 在 Phase‑9 Backlog 的基础上，为 Security 相关 Signal 增加测试用例或静态分析脚本；
  - 将结果纳入 Phase‑13 的信号合规 Backlog（signal compliance）中统一管理。
- 优先级：P3（更偏向代码整洁与契约明确，安全收益间接，可在后续迭代中处理）。

---

## 使用说明

- 对于基于本模板创建的新项目：
  - 在需要访问外部网络/文件/进程时，优先评估并实现 B1/B2，对照 Phase‑14 文档中的蓝图示例与现有 Security 组件；
  - 当审计与合规需求提高时，再逐步启用 B4（审计 JSONL 校验）和 B5（Signal 契约门禁）。

- 对于模板本身：
  - 当前 Phase 14 仅要求 `SecurityAudit` + `SqliteDataStore` + `SecurityHttpClient` 提供最小安全基线和审计输出；
  - 本 Backlog 文件用于记录蓝图中尚未落地的安全增强，避免在 Phase 14 内部继续无限扩张范围。

---

## 当前模板实现小结（2025-11，状态快照）

为便于后续维护，这里补充一段“当前 Godot 模板已经落实的安全测试与技债状态”说明：

- DB 路径安全用例（已实现）
  - 文件：`Tests.Godot/tests/Security/test_db_path_rejection.gd`
  - 行为：通过 `SqliteDataStore.TryOpen` 验证 `user://` 正常，绝对路径与 `user://../` 路径穿越返回 `false`。
  - 作用：将 Phase‑14 文档中“仅允许 res:///user://、禁止穿越”的 DB 口径落实为可执行测试。

- DB open 失败审计用例（已实现）
  - 文件：`Tests.Godot/tests/Security/test_db_open_denied_writes_audit_log.gd`
  - 行为：对绝对路径调用 `TryOpen` 失败后，读取 `logs/ci/<date>/security-audit.jsonl` 最后一条记录，并断言 `action == "db.open.fail"`。
  - 作用：验证 `SqliteDataStore.TryOpen` 的审计逻辑真实落盘，而不仅仅停留在文档描述。

- HTTP 阻断 Signal 用例（已实现）
  - 文件：`Tests.Godot/tests/Integration/Security/test_security_http_block_signal.gd`
  - 行为：创建 `SecurityHttpClient` 节点，拒绝一个 `http://` URL，并断言发出了 `RequestBlocked(reason, url)` Signal 且 URL 以 `http://` 开头。
  - 作用：为 Phase‑14 Backlog 中提到的“安全相关 Signal 契约验证”提供了一条基础示例，用于后续扩展。

- `test_db_audit_exec_query_fail.gd` 状态（保留为 SKIP 技术债占位）
  - 文件：`Tests.Godot/tests/Security/test_db_audit_exec_query_fail.gd`
  - 现状：
    - `_new_db` 使用显式类型 `var db: Node = null`，避免 GDScript 4.5 对 `null` 推断失败的 Parser Error；
    - 测试主体仅发出 `push_warning("SKIP: exec/query audit covered by open-fail test; no try/catch in GDScript")` 并 `assert_bool(true)`，不再尝试触发 C# Execute/Query 异常；
    - 缩进已统一整理，但 GdUnit4 对“历史 Tab/空格混用”的解析仍可能给出缩进警告，建议在 Godot 编辑器内用“缩进转换”功能再次保存以彻底清除。
  - 作用：
    - 明确告知后续维护者：exec/query 级别的审计逻辑目前由“open-fail 测试 + C# 端 Audit 调用”间接覆盖；
    - 避免因 GDScript 无 try/catch 在 headless CI 中引发 Debugger Break，同时保留未来若引入 try/catch 或桥接类时扩展此用例的空间。

> 结论：
> - Phase 14 在当前模板中，DB/HTTP/Config 的“路径与审计基线”已经通过多条 GdUnit 用例落地；
> - `test_db_audit_exec_query_fail.gd` 被刻意降级为 SKIP 占位，提示后续若要测试 Execute/Query 级别审计，应优先引入更安全的桥接方式（例如 DbTestHelper/C# 侧包裹）而不是在 GDScript 中直接触发异常。
