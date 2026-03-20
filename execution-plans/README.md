# Execution Plans

Store durable execution progress here.

Rules:
- one file per active initiative or focused branch
- update checkpoints instead of rewriting history in chat only
- include `Branch`, `Git Head`, `Goal`, `Current step`, `Stop-loss`, and `Next action`
- use `Related decision logs` as the durable decision-link set for recovery
- include `Recovery command`, `Open questions`, and `Exit criteria` so a later agent can resume without chat history
- include `Related run id` and `Related latest.json` when a pipeline run exists
- if a historical item has no preserved run id, write `n/a` and the reason explicitly
- keep high-frequency runtime noise in `logs/`, not here
