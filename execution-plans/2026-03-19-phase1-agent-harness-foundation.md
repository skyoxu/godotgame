# Phase 1 Agent Harness Foundation

- Title: phase1-agent-harness-foundation
- Status: active
- Branch: main
- Goal: establish durable recovery state, persistent local harness outputs, and a slim AGENTS index
- Scope: `AGENTS.md`, `docs/agents/`, `execution-plans/`, `decision-logs/`, `scripts/sc/run_review_pipeline.py`
- Current step: finish first-phase verification and prepare commit
- Last completed step: added `execution-context.json` and `repair-guide.json/md` sidecar outputs to `run_review_pipeline.py`
- Stop-loss: do not change existing `summary.json` schema in phase 1
- Next action: review docs and new outputs, then commit the first-phase foundation
- Related ADRs: pending future ADR for persistent harness and agent recovery model
- Related decision logs: `decision-logs/2026-03-19-agents-index-and-persistent-harness.md`
- Related pipeline artifacts: local dry-run artifacts under `logs/ci/2026-03-19/`
