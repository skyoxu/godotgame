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
3. [RAG Sources And Session SSoT](docs/agents/13-rag-sources-and-session-ssot.md)
4. [Repo Map](docs/agents/02-repo-map.md)
5. [README](README.md)
6. Newest file in `execution-plans/`
7. Newest file in `decision-logs/`
8. If a local review pipeline already ran, `logs/ci/<date>/sc-review-pipeline-task-<task>/latest.json`

## Task Navigation
- New session or resume failed work:
  - [RAG Sources And Session SSoT](docs/agents/13-rag-sources-and-session-ssot.md)
  - [Session Recovery](docs/agents/01-session-recovery.md)
  - [Persistent Harness](docs/agents/03-persistent-harness.md)
  - [Harness Run Protocol](docs/workflows/run-protocol.md)
  - [Agent-to-Agent Review](docs/agents/07-agent-to-agent-review.md)
- Understand the project, startup path, or stack:
  - [Startup, Stack, And Template Structure](docs/agents/14-startup-stack-and-template-structure.md)
  - [README](README.md)
  - [Project Documentation Index](docs/PROJECT_DOCUMENTATION_INDEX.md)
- Implement a feature or touch architecture:
  - [ADR Index](docs/architecture/ADR_INDEX_GODOT.md)
  - [Architecture Guardrails](docs/agents/05-architecture-guardrails.md)
  - [Execution Rules](docs/agents/12-execution-rules.md)
  - `docs/architecture/base/00-README.md`
  - [Template Customization](docs/agents/10-template-customization.md)
- Write tests, acceptance, or quality gates:
  - [Testing Framework](docs/testing-framework.md)
  - [Closed-Loop Testing](docs/agents/04-closed-loop-testing.md)
  - [Quality Gates And DoD](docs/agents/09-quality-gates-and-done.md)
  - `scripts/sc/README.md`
- Run or repair the local harness and reviews:
  - [Persistent Harness](docs/agents/03-persistent-harness.md)
  - [Harness Run Protocol](docs/workflows/run-protocol.md)
  - [Agent-to-Agent Review](docs/agents/07-agent-to-agent-review.md)
  - [DELIVERY_PROFILE](DELIVERY_PROFILE.md)
  - `scripts/sc/README.md`
- Tighten release or CI posture:
  - [Security, Release Health, And Runtime Ops Rules](docs/agents/15-security-release-health-and-runtime-ops.md)
  - [Quality Gates And DoD](docs/agents/09-quality-gates-and-done.md)
  - [DELIVERY_PROFILE](DELIVERY_PROFILE.md)
  - `docs/workflows/`
- Copy this template into a new project:
  - [Template Customization](docs/agents/10-template-customization.md)
  - [Template Bootstrap Checklist](docs/workflows/template-bootstrap-checklist.md)
  - [README](README.md)
  - [DELIVERY_PROFILE](DELIVERY_PROFILE.md)

## Problem Navigation
- Need project background, use cases, startup, or stack:
  - [Startup, Stack, And Template Structure](docs/agents/14-startup-stack-and-template-structure.md)
  - [README](README.md)
- Need repository directories or entry files:
  - [Repo Map](docs/agents/02-repo-map.md)
  - [Project Documentation Index](docs/PROJECT_DOCUMENTATION_INDEX.md)
- Need ADR, Base, Overlay, or contract placement rules:
  - [ADR Index](docs/architecture/ADR_INDEX_GODOT.md)
  - [Architecture Guardrails](docs/agents/05-architecture-guardrails.md)
  - [Template Customization](docs/agents/10-template-customization.md)
- Need security posture, release health, logs, or runtime ops rules:
  - [Security, Release Health, And Runtime Ops Rules](docs/agents/15-security-release-health-and-runtime-ops.md)
- Need tests, logs, artifacts, Test-Refs, or DoD:
  - [Testing Framework](docs/testing-framework.md)
  - [Quality Gates And DoD](docs/agents/09-quality-gates-and-done.md)
