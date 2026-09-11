# Godotgame 知识库、Impact 与工作流演进移植需求

## 1. 文档信息

- 目标仓库：`godotgame`
- 参考仓库：`newrouge`
- 文档类型：跨仓库能力移植需求
- 日期：2026-09-11
- 状态：Draft
- 目标：将 `newrouge` 已验证的通用工作流、知识库、Impact 和 Project Health Knowledge 前后台能力移植到 `godotgame`，同时剥离所有 `newrouge` 业务数据，并保留 `godotgame` 已独立演进的模板能力。
- 参考实现基线：`newrouge@467946e3751cce80995af482d18b2e6a2978f967`
- 目标仓库基线：`godotgame@6104f1ec09228a02d96e26b0f35ab4591c228b59`
- 基线状态：两个仓库在审计时均无已跟踪文件修改；本需求文档是 `godotgame` 唯一新增文件。
- 基线变化规则：实施开始前必须核对上述 SHA；任一仓库已前进时，先生成增量能力差异并更新迁移清单，禁止继续按旧基线复制。
- 文档定位：本文是迁移需求和验收基线，不代替正式 PRD、架构决策或实施 SPEC。

## 2. 原始需求

需要评估 `newrouge` 相对兄弟仓库 `godotgame` 的演进，至少覆盖：

1. `workflow.md` 及 Chapter 2-7 系列技能、脚本和恢复协议的演进。
2. Repository Knowledge Control Plane、项目资源知识目录、Knowledge Locator、上下文决策/冻结、Impact Index 与 Impact Analysis。
3. Project Health 的 `/knowledge/` 二级页面、HTTP API、配置管理、任务导航、素材预览和 Gameplay runtime 验证。
4. 两仓之间其他会影响上述能力正确移植的差异，包括 CI、测试、目录职责、初始化流程、任务三联、模板行为及 Git 发布策略。
5. 在 `godotgame` 中形成可实施需求，禁止复制 `newrouge` 的游戏业务数据。

## 3. 审计结论

### 3.1 总体判断

不能通过目录覆盖或提交摘取整批文件完成移植。两个仓库已经双向演进：

- `newrouge` 拥有较完整的知识控制面、Impact、项目资源知识、Knowledge + Impact 页面和 runtime 验证能力。
- `godotgame` 是模板仓，已在 2026-09-11 独立加入 Chapter 2.5 技术预检与任务编号强化；这些更新不能被 `newrouge` 较旧的同名工作流文件覆盖。
- `newrouge/workflow.md` 只挂载了 2026-09-07 以前的 Knowledge + Impact 基础入口，尚未完整挂载后续的 `docs/knowledge/**` 初始化、Chapter 6 资源知识回写和最新页面配置能力。因此移植权威来源必须是实际实现、专项文档与测试集合，而不是只比较根 `workflow.md`。

### 3.2 能力矩阵

| 能力 | newrouge | godotgame | 移植要求 |
| --- | --- | --- | --- |
| Chapter 2-7 基础工作流 | 有，含后续知识路由改造 | 有，且含较新的 Chapter 2.5 | 合并，不覆盖 |
| 基础 Project Health 首页与本地服务 | 有 | 有 | 扩展现有服务 |
| `/knowledge/` 二级页面 | 有 | 无 | 移植 |
| Knowledge HTTP API | 有 | 无 | 移植 |
| Knowledge Control Plane | 有 | 无 | 移植通用内核与空种子 |
| Knowledge Locator 与 consumer policy | 有 | 无 | 移植并模板化标识 |
| 上下文候选、显式决策与 freeze | 有 | 无 | 移植 |
| Impact Index/Analyzer/Handoff | 有 | 无 | 移植 |
| `docs/knowledge/**` 项目资源目录 | 有，含业务生成数据 | 无 | 只移植 schema、README、初始化器和空生成结构 |
| Chapter 6 资源知识捕获 | 有 | 无 | 移植并挂载到 Chapter 6 |
| Gameplay runtime 批量验证 | 有 | 无 | 移植通用算法与空状态 |
| 知识发布 GitHub Actions | 有 | 无 | 移植并适配模板仓 |
| Project Health 既有 schema | 有 | 有 | 增量兼容，不重复创建 |

## 4. 业务数据剥离边界

### 4.1 禁止带入 godotgame 的数据

以下内容属于 `newrouge` 业务实例，禁止复制为 `godotgame` 默认值、测试夹具或正式生成物：

- 仓库名、产品名和 schema 前缀中的 `newrouge` 固定值。
- `PRD-NEWROUGE-GAME-0001` 及其 Overlay 路径。
- 任务 18、24、95、115 等具体任务编号和对应语义结果。
- Warrior、Reward、Act 1 等与 `newrouge` 具体实体、内容 ID 或组合结构绑定的业务记录。Combat、卡牌、遗物、敌人等通用领域词本身不是泄漏证据，只有与参考仓库专属 ID、路径、数值、哈希或 provenance 组合命中时才判定泄漏。
- `Reward.tscn`、`RewardScene.gd`、`m1-warrior-starting-deck.json` 等业务路径。
- `task_scene_bindings` 中任务 115 的人工映射。
- 奖励、存档、战斗等 `query_aliases` 示例。
- `docs/knowledge/generated/task-18-semantic.json`、`task-115-semantic.json` 和现有 `task-resource-links.json` 数据。
- `knowledge/indexes/generations/**` 中基于 `newrouge` main 生成的不可变 publication。
- 现有 asset/config catalog 中的业务记录、哈希、revision 和统计数字。
- 为 `newrouge` 真实查询集生成的 evaluation 结果。

### 4.2 允许移植的通用资产

- JSON Schema、稳定数据契约和验证器。
- Knowledge/Impact 构建、查询、冻结、发布和恢复算法。
- consumer 类型及其通用职责：`repository-session`、`chapter4`、`chapter5`、`chapter6`、`review`。
- Project Health Knowledge 页面布局、交互模式、安全边界和状态模型。
- 任务三联的通用映射规则。
- 配置/场景/素材/测试的静态证据模型。
- runtime 验证的 revision 绑定、超时、串行、批次锁和 main/workspace 隔离规则。
- 空目录、空 catalog、模板配置和自检夹具。

