# Godogen Absorption Policy

## Purpose

This document records how this repository may selectively absorb ideas from the public `htdt/godogen` project.

`godogen` is not a replacement for this repository's BMAD/GDS-derived design flow, Chapter 3-7 workflow, Taskmaster integration, architecture overlays, CI gates, Windows-only Godot C# stack, or local recovery pipeline. It is treated as an external reference for automatable Godot generation, verification, and evidence-loop practices that can be converted into repository-owned rules, scripts, tests, or pipeline stages.

This policy deliberately excludes two classes of upstream material:

- Human-only validation loops where `godogen` or an agent proposes a requirement and a human must judge whether the result is acceptable.
- Prototype-only habits that do not fit the formal Chapter 3-7 routing model.

## Source

Primary upstream source:

- Repository: <https://github.com/htdt/godogen>
- Description at initial review: autonomous game development for Godot and Bevy with Claude Code and Codex.
- Relevant upstream areas as of the initial review:
  - `godot/skills/godogen/SKILL.md`
  - `godot/skills/godogen/decomposer.md`
  - `godot/skills/godogen/scaffold.md`
  - `godot/skills/godogen/scene-generation.md`
  - `godot/skills/godogen/task-execution.md`
  - `godot/skills/godogen/capture.md`
  - `godot/skills/godogen/test-harness.md`
  - `godot/skills/godogen/quirks.md`
  - `godot/skills/godot-api/`
  - `shared/skills/godogen/asset-planner.md`
  - `shared/hooks/stop_post_task_gate.py`

The initial policy decision was based on the public `htdt/godogen` repository observed on 2026-06-23. Future updates must re-check the current upstream state before changing this repository.

## Baseline And Attribution

Initial upstream baseline:

- Date checked: 2026-06-23
- Branch checked: `master`
- Commit checked: `51954f9f34d18044c501a09c0645ff0e680edbdf`
- Upstream license at check time: MIT License
- Repository metadata was checked through the GitHub API on 2026-06-23; popularity metrics are not policy inputs.

When this repository adapts concrete wording, tables, scripts, file formats, or templates from `godogen` rather than independently restating the idea, the receiving document, decision log, execution plan, or attribution record must cite `htdt/godogen` and the checked commit or release. Prefer paraphrased repository-owned rules over copied upstream prose.

Do not vendor `godogen` files directly unless the user explicitly asks for that import and the resulting license/attribution obligations are recorded in the same change.

## Integration Rule

Adopt only material that can become one of the following:

- A repository-owned Chapter 3-7 rule.
- A deterministic validation check.
- A Godot-side test harness convention.
- A CI or local review pipeline stage.
- A machine-readable manifest, structure snapshot, or evidence sidecar.
- A repair hint derived from scanned files, logs, scene data, or test output.
- A scriptable screenshot, video, or frame-sequence integrity check.

Do not adopt material that remains only prompt coaching, autonomous requirement invention, subjective visual judgment, manual playtest instruction, or prototype-lane-only practice.

## Chapter 3-7 Placement

Allowed `godogen` ideas must be absorbed into the existing formal route instead of adding a parallel workflow:

| Chapter | Absorption Target | Expected Artifact |
| --- | --- | --- |
| Chapter 3 | Godot risk and evidence classification for task candidates | Structured risk tags and required evidence fields |
| Chapter 4 | Overlay and contract separation between Core rules and Godot surfaces | Overlay references to Core contracts, scene surfaces, tests, and assets |
| Chapter 5 | Semantic stabilization of scene, UI, input, and evidence obligations | Acceptance refs that distinguish xUnit, Godot scene tests, capture evidence, and asset checks |
| Chapter 6 | Implementation and repair evidence | SceneTree/GdUnit tests, headless capture logs, structure snapshots, and artifact integrity checks |
| Chapter 7 | UI wiring closure and screenshot-backed checks | Screen contracts, fixed-resolution screenshots, focus/input checks, and screenshot artifact summaries |

Prototype lane may still use separate experiments, but prototype artifacts are not accepted as formal Chapter 3-7 evidence unless promoted and rerun through the formal route.

## Allowed Absorption Areas

### Godot SceneTree Test Harness Contract

This is the highest-value `godogen` absorption area for this repository.

Allowed ideas to adapt:

- Use deterministic Godot-side tests that can run headless.
- Prefer scripted assertions over visual-only approval.
- Standardize console assertion output such as `ASSERT PASS:` and `ASSERT FAIL:` for behavior that is easier to inspect from runtime state than from pixels.
- Treat any `ASSERT FAIL` in captured stdout as a pipeline failure.
- Keep test lifecycle under the harness instead of relying on ad hoc manual exits.
- Record Godot version, test scene, test script, viewport, frame count, duration, seed, command line, and exit code in evidence metadata.

