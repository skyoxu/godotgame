# Agents Docs Index

Purpose: keep [AGENTS.md](../../AGENTS.md) short and move durable guidance here.

Read order after a context reset:
1. [01-session-recovery.md](01-session-recovery.md)
2. [02-repo-map.md](02-repo-map.md)
3. [03-persistent-harness.md](03-persistent-harness.md)
4. [04-closed-loop-testing.md](04-closed-loop-testing.md)
5. [05-architecture-guardrails.md](05-architecture-guardrails.md)
6. [06-harness-marathon.md](06-harness-marathon.md)
7. [07-agent-to-agent-review.md](07-agent-to-agent-review.md)

Repository state files:
- `execution-plans/` stores current execution intent and checkpoints.
- `decision-logs/` stores decisions that changed architecture, workflow, or guardrails.
- `logs/ci/<date>/sc-review-pipeline-task-<task>/latest.json` points to the latest local pipeline artifacts.