### 4.3 模板化标识要求

- schema 使用固定模板级命名空间 `godot-project-knowledge`，不得硬编码为 `newrouge` 或运行时仓库名；仓库名和产品名只作为实例 metadata，由初始化器根据仓库标识生成。
- policy revision、publication metadata 和 request id 可以有稳定 schema 版本，但不得包含某个游戏的业务 ID。
- 默认配置必须根据仓库实际存在路径生成。不存在的 Taskmaster、PRD、GDD、Overlay、Godot 测试或游戏目录允许为空或标记未初始化，不得伪造样例业务文件。

### 4.4 业务泄漏检测范围

- 泄漏扫描只覆盖生产脚本及其默认值、运行时配置、页面资源、schema、fixture、catalog、snapshot、generation 和自动化工作流。
- 迁移需求、审计报告、决策日志以及专门验证“拒绝业务数据”的负面测试允许在说明性上下文中引用禁止词，但不得将其作为默认值或正向 fixture 数据。
- 检测器必须按结构化位置和 provenance 判定泄漏，不得以全仓关键字计数作为唯一门禁。
- 检测报告必须列出命中文件、JSON pointer 或代码位置、命中类别和豁免理由；没有理由的命中一律失败。

### 4.5 非目标

- 本次移植不创建 `godotgame` 的玩法、任务、角色、场景、配置或素材业务内容。
- Knowledge 层不替代 Taskmaster、PRD/GDD、ADR、Overlay、Contracts 和源代码等权威来源。
- 不建设云服务、远程访问、多用户协作、账户系统、向量数据库或在线 RAG。
- 页面机器检索不调用 LLM；Chapter 6 可选语义补全不改变机器检索的确定性定位。
- 不并行运行多个 Godot 验证进程，不用引擎启动成功替代任务级断言。
- 本需求文档不授权直接实施全量迁移；正式 PRD 和 SPEC 仍是进入实现前的门禁。

## 5. 功能需求

### FR-01：工作流能力级合并

1. 对 `workflow.md`、Chapter 2-7 skills、`dev_cli.py` 和 Chapter orchestrator 做语义级合并。
2. 保留 `godotgame` 的 Chapter 2.5 technical preflight、任务编号规则和最新模板初始化行为。
3. 将知识库入口挂载到正确阶段：
   - Chapter 2：初始化空 Knowledge Control Plane 与 `docs/knowledge/**`。
   - Chapter 4：在 Overlay/Contract 写入前生成 observe-only knowledge candidate context。
   - Chapter 5：在语义稳定化前生成任务级候选上下文。
   - Chapter 6：在 RED 前完成显式上下文决策/冻结；任务实现完成后捕获配置、素材、场景、代码与测试关联。
   - Review：使用独立 `consumer=review` 上下文和匹配 revision 的 Impact Report。
4. 根 `workflow.md` 只保留阶段入口、强制顺序、停止条件和权威专项文档链接，详细页面操作放在专项文档。
5. Chapter skill 的 `references/workflow-source.md` 必须与更新后的根工作流同步。

### FR-02：Knowledge Control Plane

1. 创建通用 `knowledge/**` 控制面结构：contracts、policies、projections、evaluation、snapshots、catalogs 和 indexes。
2. Repository facts 继续由 AGENTS、workflow、Taskmaster、PRD/GDD、ADR/Base/Overlay、Contracts 和工作流文档拥有；Knowledge 层不得成为第二 SSoT。
3. Locator 只返回候选位置、source hash、anchor 和排序证据，不得自动声称语义满足。
4. 支持 `current`、`last-known-good`、immutable generation、publication check 和 LKG 恢复。
5. publication 必须绑定可信 `refs/heads/main`，候选验证失败不得推进 current/LKG。
6. 缺失、过期、hash 不一致或 policy 不匹配时 fail closed，并允许 Chapter 流程回退到直接权威来源。
7. `knowledge/**` 是机器消费的控制面：保存 contracts、policies、source snapshot、publication generation、current/LKG pointer 和 consumer projection，仅由构建、冻结和发布工具写入。
8. `docs/knowledge/**` 是项目资源知识目录：保存允许人工审阅的配置、素材、场景、代码和测试关联，以及 Chapter 6 的资源知识记录；它是 Control Plane 的输入来源之一，不反向拥有 publication 状态。
9. 数据流固定为“权威仓库来源及 `docs/knowledge/**` -> Knowledge builder -> candidate generation -> validation -> current/LKG”；禁止由 `knowledge/**` generation 反写 Taskmaster 或人工 catalog。

### FR-03：Knowledge Context 决策与冻结

1. `prepare_knowledge_context.py` 支持五类 consumer，并产生 observe-only candidate bundle。
2. ranking 不等于 acceptance；每个候选必须显式记录 accepted/rejected、reason 和 satisfies。
3. freeze 必须绑定 candidate bundle hash、source hash、policy revision、snapshot commit、consumer 和 task id 规则。
4. Chapter 6 在 RED 前冻结上下文；RED/GREEN/REFACTOR 中不得静默扩充语义来源。
5. Chapter 6 与 Review 必须使用不同 consumer 上下文；不得通过修改 consumer 字段绕过 handoff。

### FR-04：Impact 能力

1. 移植 Impact Index、symbol/file target resolver、Analyzer、runtime、handoff 与 validation。
2. 支持 C# 代码、Godot 场景、配置、测试和已声明关系的影响分析。
3. 探索页面允许跳过无法解析的方法并公开遗漏原因；正式分析保持严格失败。
4. 正式 Impact Report 必须绑定 revision 与 frozen context hash。
5. 不得把自然语言直接当作已确认 symbol id，也不得把普通关键词相关性冒充影响关系。

### FR-05：项目资源知识目录

1. 在 `docs/knowledge/**` 初始化：README、schema、catalog、indexes、generated 占位结构。
2. 生产知识保存在 `docs/knowledge/**`；`logs/**` 只保存运行证据、候选与诊断。
3. 提供 CLI：
   - `init-knowledge-catalog --validate`
   - `generate-knowledge-links --task-id <id>`
   - `chapter6-knowledge --task-id <id> --write-task-refs`
