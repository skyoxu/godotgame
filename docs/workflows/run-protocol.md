# Harness Run Protocol

## Purpose

This document defines the local file-protocol harness used by `scripts/sc/run_review_pipeline.py` and the repo-scoped `py -3 scripts/python/dev_cli.py run-local-hard-checks` wrapper.

It is the human-readable contract for durable local runs. The executable schemas remain under `scripts/sc/schemas/` and must not be duplicated into `docs/`.

## Scope

This protocol is intentionally local and file-backed:

- no JSON-RPC server
- no daemon runtime
- no multi-client session coordination
- no SSE/Web reconnect transport

The goal is deterministic local recovery, not platform-grade remote orchestration.

## SSoT

- Producer entry: `scripts/sc/run_review_pipeline.py`
- Repo-scoped producer entry: `scripts/python/local_hard_checks_harness.py`
- Stable CLI entry for repo-scoped runs: `py -3 scripts/python/dev_cli.py run-local-hard-checks`
- Reviewer rebuild entry: `scripts/sc/agent_to_agent_review.py`
- Run-event schema: `scripts/sc/schemas/sc-run-event.schema.json`
- Harness-capabilities schema: `scripts/sc/schemas/sc-harness-capabilities.schema.json`
- Repo-scoped local-hard-checks summary schema: `scripts/sc/schemas/sc-local-hard-checks-summary.schema.json`
- Example event stream: `docs/workflows/examples/sc-run-events.example.jsonl`

## Core Model

Conceptually, the harness uses these local concepts:

- `task scope`: `logs/ci/<date>/sc-review-pipeline-task-<task>/latest.json`
- `repo scope`: `logs/ci/<date>/local-hard-checks-latest.json`
- `run`: one artifact directory identified by `run_id`
- `turn`: one lifecycle transition such as `run_started`, `run_resumed`, `run_forked`, `run_completed`, or `run_aborted`
- `item`: one step transition, sidecar file, approval artifact, or reviewer artifact

This is protocolized local orchestration, not RPC.

## Artifact Layout

For one task-scoped review run, the producer writes:

- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/summary.json`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/execution-context.json`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/repair-guide.json`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/repair-guide.md`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/marathon-state.json`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/run-events.jsonl`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/harness-capabilities.json`
- `logs/ci/<date>/sc-review-pipeline-task-<task>-<run_id>/run_id.txt`

For one repo-scoped local hard-check run, the producer writes:

- `logs/ci/<date>/local-hard-checks-<run_id>/summary.json`
- `logs/ci/<date>/local-hard-checks-<run_id>/execution-context.json`
- `logs/ci/<date>/local-hard-checks-<run_id>/repair-guide.json`
- `logs/ci/<date>/local-hard-checks-<run_id>/repair-guide.md`
- `logs/ci/<date>/local-hard-checks-<run_id>/run-events.jsonl`
- `logs/ci/<date>/local-hard-checks-<run_id>/harness-capabilities.json`
- `logs/ci/<date>/local-hard-checks-<run_id>/run_id.txt`
- `logs/ci/<date>/local-hard-checks-<run_id>/<step>.log`

Optional sidecars for task-scoped review runs:

- `approval-request.json`
- `approval-response.json`
- `agent-review.json`
- `agent-review.md`

Task-scoped pointer:

- `logs/ci/<date>/sc-review-pipeline-task-<task>/latest.json`

Repo-scoped pointer:

- `logs/ci/<date>/local-hard-checks-latest.json`

## Sidecar Roles

| Artifact | Owner | Role |
| --- | --- | --- |
| `summary.json` | producer pipeline | canonical run status and step list |
| `execution-context.json` | producer pipeline | git state, profile state, recovery pointers, latest reviewer recommendation snapshot |
| `repair-guide.json` | producer pipeline | machine-readable next repair action |
| `repair-guide.md` | producer pipeline | human-readable repair instructions |
| `marathon-state.json` | producer pipeline | checkpoint, retry, wall-time, refresh, fork metadata; task-scoped review runs only |
| `run-events.jsonl` | producer pipeline | append-only lifecycle and step timeline |
| `harness-capabilities.json` | producer pipeline | machine-readable protocol capabilities |
| `approval-request.json` | producer pipeline | soft approval request for risky fork/recovery flows; task-scoped review runs only |
| `approval-response.json` | operator or follow-up tool | soft approval response envelope; task-scoped review runs only |
| `agent-review.json` | reviewer sidecar | normalized reviewer verdict and recommended action; task-scoped review runs only |
| `agent-review.md` | reviewer sidecar | human-readable reviewer summary; task-scoped review runs only |
| `latest.json` | producer pipeline and reviewer sidecar | task-scoped pointer to newest run artifacts |
| `local-hard-checks-latest.json` | repo-scoped producer pipeline | repo-scoped pointer to newest local hard-check run artifacts |

## Event Stream Contract

`run-events.jsonl` is append-only. Each line must satisfy `scripts/sc/schemas/sc-run-event.schema.json`.

Required fields:

- `schema_version`
- `ts`
- `event`
- `task_id`
- `run_id`
- `delivery_profile`
- `security_profile`
- `step_name`
- `status`
- `details`

Field rules:

- `step_name` may be `null` for run-level events
- `status` may be `null` for run-level events
- `details` is always an object and may be empty
- `task_id` and `run_id` are strings, even when the task number is numeric

Common event names:

- `run_started`
- `run_resumed`
- `run_forked`
- `run_completed`
- `run_aborted`
- `wall_time_exceeded`
- `step_planned`
- `step_skipped`
- `step_completed`
- `step_failed`
- `approval_updated` when approval state changes

The protocol does not currently reserve a transport-level request id. Correlation happens through `task_id`, `run_id`, and artifact paths.

## Recovery Actions

`harness-capabilities.json` declares the currently supported recovery actions:

- `resume`
- `refresh`
- `fork`
- `abort`

Interpretation:

- `resume`: continue the same run artifact set
- `refresh`: same run intent, but context should be refreshed before continuing
- `fork`: create a clean continuation run, optionally gated by soft approval
- `abort`: mark the run as intentionally stopped

## Consumer Read Order

When recovering after context loss, read in this order:

1. `latest.json`
2. `summary.json`
3. `execution-context.json`
4. `repair-guide.json` or `repair-guide.md`
5. `agent-review.json` if present
6. `run-events.jsonl` if lifecycle sequencing is still unclear
7. approval files only when the recovery action is `fork`

Do not scrape console logs first if these files already exist.

## Design Rules

- `summary.json` stays producer-owned and must not be rewritten by reviewer sidecars.
- Recovery metadata belongs in sidecars, not in git-tracked heartbeat files.
- `latest.json` is the task-scoped entry point; consumers should not guess the newest run by directory scanning first.
- Schemas under `scripts/sc/schemas/` are executable SSoT; docs explain them but do not duplicate them.

## Minimal Validation

- Validate event lines against `scripts/sc/schemas/sc-run-event.schema.json`
- Validate capabilities against `scripts/sc/schemas/sc-harness-capabilities.schema.json`
- Keep `docs/workflows/examples/sc-run-events.example.jsonl` aligned with the executable schema
- Keep `scripts/sc/tests/test_pipeline_sidecar_protocol.py` green after protocol changes

