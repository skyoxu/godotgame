# Claude Subagents 配置说明

本项目已安装以下 Subagents 用于自动化代码质量保证和架构验收。

## 已安装的 Subagents

### 项目特定 Subagents（2个）

这些 Subagents 是专门为本项目定制的，针对项目的 ADR 和质量标准进行验收。

#### 1. adr-compliance-checker
- **位置**: `.claude/agents/adr-compliance-checker.md`
- **模型**: Sonnet
- **职责**: ADR 合规性验证
- **检查项**:
  - ADR-0002: 安全基线（路径使用、外链白名单、配置开关）
  - ADR-0004: 事件契约（命名规范、CloudEvents 字段、契约位置）
  - ADR-0005: 质量门禁（覆盖率、重复度、测试通过）
  - ADR-0011: Windows-only 策略（文档标注、禁止跨平台抽象）
- **使用方式**:
  ```
  Use adr-compliance-checker to verify task 1.1
  ```

#### 2. performance-slo-validator
- **位置**: `.claude/agents/performance-slo-validator.md`
- **模型**: Haiku
- **职责**: 性能 SLO 验证
- **检查项**:
  - 启动时间 ≤3s
  - 帧耗时 P95 ≤16.6ms (60 FPS)
  - 初始内存 ≤500MB
  - 峰值内存 ≤1GB
  - 内存增长率 ≤5% /小时
- **数据来源**: `logs/perf/<latest>/summary.json`
- **使用方式**:
  ```
  Use performance-slo-validator to check latest perf results
  ```

### 社区 Subagents（需要单独安装）

以下 4 个 Subagents 来自 lst97 社区，需要安装到全局目录 `~/.claude/agents/lst97/`：

#### 3. architect-reviewer
- **职责**: 架构一致性审查
- **检查项**: SOLID 原则、依赖方向、循环依赖、抽象层次

#### 4. code-reviewer
- **职责**: 代码质量审查
- **检查项**: 安全漏洞、SOLID 原则、测试覆盖、性能优化

#### 5. security-auditor
- **职责**: 安全审计
- **检查项**: OWASP Top 10、威胁建模、加密实现、依赖漏洞

#### 6. test-automator
- **职责**: 测试质量验证
- **检查项**: 测试金字塔比例、覆盖率门禁、测试确定性

## 自定义命令

### /acceptance-check
- **位置**: `.claude/commands/acceptance-check.md`
- **职责**: 执行多 Subagent 协作的综合架构验收
- **工作流**: 并行调用 6 个 Subagents 进行全面验收
- **使用方式**:
  ```bash
  /acceptance-check 1.1
  /acceptance-check 2.3
  ```

### Godot 开发命令（4个）

这些命令专门用于 Godot 4.x + C# 项目的快速开发，遵循三层架构（Core / Adapter / Scene）。

#### /godot-component
- **位置**: `.claude/commands/godot-component.md`
- **职责**: 创建完整的 Godot 组件（场景 + 脚本 + 测试）
- **参数**: `<组件名称> [节点类型] [层级]`
- **层级选项**:
  - `UI`: UI 组件（Control 节点）
  - `Core`: 纯 C# 业务逻辑（无引擎依赖）
  - `Adapter`: Godot API 封装层
  - `Scene`: 游戏场景组件
- **功能**:
  - 创建场景文件（.tscn）
  - 创建对应 C# 脚本（带命名空间和 XML 注释）
  - 创建测试文件骨架（xUnit for Core/Adapter, GdUnit4 for UI/Scene）
  - ADR 合规性自检
- **使用方式**:
  ```bash
  /godot-component GuildPanel
  /godot-component InventoryManager Node Core
  /godot-component PlayerInput Control UI
  ```

#### /godot-scene
- **位置**: `.claude/commands/godot-scene.md`
- **职责**: 创建 Godot 场景文件（.tscn）
- **参数**: `<场景名称> [根节点类型] [目标目录]`
- **默认设置**:
  - 根节点类型: `Control`
  - 目标目录: `Game.Godot/Scenes/`
- **功能**:
  - 生成标准 .tscn 文件结构
  - 设置合理的默认属性
  - 引用相关 ADR（ADR-0004, ADR-0006, ADR-0007）
- **使用方式**:
  ```bash
  /godot-scene MainMenu
  /godot-scene GameWorld Node2D Game.Godot/Scenes/World/
  ```

#### /godot-script
- **位置**: `.claude/commands/godot-script.md`
- **职责**: 创建 Godot C# 脚本（带层级感知）
- **参数**: `<脚本名称> [基类] [层级] [命名空间]`
- **层级模板**:
  - `Core`: 纯 C# 类（无 Godot 依赖）
  - `Adapter`: 接口实现（封装 Godot API）
  - `UI/Scene`: Godot 节点类（带 Signals 和 Exports）
- **功能**:
  - 生成带 XML 注释的 C# 代码
  - 自动设置命名空间
  - 包含 Godot 生命周期方法（_Ready, _Process）
  - 遵循项目命名规范（PascalCase/camelCase）
- **使用方式**:
  ```bash
  /godot-script GuildService Node Core
  /godot-script TimeAdapter Control Adapter
  /godot-script HealthBar Control UI
  ```

#### /gm-0101-eventengine
- **位置**: `.claude/commands/gm-0101-eventengine.md`
- **职责**: EventEngine Core 实现指引（任务特定）
- **适用场景**: 实现 Guild Manager 的事件引擎核心逻辑
- **约束**:
  - 仅修改白名单内的文件
  - 保持 Game.Core 层纯粹（零 Godot 依赖）
  - 遵循 ADR-0004 事件命名规范
  - TDD 驱动开发（xUnit 测试先行）
- **支持的事件**:
  - `core.guild.created`
  - `core.guild.member.joined`
  - `core.guild.member.left`
- **使用方式**:
  ```bash
  /gm-0101-eventengine
  ```

### 命令关系

```
/godot-component          (组合命令)
    ├── /godot-scene      (创建场景)
    └── /godot-script     (创建脚本)
```

**建议工作流**:
1. 使用 `/godot-component` 快速创建完整组件
2. 需要单独创建场景或脚本时，使用 `/godot-scene` 或 `/godot-script`
3. 实现特定任务（如 EventEngine）时，参考对应指引（如 `/gm-0101-eventengine`）

## 验证安装

检查所有文件是否正确安装：

```powershell
# 检查项目特定 Subagents
Test-Path .claude/agents/adr-compliance-checker.md
Test-Path .claude/agents/performance-slo-validator.md

# 检查自定义命令
Test-Path .claude/commands/acceptance-check.md

# 检查权限配置
Test-Path .claude/settings.local.json
```

## 权限说明

`settings.local.json` 已配置以下权限：

- **Skills**: test-driven-development, systematic-debugging
- **MCP 工具**: serena, context7, task-master-ai
- **Git 操作**: push, pr create, merge, add, commit
- **测试工具**: dotnet test, py 脚本
- **SuperClaude 命令**: /sc:build, /sc:test, /sc:help, /sc:git
- **验收命令**: /acceptance-check
- **Coverage 门禁**: 支持环境变量和 override 机制

## 最佳实践

- 完成任务后，标记 `done` 之前运行 `/acceptance-check`
- 重构后验证架构一致性
- 提交 PR 前最终检查
- 发布前质量守门

## 更新日志

- 2025-12-11: 从 newguild 项目迁移配置
  - 添加 2 个项目特定 Subagents
  - 添加 /acceptance-check 命令
  - 合并权限配置（从 17 条扩展到 84 条）
