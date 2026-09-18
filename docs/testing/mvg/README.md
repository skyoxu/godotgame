# MVG integration manifests

This template intentionally ships with **no business MVG manifest** and no task IDs.

Create a project-specific manifest only after the project has real flows, contracts, tests, and Taskmaster data. The reusable runner accepts a repository-relative manifest:

```powershell
py -3 scripts/python/dev_cli.py run-mvg-acceptance --manifest docs/testing/mvg/<project>.json --mode plan
py -3 scripts/python/dev_cli.py run-mvg-acceptance --manifest docs/testing/mvg/<project>.json --mode recommend --base origin/main
py -3 scripts/python/dev_cli.py run-mvg-acceptance --manifest docs/testing/mvg/<project>.json --mode run --snapshot commit --revision HEAD --godot-bin $env:GODOT_BIN
```

The schema is `godotgame.mvg-integration.v1`.

Each manifest contains non-empty `flows` and `tests`. Every flow requires non-empty `task_ids` that resolve against `.taskmaster/tasks/tasks.json`. Every handoff requires `producer_task`, `consumer_task`, and `owner_task`, all owned by that flow. The reusable template stays empty by shipping no production MVG manifest; CI injects minimal neutral Taskmaster data only inside a temporary runtime smoke.

Supported test evidence levels are:

- dotnet: `domain-integration`
- gdunit: `scene-method` or `engine-input`

A planned test may be absent during `plan`; `run` requires every test to be implemented and present. The runner never writes task status.

Optional negative wiring challenges are declared on a test as an object with a stable `id`, string environment variables under `env`, and `expected_failure_contains`. They run only with `--challenge-input` after the baseline succeeds. A timeout, missing runtime, or compilation failure does not count as detecting the seeded defect.

## Impact recommendation boundary

The recommendation layer compares changed Git paths with explicit manifest source, contract, and test paths. It is positive evidence only:

- a fully mapped change can produce `related-first`;
- any unmapped path, empty/unknown change range, or unavailable Git comparison produces `full-mvg`;
- `required_tests` always contains the complete manifest test inventory;
- `authorizes_test_exclusion` is always false.

This does not replace the formal revision-bound Impact Index or Knowledge Control Plane.

## Optional mutation experiment

The template also provides a parameterized mutation probe:

```powershell
py -3 scripts/python/run_mvg_mutation_probe.py --spec docs/testing/mvg/<project>-mutation.json --snapshot commit --revision HEAD
```

The mutation spec schema is `godotgame.mvg-mutation-probe.v1` and supplies one source path, one focused dotnet test, and explicit before/after mutations. No mutation targets are shipped by the template. The probe first requires a passing baseline, restores source bytes between mutants, and reports `killed`, `survived`, or `unverified`. It is not a default quality gate or a whole-program mutation score.
