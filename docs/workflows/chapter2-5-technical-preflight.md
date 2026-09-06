# Chapter 2.5 Technical Preflight

Purpose: route technical feasibility signals after Chapter 2 capability discovery and before Chapter 3 formal task generation.

This is a recommendation pass. It does not install plugins, edit `project.godot`, create formal tasks, or change production scenes.

## Position

Use this order:

1. Chapter 2 establishes repository and engine capabilities.
2. Chapter 2.5 reads GDD, prototype records, task text, and optional capability snapshots.
3. Chapter 3 consumes task hints from Chapter 2.5.
4. Chapter 4 records ADR or overlay decisions when needed.
5. Chapter 5 preserves or removes engine constraints based on Chapter 2.5 and ADR state.
6. Chapter 6 implements only after the required spike or decision evidence exists.
7. Chapter 7 consumes confirmed runtime state and UI surface needs; it does not choose engine backends.

## Stable Entrypoint

```powershell
py -3 scripts/python/dev_cli.py run-technical-preflight --source docs/prototypes/<file>.md --source-kind prototype --recommendation-only
```

Optional JSON output:

```powershell
py -3 scripts/python/dev_cli.py run-technical-preflight --source docs/gdd/<file>.md --source-kind gdd --capability-snapshot logs/ci/project-health/engine-capabilities.json --out-json logs/ci/technical-preflight/summary.json
```

Chapter 3 enrichment can consume the output:

```powershell
py -3 scripts/python/enrich_task_candidates.py --technical-preflight logs/ci/technical-preflight/summary.json
```

## Output Contract

The output schema is `technical-preflight.v1`.

Key fields:

- `technical_preflight.chapter`
  - Always `2.5`.
- `source.path`
  - CLI output uses the resolved source path so downstream repo matching can avoid stale summaries.
- `capability_snapshot_status`
  - `not_provided`
  - `provided`
  - `missing`
  - `invalid_json`
- `technical_preflight.engine_route.recommended_action`
  - `no_engine_change`
  - `use_default_backend`
  - `engine_spike_required`
- `technical_preflight.engine_route.candidate_backend`
  - `none`
  - `godot_physics_2d`
  - `jolt_3d`
  - `undecided_physics_backend`
  - `rapier_2d`
  - `rapier_3d` can be added later when a 3D plugin spike is explicitly supported.
- `technical_preflight.engine_route.adr_required`
  - `true` when a plugin or global backend change is being proposed.
- `technical_preflight.engine_route.apply_mode`
  - Always `recommend_only`.
- `chapter3_task_hints`, `chapter4_overlay_hints`, `chapter5_semantic_guards`, `chapter6_acceptance_gates`, and `chapter7_ui_notes`
  - Downstream guidance for formal stages.

## Routing Rules

Default posture:

- UI, card, route, settlement, menu, shop, save, or state-driven loops -> `no_engine_change`.
- Ordinary 2D collisions, hitboxes, platformer movement, or `CharacterBody2D` use -> `use_default_backend` with `godot_physics_2d`.
- Ordinary 3D physics -> `use_default_backend` with `jolt_3d`.
- Generic vehicle, destructible, or heavy physics without Web, determinism, or plugin signals -> `engine_spike_required` with `undecided_physics_backend`.
- Many rigid bodies, physics sandbox, Web/WASM physics, or named Rapier candidate -> `engine_spike_required`.
- Determinism, rollback, or replay alone does not imply a physics backend. Pure card, deck, RNG, state-machine, or save determinism should stay in Core without engine changes.
- Plugin backend or global backend change -> ADR or decision-log before implementation.

## Hard Boundaries

Chapter 2.5 must not:

- install Rapier or any other plugin,
- modify `project.godot`,
- change export settings,
- create or modify formal `.taskmaster/tasks/*.json`,
- migrate scenes,
- treat a prototype recommendation as a production decision.

## Promotion To Formal Work

If Chapter 2.5 recommends `engine_spike_required`, Chapter 3 should generate a spike-shaped task rather than a backend installation task.

The deterministic enrichment step supports this directly: `enrich_task_candidates.py --technical-preflight <summary.json>` appends a technical-preflight spike candidate and makes gameplay candidates depend on it.

`run_chapter3_regression_check.py` does not automatically consume `logs/ci/technical-preflight/summary.json`. Pass `--technical-preflight <summary.json>` explicitly when the current Chapter 3 run should consume Chapter 2.5 output.

The spike should prove:

- target platform compatibility,
- minimal gameplay behavior,
- deterministic or performance requirements when claimed,
- Godot/GdUnit or smoke evidence,
- fallback plan if the candidate backend is rejected.

Only after spike evidence and the required ADR/decision-log exist should Chapter 6 install plugins, edit `project.godot`, or migrate production scenes.
