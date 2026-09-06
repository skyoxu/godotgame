# Workflow Source Summary: Chapter 2.5 Technical Preflight

Generated from `docs/workflows/chapter2-5-technical-preflight.md` by `scripts/python/update_workflow_chapter_skills.py`.

- Source line span: 1-109
- Heading count: 7
- Command-like line count: 3
- Artifact/reference line count: 10

## Headings

- Chapter 2.5 Technical Preflight
- Position
- Stable Entrypoint
- Output Contract
- Routing Rules
- Hard Boundaries
- Promotion To Formal Work

## Command And Artifact Signals

- `py -3 scripts/python/dev_cli.py run-technical-preflight --source docs/prototypes/<file>.md --source-kind prototype --recommendation-only`
- `py -3 scripts/python/dev_cli.py run-technical-preflight --source docs/gdd/<file>.md --source-kind gdd --capability-snapshot logs/ci/project-health/engine-capabilities.json --out-json logs/ci/technical-preflight/summary.j`
- `py -3 scripts/python/enrich_task_candidates.py --technical-preflight logs/ci/technical-preflight/summary.json`
- `The output schema is `technical-preflight.v1`.`
- `- `engine_spike_required``
- `- Always `recommend_only`.`
- `- Generic vehicle, destructible, or heavy physics without Web, determinism, or plugin signals -> `engine_spike_required` with `undecided_physics_backend`.`
- `- Many rigid bodies, physics sandbox, Web/WASM physics, or named Rapier candidate -> `engine_spike_required`.`
- `If Chapter 2.5 recommends `engine_spike_required`, Chapter 3 should generate a spike-shaped task rather than a backend installation task.`
- `The deterministic enrichment step supports this directly: `enrich_task_candidates.py --technical-preflight <summary.json>` appends a technical-preflight spike candidate and makes gameplay candidates depend on it.`
- ``run_chapter3_regression_check.py` does not automatically consume `logs/ci/technical-preflight/summary.json`. Pass `--technical-preflight <summary.json>` explicitly when the current Chapter 3 run should consume Chapter 2`
