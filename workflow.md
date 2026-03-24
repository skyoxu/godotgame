# workflow.md

## 0. Scope

This is the daily executable workflow for this repository.

- OS: Windows
- Shell: PowerShell
- Python launcher: `py -3`
- Commands below are single-line PowerShell-safe commands.
- Real project task files must live under `.taskmaster/tasks/`.
- `examples/taskmaster/**` is template fallback only.
- The default task-level entrypoint is `scripts/sc/run_review_pipeline.py`.
- Do not hand-stitch `scripts/sc/test.py + scripts/sc/acceptance_check.py + scripts/sc/llm_review.py` in normal work.

## 1. Global Rules

### 1.1 Recovery first

Recover in this order:

1. Read `AGENTS.md` and `docs/agents/00-index.md`.
2. If present, read `logs/ci/active-tasks/task-<id>.active.md`.
3. Run `py -3 scripts/python/dev_cli.py resume-task --task-id <id>`.
4. Only when the recovery summary is insufficient, run `py -3 scripts/python/inspect_run.py --kind pipeline --task-id <id>`.

### 1.2 Delivery profile first

Choose a delivery profile before large or repeated work.

- `playable-ea`: fastest playable validation
- `fast-ship`: default daily mode
- `standard`: tighter convergence mode

Default security mapping:

- `playable-ea` -> `host-safe`
- `fast-ship` -> `host-safe`
- `standard` -> `strict`

Reference: `DELIVERY_PROFILE.md`

### 1.3 Serena is an accelerator, not a blocker

Use Serena MCP when you need symbol lookup, reference tracing, or safer refactor context.
If Serena is unavailable, continue with the deterministic toolchain.
Optional local notes can be written to `taskdoc/<id>.md` in UTF-8.

### 1.4 Prototype work stays outside the formal task loop

If the work is still exploratory and not ready for formal Taskmaster tracking, use the prototype lane first.
Reference: `docs/workflows/prototype-lane.md`

## 2. Phase 0: Repository Bootstrap

Run this after creating a new repo from the template.

### 2.1 Clean naming and path leftovers

Update at minimum:

- `README.md`
- `AGENTS.md`
- `docs/**`
- `.github/**`
- `project.godot`
- workflow names, release names, project paths, PRD ids

Goal:

- no old repo names left behind
- no old legacy stack language left behind
- no broken entry links

### 2.2 Rebuild entry indexes

Verify these entry documents point to the new repo state:

- `README.md`
- `AGENTS.md`
- `docs/PROJECT_DOCUMENTATION_INDEX.md`
- `docs/agents/00-index.md`

### 2.3 Run repository hard checks immediately

Do not wait until commit time.

```powershell
py -3 scripts/python/dev_cli.py run-local-hard-checks --godot-bin "$env:GODOT_BIN"
py -3 scripts/python/inspect_run.py --kind local-hard-checks
```

## 3. Phase 1: Task Triplet Bootstrap

### 3.1 Prepare planning inputs

Prepare PRD, GDD, and any supporting traceability or rules documents needed by the project.

### 3.2 Build the authoritative triplet

Normal real-project shape:

- `.taskmaster/tasks/tasks.json`
- `.taskmaster/tasks/tasks_back.json`
- `.taskmaster/tasks/tasks_gameplay.json`

If `tasks_back.json` / `tasks_gameplay.json` already exist and you need to rebuild `tasks.json`, run:

```powershell
py -3 scripts/python/build_taskmaster_tasks.py
```

### 3.3 Validate the triplet baseline

```powershell
py -3 scripts/python/task_links_validate.py
py -3 scripts/python/check_tasks_all_refs.py
py -3 scripts/python/validate_task_master_triplet.py
```

### 3.4 Normalize semantic review tier early

Recommended default:

```powershell
py -3 scripts/python/backfill_semantic_review_tier.py --mode conservative --write
py -3 scripts/python/validate_semantic_review_tier.py --mode conservative
```

Use `conservative` by default. Do not materialize effective profile defaults unless you intentionally want to write them into task views.

## 4. Phase 2: Overlays and Contracts Baseline

### 4.1 Generate overlay skeletons only after the triplet is valid

Recommended order:

1. batch dry-run
2. batch simulate
3. single-page repair for outliers
4. limited apply

Batch dry-run:

```powershell
py -3 scripts/sc/llm_generate_overlays_batch.py --prd <prd-main.md> --prd-id <PRD-ID> --prd-docs <prd-extra-a.md>,<prd-extra-b.md> --page-family core --page-mode scaffold --timeout-sec 1200 --dry-run --batch-suffix first-core-dryrun
```

Batch simulate:

```powershell
py -3 scripts/sc/llm_generate_overlays_batch.py --prd <prd-main.md> --prd-id <PRD-ID> --prd-docs <prd-extra-a.md>,<prd-extra-b.md> --page-family core --page-mode scaffold --timeout-sec 1200 --batch-suffix first-core-sim
```

Single-page repair:

