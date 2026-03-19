# Agent-to-Agent Review

Phase 2 target: producer and reviewer agents work on stable artifacts, not full ad-hoc repo scans.

Producer outputs:
- `summary.json`
- `execution-context.json`
- `repair-guide.json`
- step logs and step summary files

Reviewer contract:
- read the producer artifacts first
- produce a deterministic verdict: `pass`, `needs-fix`, or `block`
- attach evidence path and suggested fix for each finding
- stop after one or two repair rounds before escalation
