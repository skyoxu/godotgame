# ADR-0019: Godot 4.5 安全基线（Windows Only）

- Status: Accepted
- Context: 原 ADR-0002 针对 LegacyDesktopShell 的安全基线（CSP、contextIsolation 等）已不再适用。Godot 运行时与文件系统/外链策略、插件与执行模型与 LegacyDesktopShell 存在根本差异，需要建立防御性基线并与质量门禁协同。
- Decision:
  - 统一安全配置采用 `SECURITY_PROFILE`，默认值为 `host-safe`；可选值 `strict`。详细映射见 `ADR-0031-security-profile-host-safe-default.md`。
  - 文件系统与资源（所有 profile 均必须）：仅允许 `res://`（只读）与 `user://`（读写）；拒绝绝对路径与越权访问（路径规范化 + 扩展名/大小白名单）；失败统一审计（见 6.3 日志与工件）。
  - 外链与网络（所有 profile 均必须）：仅 HTTPS；主机白名单 `ALLOWED_EXTERNAL_HOSTS`；`GD_OFFLINE_MODE=1` 时拒绝所有出网并审计。
  - 代码与插件（所有 profile 均必须）：禁止运行期动态加载外部程序集/脚本；插件白名单（导出/发布剔除 dev-only 插件）；禁用远程调试与编辑器残留。
  - `OS.execute` 与权限（所有 profile 均必须）：默认禁用 `OS.execute`（或仅开发态开启并严审计）；CI/headless 下摄像头/麦克风/文件选择默认拒绝。
  - `host-safe` 口径：只保障主机与进程边界安全，不将“本地数据不可篡改”作为硬门禁；本地快照/存档异常采用“告警 + 可恢复”而非强拒绝/清空。
  - `strict` 口径：在 `host-safe` 基础上，允许项目按需增加本地完整性校验与更严格拒绝策略（例如签名/HMAC/强一致拒绝），但不作为模板默认要求。
  - 配置开关：`SECURITY_PROFILE=host-safe|strict`、`GD_SECURE_MODE=1`、`ALLOWED_EXTERNAL_HOSTS=<csv>`、`GD_OFFLINE_MODE=0/1`、`SECURITY_TEST_MODE=1`。
  - 安全烟测（CI 最小集）：外链 allow/deny/invalid 三态 + 审计文件存在；网络白名单验证；`user://` 写入成功、绝对/越权写入拒绝；权限在 headless 下默认拒绝。
- Consequences:
  - 安全相关改动必须附带就地验收（xUnit/GdUnit4）与审计产物（`logs/` 路径见 6.3）。
  - Overlay 的 08 章仅引用本基线，不复制阈值；契约与事件统一落盘 `Game.Core/Contracts/**`。
  - CI 中安全门禁按 `SECURITY_PROFILE` 解析，避免“代码想快、门禁想严”的默认冲突。
- Supersedes: ADR-0002-legacy-desktop-shell-security-baseline
- References: ADR-0031-security-profile-host-safe-default, ADR-0011-windows-only-platform-and-ci, ADR-0003-observability-release-health, docs/architecture/base/02-security-baseline-godot-v2.md