4. Chapter 6 捕获配置、素材、场景、代码和测试关联，并记录用途、调参建议、影响、具体字段/值、读取代码与证据链。
5. 关联状态至少区分 confirmed、inferred、unverified、removed；模型推断不得显示为静态确认。
6. Taskmaster 视图只保存轻量引用，不嵌入完整 catalog 内容。
7. 初始化阶段生成空字典；新任务由 Chapter 6 实施时增量填充；已有项目允许用语义重建工具补齐，但重建结果必须标注 provenance。
8. 语义字段的生产者必须显式标记为 `deterministic`、`llm` 或 `human`；`llm` 结果默认只能进入 `inferred`，经人工确认或可重复的代码证据验证后才可提升为 `confirmed`。
9. LLM 语义补全必须记录 provider、model、prompt/schema version、输入 source revision、开始/结束时间和重试结果；密钥、完整私有提示和敏感环境变量不得写入仓库。
10. LLM 不可用、超时或达到重试上限时，Chapter 6 保留确定性证据并明确标记 `semantic_enrichment_failed`，不得阻断代码实现、测试和基础知识捕获，也不得伪造 Function、Tuning 或 Impact。
11. LLM 语义补全默认关闭，只能由 Chapter 6 的显式参数或仓库配置启用；`GD_OFFLINE_MODE=1` 时必须跳过外部调用并保留可诊断的降级状态。
12. 单次语义补全最多执行 5 次有界重试，使用带上限的退避并记录每次失败；第 5 次失败后进入 `semantic_enrichment_failed`，不得无限等待或重启整个 Chapter 6。

### FR-06：Project Health Knowledge 页面

1. 在现有 Project Health 服务增加 `/knowledge/`，不得新建第二套常驻服务。
2. 页面提供：
   - main-only snapshot 扫描；
   - consumer 分类查询与动态说明；
   - Knowledge 候选、GDD 补充和 Impact target；
   - tasks.json SSoT 列表、分页、多选和状态筛选；
   - 任务详情中的配置、代码、场景节点、素材和测试导航；
   - 原始证据按需展开。
3. 配置编辑器默认隐藏，通过按钮以 modal 浮层打开，不得撑开主页。
4. 扫描来源采用“原因在左、可编辑路径在右”的分类行；每项路径允许为空。
5. 使用稳定 `source_path_bindings` 分类键持久化空值，同时生成扫描器使用的非空 `source_paths`。
6. 配置浮层至少覆盖扫描来源、GDD 来源、任务场景人工映射和机器查询别名。
7. 查询为确定性机器检索，不调用大模型；默认区分中英文，别名是独立查询，不伪装成翻译或向量语义搜索。
8. 服务端口通过 `serve-project-health --port <port>` 配置；`8783` 仅是当前本地实例示例，不是协议常量。启动输出必须打印实际 URL。
9. 扫描必须同时读取 `.taskmaster/tasks/tasks.json`、`tasks_back.json` 和 `tasks_gameplay.json`；以 `tasks.json.master.tasks[].id` 为 SSoT，两个视图按 `taskmaster_id` 映射。重复映射合并，孤立、重复冲突或字段漂移必须进入诊断，不能静默覆盖。
10. runtime 候选仍只来自 `tasks_gameplay.json`；`tasks_back.json` 只参与知识导航、治理上下文和跨视图一致性检查，不启动 Godot。
11. 页面控件、状态说明、查询类别名称和动态帮助使用简明中文；原始来源和 LLM 生成的英文 Function、Tuning、Impact 等语义内容保持原文，不做自动翻译。切换查询类别时，框体下方的中文说明必须同步切换。

### FR-07：任务修改导航

1. 默认只展示任务明确来源、核心代码、映射场景、直接配置和素材引用。
2. 间接依赖、共享 ID 和测试符号候选放入折叠的“更多关联”。
3. 配置关联分为已确认字段、语义建议和仅间接关联。
4. JSON 配置展示具体 pointer、当前值、行号、读取代码和证据链。
5. 打开配置源码时高亮已确认字段与语义建议字段，并保持 revision 一致。
6. PNG/JPEG/WebP 相对路径支持悬停预览和点击打开；图片必须来自扫描 allowlist 且绑定导航 revision。
7. 场景导航展示 node path、type、properties、ExtResource/SubResource 和有限深度引用链。
8. `task_scene_bindings` 只是经审查的例外映射，不是全任务清单；新模板默认应为空。

### FR-08：Gameplay runtime 验证

1. 只从 `tasks_gameplay.json` 选择候选，并按 `taskmaster_id` 映射到 tasks.json SSoT。
2. 只有存在可定位 `Tests.Godot/**` 任务级测试引用时才执行 Godot；启动成功不等于任务通过。
3. 验证顺序为 runtime -> static attachment -> candidate/unmapped，runtime 失败后仍继续静态检测。
4. 状态至少包括 runtime_verified、static_attached、runtime_failed_static_attached、candidate、unmapped，并单独保留 runtime_unverified/runtime_failed 原因。
5. main 模式从扫描 commit 创建隔离副本；workspace 模式复制当前工作区并绑定内容 digest。两者证据不得互相覆盖。
6. 测试默认串行，具备单任务超时、全局超时、批次锁和进程树终止。
7. 页面提供 eligible 批量、all gameplay 审计、任务多选和单任务验证。
8. 任一扫描或验证操作进行时，所有已打开页面通过 operation API 进入全页锁定。
9. 所有运行证据写入 `logs/ci/project-health-knowledge/runtime/**`，不得修改任务文件或游戏源码。

### FR-09：安全边界

1. 服务只绑定 `127.0.0.1`。
2. 写 API 校验 Host、Origin、session token、请求大小和固定参数集合。
3. 禁止任意 shell 命令、任意分支、任意输出路径和越界文件读取。
4. source/image API 只访问扫描 allowlist；拒绝根目录、`logs/**`、`.git/**`、软链接、junction 和 `..`。
5. 页面打开的源码必须与任务导航 revision 一致；扫描变化后拒绝混用旧详情。
6. 配置写入采用临时文件、flush、校验后原子替换；请求必须携带读取时的 config revision，revision 冲突返回 `409`，不得覆盖另一标签页或进程的新修改。
7. 空字符串表示“该分类尚未配置”；删除绑定必须使用显式删除操作，不得把空值、缺失键和删除混为一谈。

