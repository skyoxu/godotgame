# Persistent Harness

The first-phase harness contract is local-file based. The second-phase reviewer consumes those files without changing the producer schema.

## Pipeline Outputs
`py -3 scripts/sc/run_review_pipeline.py --task-id <id>` writes and, unless `--dry-run` or `--skip-agent-review` is set, also refreshes the reviewer sidecar:
- `summary.json`: pipeline status and step list.
- `execution-context.json`: git state, recovery pointers, delivery profile, and security profile.
- `repair-guide.json`: deterministic repair actions for the first failed step.
- `repair-guide.md`: human-readable version of the repair guide.
- `run_id.txt`: stable run id for the artifact directory.
- `latest.json`: task-scoped pointer to the newest pipeline run for the current day.

## Reviewer Sidecar Outputs
`py -3 scripts/sc/agent_to_agent_review.py --task-id <id>` can also be run standalone to rebuild reviewer artifacts from the latest producer outputs:
- `agent-review.json`: deterministic machine-readable reviewer contract.
- `agent-review.md`: human-readable reviewer summary.
- `latest.json`: updated with `agent_review_json_path` and `agent_review_md_path`.

## Design Rule
- Keep `summary.json` schema stable.
- Add new recovery state as sidecar files.
- Do not use git-tracked files for high-frequency heartbeat events.
- Use git-tracked files only for durable intent and decisions.
- Consume stable artifact paths before falling back to broader repo inspection.
