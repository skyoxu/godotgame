# MVG integration acceptance

MVG integration acceptance verifies that multiple implemented capabilities still compose into a bounded, observable game flow on one version. It supplements existing Chapter 3–7 responsibilities and does not create a second task-status system.

## Responsibilities by phase

| Phase | MVG supplement |
| --- | --- |
| Chapter 3 | Assign integration responsibility to existing tasks when task data exists. Add a new integration task only when no existing task owns the handoff. |
| Chapter 4 | Record producer/consumer contract boundaries, observable behavior, and integration-test responsibility. |
| Chapter 5 | Stabilize planned test semantics and acceptance references. |
| Chapter 6 | Implement flow tests incrementally; for MVG closure run the full manifest against one isolated snapshot. |
| Chapter 7 | For critical UI flows prefer real scenes, engine input, bounded state waits, and cleanup. Keep scene-method and engine-input evidence distinct. |

A fresh template contains no MVG business manifest. Once a project creates one, task ownership is mandatory: each flow binds real Taskmaster IDs and every handoff names a producer, consumer, and owner. See `docs/testing/mvg/README.md` for the reusable schema.

## Coverage scope contract

Every project manifest declares whether it is a `pilot`, `critical`, or `full` scope. It also records a stable `scope_id`, the exact ordered flow inventory, scoped non-done Taskmaster blockers, and explicit excluded claims. This separates "all tests in this manifest ran" from "the project's complete MVG scope is covered."

The template ships no critical/full business inventory. Its temporary neutral runtime smoke is a `pilot` only. Projects define their own critical/full flows after real Taskmaster, contracts, and tests exist. Executable critical/full scopes fail closed until every scoped task is `done`.

## Evidence contract

The runner creates `logs/ci/mvg-acceptance/<run-id>/summary.json` and raw test evidence. A runtime run is verified only when every required manifest test:

- executes from the same isolated commit/workspace snapshot;
- matches the exact dotnet class or GdUnit suite identity;
- produces a parseable, non-empty report;
- has internally consistent test counts and no duplicate result identities;
- reaches the declared minimum test count;
- has zero failed and zero skipped cases;
- exits successfully.

Missing reports, malformed XML, suite/setup errors, wrong selection, count mismatch, duplicates, timeouts, or process-launch failures block verification. Planning/recommendation never sets `runtime_verified=true`, and no mode authorizes task-status writes.

Only the first successful GdUnit suite in one snapshot performs prewarm. Later suites and negative wiring challenges reuse that prepared build while keeping independent processes and reports.

## Version-bound impact recommendation

`--mode recommend --base <ref>` compares Git paths against explicit manifest source paths, contract references, and integration test paths. Commit mode reads the manifest from `--revision` and compares to that revision without mixing current workspace changes. Workspace mode explicitly records that working changes are included.

The recommendation is deliberately conservative. Unknown paths, missing mappings, empty change sets, or unavailable Git ranges force `full-mvg`. Here `full-mvg` means every required test in the selected manifest, not automatic product-wide coverage. Recommendation output carries `manifest_coverage_mode`, `manifest_scope_id`, and `manifest_blocking_task_ids`. Even `related-first` is only ordering guidance: all manifest tests stay in `required_tests`, and the current run mode executes all of them. This layer is not a call graph and does not replace formal Impact/KCP analysis.

## Commands

```powershell
py -3 scripts/python/dev_cli.py run-mvg-acceptance --manifest docs/testing/mvg/<project>.json --mode plan
py -3 scripts/python/dev_cli.py run-mvg-acceptance --manifest docs/testing/mvg/<project>.json --mode recommend --base origin/main
py -3 scripts/python/dev_cli.py run-mvg-acceptance --manifest docs/testing/mvg/<project>.json --mode run --snapshot commit --revision HEAD --godot-bin $env:GODOT_BIN --challenge-input
```

For uncommitted development, use `--snapshot workspace`. Workspace evidence must not be represented as verification of a commit.

The optional parameterized mutation probe is documented in `docs/testing/mvg/README.md`; it is an experiment, not a default gate.

## CI

`.github/workflows/mvg-integration.yml` always runs neutral framework regressions plus a real end-to-end MVG runtime smoke. The smoke temporarily injects neutral Taskmaster, dotnet, and GdUnit fixtures, executes the same isolated runner used by projects, then restores the checkout. Project-specific runtime remains opt-in through workflow-dispatch inputs `manifest`, `challenge_input`, and `mutation_spec`; those inputs are passed through environment variables rather than interpolated into PowerShell source.