### FR-10：Knowledge HTTP API 契约

| Method | Route | 用途 | 成功响应 | 主要失败 |
| --- | --- | --- | --- | --- |
| GET | `/session` | 获取 session token 和服务能力 | session envelope | `403` Host 不合法 |
| GET | `/operation` | 获取页面锁及当前操作 | operation state | `500` 状态损坏 |
| GET | `/status` | 获取 snapshot、统计和 runtime 摘要 | status schema | `409` snapshot 不可用 |
| GET | `/config` | 获取分类配置及 config revision | config envelope | `422` 配置不合法 |
| PUT | `/config` | 校验并原子更新配置 | 新 config revision | `409` revision 冲突，`422` schema 失败 |
| GET | `/tasks` | 分页、筛选任务列表 | page envelope | `400` 查询参数非法 |
| GET | `/task?id=<id>` | 获取任务详情和导航 | task detail | `404` 任务不存在 |
| GET | `/source?path=<path>&revision=<rev>` | 打开 allowlist 内源文件 | UTF-8 source envelope | `403` 越界，`409` revision 变化 |
| GET | `/image?path=<path>&revision=<rev>` | 预览 allowlist 内图片 | image bytes | `403` 越界，`415` 类型不支持 |
| POST | `/scan` | 创建 main-only 扫描操作 | accepted operation | `409` 已锁定 |
| POST | `/query` | 执行确定性知识查询 | ranked result | `422` 请求非法 |
| POST | `/runtime` | 创建 main/workspace runtime 操作 | accepted operation | `409` 已锁定，`422` 缺少 Godot |

1. 所有路由使用统一前缀 `/api/knowledge`。
2. 所有 JSON 响应使用 `{schema_version, request_id, status, data, error}` envelope；错误必须包含稳定 `code` 和面向用户的 message，不返回 traceback 或绝对路径。
3. 当前 operation 状态机固定为 `idle -> queued -> running -> idle`；`queued/running` 时页面除状态轮询外全部不可操作。操作结束后立即解除页面锁，并把 `succeeded|failed|timed_out` 结果写入独立 `last_operation`，直到下一次操作完成后覆盖。
4. 服务重启时若发现遗留 `queued/running`，必须把 `last_operation` 写为 `failed` 并标记 `interrupted_by_restart`，同时把当前状态恢复为 `idle`；锁不能永久遗留。
5. API schema 单独版本化并由前后端契约测试固定；兼容期内只允许增加可选字段，删除或改义必须升级 major schema version。
6. operation 锁按仓库工作区生效，使用原子创建的锁文件和进程内互斥共同保护；同一工作区的不同端口服务、不同标签页或并发请求只能有一个获得锁。锁记录 PID、process start identity、operation id 和时间戳；只有确认原进程不存在时才能回收陈旧锁。

### FR-11：模板初始化和空项目行为

1. `godotgame` 初始状态没有真实业务任务、PRD、Overlay、配置或素材时，初始化和页面仍应可启动。
2. 缺失来源显示“未初始化/未配置”，不得生成 Warrior、Reward 或其他示例业务数据。
3. `source_path_bindings` 默认值只填写当前模板真实存在的通用目录；其他类别保留空值。
4. Taskmaster 三联创建后，可重新初始化/刷新扫描而不破坏已有人工配置。
5. `docs/knowledge/generated/**` 的空状态与正式生成状态必须有 schema 和 manifest 可验证。

### FR-12：CI 与发布

1. 增加 Knowledge Control Plane 的 kernel、freeze、publication、routing 和 repository smoke 测试。
2. 增加 Project Health Knowledge HTTP、UI 契约、导航、图片和 runtime snapshot 测试。
3. 增加 Chapter 6 knowledge 初始化、生成、捕获和失败恢复测试。
4. 评估并移植 `publish-knowledge-catalog.yml`：只能通过 automation branch/PR 更新派生 `knowledge/**`，不得直接写 protected main。
5. 生成状态与业务源变更必须避免形成无限自动 PR 循环。
6. 新门禁应接入现有 hard/soft gate 体系，不得重复运行已有 Project Health schema 测试。
7. workflow 必须声明最小 `contents`/`pull-requests` 权限，并处理 token 无写权限、fork 事件、同名 automation branch、已有开放 PR、并发取消和 `gh` 不可用；这些情况必须产生可诊断失败或只读检查结果，不能无限重试。
8. publication 使用以 source SHA 为键的幂等分支和 PR；相同 source SHA 已有成功 publication 时不得再次创建 PR。

### FR-13：文档与入口同步

必须更新并互相链接：

- `workflow.md`
- `AGENTS.md` 路由项
- `docs/agents/00-index.md`
- `docs/agents/13-rag-sources-and-session-ssot.md`
- `docs/agents/16-directory-responsibilities.md`
- `docs/PROJECT_DOCUMENTATION_INDEX.md`
- `docs/workflows/project-health-dashboard.md`
- 新增的 Knowledge/Impact 专项工作流文档
- Chapter 2、4、5、6、Review skills 及其 workflow-source references

### FR-14：配置持久化契约

1. `scripts/python/project_health_knowledge_config.json` 是 Project Health Knowledge 的人工配置 SSoT；页面不得直接改写生成的 `source_paths`、catalog 或 generation。
2. 配置 schema 至少包含 `schema_version`、`config_revision`、`source_path_bindings`、`task_scene_bindings`、`query_aliases` 和各分类说明；受支持 schema major version 中的未知字段必须原样保留，未知 major version 拒绝写入，不得静默丢失。
3. `source_path_bindings` 保存包括空值在内的用户输入；扫描器从中派生仅包含有效非空路径的 `source_paths`，派生结果不得反写覆盖用户配置。
4. 保存前校验相对仓库路径、分类键、重复路径、文件类型和 allowlist；保存后重新读取并校验，失败时保留旧文件并返回稳定错误码。
5. `task_scene_bindings` 只保存无法由结构证据可靠推导的例外映射；新项目默认为空，不要求穷举所有任务。

