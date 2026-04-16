# Cloud Platform Evolution Plan

This document records the recommended evolution path for moving the current template workflow to the cloud while keeping the repository-native Codex orchestration model.

## Goal

Keep the current repository workflow as the execution kernel:

- `workflow.md`
- `AGENTS.md`
- `scripts/python/dev_cli.py`
- `scripts/sc/run_review_pipeline.py`
- `scripts/sc/llm_review_needs_fix_fast.py`
- task sidecars under `logs/ci/**`
- durable docs under `execution-plans/**` and `decision-logs/**`

Do not rewrite the workflow into a new platform-specific state machine. The cloud layer should host, index, and recover the existing workflow instead of replacing it.

## Core Principle

Separate three layers:

1. Git source of truth
2. Cloud workspace as the execution source of truth
3. Browser as the access surface

Git stores code and durable docs. The cloud workspace stores runtime state, sidecars, and evidence. The browser only triggers runs, reads artifacts, and handles approvals.

## What Stays In Git

Keep these in the Git repository:

- source code
- docs under `docs/**`
- workflow docs such as `workflow.md`
- scripts under `scripts/**`
- durable intent under `execution-plans/**`
- durable decisions under `decision-logs/**`

## What Stays In Cloud Workspaces

Keep these in the cloud execution workspace, not as the primary local user copy:

- `logs/**`
- `logs/ci/active-tasks/**`
- task run sidecars such as `latest.json`, `summary.json`, `execution-context.json`
- repair artifacts such as `repair-guide.json`, `repair-guide.md`
- agent review artifacts such as `agent-review.json`, `agent-review.md`
- event streams such as `run-events.jsonl`
- local task/runtime caches

These files are the recovery substrate for:

- `resume-task`
- `chapter6-route`
- `inspect-run`
- `project-health-scan`

## Why The Workspace Must Be Cloud-Resident

The repository already relies on sidecar-driven recovery. A pure local-user workspace would break long-running execution, recovery after disconnect, and consistent environment control.

Cloud-resident workspaces provide:

- stable dependency versions
- durable recovery artifacts
- long-running task execution
- browser-only access for end users
- better session continuity across devices and days

## Recommended MVP Architecture

Build a minimal platform around the current workflow with six components.

### 1. Git Source

Responsibilities:

- clone/fetch/checkout
- branch selection
- source history

Do not run tasks here.

### 2. Workspace Manager

Responsibilities:

- allocate one workspace per tenant/project/workspace-id
- restore an existing workspace
- sync repository state into the workspace
- clean up expired workspaces

Recommended path layout:

```text
/workspaces/<tenant>/<project>/<workspace-id>/
```

### 3. Runner

Responsibilities:

- run only top-level repository entrypoints
- never reimplement workflow logic

Recommended commands:

```powershell
py -3 scripts/python/dev_cli.py resume-task --task-id <id> --recommendation-only
py -3 scripts/python/dev_cli.py chapter6-route --task-id <id> --recommendation-only
py -3 scripts/python/dev_cli.py run-single-task-chapter6 --task-id <id> --godot-bin "<...>" --delivery-profile fast-ship
py -3 scripts/python/dev_cli.py project-health-scan
```

### 4. Artifact Indexer

Responsibilities:

- discover the latest task/run artifacts
- expose compact summaries to the web layer
- point the UI at authoritative files instead of copying logic into the frontend

First-class indexed artifacts should include:

- `logs/ci/project-health/latest.html`
- `logs/ci/active-tasks/task-<id>.active.md`
- task-scoped `latest.json`
- `summary.json`
- `repair-guide.md`
- `agent-review.md`
- `execution-plans/**`
- `decision-logs/**`

### 5. Web API

Responsibilities:

- start runs
- resume runs
- read artifacts
- expose approvals
- expose run status

Do not compute workflow decisions here when the repository scripts already do.

### 6. Browser UI

Responsibilities:

- project list
- workspace list
- task start/recovery page
- project health view
- artifact viewing
- approval actions

Do not make the browser a second workflow engine.

## Workspace Layout

A practical first layout is:

```text
/workspaces/<tenant>/<project>/<workspace-id>/
  /repo
  /runtime
    /stdout
    /stderr
    /commands
  /meta
    workspace.json
    latest-run.json
    approvals.json
```

Notes:

- `repo/` contains the checked-out project and all existing repository-native logs/sidecars.
- `runtime/` stores platform-level execution logs.
- `meta/` stores platform metadata, not workflow truth.

## Minimal Platform Database

A single SQLite database is enough for the first version.

### projects

- `id`
- `name`
- `repo_url`
- `default_branch`
- `created_at`