Repository direction:

- Convert this into `Tests.Godot` conventions, `docs/testing-framework.md` rules, and `run_review_pipeline.py` stages.
- Keep GdUnit4 for Godot-side unit and integration tests; use SceneTree harness tests primarily for headless capture, runtime assertions, and end-to-end scene evidence.
- Keep pure domain logic in `Game.Core.Tests`; use Godot-side tests only for engine, scene, signal, input, UI, viewport, and asset integration behavior.

### Headless Capture And Artifact Integrity

Allowed ideas to adapt:

- Generate fixed-resolution screenshots, frame sequences, or videos as machine-checkable evidence.
- Require screenshot files to exist, be readable, match expected dimensions, and be nonblank.
- Detect all-black, all-transparent, or near-uniform screenshots before treating visual evidence as valid.
- Capture stdout and stderr next to visual artifacts.
- Store capture summaries under `logs/` and include them in task recovery sidecars.
- Prefer fixed FPS, fixed viewport, deterministic input schedules, and recorded seeds.

Repository direction:

- Treat capture evidence as automated artifact integrity and regression input, not as human-only visual approval.
- Integrate with Chapter 7 screenshot acceptance and formal task `summary.json` sidecars.

### Programmatic Scene Builder Validation

Allowed ideas to adapt:

- Use deterministic builders or validators for complex `.tscn` wiring instead of brittle hand-edited scene text.
- Save, reopen, and validate generated scenes before accepting them.
- Validate required node paths, owner chain, attached scripts, exported `NodePath` values, signal/event wiring, resource references, input actions, and autoload dependencies.
- Prefer repair hints that move brittle deep `GetNode` paths toward exported references when the formal task is already touching scene wiring.

Repository direction:

- Builders must not become a gameplay logic layer. Godot scripts own lifecycle, presentation, input, and scene wiring; `Game.Core` owns rules, state mutation, deterministic simulation, and domain services.
- Builder output must stay compatible with `docs/workflows/chapter3-7-component-routing.md`.

### Godot Structure Snapshot

Allowed ideas to adapt:

- Maintain a generated structure view of scenes, scripts, resources, autoloads, input actions, and exported references.
- Use the generated structure to prefill or validate screen contracts, UI wiring matrices, and repair guides.
- Detect missing script/resource references and scene path drift.

Repository direction:

- Prefer generated `structure.json` and optional generated `structure.md` under `logs/` over hand-maintained `STRUCTURE.md` files.
- Any generated `structure.md` must be derived from `structure.json`; do not maintain it as an independent source.
- Use the default output path `logs/ci/<date>/godot-structure/structure.json` unless a task-scoped run directory supplies a narrower evidence path.
- The minimum snapshot schema should include `scenes`, `scripts`, `autoloads`, `input_actions`, `resources`, and `missing_references`.
- Use snapshots as evidence and repair context, not as a second source of truth that overrides the repository's architecture docs.

### Asset Manifest And Provenance Checks

Allowed ideas to adapt:

- Track runtime asset paths, dimensions, type, intended use, source/provenance, and license status in a machine-readable manifest.
- Validate that scene-referenced assets exist and are importable.
- Validate that shipped assets stay inside allowed Godot paths and comply with host boundary rules.
- Record unknown, unused, or unmanifested assets as warnings or technical debt according to delivery profile.

Repository direction:

- Prefer `Game.Godot/Assets/assets.manifest.json` or feature-overlay manifests over prose-only asset planning.
- Feature-overlay manifests are task or PRD inputs; runtime packaging and release gates should consume `Game.Godot/Assets/assets.manifest.json` or a generated merged manifest as the final asset SSoT.
- A generated merged manifest must be written to `logs/` or a fixed runtime manifest path and must record the source manifests it consumed.
- Release and security gates may require provenance fields before assets enter a shippable profile.

### Godot C# Quirks As Validators

Allowed ideas to adapt:

- Convert repeated Godot C# pitfalls into static checks or targeted repair hints.
- Check for `.gdignore` placement that silently blocks imports.
- Check for missing `.tscn` script/resource references.
- Warn on brittle deep node lookup patterns when exported references are more appropriate.
- Check input-map drift between tests, scene scripts, and `project.godot`.
- Keep common Godot API mismatch notes available for Chapter 6 repair.

Repository direction:

- Store only repository-verified quirks as durable rules.
- Prefer validators and repair hints over long prose warnings.

### Godot API Local Reference

Allowed ideas to adapt:

- Maintain or generate a local Godot API reference index for the Godot version used by this repository.
- Use the reference during implementation and repair to reduce hallucinated C# APIs and version mismatches.
- Prefer local indexed lookup before adding new Godot API usage in formal Chapter 6/7 work.