```powershell
py -3 scripts/sc/llm_generate_overlays_from_prd.py --prd <prd-main.md> --prd-id <PRD-ID> --prd-docs <prd-extra-a.md>,<prd-extra-b.md> --page-filter <overlay-file.md> --page-mode scaffold --timeout-sec 1200 --run-suffix fix-page-1
```

Limited apply:

```powershell
py -3 scripts/sc/llm_generate_overlays_batch.py --prd <prd-main.md> --prd-id <PRD-ID> --prd-docs <prd-extra-a.md>,<prd-extra-b.md> --pages _index.md,ACCEPTANCE_CHECKLIST.md,08-rules-freeze-and-assertion-routing.md --page-mode scaffold --timeout-sec 1200 --apply --batch-suffix apply-core
```

Stop-loss:

- do not apply everything in the first pass
- do not mutate acceptance in the same step
- keep this phase overlay-only

### 4.2 Freeze overlay refs after apply

```powershell
py -3 scripts/python/sync_task_overlay_refs.py --prd-id <PRD-ID> --write
py -3 scripts/python/validate_overlay_execution.py --prd-id <PRD-ID>
py -3 scripts/python/check_tasks_all_refs.py
py -3 scripts/python/validate_task_master_triplet.py
```

### 4.3 Create or adjust contract skeletons

Use:

- `docs/workflows/contracts-template-v1.md`
- `docs/workflows/templates/contracts-event-template-v1.md`
- `docs/workflows/templates/contracts-dto-template-v1.md`
- `docs/workflows/templates/contracts-interface-template-v1.md`

Rules:

- contracts live under `Game.Core/Contracts/**`
- no Godot dependency in contracts
- XML docs are required
- overlays must link back to contract paths

### 4.4 Contract baseline freeze

```powershell
py -3 scripts/python/validate_contracts.py
py -3 scripts/python/check_domain_contracts.py
dotnet test Game.Core.Tests/Game.Core.Tests.csproj
```

## 5. Phase 3: Conditional Semantics Stabilization

This phase is conditional. Do not run it for every task.

Enter this phase only when acceptance quality is clearly weak, refs are drifting, subtasks are not obviously covered, or repeated `Needs Fix` points back to semantics rather than code.

### 5.1 Per-task light lane

Extract obligations:

```powershell
py -3 scripts/sc/llm_extract_task_obligations.py --task-id <id> --delivery-profile fast-ship --reuse-last-ok --explain-reuse-miss
```

Align acceptance semantics:

```powershell
py -3 scripts/sc/llm_align_acceptance_semantics.py --task-ids <id> --apply --strict-task-selection
```

Check subtasks coverage:

```powershell
py -3 scripts/sc/llm_check_subtasks_coverage.py --task-id <id> --strict-view-selection
```

Run batch semantic gate for a small set:

```powershell
py -3 scripts/sc/llm_semantic_gate_all.py --task-ids <id> --max-needs-fix 0 --max-unknown 3
```

Fill acceptance refs dry-run:

```powershell
py -3 scripts/sc/llm_fill_acceptance_refs.py --task-id <id>
```

Write back refs:

```powershell
py -3 scripts/sc/llm_fill_acceptance_refs.py --task-id <id> --write
```

Verify convergence:

```powershell
py -3 scripts/sc/llm_fill_acceptance_refs.py --task-id <id>
```

### 5.2 Batch instability lane

Use only when multiple tasks show unstable obligations extraction.

```powershell
py -3 scripts/python/run_obligations_jitter_batch5x3.py --task-ids 1,2,3 --batch-size 3 --rounds 3 --timeout-sec 420 --garbled-gate on --auto-escalate on --escalate-max-runs 3 --max-schema-errors 5 --reuse-last-ok --explain-reuse-miss
```

```powershell
py -3 scripts/python/run_obligations_freeze_pipeline.py --task-ids 1,2,3 --batch-size 3 --rounds 3 --timeout-sec 420 --garbled-gate on --auto-escalate on --reuse-last-ok --explain-reuse-miss
```

Do not promote a freeze baseline by default.

## 6. Phase 4: Single Task Daily Loop

This is the main daily path.

### 6.1 Recover state first

```powershell
py -3 scripts/python/dev_cli.py resume-task --task-id <id>
```

Only when needed:

```powershell
py -3 scripts/python/inspect_run.py --kind pipeline --task-id <id>
```

First files to read in a failed or resumed run:

- `summary.json`
- `execution-context.json`
- `repair-guide.json`
- `repair-guide.md`
- `agent-review.json`
- `run-events.jsonl`
- `logs/ci/active-tasks/task-<id>.active.md`

### 6.2 Create recovery documents only when justified

Execution plan:

```powershell
py -3 scripts/python/dev_cli.py new-execution-plan --title "<topic>" --task-id <id>
```

Decision log:

```powershell
py -3 scripts/python/dev_cli.py new-decision-log --title "<topic>" --task-id <id>
```

Use these only when they improve recovery or make a real tradeoff auditable.

### 6.3 TDD preflight decision

Recommended default:

```powershell
py -3 scripts/sc/check_tdd_execution_plan.py --task-id <id> --tdd-stage red-first --verify unit --execution-plan-policy draft
```