- Need RAG source discipline, overlay source selection, or session source SSoT:
  - [RAG Sources And Session SSoT](docs/agents/13-rag-sources-and-session-ssot.md)
- Need delivery strictness or profile behavior:
  - [DELIVERY_PROFILE](DELIVERY_PROFILE.md)
- Need planning discipline, implementation stop-loss, or script size rules:
  - [Execution Rules](docs/agents/12-execution-rules.md)
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
- Code or test changes should cite at least one accepted ADR; if thresholds, contracts, security posture, or release policy change, update or supersede the ADR set.

- Route architecture work in arc42 order: irreversible decisions -> cross-cutting rules -> runtime backbone -> feature slices.
- For overlay work, prefer generated shard or index sources when present; otherwise use the current repo indexes and do not blind-scan `docs/`.
- Ask before high-risk actions and never disable tests to get green.

## Template Reality Checks
- Legacy references such as `architecture_base.index`, `prd_chunks.index`, `shards/flattened-*.xml`, and `tasks/tasks.json` may not exist in this template.
- Current equivalents are routed by `docs/agents/13-rag-sources-and-session-ssot.md`.
- In the bare template, use `docs/PROJECT_DOCUMENTATION_INDEX.md`, `docs/architecture/base/00-README.md`, `docs/architecture/ADR_INDEX_GODOT.md`, and `docs/prd/**/*.md` first.
- Use `.taskmaster/tasks/*.json` only after the copied project has generated real triplet files.

## Hard Architecture Invariants
- Base chapter 08 stays a template only; concrete feature slices belong in `docs/architecture/overlays/<PRD-ID>/08/`.
- Overlay text should reference base chapters and ADRs instead of copying thresholds or policy text.
- Contracts stay in `Game.Core/Contracts/**`; do not duplicate contract definitions across docs and code.
- Route architectural change in arc42 order: irreversible decisions -> cross-cutting rules -> runtime backbone -> feature slices.

## Delivery And Security Quick Map
- `DELIVERY_PROFILE=playable-ea` -> default `SECURITY_PROFILE=host-safe`
- `DELIVERY_PROFILE=fast-ship` -> default `SECURITY_PROFILE=host-safe`
- `DELIVERY_PROFILE=standard` -> default `SECURITY_PROFILE=strict`
- CI should emit both `DeliveryProfile: <...>` and `SecurityProfile: <...>` in Step Summary.
- Host boundary rules stay hard in all profiles: `res://` and `user://` only, HTTPS only, `ALLOWED_EXTERNAL_HOSTS`, `GD_OFFLINE_MODE`, no dynamic external code loading.

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
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/run-events.jsonl`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/harness-capabilities.json`
- `logs/ci/<date>/sc-review-pipeline-task-<task>/latest.json`

## Docs Index

- [README](README.md)
- [Project Documentation Index](docs/PROJECT_DOCUMENTATION_INDEX.md)
- [Testing Framework](docs/testing-framework.md)
- [DELIVERY_PROFILE](DELIVERY_PROFILE.md)
- [ADR Index](docs/architecture/ADR_INDEX_GODOT.md)
- [Agents Docs Index](docs/agents/00-index.md)
- [Execution Rules](docs/agents/12-execution-rules.md)
- [RAG Sources And Session SSoT](docs/agents/13-rag-sources-and-session-ssot.md)
- [Startup, Stack, And Template Structure](docs/agents/14-startup-stack-and-template-structure.md)
- [Security, Release Health, And Runtime Ops Rules](docs/agents/15-security-release-health-and-runtime-ops.md)

## Change Policy
- Keep `summary.json` schema stable.
- Add new recovery data as sidecar files.
- Keep `AGENTS.md` as a routing map, not a duplicate rules catalog.
- Put detailed guidance into `docs/agents/`, `README.md`, or the relevant source doc.
- Put durable intent in git-tracked markdown under `execution-plans/` and `decision-logs/`.
- Put high-frequency evidence in `logs/`.
