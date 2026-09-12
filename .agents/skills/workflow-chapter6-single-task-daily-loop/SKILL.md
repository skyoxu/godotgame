---
name: workflow-chapter6-single-task-daily-loop
description: Run the fixed Chapter 6 single-task daily loop from workflow.md. Use when a business repo needs resume-task, chapter6-route, TDD red/green/refactor, 6.7 review pipeline, 6.8 Needs Fix cleanup, 6.9 repository validation, stop-loss, rerun guard, or idempotent recovery from Chapter 6 logs.
---

# Workflow Chapter 6 Single Task Daily Loop

## Role

Operate Chapter 6 from `workflow.md` idempotently for a business repository that is a sibling of the template repository.

## Operating Contract

- Treat `workflow.md` as the normative workflow source.
- Treat business-repo logs as empirical evidence, not policy overrides.
- Use Python with UTF-8 for documentation reads and writes.
- Keep generated code, scripts, tests, comments, and log messages in English.
- Do not modify the business repo unless the user explicitly asks for that change.
- Do not rerun expensive steps before reading existing recovery artifacts.
- Before RED, Chapter 6 must use an explicit `consumer=chapter6` candidate decision/freeze. Candidate ranking is never implicit acceptance.
- Review must use a separate `consumer=review` context; never relabel or reuse a Chapter 6 freeze as Review.

- Apply `docs/workflows/chapter3-7-component-routing.md` as a soft generation and repair preference for Chapter 3-7 only.
- Treat `Component` as a Godot Node/Scene Component, not an ECS component.
- Keep Godot scripts focused on lifecycle, presentation, input, and wiring; keep rules, state mutation, and simulation logic in `Game.Core` unless an ADR or task explicitly scopes otherwise.

## Repository Layout

Template and business repositories are siblings under one parent directory, for example `<parent>/godotgame`, `<parent>/<business-repo-a>`, and `<parent>/<business-repo-b>`.

## Purpose

Use this skill to drive one task through bounded-context implementation, impact analysis, review, repair, resource-knowledge capture, and repository validation.

## Default Lane

Use the top-level Chapter 6 orchestrator unless active-task or chapter6-route already recommends a narrower recovery command. Freeze semantic context before RED; do not silently expand it during RED/GREEN/REFACTOR.

## Primary Command Or Action

`py -3 scripts/python/dev_cli.py run-single-task-chapter6 --task-id <id> --godot-bin "$env:GODOT_BIN" --delivery-profile <profile>`

## Evidence Rule

Chapter 6 has dense business-repo logs. Always read active-task, latest.json, summary.json, repair-guide, agent-review, and run-events before paying for another 6.7 or 6.8. Knowledge and Impact artifacts are bounded evidence and do not replace task/PRD/GDD/ADR/Overlay/Contract/source authority.

## Required Reading

1. Read the relevant Chapter 6 section in the template repo `workflow.md`.
2. Read `docs/workflows/knowledge-context-shadow.md` and `docs/workflows/knowledge-context-freeze.md`.
3. Read `docs/workflows/chapter3-7-component-routing.md` for the formal Chapter 3-7 soft routing preferences.
4. Read `docs/workflows/ui-ux-implementation-policy.md` when the task carries `ui_ux_seed`; Chapter 6 should preserve stable scene, input, text-key, and state boundaries but should not run a broad visual retrofit.
5. Optionally read `references/business-repos/<repo>.md` only as empirical validation evidence when the target business repo has a generated reference.

## Knowledge / Impact Contract

- Before RED, prepare `consumer=chapter6` candidates, re-read sources directly, record explicit accept/reject decisions with reasons, and freeze them with `freeze_knowledge_context.py`.
- Run `analyze_impact.py --target <path-or-symbol> --strict` and validate revision/frozen-context lineage with `impact_analysis_handoff.py` before implementation consumes the report.
- Frozen semantic scope must not expand silently during RED/GREEN/REFACTOR. A genuine scope change requires a new candidate/decision/freeze revision.
- Review uses a separate `consumer=review` candidate set and freeze. Never relabel or reuse a Chapter 6 freeze as Review.
- After implementation evidence is stable, run `chapter6_knowledge.py --task-id <id> --path <reviewed-resource>` only for resources actually reviewed by the task. With no reviewed paths, the explicit-reviewed resource record must skip instead of inventing associations.
- When developer-facing semantic explanation would materially help, add `--semantic --llm-backend <codex-cli|openai-api>`. Semantic output is accepted only when every resource path, JSON pointer, scene node, and asset binding resolves to reconstructed snapshot evidence; generated explanations remain non-authoritative.
- `generate_knowledge_links.py` is the deterministic task-resource reconstruction layer used before semantic enrichment. Do not hand-author generated links to make a page look complete.
- Knowledge and Impact artifacts are bounded evidence; they never replace Taskmaster, PRD/GDD, ADR/Base/Overlay, Contracts, source, or test authority.

