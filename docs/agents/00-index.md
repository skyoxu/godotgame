# Agents Docs Index

Purpose: keep [AGENTS.md](../../AGENTS.md) short and move durable guidance here.

## Read Order After Context Reset
1. [01-session-recovery.md](01-session-recovery.md)
2. [02-repo-map.md](02-repo-map.md)
3. [03-persistent-harness.md](03-persistent-harness.md)
4. [07-agent-to-agent-review.md](07-agent-to-agent-review.md)
5. Newest files in `execution-plans/` and `decision-logs/`
6. `logs/ci/<date>/sc-review-pipeline-task-<task>/latest.json` if a local run already exists

## By Topic
- Project overview, startup, stack, and legacy AGENTS background sections:
  - [08-project-basics.md](08-project-basics.md)
  - [../../README.md](../../README.md)
  - [../PROJECT_DOCUMENTATION_INDEX.md](../PROJECT_DOCUMENTATION_INDEX.md)
- Harness, recovery, and review handoff:
  - [01-session-recovery.md](01-session-recovery.md)
  - [03-persistent-harness.md](03-persistent-harness.md)
  - [07-agent-to-agent-review.md](07-agent-to-agent-review.md)
- Closed-loop testing, quality gates, and Definition of Done:
  - [04-closed-loop-testing.md](04-closed-loop-testing.md)
  - [09-quality-gates-and-done.md](09-quality-gates-and-done.md)
  - [../testing-framework.md](../testing-framework.md)
- Architecture, ADRs, and template rules:
  - [05-architecture-guardrails.md](05-architecture-guardrails.md)
  - [10-template-customization.md](10-template-customization.md)
  - [../architecture/ADR_INDEX_GODOT.md](../architecture/ADR_INDEX_GODOT.md)
- AGENTS maintenance and information architecture:
  - [11-agents-construction-principles.md](11-agents-construction-principles.md)

## Repository State Files
- `execution-plans/` stores current execution intent and checkpoints.
- `decision-logs/` stores decisions that changed architecture, workflow, or guardrails.
- `logs/ci/<date>/sc-review-pipeline-task-<task>/latest.json` points to the latest local pipeline artifacts, including `summary.json`, `execution-context.json`, `repair-guide.*`, and `agent-review.*` when generated.
