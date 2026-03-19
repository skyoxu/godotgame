# Persistent Harness

The first-phase harness contract is local-file based.

## Pipeline Outputs
`py -3 scripts/sc/run_review_pipeline.py --task-id <id>` writes:
- `summary.json`: pipeline status and step list.
- `execution-context.json`: git state, recovery pointers, delivery profile, security profile.
- `repair-guide.json`: deterministic repair actions for the first failed step.
- `repair-guide.md`: human-readable version of the repair guide.
- `run_id.txt`: stable run id for the artifact directory.
- `latest.json`: task-scoped pointer to the newest pipeline run for the current day.

## Design Rule
- Keep `summary.json` schema stable.
- Add new recovery state as sidecar files.
- Do not use git-tracked files for high-frequency heartbeat events.
- Use git-tracked files only for durable intent and decisions.