### FR-15：迁移、启用与回退

1. 新路由和新 schema 先以兼容模式落地；现有 `/` Project Health 首页、既有 CLI 和五个 schema 的回归测试保持通过后，才启用 `/knowledge/` 写操作。
   - `sc-project-health-dashboard.schema.json`：`eeadcffb9b6cc32b72b6f343861de41740882e621d2601880f72e327d6499b0b`
   - `sc-project-health-report-catalog.schema.json`：`d87447e3bbff01964c0d007960e93c12fd8eafe6da6677180ee6659e49187ee9`
   - `sc-project-health-server.schema.json`：`87d3927da4f45aa4457ebae6cbc2c706c4f64cf251871341769bf55ea7b8b2f9`
   - `sc-project-health-record.schema.json`：`cf0bda229f7aee6dea1eedb112c82bb8f59d1fd91b36966ffb85c21fcba34a82`
   - `sc-project-health-scan.schema.json`：`5884b58e6ac6f05dd4fb02071312231aedf55f7301d2310858a5e5c7565f63d1`
2. 初始化和迁移命令必须提供 `--check` 或 dry-run，输出计划新增、合并、跳过和冲突的文件，不在检查模式写盘。
3. 每个 Batch 都必须可独立回退：新增文件可删除；对共享文件的修改以基线 diff 反向恢复；不得用整仓覆盖回退。
4. schema 或配置迁移必须先备份原文件到 `logs/ci/<date>/knowledge-port/backup/**`，记录 SHA-256 和恢复命令；备份是证据，不是生产 SSoT。
5. publication workflow 只有在本地 kernel、API、UI 和业务泄漏门禁全部通过后启用；失败回退时禁用触发器并关闭由本次迁移创建的 automation PR，不修改 protected main 历史。
6. 每个 Batch 完成后生成 manifest，记录源 SHA、目标 SHA、文件动作、测试结果和未解决项；下一 Batch 只能消费成功 manifest。

## 6. 非功能需求

### NFR-01：兼容性

- Windows-only，所有正式命令可由 PowerShell 调用。
- Python 入口使用 `py -3`。
- 保持 Godot 4.5.1 + C#/.NET 8 边界。
- 保持现有 Project Health server schema 向后兼容；新增字段优先可选或通过 schema version 演进。

### NFR-02：可恢复性

- 扫描失败保留上一次成功结果。
- publication 失败不得推进 current/LKG。
- runtime 中断保留批次输入清单、测试报告和失败原因。
- Chapter 6 knowledge 捕获失败必须显示独立 `knowledge_capture_failed`，不得伪装成 runtime 或任务验收失败。

### NFR-03：性能

- 默认不在普通 Project Health 扫描中运行 Godot。
- runtime 默认串行，避免多个 Godot 进程争用项目目录。
- 任务详情和原始证据按需加载；大素材不进入文本扫描。
- 查询和 Impact target 必须设定有界数量，并公开总数和截断信息。
- 基准环境以 `godotgame` CI Windows runner 为准：不启动 Godot 的 `/knowledge/` 首次状态加载 p95 不超过 2 秒，普通确定性查询 p95 不超过 1 秒，任务列表翻页 p95 不超过 500 毫秒。
- 性能验收使用固定的中性数据集连续预热 3 次、测量至少 20 次并报告 p50/p95；runner 规格和数据规模写入证据，单次偶然结果不能作为通过依据。
- 默认分页 50 条、最大 200 条；查询文本最大 4096 字符；源文件查看默认最大 2 MiB；图片预览默认最大 10 MiB。阈值必须集中配置并由边界测试覆盖。
- 超出限制时返回明确的截断标记或 `413/422`，不得静默丢失结果。
- 固定中性性能 fixture 包含 500 个 SSoT 任务、两个各 250 条的任务视图、10,000 个可扫描文件、2,000 条配置记录、1,000 条素材记录、200 个场景和 5,000 条资源关联；fixture manifest 和 SHA-256 纳入仓库，规模变化必须显式更新性能基线。

### NFR-04：可解释性

- 每条关联公开证据类型、provenance、revision 和置信状态。
- UI 明确区分静态确认、模型建议、间接候选和实际 runtime 观察。
- 机器检索的 token/别名规则必须公开，不得用“语义搜索”描述普通关键词匹配。

### NFR-05：浏览器、响应式与可访问性

- 支持当前稳定版 Microsoft Edge 和 Chrome；Windows 缩放 100% 与 150%、视口宽度 1280 至 1920 像素不得出现控件重叠或不可达操作。
- 所有按钮、选择框、任务多选和 modal 均可仅用键盘完成；modal 打开后聚焦首个控件，焦点限制在 modal 内，`Esc` 关闭并把焦点返回触发按钮。
- 图标按钮必须有 accessible name；状态不能只靠颜色表达；图片预览失败必须有文本原因。
- 前端契约测试覆盖标签、焦点和锁定态；至少使用一个桌面浏览器执行截图和交互冒烟测试。

### NFR-06：证据保留与清理

- runtime batches、LLM 诊断和配置迁移备份默认保留 30 天，且每类最多保留最近 20 个批次；满足任一淘汰条件即进入清理范围。
- 提供 `dev_cli.py cleanup-project-health-knowledge --check|--apply`；`--check` 只列出目标、大小和原因，`--apply` 只能删除 allowlist 内符合 manifest 的证据目录。
- CI 在生成新证据前执行清理检查，并在明确启用 apply 的维护步骤中清理；普通扫描、查询和 Chapter 6 不得隐式删除证据。
- 清理操作生成包含路径、manifest id、创建时间、大小和规则版本的审计记录；生产知识、current/LKG 和未过期的失败证据不得被清理。

## 7. 迁移实施批次

### Batch A：共同基线与反覆盖保护

