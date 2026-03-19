# Repository Guide

This file is the repository map. It routes you to the right source document by task stage, problem type, and durable run state. Do not turn it back into a 600-line encyclopedia.

## Purpose
- Windows-only Godot + C# game template.
- `AGENTS.md` is the routing layer.
- `README.md` is the project-facing overview and startup entry.
- `docs/agents/` holds agent workflow, recovery, and navigation docs.
- `docs/architecture/**`, `docs/adr/**`, `docs/testing-framework.md`, and `DELIVERY_PROFILE.md` remain the deep source documents.

## Start Here
1. [Agents Docs Index](docs/agents/00-index.md)
2. [Session Recovery](docs/agents/01-session-recovery.md)
3. [Repo Map](docs/agents/02-repo-map.md)
4. [README](README.md)
5. Newest file in `execution-plans/`
6. Newest file in `decision-logs/`
7. If a local review pipeline already ran, `logs/ci/<date>/sc-review-pipeline-task-<task>/latest.json`

## Task Navigation
- New session or resume failed work:
  - [Session Recovery](docs/agents/01-session-recovery.md)
  - [Persistent Harness](docs/agents/03-persistent-harness.md)
  - [Agent-to-Agent Review](docs/agents/07-agent-to-agent-review.md)
- Understand the project, startup path, or stack:
  - [README](README.md)
  - [Project Basics](docs/agents/08-project-basics.md)
  - [Project Documentation Index](docs/PROJECT_DOCUMENTATION_INDEX.md)
- Implement a feature or touch architecture:
  - [ADR Index](docs/architecture/ADR_INDEX_GODOT.md)
  - [Architecture Guardrails](docs/agents/05-architecture-guardrails.md)
  - `docs/architecture/base/00-README.md`
  - [Template Customization](docs/agents/10-template-customization.md)
- Write tests, acceptance, or quality gates:
  - [Testing Framework](docs/testing-framework.md)
  - [Closed-Loop Testing](docs/agents/04-closed-loop-testing.md)
  - [Quality Gates And DoD](docs/agents/09-quality-gates-and-done.md)
  - `scripts/sc/README.md`
- Run or repair the local harness and reviews:
  - [Persistent Harness](docs/agents/03-persistent-harness.md)
  - [Agent-to-Agent Review](docs/agents/07-agent-to-agent-review.md)
  - [DELIVERY_PROFILE](DELIVERY_PROFILE.md)
  - `scripts/sc/README.md`
- Tighten release or CI posture:
  - [Quality Gates And DoD](docs/agents/09-quality-gates-and-done.md)
  - [DELIVERY_PROFILE](DELIVERY_PROFILE.md)
  - `docs/workflows/`
- Copy this template into a new project:
  - [Template Customization](docs/agents/10-template-customization.md)
  - [README](README.md)
  - [DELIVERY_PROFILE](DELIVERY_PROFILE.md)

## Problem Navigation
- Need project background, use cases, startup, or stack:
  - [README](README.md)
  - [Project Basics](docs/agents/08-project-basics.md)
- Need repository directories or entry files:
  - [Repo Map](docs/agents/02-repo-map.md)
  - [Project Documentation Index](docs/PROJECT_DOCUMENTATION_INDEX.md)
- Need ADR, Base, Overlay, or contract placement rules:
  - [ADR Index](docs/architecture/ADR_INDEX_GODOT.md)
  - [Architecture Guardrails](docs/agents/05-architecture-guardrails.md)
  - [Template Customization](docs/agents/10-template-customization.md)
- Need tests, logs, artifacts, Test-Refs, or DoD:
  - [Testing Framework](docs/testing-framework.md)
  - [Quality Gates And DoD](docs/agents/09-quality-gates-and-done.md)
- Need delivery strictness or profile behavior:
  - [DELIVERY_PROFILE](DELIVERY_PROFILE.md)
- Need AGENTS structure or maintenance rules:
  - [AGENTS Construction Principles](docs/agents/11-agents-construction-principles.md)

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
- `docs/`: project, architecture, workflow, testing, and agents docs.
- `scripts/sc/`: review pipeline and task-facing automation.
- `scripts/python/`: validation, gates, sync, reporting, and guardrails.
- `.github/workflows/`: CI entry points.
- `.taskmaster/`: task triplet data.
- `execution-plans/` and `decision-logs/`: durable intent and decisions.
- `logs/`: runtime, CI, and review artifacts.

## Main Commands
- Full local review: `py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin "$env:GODOT_BIN"` (auto-writes `agent-review.*` unless `--dry-run`, `--skip-agent-review`, or the active profile sets `agent_review.mode=skip`)
- Targeted test step: `py -3 scripts/sc/test.py --task-id <id> --godot-bin "$env:GODOT_BIN"`
- Targeted acceptance step: `py -3 scripts/sc/acceptance_check.py --task-id <id> --godot-bin "$env:GODOT_BIN"`
- Targeted llm review: `py -3 scripts/sc/llm_review.py --task-id <id>`
- Agent-to-agent review rebuild: `py -3 scripts/sc/agent_to_agent_review.py --task-id <id>`

## Recovery Files
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/summary.json`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/execution-context.json`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/repair-guide.json`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/repair-guide.md`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/agent-review.json`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/agent-review.md`
- `logs/ci/<date>/sc-review-pipeline-task-<task>/latest.json`

## Docs Index
- [README](README.md)
- [Project Documentation Index](docs/PROJECT_DOCUMENTATION_INDEX.md)
- [Testing Framework](docs/testing-framework.md)
- [DELIVERY_PROFILE](DELIVERY_PROFILE.md)
- [ADR Index](docs/architecture/ADR_INDEX_GODOT.md)
- [Agents Docs Index](docs/agents/00-index.md)
- [Project Basics](docs/agents/08-project-basics.md)
- [Quality Gates And DoD](docs/agents/09-quality-gates-and-done.md)
- [Template Customization](docs/agents/10-template-customization.md)
- [AGENTS Construction Principles](docs/agents/11-agents-construction-principles.md)

## Change Policy
- Keep `summary.json` schema stable.
- Add new recovery data as sidecar files.
- Keep `AGENTS.md` as a routing map, not a duplicate rules catalog.
- Put detailed guidance into `docs/agents/`, `README.md`, or the relevant source doc.
- Put durable intent in git-tracked markdown under `execution-plans/` and `decision-logs/`.
- Put high-frequency evidence in `logs/`.
