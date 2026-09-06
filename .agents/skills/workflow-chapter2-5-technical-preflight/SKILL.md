---
name: workflow-chapter2-5-technical-preflight
description: Run the fixed Chapter 2.5 technical preflight workflow before Chapter 3 task generation. Use when GDD, prototype, or task text may imply engine/backend/platform feasibility work, physics backend choice, plugin adoption, Web/WASM constraints, deterministic physics, rendering, networking, save, or performance feasibility decisions.
---

# Workflow Chapter 2.5 Technical Preflight

## Role

Operate Chapter 2.5 from `workflow.md` idempotently for a business repository that is a sibling of the template repository.

## Operating Contract

- Treat `workflow.md` as the normative workflow source.
- Treat business-repo logs as empirical evidence, not policy overrides.
- Use Python with UTF-8 for documentation reads and writes.
- Keep generated code, scripts, tests, comments, and log messages in English.
- Do not modify the business repo unless the user explicitly asks for that change.
- Do not rerun expensive steps before reading existing recovery artifacts.


## Repository Layout

Template and business repositories are siblings under one parent directory, for example `<parent>/godotgame`, `<parent>/<business-repo-a>`, and `<parent>/<business-repo-b>`.

## Purpose

Use this skill to turn GDD, prototype, task, and optional capability-snapshot signals into a recommendation-only technical route before Chapter 3 creates formal tasks.

## Default Lane

Run a recommendation-only technical preflight after Chapter 2 repository bootstrap and before Chapter 3 task generation whenever engine, backend, plugin, platform, or feasibility signals are present. Do not install plugins, edit project.godot, or create final tasks in Chapter 2.5.

## Primary Command Or Action

`py -3 scripts/python/dev_cli.py run-technical-preflight --source <docs/prototypes-or-gdd-file.md> --source-kind auto --out-json logs/ci/technical-preflight/summary.json`

## Evidence Rule

Chapter 2.5 is a read-only feasibility routing pass. Use the source document text, optional capability snapshot, and generated technical-preflight summary as evidence; do not treat old summaries as reusable unless explicitly selected for the current Chapter 3 run.

## Required Reading

1. Read `docs/workflows/chapter2-5-technical-preflight.md`.
2. Read the Chapter 2 and Chapter 3 boundary sections in `workflow.md` to preserve the order: bootstrap, technical preflight, then task generation.
3. Read `docs/workflows/chapter3-7-component-routing.md` when Chapter 3 will consume an engine spike hint.
4. Refresh this skill with `py -3 scripts/python/update_workflow_chapter_skills.py <repo>` when the Chapter 2.5 workflow document changes.

## Idempotent Procedure

1. Identify the current GDD, prototype record, or task source that may contain technical feasibility signals.
2. Run run-technical-preflight through dev_cli with --source-kind auto unless the source kind is already known.
3. Pass --capability-snapshot only when a current Chapter 2 capability snapshot exists; review capability_snapshot_status when it is missing or invalid.
4. Use --recommendation-only for quick triage, and use --out-json logs/ci/technical-preflight/summary.json when Chapter 3 may consume the result.
5. Treat no_engine_change as a hard instruction to avoid adding engine tasks.
6. Treat use_default_backend as permission to use Godot's default backend without an ADR unless later implementation evidence proves it insufficient.
7. Treat engine_spike_required as a request for a spike-shaped task in Chapter 3, not as permission to install plugins or edit project.godot.
8. When Chapter 3 should consume the result, pass --technical-preflight <summary.json> explicitly to enrich_task_candidates.py or run_chapter3_regression_check.py.
9. Record plugin or global backend changes in Chapter 4 ADR or decision-log only after spike evidence supports the change.

## Output Contract

- Output schema is `technical-preflight.v1`.
- `source.path` is resolved by the CLI so downstream repo matching can avoid stale summaries.
- `technical_preflight.engine_route.recommended_action` is one of `no_engine_change`, `use_default_backend`, or `engine_spike_required`.
- Chapter 2.5 is `recommend_only`; it must not install plugins, modify project.godot, or write final Taskmaster triplets.

## User Interaction Requirements

- Ask the user in Chinese only when the current source document cannot be identified from the repository.
- Keep commands, file paths, script names, schema values, and logs in English.
- If the user asks whether an engine should be used, answer from the current technical-preflight route and clearly separate recommendation from implementation permission.


## Stop-Loss Signals

- Existing `forbidden_commands` blocks the command about to be run.
- `artifact_integrity`, `planned_only_incomplete`, or planned-only run type appears in recovery evidence.
- Route evidence recommends inspect-first, record-residual, fix-deterministic, repo-noise-stop, or pause.
- The same deterministic failure fingerprint appears repeatedly.
- The next action would duplicate work already covered by task, overlay, candidate, or manifest evidence.

## Business Evidence References

Generated evidence may live under `references/business-repos/<repo>.md`. These files are optional regression evidence from known business repositories; they must not define production generation rules.

## Maintenance

Refresh optional evidence after new business-repo logs are generated:

```powershell
py -3 scripts/python/update_workflow_chapter_skills.py <business-repo>
py -3 scripts/python/update_workflow_chapter_skills.py <business-repo-a>,<business-repo-b>
```