1. 校验本文记录的两个基线 SHA；发生变化时先更新差异审计和本文，不得静默采用新 HEAD。
2. 为 Chapter 2.5、任务编号和现有 Project Health 行为增加/确认回归测试。
3. 建立文件级三方比较：godotgame current、newrouge reference、target merged。
4. 禁止整文件覆盖 workflow、dev_cli、Chapter skills 和 Project Health server。
5. Batch A 必须生成并人工复核逐文件迁移清单；清单未覆盖所有参考通配符匹配项、辅助模块和关联测试时，Batch B 不得开始。
6. 逐文件清单作为生产计划保存到 `execution-plans/knowledge-impact-workflow-port/file-migration-manifest.json`；运行过程和校验输出另存 `logs/ci/**`，不得把唯一生产清单放在日志目录。

### Batch B：Knowledge/Impact 内核

1. 移植 contracts、policies、projections 和空 evaluation suite。
2. 移植 builder、locator、freeze、publication、Impact Index/Analyzer/Handoff。
3. 替换产品命名空间和 repository-real fixtures。
4. 先通过 kernel 单元测试，再生成任何跟踪 publication。

### Batch C：模板初始化与 Chapter 路由

1. 增加 Knowledge 与 `docs/knowledge/**` 初始化 CLI。
2. 合并 `dev_cli.py` 命令。
3. 将 shadow/freeze/impact/resource capture 挂载到 Chapter 2/4/5/6/Review。
4. 同步根 workflow 和 Chapter skill references。

### Batch D：Project Health Knowledge 前后台

1. 在现有 server 增加 Knowledge API 和静态页面资源。
2. 实现 snapshot、查询、任务分页、导航、配置 modal、图片预览和 operation lock。
3. 使用 godotgame 空模板数据验证无任务/无 GDD/无 Overlay 的状态。

### Batch E：runtime 验证

1. 移植隔离 snapshot builder、GdUnit prewarm、任务选择和证据写入。
2. 验证 main/workspace 身份和结果隔离。
3. 验证 eligible、selected、all gameplay 和 single task 四类入口。

### Batch F：CI、发布与收口

1. 合并测试到现有 gates。
2. 增加 publication automation PR 流程。
3. 执行完整本地 hard checks、Project Health 测试、Knowledge/Impact 测试和最小 Godot runtime self-check。
4. 审计业务词、任务号、PRD ID、路径和 schema 命名，确认无 `newrouge` 数据泄漏。
5. 执行回退演练：至少恢复一次配置、一次共享脚本修改和一次 publication 失败状态，并验证原 Project Health 仍可运行。

## 8. 验收标准

### AC-01：业务隔离

- 第 4.4 节定义的生产扫描范围中，不存在从参考实现带入的 Warrior、Reward、任务 18/115、`PRD-NEWROUGE-GAME-0001` 或对应资源哈希。
- 所有模板 fixture 明确标为 fixture，并使用中性标识。
- 需求、审计和负面测试中的说明性命中具有结构化豁免；任何生产默认值、正向 fixture 或生成数据命中均使门禁失败。

### AC-02：初始化

- 在干净 `godotgame` clone 中运行 Knowledge 初始化命令成功。
- 空项目生成有效 schema/manifest，不生成虚构业务记录。
- 重复初始化幂等，不覆盖人工维护数据。

### AC-03：工作流

- Chapter 2.5 与现有任务编号回归保持通过。
- Chapter 4/5/6/Review 能按 consumer 生成候选；缺 publication 时按规范回退。
- Chapter 6 在 RED 后不能静默扩展冻结上下文。
- Chapter 6 完成后能捕获资源知识并写入 `docs/knowledge/**`。
- 三联扫描能识别孤立视图项、重复 `taskmaster_id` 和与 SSoT 冲突的字段；`tasks_back.json` 中的治理任务不会触发 Godot runtime。
- LLM 关闭、离线、首次成功、重试后成功和连续 5 次失败均有测试；provider/model/schema version 等 provenance 完整，敏感值未落盘，`inferred` 不会未经确认提升为 `confirmed`。

### AC-04：页面与 API

- `serve-project-health` 启动后，首页可进入 `/knowledge/`。
- 配置默认隐藏，以 modal 打开。
- 来源配置每行先说明原因，后半部分直接编辑路径，空值刷新后不丢失或错位。
- 状态统计可筛选任务；任务支持分页、多选和单任务详情。
- 不存在任务时页面显示有效空状态，不抛异常。
- FR-10 的全部 route、envelope、错误码、operation 转移和服务重启恢复均有前后端契约测试。
- 两个标签页基于同一 config revision 编辑时，后提交者收到 `409`，原配置不被覆盖。
- 操作完成后页面立即解锁，结果保存在 `last_operation`；服务重启中断操作后也不会遗留页面锁。
- 同一工作区启动两个不同端口的服务并并发提交操作时，只有一个请求成功获得锁，另一个返回 `409`；原进程异常退出后可按 process identity 安全回收陈旧锁。
- 查询类别、控件和帮助文字使用中文并随选择同步变化；英文来源和英文语义结果逐字保持，不自动翻译。

### AC-05：任务导航

- 中性 fixture 任务能展示配置 pointer/value、读取代码、场景节点、素材预览和测试证据。
- 静态确认、语义建议和间接关联有明确区分。
- revision 改变后旧导航源码请求被拒绝。

### AC-06：runtime

- 没有 `Tests.Godot/**` 的任务只得到 runtime_unverified，不启动 Godot。
- 任务级断言通过且 revision/证据完整时才得到 runtime_verified。
- runtime 失败后继续静态检测，并保留失败原因。
- main 和 workspace 证据相互独立；验证过程不修改业务源或任务文件。

### AC-07：安全

- Host/Origin/token/size/path traversal/allowlist 测试全部通过。
- API 无任意命令执行和任意文件读取能力。
- 服务只监听 `127.0.0.1`。

### AC-08：发布与恢复

- candidate publication 失败不会更新 current/LKG。
- LKG 可恢复 canonical generated layers。
- GitHub Actions 只创建派生知识更新 PR，不直接推送 main。
- 相同 source SHA 重跑不会创建重复分支或 PR；无写权限和 fork 情况产生明确只读结果。
- Batch C 至 F 各完成一次规定的 dry-run 或回退演练，恢复后的旧入口和配置校验通过。

### AC-09：总体回归

