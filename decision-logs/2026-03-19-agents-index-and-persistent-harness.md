# Agents Index And Persistent Harness

- Title: agents-index-and-persistent-harness
- Date: 2026-03-19
- Status: accepted
- Context: `AGENTS.md` had grown into a long encyclopedia and the local review pipeline produced only `summary.json`, which was not enough for fast recovery after a context reset.
- Decision: keep `AGENTS.md` short and index-only, move durable guidance into `docs/agents/`, add git-tracked `execution-plans/` and `decision-logs/`, and add `execution-context.json` plus `repair-guide.json/md` as sidecar outputs of `scripts/sc/run_review_pipeline.py`.
- Consequences: recovery now depends on a small set of stable files instead of chat history alone; `summary.json` schema stays stable; future harness work should extend sidecar files instead of mutating the current summary contract.
- Related ADRs: pending future ADR for agent recovery and harness persistence
- Related execution plans: `execution-plans/2026-03-19-phase1-agent-harness-foundation.md`
