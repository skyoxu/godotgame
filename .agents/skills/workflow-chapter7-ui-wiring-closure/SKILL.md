---
name: workflow-chapter7-ui-wiring-closure
description: Run the fixed Chapter 7 UI wiring closure workflow from workflow.md. Use when a business repo needs UI/GDD closure after Chapter 6, chapter7 profile overrides, UI wiring GDD generation, candidate sidecars, artifact manifests, hard gates, task generation, or idempotent Chapter 7 readiness checks.
---

# Workflow Chapter 7 UI Wiring Closure

## Role

Operate Chapter 7 from `workflow.md` idempotently for a business repository that is a sibling of the template repository.

## Operating Contract

- Treat `workflow.md` as the normative workflow source.
- Treat business-repo logs as empirical evidence, not policy overrides.
- Use Python with UTF-8 for documentation reads and writes.
- Keep generated code, scripts, tests, comments, and log messages in English.
- Do not modify the business repo unless the user explicitly asks for that change.
- Do not rerun expensive steps before reading existing recovery artifacts.

- Apply `docs/workflows/chapter3-7-component-routing.md` as a soft generation and repair preference for Chapter 3-7 only.
- Treat `Component` as a Godot Node/Scene Component, not an ECS component.
- Keep Godot scripts focused on lifecycle, presentation, input, and wiring; keep rules, state mutation, and simulation logic in `Game.Core` unless an ADR or task explicitly scopes otherwise.


## Repository Layout

Template and business repositories are siblings under one parent directory, for example `<parent>/godotgame`, `<parent>/<business-repo-a>`, and `<parent>/<business-repo-b>`.

## Purpose

Use this skill to convert completed domain and gameplay capabilities into player-facing UI wiring and governed Chapter 7 artifacts.

## Default Lane

Start with self-check, then write-doc, then create-tasks only after the candidate sidecar and artifact manifest are valid.

## Primary Command Or Action

`py -3 scripts/python/dev_cli.py run-chapter7-ui-wiring --delivery-profile <profile> --self-check`

## Evidence Rule

Chapter 7 currently has little or no business-repo runtime history. Use workflow.md, chapter7-profile.json, the profile guide, and generated manifests as the stable source until real logs exist.

## Required Reading

1. Read the relevant Chapter 7 section in the template repo `workflow.md`.
2. Read `docs/workflows/chapter3-7-component-routing.md` for the formal Chapter 3-7 soft routing preferences.
3. Read `docs/workflows/ui-ux-implementation-policy.md`; Chapter 7 consumes Chapter 3 `ui_ux_seed` metadata and turns it into screen contracts, component kit decisions, screenshot acceptance, accessibility checks, and localization checks.
4. Optionally read `references/business-repos/<repo>.md` only as empirical validation evidence when the target business repo has a generated reference.
5. If that optional evidence file is missing or stale, run `py -3 scripts/python/update_workflow_chapter_skills.py <repo>` from the template repo.

## Idempotent Procedure

1. Confirm Chapter 6 has no unrecorded P0/P1 Needs Fix.
2. Confirm real task triplet files exist before treating the Chapter 7 gate as complete.
3. Use a Chapter 7 profile override for policy-level business repo differences instead of forking scripts.
4. Run self-check before write-doc.
5. Validate UI GDD, candidates, artifact manifest, and hard gate outputs before task creation.
6. When Chapter 3 generated `ui_ux_seed`, confirm the Chapter 7 UI GDD maps its categories into concrete screen contracts, screenshot acceptance rows, accessibility/localization checks, or explicit waivers.
7. Stop when backlog-gap evidence says candidate tasks are already covered.


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
