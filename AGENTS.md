# Repository Guide

This file is an index, not a knowledge dump. Read the linked docs instead of expanding this file.

## Purpose
- Windows-only Godot + C# game template.
- arc42 + ADR + Taskmaster workflow.
- Durable agent recovery uses `docs/agents/`, `execution-plans/`, `decision-logs/`, and pipeline artifacts in `logs/ci/`.

## Start Here
1. Read `docs/agents/00-index.md`.
2. Read `docs/agents/01-session-recovery.md`.
3. Read `docs/agents/02-repo-map.md`.
4. Read the newest files in `execution-plans/` and `decision-logs/`.
5. Read `git log --oneline --decorate -n 10`.
6. If a local review pipeline already ran, open `logs/ci/<date>/sc-review-pipeline-task-<task>/latest.json`.

## Core Rules
- Communicate with the user in Chinese.
- Default environment is Windows.
- Use Windows-compatible commands and paths.
- Read and write docs with Python and UTF-8.
- Do not use PowerShell text pipelines for doc edits.
- Keep code, scripts, tests, comments, and printed messages in English.
- Do not use emoji.
- Write logs and evidence under `logs/`.
- Do not revert user changes unless explicitly requested.
- Prefer small, deterministic, testable changes.
- Use accepted ADRs when code or tests change architecture or guardrails.

## Repo Map
- `Game.Core/`: pure C# domain and contracts.
- `Game.Core.Tests/`: xUnit tests for core logic.
- `Game.Godot/`: Godot runtime project.
- `Tests.Godot/`: Godot-side tests and reports.
- `docs/adr/`: architecture decisions.
- `docs/architecture/base/`: arc42 base chapters.
- `docs/architecture/overlays/`: PRD-scoped overlays.
- `docs/agents/`: agent recovery, harness, and review docs.
- `execution-plans/`: durable progress checkpoints.
- `decision-logs/`: durable decisions.
- `scripts/sc/`: review pipeline and task-facing automation.
- `scripts/python/`: guardrails, validation, sync, and reports.
- `.github/workflows/`: CI workflows.
- `.taskmaster/`: task triplet data.
- `examples/taskmaster/`: template fallback task data.
- `logs/`: runtime, CI, and evidence artifacts.

## Main Commands
- Full local review: `py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin "$env:GODOT_BIN"`
- Targeted test step: `py -3 scripts/sc/test.py --task-id <id> --godot-bin "$env:GODOT_BIN"`
- Targeted acceptance step: `py -3 scripts/sc/acceptance_check.py --task-id <id> --godot-bin "$env:GODOT_BIN"`
- Targeted llm review: `py -3 scripts/sc/llm_review.py --task-id <id>`

## Recovery Files
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/summary.json`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/execution-context.json`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/repair-guide.json`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/repair-guide.md`
- `logs/ci/<date>/sc-review-pipeline-task-<task>/latest.json`

## Docs Index
- `docs/agents/00-index.md`
- `docs/agents/03-persistent-harness.md`
- `docs/agents/04-closed-loop-testing.md`
- `docs/agents/05-architecture-guardrails.md`
- `docs/agents/06-harness-marathon.md`
- `docs/agents/07-agent-to-agent-review.md`
- `docs/testing-framework.md`
- `docs/PROJECT_DOCUMENTATION_INDEX.md`
- `DELIVERY_PROFILE.md`

## Change Policy
- Keep `summary.json` schema stable.
- Add new recovery data as sidecar files.
- Put durable intent in git-tracked markdown under `execution-plans/` and `decision-logs/`.
- Put high-frequency evidence in `logs/`.
