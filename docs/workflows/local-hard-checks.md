# Local Hard Checks Workflow

本文档定义 `py -3 scripts/python/dev_cli.py run-local-hard-checks` 的使用口径。

## 目标

- 给本地开发提供一条稳定的完整硬验证入口。
- 避免手工拼接多条命令时漏掉步骤或顺序漂移。
- 避免重复执行 `run_gate_bundle.py --mode hard`，减少日志噪声和耗时。

## 适用场景

- 在提交前做一次完整本地硬验证。
- 在 PR 前确认语义 / 契约 / 单测 / 引擎侧小集都已通过。
- 在排查 CI 失败时，先本地复现仓库当前推荐顺序。

## 默认顺序

`run-local-hard-checks` 会按以下顺序执行，并在首个失败步骤处立即停止：

1. `scripts/python/run_gate_bundle.py --mode hard`
2. `scripts/python/run_dotnet.py`
3. `scripts/python/run_gdunit.py`（Adapters/Config + Security hard set，仅当提供 `--godot-bin` 时执行）
4. `scripts/python/smoke_headless.py --strict`（仅当提供 `--godot-bin` 时执行）

这条入口的核心约束是：

- `run_gate_bundle.py` 只执行一次。
- `quality_gates.py all` 不参与这条完整链路，避免再次触发 hard bundle。
- 未提供 `--godot-bin` 时，入口只执行 gate bundle + dotnet，用于无引擎环境或快速本地验证。

## 推荐命令

```powershell
# 完整本地硬验证
py -3 scripts/python/dev_cli.py run-local-hard-checks --godot-bin $env:GODOT_BIN

# 无 Godot 环境时，只跑语义 / 契约 / 单测
py -3 scripts/python/dev_cli.py run-local-hard-checks
```

## 主要参数

- `--godot-bin <path>`：提供后才会追加 GdUnit4 hard set 和 strict smoke。
- `--solution <path>`：传给 `run_dotnet.py`，默认 `Game.sln`。
- `--configuration <Debug|Release>`：传给 `run_dotnet.py`，默认 `Debug`。
- `--delivery-profile <profile>`：传给 hard gate bundle，用于控制 profile 化门禁默认值。
- `--task-file <path>`：可重复，覆盖默认 task views。
- `--out-dir <path>`：传给 hard gate bundle，覆盖默认输出目录。
- `--run-id <id>`：传给 hard gate bundle，用于稳定关联本次运行产物。
- `--timeout-sec <n>`：传给 strict smoke，默认 `5`。

## 与其他入口的区别

### `run-ci-basic`

- 目标：最小硬门入口。
- 默认只跑 `run_gate_bundle.py --mode hard`。
- 只有显式传 `--legacy-preflight` 时才追加旧的 `ci_pipeline.py`。

### `run-quality-gates`

- 目标：包装 `quality_gates.py all`。
- 默认先跑 hard gate bundle，再按需追加 `--gdunit-hard` / `--smoke`。
- 适合单独验证引擎小集，但不适合作为“完整本地硬验证”主入口，因为会和 `run_gate_bundle.py` 形成重复调用风险。

### 手工拆开执行

适合排查某个步骤失败时使用，但不应作为日常默认方式。

## 产物与日志

- hard gate bundle：`logs/ci/<YYYY-MM-DD>/gate-bundle/runs/<run-id>/hard/`
- dotnet：`logs/unit/<YYYY-MM-DD>/`
- GdUnit4 hard set：`logs/e2e/dev-cli/local-hard-checks-gdunit-hard/`
- strict smoke：`logs/ci/<YYYY-MM-DD>/smoke/<timestamp>/`

## 止损边界

- 如果你只想验证语义 / 契约门禁，不要用这条入口，直接跑 `run-ci-basic`。
- 如果你只想追加 GdUnit4 hard 或 smoke，不要用这条入口，直接跑 `run-quality-gates` 或专门子命令。
- 如果后续要继续扩展这条入口，不要再把命令构造写回 `dev_cli.py`，应优先扩展 `scripts/python/dev_cli_builders.py`。

## 相关文档

- `docs/testing-framework.md`
- `docs/workflows/gate-bundle.md`
- `DELIVERY_PROFILE.md`