### 6.4 Red stage

Unit-focused red-first:

```powershell
py -3 scripts/sc/llm_generate_tests_from_acceptance_refs.py --task-id <id> --tdd-stage red-first --verify unit
```

Mixed `.cs` + `.gd` or Godot-aware verification:

```powershell
py -3 scripts/sc/llm_generate_tests_from_acceptance_refs.py --task-id <id> --tdd-stage red-first --verify auto --godot-bin "$env:GODOT_BIN"
```

### 6.5 Green stage

```powershell
py -3 scripts/sc/build.py tdd --task-id <id> --stage green
```

### 6.6 Refactor stage

```powershell
py -3 scripts/sc/build.py tdd --task-id <id> --stage refactor
```

`build.py tdd` already runs task preflight, `sc-analyze`, and required task-context validation.

### 6.7 Unified task-level review pipeline

Daily default:

```powershell
py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin "$env:GODOT_BIN" --delivery-profile fast-ship
```

Heavier convergence:

```powershell
py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin "$env:GODOT_BIN" --delivery-profile standard
```

Fast playable validation:

```powershell
py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin "$env:GODOT_BIN" --delivery-profile playable-ea
```

Notes:

- the default template is already `scripts/sc/templates/llm_review/bmad-godot-review-template.txt`
- do not pass `--security-profile` unless you want to override the default mapping
- this pipeline writes sidecars, latest pointers, active-task summaries, repair guidance, and technical debt sync outputs

### 6.8 Needs Fix cleanup

Daily quick cleanup:

```powershell
py -3 scripts/sc/llm_review_needs_fix_fast.py --task-id <id> --max-rounds 1 --rerun-failing-only --time-budget-min 20 --agents code-reviewer,test-automator,semantic-equivalence-auditor
```

Standard cleanup:

```powershell
py -3 scripts/sc/llm_review_needs_fix_fast.py --task-id <id> --max-rounds 2 --rerun-failing-only --time-budget-min 30
```

Security-sensitive cleanup:

```powershell
py -3 scripts/sc/llm_review_needs_fix_fast.py --task-id <id> --security-profile strict --max-rounds 2 --rerun-failing-only --time-budget-min 45 --agents code-reviewer,security-auditor,test-automator,semantic-equivalence-auditor
```

### 6.9 Commit-time repository verification

```powershell
py -3 scripts/python/dev_cli.py run-local-hard-checks --godot-bin "$env:GODOT_BIN"
py -3 scripts/python/inspect_run.py --kind local-hard-checks
```

## 7. Profile Quick Guide

### 7.1 playable-ea

Use when the primary goal is playable validation.

```powershell
py -3 scripts/sc/check_tdd_execution_plan.py --task-id <id> --tdd-stage red-first --verify unit --execution-plan-policy warn
py -3 scripts/sc/llm_generate_tests_from_acceptance_refs.py --task-id <id> --tdd-stage red-first --verify unit
py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin "$env:GODOT_BIN" --delivery-profile playable-ea
```

### 7.2 fast-ship

Use for normal daily work. This is the default recommendation.

```powershell
py -3 scripts/sc/check_tdd_execution_plan.py --task-id <id> --tdd-stage red-first --verify unit --execution-plan-policy draft
py -3 scripts/sc/llm_generate_tests_from_acceptance_refs.py --task-id <id> --tdd-stage red-first --verify unit
py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin "$env:GODOT_BIN" --delivery-profile fast-ship
```

### 7.3 standard

Use for cross-cutting, risky, or pre-PR convergence work.

```powershell
py -3 scripts/sc/check_tdd_execution_plan.py --task-id <id> --tdd-stage red-first --verify auto --execution-plan-policy draft
py -3 scripts/sc/llm_generate_tests_from_acceptance_refs.py --task-id <id> --tdd-stage red-first --verify auto --godot-bin "$env:GODOT_BIN"
py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin "$env:GODOT_BIN" --delivery-profile standard
```

## 8. Stop-Loss Rules

- Do not start overlays before the task triplet is valid.
- Do not run the heavy obligations freeze toolchain by default.
- Do not recover from chat history before reading sidecars.
- Do not force `--security-profile host-safe` on `standard`; let it derive to `strict` unless you intentionally override it.
- Do not invent a `--dry-run` flag for `llm_fill_acceptance_refs.py`; dry-run is simply the mode without `--write`.
- Do not block the whole task only because Serena is temporarily unavailable.
- Do not delay `run-local-hard-checks` until the end of a new repo migration.

## 9. Best Default

For most real work in this repository, use this default path:

1. `fast-ship`
2. `resume-task` when continuing work
3. `check_tdd_execution_plan.py --execution-plan-policy draft`
4. `llm_generate_tests_from_acceptance_refs.py --tdd-stage red-first`
5. `build.py tdd --stage green`
6. `build.py tdd --stage refactor`
7. `run_review_pipeline.py --delivery-profile fast-ship`
8. `llm_review_needs_fix_fast.py` only when the pipeline produces actionable `Needs Fix`
9. `run-local-hard-checks` before commit or PR