Repository direction:

- Scope the index to Godot 4.5.x and this repository's C#/.NET stack.
- Do not add a live online dependency to the deterministic local gate path.

### Risk-To-Evidence Classification

Allowed ideas to adapt:

- Classify task candidates for Godot-specific risk tags such as `scene_wiring`, `camera`, `input`, `ui_focus`, `runtime_asset_loading`, `shader`, `navigation`, `physics`, or `capture_required`.
- Convert risk tags into required evidence, not human approval prompts.
- Feed required evidence into Chapter 4 overlays, Chapter 5 acceptance refs, Chapter 6 tests, and Chapter 7 screen contracts.

Repository direction:

- Implement classification as deterministic enrichment that writes structured fields.
- Allowed deterministic inputs include Taskmaster fields, overlay refs, acceptance refs, test refs, scene scans, script scans, asset manifests, `project.godot`, and prior pipeline sidecars.
- LLM review may propose candidate risk tags, but formal routing should accept them only after deterministic validation or explicit task metadata records the requirement.
- Do not let an external decomposer create a second task-routing system.

### Post-Task Evidence Gate

Allowed ideas to adapt:

- Bind task completion claims to required artifacts.
- Fail or block completion when task metadata says a feature is complete but required tests, capture evidence, structure snapshots, or manifests are missing.
- Write missing-evidence reasons into active-task summaries and repair guides.

Repository direction:

- Integrate with `scripts/sc/run_review_pipeline.py`, `logs/ci/active-tasks/`, and existing recovery sidecars.
- Do not add a separate chat-only or notification-only completion hook.

## Excluded Absorption Areas

The following `godogen` areas are not planned for adoption as formal repository workflow rules:

- Human-only visual approval, taste judgment, or prompt-driven acceptance.
- Agent-generated requirements that require a human to decide whether they are valid before the pipeline can proceed.
- Prototype-only `PLAN.md`, `MEMORY.md`, `STRUCTURE.md`, or `ASSETS.md` habits unless converted into generated, validated, formal Chapter 3-7 artifacts.
- Full autonomous game-generation workflow replacement.
- Multi-engine Bevy, Babylon.js, or generic engine routing.
- Linux/Xvfb/tmux-specific run assumptions.
- Telegram or notification hooks.
- Direct import of upstream skills as an active second agent system.
- External asset-generation services as a delivery gate dependency.
- Prompt-only instructions that cannot be tied to files, tests, logs, captures, manifests, or deterministic checks.

## Upgrade Procedure

When the user asks to refresh this repository against a newer `godogen` version:

1. Check the current upstream repository and release state.
2. Record the upstream branch, tag or release, commit, check date, and license status in the proposed change.
3. Review only the allowed absorption areas listed in this document.
4. Compare upstream changes against this repository's Chapter 3-7 routing, testing framework, review pipeline, CI gates, security posture, and recovery sidecars.
5. Propose a narrow upgrade plan that separates:
   - Godot-side test harness changes,
   - capture and artifact integrity changes,
   - scene builder or structure snapshot changes,
   - asset manifest changes,
   - Godot C# quirks or API-reference changes,
   - risk-to-evidence routing changes.
6. Reject upstream changes that remain human-only, prototype-only, prompt-only, or duplicate existing BMAD/GDS coverage.
7. Preserve this repository's Windows-only Godot C# stack, architecture invariants, host-safe security boundary, CI gates, and recovery protocol.
8. Record any accepted upgrade as repository-owned documentation, code, tests, scripts, manifests, or pipeline stages, not as a blind copy of `godogen` routing.
9. Add attribution when adapted content is more specific than a general idea or engineering principle.
10. Record accepted upgrades in the changed document, an execution plan, or a decision log when the change affects future workflow behavior.

## Decision Summary

`godogen` is useful here as a selective source of automatable Godot evidence-loop practices, not as a workflow dependency. The preferred adoption path is:

1. Godot SceneTree test harness conventions and stdout assertion parsing.
2. Headless capture artifact integrity for Chapter 6 and Chapter 7 evidence.
3. Generated Godot structure snapshots for scene, script, asset, and input drift detection.
4. Programmatic scene builder validation for complex `.tscn` wiring.
5. Asset manifest and provenance checks.
6. Godot C# quirks validators and local Godot API reference support.
7. Risk-to-evidence classification that feeds formal Chapter 3-7 routing.
8. Post-task evidence gates integrated into the existing review pipeline and recovery sidecars.

Everything else remains outside the main flow unless a future upstream version adds concrete, automatable, Chapter 3-7-compatible material.
