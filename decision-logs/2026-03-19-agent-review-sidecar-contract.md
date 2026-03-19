# Agent Review Sidecar Contract

- Title: agent-review-sidecar-contract
- Date: 2026-03-19
- Status: accepted
- Context: phase 1 added stable producer artifacts for the local review pipeline, but there was still no normalized reviewer verdict that could be trusted after a context reset or handed from one agent to another.
- Decision: add `scripts/sc/_agent_review_contract.py` and `scripts/sc/agent_to_agent_review.py` as a sidecar reviewer that reads `summary.json`, `execution-context.json`, `repair-guide.json`, and optional `sc-llm-review` summaries, then writes `agent-review.json` and `agent-review.md` without modifying the producer schema.
- Consequences: reviewer state becomes deterministic and portable across sessions; `latest.json` becomes the single recovery pointer for both producer and reviewer artifacts; future reviewer features should extend sidecar files instead of mutating `summary.json`.
- Related ADRs: pending future ADR for agent recovery and reviewer contracts
- Related execution plans: `execution-plans/2026-03-19-phase2-agent-review-sidecar.md`
