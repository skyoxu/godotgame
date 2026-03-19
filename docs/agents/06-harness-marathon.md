# Harness Marathon

Phase 2 target: long-running harness execution with controlled resume.

Planned policy:
- max wall time per run
- max retries per failing step
- checkpoint after each completed step
- context refresh after repeated failure or large diff growth
- explicit resume, fork, and abort rules

First-phase stop-loss:
- use `execution-plans/` and `decision-logs/` for durable state
- use `execution-context.json` as the latest local recovery snapshot
