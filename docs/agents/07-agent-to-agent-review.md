# Agent-to-Agent Review

`py -3 scripts/sc/agent_to_agent_review.py --task-id <id>` builds a stable reviewer verdict from local pipeline artifacts.

## Inputs
Required producer files in `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/`:
- `summary.json`
- `execution-context.json`
- `repair-guide.json`

Optional producer inputs:
- `sc-llm-review` step `summary_file`
- step log files referenced by `summary.json`

The reviewer does not rescan the full repository when these artifacts exist.

## Outputs
The reviewer writes sidecar files next to the producer artifacts:
- `agent-review.json`
- `agent-review.md`

It also updates `logs/ci/<date>/sc-review-pipeline-task-<task>/latest.json` with:
- `agent_review_json_path`
- `agent_review_md_path`

## Verdict Rules
- `block`
  - required producer artifacts are missing
  - `summary.json` shows a failed `sc-test` step
  - `summary.json` shows a failed `sc-acceptance-check` step
- `needs-fix`
  - required artifacts exist, but `sc-llm-review` reports non-OK findings
  - non-blocking artifact-integrity issues exist
- `pass`
  - no blocking or non-blocking findings remain

## Finding Contract
Each finding carries:
- `finding_id`
- `severity`
- `category`
- `owner_step`
- `evidence_path`
- `message`
- `suggested_fix`
- `commands`

## Operator Flow
1. Run `py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin "$env:GODOT_BIN"`.
2. If the run was not `--dry-run` and did not use `--skip-agent-review`, open `agent-review.md` directly.
3. If you need to rebuild reviewer artifacts only, run `py -3 scripts/sc/agent_to_agent_review.py --task-id <id>`.
4. If verdict is `block`, follow `repair-guide.md` before any broader diagnosis.
5. If verdict is `needs-fix`, address the listed reviewer findings and rerun the relevant step.
6. If verdict is `pass`, keep `latest.json` as the recovery pointer for the next session.

## Stop-Loss
- Do not mutate the producer `summary.json` schema just to satisfy reviewer needs.
- Add reviewer-specific data only as sidecar artifacts.
- Treat empty or missing `summary_file` paths as absent, not as repository-root fallbacks.
