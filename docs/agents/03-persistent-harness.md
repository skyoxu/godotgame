# Persistent Harness

The first-phase harness contract is local-file based. The second-phase reviewer consumes those files without changing the producer schema.

## Pipeline Outputs
`py -3 scripts/sc/run_review_pipeline.py --task-id <id>` writes and, unless `--dry-run`, `--skip-agent-review`, or the active delivery profile sets `agent_review.mode=skip`, also refreshes the reviewer sidecar:
- `summary.json`: pipeline status and step list.
- `execution-context.json`: git state, recovery pointers, delivery profile, security profile, marathon recovery snapshot, diff summary, and the latest agent-review recommendation snapshot.
- `repair-guide.json`: deterministic repair actions for the first failed step, wall-time/context-refresh stop, or isolated reviewer follow-up.
- `repair-guide.md`: human-readable version of the repair guide.
- `run_id.txt`: stable run id for the artifact directory.
- `marathon-state.json`: resumable step checkpoint state, attempt counters, wall-time stop markers, fork metadata, diff baseline/current/growth snapshot, category/axis summary, context-refresh flags, and the normalized agent-review action (`resume|refresh|fork`).
- `latest.json`: task-scoped pointer to the newest pipeline run for the current day, including `marathon_state_path`.

## Reviewer Sidecar Outputs
`py -3 scripts/sc/agent_to_agent_review.py --task-id <id>` can also be run standalone to rebuild reviewer artifacts from the latest producer outputs:
- `agent-review.json`: deterministic machine-readable reviewer contract, including `explain.recommended_action`, `explain.summary`, and `explain.reasons` for direct recovery guidance.
- `agent-review.md`: human-readable reviewer summary.
- `latest.json`: updated with `agent_review_json_path` and `agent_review_md_path`; the pipeline preserves those pointers for the same run id when it persists later sidecars.

## Design Rule
- Keep `summary.json` schema stable.
- Add recovery state only as sidecar files.
- Agent-review verdicts must not overwrite producer status; they only influence `marathon-state.json`, `execution-context.json`, and `repair-guide.json/md`.
- Do not use git-tracked files for high-frequency heartbeat events.
- Use git-tracked files only for durable intent and decisions.
- Consume stable artifact paths before falling back to broader repo inspection.
