# Phase 2 Agent Review Sidecar

- Title: phase2-agent-review-sidecar
- Status: done
- Branch: main
- Goal: add a deterministic reviewer sidecar that consumes pipeline artifacts and survives context resets
- Scope: `scripts/sc/_agent_review_contract.py`, `scripts/sc/agent_to_agent_review.py`, `scripts/sc/tests/test_agent_review_contract.py`, `scripts/sc/tests/test_agent_to_agent_review.py`, `docs/agents/`, `execution-plans/`, `decision-logs/`
- Current step: archived after phase 2 verification and regression
- Last completed step: implemented `agent-review.json/md` generation and task-scoped `latest.json` updates
- Stop-loss: do not change the existing `summary.json` producer schema in phase 2
- Next action: decide whether phase 3 should invoke agent review automatically from the broader harness
- Related ADRs: pending future ADR for agent recovery and reviewer contracts
- Related decision logs: `decision-logs/2026-03-19-agents-index-and-persistent-harness.md`, `decision-logs/2026-03-19-agent-review-sidecar-contract.md`
- Related pipeline artifacts: `logs/ci/2026-03-19/sc-review-pipeline-task-1-2164e633e28042e2a223cee8b0fb267d/`