<!-- KNOWLEDGE_IMPACT_OVERLAY_BEGIN -->
## Knowledge / Impact Contract

- Before RED, Chapter 6 context preparation requires `publication_state = published-current`. If local main or the control plane changed, rebuild/publish the Knowledge generation before freezing; do not freeze an ephemeral catalog.
- Prepare `consumer=chapter6` candidates, re-read sources directly, record explicit accept/reject decisions with reasons and satisfies fields, and freeze them with `freeze_knowledge_context.py`.
- Read the frozen context revision, then build/reuse an immutable Impact Index for that exact revision with `build_impact_index.py --revision <frozen-revision> --trusted-ref refs/heads/main`.
- Run `analyze_impact.py --target <path-or-symbol-or-config-pointer> --strict --frozen-context <frozen.json>` and validate revision/frozen-context/index lineage with `impact_analysis_handoff.py` before implementation consumes the report.
- Frozen semantic scope must not expand silently during RED/GREEN/REFACTOR. A genuine scope change requires a new candidate/decision/freeze revision and a matching revision-bound Impact Index.
- Review uses a separate `consumer=review` candidate set and freeze and also requires published-current Knowledge. Never relabel or reuse a Chapter 6 freeze as Review.
- After implementation evidence is stable, run `chapter6_knowledge.py --task-id <id> --path <reviewed-resource>` only for resources actually reviewed by the task. With no reviewed paths, the explicit-reviewed resource record must skip instead of inventing associations.
- When developer-facing semantic explanation would materially help, add `--semantic --llm-backend <codex-cli|openai-api>`. Semantic output is accepted only when every resource path, JSON pointer, scene node, and asset binding resolves to reconstructed snapshot evidence; generated explanations remain non-authoritative.
- `generate_knowledge_links.py` is the deterministic task-resource reconstruction layer used before semantic enrichment. Do not hand-author generated links to make a page look complete.
- Knowledge and Impact artifacts are bounded evidence; they never replace Taskmaster, PRD/GDD, ADR/Base/Overlay, Contracts, source, or test authority.
<!-- KNOWLEDGE_IMPACT_OVERLAY_END -->

## Idempotent Procedure

1. Read active-task first when a task id exists.
2. Run resume-task and chapter6-route recommendation-only before expensive reruns.
3. Before RED, run `prepare_knowledge_context.py --consumer chapter6 --task-id <id> --query "<implementation intent>"`, re-read candidates directly, record explicit accept/reject decisions with reasons, and freeze the bundle with `freeze_knowledge_context.py`.
4. Run `analyze_impact.py --target <path-or-symbol> --strict` for the implementation target and validate lineage with `impact_analysis_handoff.py`. Do not turn text-only matches into confirmed dependencies.
5. Use the TDD order 6.3, 6.4, 6.5, 6.6 before 6.7 unless recovery evidence says otherwise. Do not silently add new semantic sources after the freeze; if scope genuinely changes, stop and produce a new candidate/decision/freeze revision.
6. When a task includes `ui_ux_seed`, keep the implementation compatible with seeded screens, input model, localization keys, and accessibility baseline, but defer broad theme/component-kit/screenshot retrofit work to Chapter 7.
7. Run 6.7 only when deterministic evidence is stale or required by changed implementation, tests, contracts, scripts, or runtime assets. Review preparation uses a separate `consumer=review` candidate/freeze.
8. Run 6.8 only when route evidence says Needs Fix cleanup is the right lane.
9. After implementation evidence is stable, run `chapter6_knowledge.py --task-id <id> --path <reviewed-resource>` for resources actually reviewed in the task. Add `--semantic --llm-backend <backend>` only when semantic explanation is useful; the command first reconstructs `task-resource-links.json`, then validates every generated pointer/binding against static snapshot evidence.
10. Run 6.9 repository validation before commit or PR closure.

## Stop-Loss Signals

- Existing `forbidden_commands` blocks the command about to be run.
- `artifact_integrity`, `planned_only_incomplete`, or planned-only run type appears in recovery evidence.
- Route evidence recommends inspect-first, record-residual, fix-deterministic, repo-noise-stop, or pause.
- The same deterministic failure fingerprint appears repeatedly.
- Frozen context revision/hash no longer matches the task or Impact evidence.
- The next action would duplicate work already covered by task, overlay, candidate, or manifest evidence.
- Semantic enrichment returns `unverified`: inspect the generated error and reconstructed links; do not promote the explanation or retry blindly with invented evidence.

## Business Evidence References

Generated evidence may live under `references/business-repos/<repo>.md`. These files are optional regression evidence from known business repositories; they must not define production generation rules.

## Maintenance

```powershell
py -3 scripts/python/update_workflow_chapter_skills.py <business-repo>
py -3 scripts/python/update_workflow_chapter_skills.py <business-repo-a>,<business-repo-b>
```
