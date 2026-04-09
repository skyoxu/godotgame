# Project Documentation Index (godotgame)

This file is the top-level navigation for project docs in the Godot + C# template repo.

## Start Order After Context Reset

1. `README.md`
2. `AGENTS.md`
3. `docs/agents/00-index.md`
4. `docs/agents/01-session-recovery.md`
5. `docs/PROJECT_DOCUMENTATION_INDEX.md`
6. `docs/agents/13-rag-sources-and-session-ssot.md`
7. `DELIVERY_PROFILE.md`
8. `docs/testing-framework.md`
9. `docs/agents/16-directory-responsibilities.md`
10. `docs/workflows/prototype-lane.md`
11. Newest file in `execution-plans/`
12. Newest file in `decision-logs/`
13. If available: `logs/ci/<date>/sc-review-pipeline-task-<task-id>/latest.json`

## Authoritative Sources

- Taskmaster triplet: `.taskmaster/tasks/tasks.json`, `.taskmaster/tasks/tasks_back.json`, `.taskmaster/tasks/tasks_gameplay.json`
- PRD: `docs/prd/**`
- ADR: `docs/adr/ADR-*.md`, `docs/architecture/ADR_INDEX_GODOT.md`
- Base architecture: `docs/architecture/base/**`
- Overlay slices: `docs/architecture/overlays/**`
- Testing rules: `docs/testing-framework.md`
- Delivery and run protocol: `DELIVERY_PROFILE.md`, `docs/workflows/run-protocol.md`, `docs/workflows/local-hard-checks.md`

## Workflow Docs

- Daily workflow (authoritative execution order): `workflow.md`
- Example bootstrap workflow: `workflow.example.md`
- Chapter 6 optimization guide: `docs/workflows/chapter-6-t56-optimization-guide.md`
- Upgrade guide: `docs/workflows/business-repo-upgrade-guide.md`
- Template upgrade protocol: `docs/workflows/template-upgrade-protocol.md`
- Project health dashboard: `docs/workflows/project-health-dashboard.md`
- Local hard checks: `docs/workflows/local-hard-checks.md`
- Stable entrypoint index: `docs/workflows/stable-public-entrypoints.md`
- Script entrypoint index: `docs/workflows/script-entrypoints-index.md`
- Prototype lane: `docs/workflows/prototype-lane.md`

## Recovery And Stop-Loss

- Canonical recovery command: `py -3 scripts/python/dev_cli.py resume-task --task-id <task-id>`
- Deep inspection command: `py -3 scripts/python/inspect_run.py --kind pipeline --task-id <task-id>`
- Recovery reading order: `docs/agents/01-session-recovery.md`
- Stable recovery and entry routing: `docs/workflows/stable-public-entrypoints.md`
- Sidecar and consumer contract: `docs/workflows/run-protocol.md`

Read these recovery signals before reopening a full Chapter 6 pipeline:

- `latest_summary_signals.reason`
- `latest_summary_signals.run_type`
- `latest_summary_signals.reuse_mode`
- `latest_summary_signals.artifact_integrity_kind`
- `latest_summary_signals.diagnostics_keys`
- `chapter6_hints.next_action`
- `chapter6_hints.blocked_by`
- `recommended_action_why` from `active-task` or project-health when available

High-value interpretation rules:

- `run_type = planned-only` or `reason = planned_only_incomplete` means the newest bundle is evidence-only, not a resumable producer run.
- `artifact_integrity_kind` means you should fall back to the previous real producer bundle before rerunning Chapter 6.
- `recommended_action = needs-fix-fast` usually means the deterministic evidence is already good enough and you should close targeted anchors instead of paying for another full rerun.

Current stop-loss families:

- `rerun_guard`
- `llm_retry_stop_loss`
- `sc_test_retry_stop_loss`
- `waste_signals`
- `artifact_integrity`
- `recent_failure_summary`

## Evidence And Logs

- CI and local evidence: `logs/ci/<YYYY-MM-DD>/`
- Review pipeline artifact entry: `logs/ci/<YYYY-MM-DD>/sc-review-pipeline-task-<task>/latest.json`
- Local hard-check latest pointer: `logs/ci/<YYYY-MM-DD>/local-hard-checks-latest.json`
- Active-task sidecars: `logs/ci/active-tasks/task-<task>.active.json`, `logs/ci/active-tasks/task-<task>.active.md`
- Project-health latest pointer: `logs/ci/project-health/latest.json`
- Project-health dashboard page: `logs/ci/project-health/latest.html`
- Project-health report catalog: `logs/ci/project-health/report-catalog.latest.json`

## Template-Specific Navigation

- Repo map and startup stack: `docs/agents/14-startup-stack-and-template-structure.md`
- Directory responsibilities: `docs/agents/16-directory-responsibilities.md`
- Architecture guardrails: `docs/agents/05-architecture-guardrails.md`
- Persistent harness: `docs/agents/03-persistent-harness.md`
- Closed-loop testing: `docs/agents/04-closed-loop-testing.md`
- Quality gates and DoD: `docs/agents/09-quality-gates-and-done.md`
- Execution rules: `docs/agents/12-execution-rules.md`
- Security, release health, and runtime ops: `docs/agents/15-security-release-health-and-runtime-ops.md`

## Notes

- `AGENTS.md` is the repository map; keep detailed guidance in `docs/agents/**` and workflow docs instead of duplicating long-form rules there.
- `docs/workflows/script-entrypoints-index.md` is the parameter and dependency index, not the default daily execution order.
- Business repos copied from this template should read `docs/workflows/business-repo-upgrade-guide.md` and `docs/workflows/template-upgrade-protocol.md` together when upgrading.