- `validate_recovery_docs.py --dir all` 通过。
- hard gate bundle 通过。
- 现有 Project Health、Chapter 2.5、任务编号和 Chapter 6 tests 无回归。
- 新增 Knowledge/Impact/页面/runtime 测试全部通过。
- NFR-03 性能边界和 NFR-05 浏览器/键盘冒烟测试通过，证据写入 `logs/ci/**`。
- 五个既有 Project Health schema 的路径和 SHA-256 与 FR-15 基线一致，或存在经审查的显式 schema 版本迁移记录。
- NFR-06 的 30 天/20 批次边界、check/apply、安全 allowlist 和未过期失败证据保护测试通过。

## 9. 风险与止损

1. 若移植导致 `godotgame` Chapter 2.5 或任务编号行为退化，立即停止整合并回到三方语义合并，不允许用参考仓文件覆盖。
2. 若 schema 命名仍依赖 `newrouge`，先完成命名空间决策再发布任何 generation。
3. 若空模板无法生成 repository-real evaluation query，应保留 kernel fixture 与初始化后待配置状态，不得复制参考游戏查询。
4. 若 runtime fixture 需要完整业务场景才能通过，应建立最小中性 Godot fixture，不得引入参考游戏场景。
5. 若自动 publication 形成循环 PR，暂停 workflow，只保留本地 publish/check 入口，修复 commit identity 与派生文件边界后再启用。
6. 若确定性检索无法支持自然语言需求，不得在本次移植中悄悄接入 LLM；应另立语义检索需求并明确成本、隐私和 provenance。

## 10. 实施完成定义

只有同时满足以下条件，才视为移植完成：

1. 通用能力、测试、专项文档和 workflow 挂载全部落地。
2. `godotgame` 独立演进能力无回归。
3. 第 4.4 节定义的生产范围内，`newrouge` 业务数据未豁免命中为零；说明性引用均有结构化豁免记录。
4. 空模板与中性 fixture 两种模式均通过验收。
5. Knowledge publication、Context freeze、Impact handoff 和 Project Health runtime 均有失败路径测试。
6. 本地 hard gates 和 GitHub Actions 全绿。

## 11. 参考实现来源

实施时优先按以下来源理解能力，不按目录盲拷贝：

- `../newrouge/knowledge/README.md`
- `../newrouge/docs/knowledge/README.md`
- `../newrouge/docs/workflows/knowledge-context-shadow.md`
- `../newrouge/docs/workflows/knowledge-context-freeze.md`
- `../newrouge/docs/workflows/knowledge-catalog-main-publish.md`
- `../newrouge/docs/workflows/project-health-knowledge.md`
- `../newrouge/scripts/python/*knowledge*.py`
- `../newrouge/scripts/python/impact*.py`
- `../newrouge/scripts/python/project_health_knowledge.*`
- `../newrouge/scripts/python/project_health_runtime.py`
- `../newrouge/scripts/sc/tests/test_*knowledge*.py`
- `../newrouge/scripts/sc/tests/test_project_health_*.py`
- `godotgame/workflow.md`、Chapter skills、`dev_cli.py` 与当前 Project Health 实现，作为合并目标和反回归权威。

## 12. 能力迁移清单

实施前将通配符展开为实际文件，并以本表作为最低迁移范围；源文件均固定到本文记录的 `newrouge` SHA。

| 能力 | 参考来源 | 目标动作 | 验证 |
| --- | --- | --- | --- |
| Control Plane contracts/policies | `../newrouge/knowledge/contracts/**`、`policies/**`、`projections/**` | 重写仓库标识后新增；不复制 generations | schema + kernel tests |
| Locator/freeze/publication | `knowledge_locator.py`、`prepare_knowledge_context.py`、`freeze_knowledge_context.py`、`publish_knowledge_catalog.py` | 新增并接入 `dev_cli.py` | locator/freeze/publication tests |
| Impact | `build_impact_index.py`、`impact_analysis_*.py`、`impact_analyzer.py`、`impact_runtime.py` | 新增；配置改为仓库中性 | unit + repository smoke |
| Resource catalog | `init_knowledge_catalog.py`、`generate_knowledge_links.py`、`chapter6_knowledge.py`、`docs/knowledge/schema/**` | 新增空目录/schema；不复制生成业务数据 | init/generate/chapter6 tests |
| Project Health backend | `_project_health_http.py`、`_project_health_navigation.py`、`_project_health_runtime_snapshot.py`、`project_health_knowledge.py` | 与 godotgame 现有 server 三方合并 | HTTP/schema/security tests |
| Project Health frontend | `project_health_knowledge.html`、`.css`、`.js` | 移植交互；移除业务示例 | UI contract + browser smoke |
| Runtime verifier | `project_health_runtime.py` 及 GdUnit runner 集成 | 新增 main/workspace、批量和单任务模式 | snapshot/runtime tests |
| Workflow wiring | `workflow.md`、Chapter 2/4/5/6/Review references、`dev_cli.py` | 三方语义合并，保留 Chapter 2.5 和任务编号能力 | recovery/chapter regression |
| CI publication | `../newrouge/.github/workflows/publish-knowledge-catalog.yml` | 按 godotgame 权限和分支策略重写 | action lint + dry-run |

每一行实施时必须在 Batch manifest 中展开为逐文件记录：`source_path`、`target_path`、`action=copy|merge|rewrite|exclude`、`business_data_risk`、`tests`。没有记录的参考文件不得顺带复制。

### 12.1 组件与数据所有权

| 数据或工件 | 唯一写入者 | 主要读取者 | 验证者 |
| --- | --- | --- | --- |
| `project_health_knowledge_config.json` | shared config writer，由配置 API/初始化 CLI 调用 | scanner、页面服务 | config schema validator |
| `docs/knowledge/catalog/**` | resource knowledge writer，由 Chapter 6/受控人工补录调用 | link generator、页面导航 | resource knowledge validator |
| `docs/knowledge/generated/**` | knowledge link generator | Chapter 6、页面导航、builder | manifest/schema validator |
| `knowledge/indexes/generations/**` | publication builder | locator、consumer projection | publication checker |
| `knowledge/indexes/current.json`、LKG | publication promoter/recovery | locator | publication checker |
| frozen context/Impact handoff | freeze/impact CLI | Chapter 6、Review | freeze/handoff validator |
| runtime evidence | runtime verifier | Project Health status/navigation | runtime evidence validator |
| operation/`last_operation` | Project Health operation manager | 所有已打开页面 | HTTP contract tests |

