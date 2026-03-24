# workflow.example.md

## Scope

This file is the bootstrap example for a new business repo cloned from this template.

Use it during the first week after repo creation.
Use `workflow.md` for the stable daily loop after the repo is already bootstrapped.

## Day 1: Rename and make the repo runnable

1. Rename project identity and path leftovers in:
   - `README.md`
   - `AGENTS.md`
   - `docs/**`
   - `.github/**`
   - `project.godot`
2. Fix broken links and old repo names.
3. Set `GODOT_BIN` locally.
4. Run repo hard checks immediately:

```powershell
py -3 scripts/python/dev_cli.py run-local-hard-checks --godot-bin "$env:GODOT_BIN"
py -3 scripts/python/inspect_run.py --kind local-hard-checks
```

Goal:

- the cloned repo is renamed correctly
- core entry docs are usable
- no early CI-hard failures remain from template copy

## Day 2: Build the real task triplet

Create or import the real task triplet under `.taskmaster/tasks/`:

- `tasks.json`
- `tasks_back.json`
- `tasks_gameplay.json`

If view files already exist and `tasks.json` must be rebuilt:

```powershell
py -3 scripts/python/build_taskmaster_tasks.py
```

Validate the triplet:

```powershell
py -3 scripts/python/task_links_validate.py
py -3 scripts/python/check_tasks_all_refs.py
py -3 scripts/python/validate_task_master_triplet.py
```

Normalize semantic review tier early:

```powershell
py -3 scripts/python/backfill_semantic_review_tier.py --mode conservative --write
py -3 scripts/python/validate_semantic_review_tier.py --mode conservative
```

## Day 3: Generate overlays and baseline contracts

Dry-run overlays first:

```powershell
py -3 scripts/sc/llm_generate_overlays_batch.py --prd <prd-main.md> --prd-id <PRD-ID> --prd-docs <prd-extra-a.md>,<prd-extra-b.md> --page-family core --page-mode scaffold --timeout-sec 1200 --dry-run --batch-suffix first-core-dryrun
```

Then simulate:

```powershell
py -3 scripts/sc/llm_generate_overlays_batch.py --prd <prd-main.md> --prd-id <PRD-ID> --prd-docs <prd-extra-a.md>,<prd-extra-b.md> --page-family core --page-mode scaffold --timeout-sec 1200 --batch-suffix first-core-sim
```

Repair only outlier pages if needed:

```powershell
py -3 scripts/sc/llm_generate_overlays_from_prd.py --prd <prd-main.md> --prd-id <PRD-ID> --prd-docs <prd-extra-a.md>,<prd-extra-b.md> --page-filter <overlay-file.md> --page-mode scaffold --timeout-sec 1200 --run-suffix fix-page-1
```

Apply only the pages you trust:

```powershell
py -3 scripts/sc/llm_generate_overlays_batch.py --prd <prd-main.md> --prd-id <PRD-ID> --prd-docs <prd-extra-a.md>,<prd-extra-b.md> --pages _index.md,ACCEPTANCE_CHECKLIST.md,08-rules-freeze-and-assertion-routing.md --page-mode scaffold --timeout-sec 1200 --apply --batch-suffix apply-core
```

Freeze overlay refs:

```powershell
py -3 scripts/python/sync_task_overlay_refs.py --prd-id <PRD-ID> --write
py -3 scripts/python/validate_overlay_execution.py --prd-id <PRD-ID>
```

Baseline contract checks:

```powershell
py -3 scripts/python/validate_contracts.py
py -3 scripts/python/check_domain_contracts.py
dotnet test Game.Core.Tests/Game.Core.Tests.csproj
```

## Day 4+: Start real task execution

Default daily mode: `fast-ship`

Continue a task:

```powershell
py -3 scripts/python/dev_cli.py resume-task --task-id <id>
```

Create an execution plan only when the task is long-running or cross-cutting:

```powershell
py -3 scripts/python/dev_cli.py new-execution-plan --title "<topic>" --task-id <id>
```

TDD preflight:

```powershell
py -3 scripts/sc/check_tdd_execution_plan.py --task-id <id> --tdd-stage red-first --verify unit --execution-plan-policy draft
```

Generate failing tests:

```powershell
py -3 scripts/sc/llm_generate_tests_from_acceptance_refs.py --task-id <id> --tdd-stage red-first --verify unit
```

Green:

```powershell
py -3 scripts/sc/build.py tdd --task-id <id> --stage green
```

Refactor:

```powershell
py -3 scripts/sc/build.py tdd --task-id <id> --stage refactor
```

Unified review pipeline:

```powershell
py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin "$env:GODOT_BIN" --delivery-profile fast-ship
```

If `Needs Fix` appears and is actionable:

```powershell
py -3 scripts/sc/llm_review_needs_fix_fast.py --task-id <id> --max-rounds 1 --rerun-failing-only --time-budget-min 20 --agents code-reviewer,test-automator,semantic-equivalence-auditor
```

Before commit or PR:

```powershell
py -3 scripts/python/dev_cli.py run-local-hard-checks --godot-bin "$env:GODOT_BIN"
py -3 scripts/python/inspect_run.py --kind local-hard-checks
```

## When to use heavier lanes

Use the semantics stabilization lane only when:

- acceptance is weak or drifting
- refs are placeholders
- subtasks are not clearly covered
- repeated `Needs Fix` points back to task semantics instead of code

Use `standard` profile only when:

- the task is risky or cross-cutting
- contracts or architecture boundaries changed
- you are converging before PR or milestone freeze

## Stop-Loss

- Do not use `examples/taskmaster/**` as the business repo SSoT.
- Do not start overlays before the real triplet exists.
- Do not run heavy obligations freeze tooling by default.
- Do not recover from chat history before reading sidecars.
- Do not force `host-safe` on `standard` unless you intentionally want that override.
- Do not hand-stitch test + acceptance + llm review when `run_review_pipeline.py` already exists.