### workspaces

- `id`
- `project_id`
- `tenant`
- `branch`
- `path`
- `status`
- `last_synced_at`

### runs

- `id`
- `workspace_id`
- `task_id`
- `run_type`
- `command`
- `status`
- `started_at`
- `finished_at`
- `run_dir`
- `stdout_path`
- `stderr_path`

### approvals

- `id`
- `workspace_id`
- `task_id`
- `status`
- `decision`
- `reason`
- `updated_at`

## Minimal API Surface

Recommended first endpoints:

### Projects

- `POST /projects`
- `GET /projects`
- `GET /projects/:id`

### Workspaces

- `POST /projects/:id/workspaces`
- `GET /projects/:id/workspaces`
- `GET /workspaces/:id`
- `POST /workspaces/:id/sync`

### Runs

- `POST /workspaces/:id/run/resume-task`
- `POST /workspaces/:id/run/chapter6-route`
- `POST /workspaces/:id/run/chapter6`
- `POST /workspaces/:id/run/project-health`
- `GET /runs/:run_id`
- `GET /runs/:run_id/logs`
- `POST /runs/:run_id/cancel`

### Artifacts

- `GET /workspaces/:id/artifacts/active-task?task_id=...`
- `GET /workspaces/:id/artifacts/latest?task_id=...`
- `GET /workspaces/:id/artifacts/repair-guide?task_id=...`
- `GET /workspaces/:id/artifacts/agent-review?task_id=...`
- `GET /workspaces/:id/artifacts/project-health`
- `GET /workspaces/:id/artifacts/execution-plans`
- `GET /workspaces/:id/artifacts/decision-logs`

## Minimal UI Pages

A minimal usable browser UI only needs:

1. Project list
2. Workspace list
3. Task execution page
4. Recovery/active-task page
5. Artifact viewer page
6. Project health page

The task execution page should first call recovery commands before offering a full Chapter 6 run.

## Execution Contract

The platform should treat repository scripts as the decision authority.

The browser/API/runner should not reinterpret:

- `preferred_lane`
- `Recommended command`
- `Forbidden commands`
- stop-loss families
- approval state transitions

Those should remain owned by repository-native commands:

- `resume-task`
- `chapter6-route`
- `inspect-run`
- `run-single-task-chapter6`

## Dependency Model

### End User Device

The end user should normally need only:

- browser
- network access
- login credential

The end user should not need local installation of:

- `git`
- `python`
- `node.js`
- `codex`
- `.NET SDK`
- `Godot .NET`

### Cloud Worker

The cloud worker should carry the real execution dependencies:

- Windows environment
- `git`
- `python`
- `node.js`
- `codex`
- `.NET SDK 8`
- `Godot .NET`
- project-specific runtime dependencies
- `OPENAI_API_KEY` when `openai-api` transport is enabled

## What To Borrow From A Multi-Tenant Agent Platform

The right lessons are runtime and hosting lessons, not a language rewrite:

- separate workspace/runtime concerns from workflow concerns
- keep session state rebuildable from disk artifacts
- store hot state in cache, rebuild cold state from durable files
- isolate users/projects/workspaces at the filesystem boundary
- let the frontend observe and trigger, not decide

## What Not To Do First

Do not start with:

- rewriting the workflow into a new orchestration engine
- building a new Rust claw runtime
- a full skills marketplace
- distributed session infrastructure
- object storage as a hard requirement
- complex multi-agent collaboration UX

Those are later-stage concerns.

## Suggested Evolution Phases

### Phase A: Single-Node Cloud Runner

Goal:

- one Windows cloud machine
- one web service
- one runner process
- one SQLite metadata DB
- durable workspaces on local disk

Success criteria:

- can run existing top-level commands remotely
- can recover tasks from browser
- can browse project-health and task artifacts

### Phase B: Multi-Tenant Workspace Hosting

Goal:

- user login
- project/workspace catalog
- approval handling in the browser
- multiple persistent workspaces
- stable runner queueing

Success criteria:

- one platform can host multiple users/projects without workspace collisions
- sidecars remain isolated and durable

### Phase C: Storage Abstraction And Scale-Out

Goal:

- abstract file storage for artifacts and durable docs
- support remote/object-backed storage later
- support node affinity and worker expansion

Success criteria:

- workspace restoration is not tied to one machine forever
- platform can scale without rewriting repository workflow logic

## Suggested First Build Order

1. workspace manager
2. runner for top-level commands
3. artifact indexer
4. web API
5. browser UI
6. approval handling

This order preserves the existing repository kernel and delivers value early.

## One-Sentence Rule

The platform should host the current workflow, not replace it.