除表中唯一写入者外，其他组件只读。人工修改生成层、publication pointer、runtime evidence 或 operation 状态均视为契约违规。

## 13. 需求追踪矩阵

| 需求 | 实施批次 | 验收 | 最低测试证据 |
| --- | --- | --- | --- |
| FR-01、FR-13 | A、C | AC-03、AC-09 | recovery、Chapter 2.5/4/5/6/Review |
| FR-02、FR-03 | B | AC-02、AC-03、AC-08 | kernel、locator、freeze、publication |
| FR-04 | B | AC-05、AC-09 | impact index/analyzer/handoff smoke |
| FR-05 | C | AC-02、AC-03、AC-05 | init、generate links、semantic fallback |
| FR-06、FR-07、FR-10 | D | AC-04、AC-05、AC-07 | HTTP、UI contract、navigation、browser smoke |
| FR-08 | E | AC-06 | main/workspace snapshot、timeout、failure fallback |
| FR-09、FR-14 | D | AC-04、AC-07 | security、config conflict、atomic recovery |
| FR-11 | C、D | AC-01、AC-02 | empty-template and leakage tests |
| FR-12、FR-15 | F | AC-08、AC-09 | CI dry-run、idempotency、rollback drill |

## 14. 术语表

| 术语 | 含义 |
| --- | --- |
| Candidate | 尚未被任务显式接受或拒绝的知识候选，不代表事实成立。 |
| Decision | 对候选作出的 accepted/rejected 记录，包含原因和满足的需求。 |
| Freeze | 在任务 RED 前把选定上下文、来源和 revision 固定为不可静默变化的输入。 |
| Publication | 与 main commit 绑定、通过校验后可供消费者定位的知识索引版本。 |
| LKG | Last Known Good，最近一次成功校验且可以恢复的 publication。 |
| Consumer | 使用知识上下文的工作流角色，如 chapter4、chapter5、chapter6、review。 |
| Impact handoff | 将冻结上下文与影响分析结果绑定后交给实现或评审阶段的工件。 |
| Static attachment | 场景、节点、脚本或资源的静态结构证据，不代表运行时断言通过。 |
| Runtime verified | 任务级 Godot/GdUnit 断言在绑定 revision 上通过且证据完整。 |
| Inferred | 由规则或 LLM 推断、尚未获得足够确定性证据的知识记录。 |

## 15. 后续 BMad 工件顺序

1. 使用 `bmad-prd` 将本文提升为正式产品需求，补齐目标用户、用户旅程、成功指标和范围优先级；实现机制细节进入 PRD addendum，不挤入产品叙事。
2. PRD 评审通过后使用 `bmad-spec`，把能力、约束、非目标和成功信号固化为稳定 CAP ID，并将本文件的 API、迁移清单、状态机和追踪矩阵作为 companions。
3. SPEC 自校验通过后再进入架构、故事拆分和 `bmad-build`；禁止直接从本 Draft 启动全量迁移。
## 16. Actionable Deterministic Search Portability Addendum

This section records the backend search improvements validated in `newrouge` for migration into `godotgame`. Migrate algorithms, contracts, tests, and empty-directory initialization only. Do not migrate `newrouge` task IDs, game entities, business paths, query evidence, or generated data.

### 16.1 Deterministic Search Boundary

1. Project Health Knowledge queries must use deterministic machine search. They must not call an LLM or present generated text as a RAG answer.
2. Preserve existing `knowledge`, `gdd_supplements`, `impact_targets`, and formal handoff semantics. Actionable results are additive and must not relax KCP or Impact gates.
3. Score each query variant independently, including configured aliases, then merge and deduplicate. An original-language term must not dilute an alias hit; unconfigured Chinese input must not be implicitly translated.
4. CamelCase splitting, light English normalization, and path normalization must be testable pure behavior. Exact path matches must use token boundaries so longer substrings cannot produce false direct evidence.

### 16.2 Actionable Result Contract

1. The API should return `actionable_results` grouped into `tasks`, `configs`, `code`, and `tests`. Each group returns `items`, `total`, and `truncated`.
2. Each item must include `kind`, `score`, `evidence_strength`, and `reason`. Task items include the task identifier; resource items include repository-relative paths. `related_task_ids` may be added only when backed by scanned evidence.
3. Evidence strength must distinguish at least `direct`, `confirmed`, and `inferred`. Sort by evidence strength before relevance, and do not let inferred results displace direct or confirmed results from the aggregate top results.
4. Task navigation must reuse the existing task, configuration, reader, and test evidence chain. Keyword matching cannot upgrade a relation to confirmed, and Godot startup cannot count as a task assertion.
5. Bound task-navigation expansion and per-group result count. Expose truncation through `truncated` and cover the limits with backend regression tests.

### 16.3 Snapshot and Query Evidence

1. Every query response must include the scanned revision, current HEAD revision, `stale`, and a readable message. A stale snapshot remains exploratory but must not be described as current workspace truth.
2. Write query evidence under `logs/**`. Production knowledge directories contain reviewed schemas, catalogs, bindings, and reusable indexes, not runtime logs.
3. Representative backend queries must cover a feature phrase, a domain query, an exact configuration path, a configured Chinese alias, an unconfigured Chinese query, and cross-domain noise isolation.
4. Acceptance is based on Python/API backend behavior. Browser tests are optional supplementary coverage, not a required gate for this search capability.

### 16.4 Chapter 6 Integration

1. Configuration, asset, scene, reader-code, and test relations captured when Chapter 6 completes a task must be consumable by search navigation. Missing relations may only produce static or inferred results.
2. Initialization creates empty schemas, catalogs, policies, projections, and index directories only. It must not create business examples to satisfy search acceptance.
3. Before migration is considered complete, add backend regression tests for independent alias scoring, exact-path boundaries, evidence-strength ordering, stale snapshots, truncation metadata, and backward-compatible legacy fields.
