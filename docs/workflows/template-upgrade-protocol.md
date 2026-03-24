# Template Upgrade Protocol

Purpose: define the **stable** migration protocol for moving a business repository onto newer template behavior.

This file is the durable protocol. Use `docs/workflows/business-repo-upgrade-guide.md` as the compare-range-specific report that tells you **what changed this time**.

## Inputs
1. Current target-repo state:
   - branch / git head
   - solution and project names
   - real `.taskmaster/tasks/*.json` presence
   - enabled workflows and secrets
2. Current template compare report:
   - `docs/workflows/business-repo-upgrade-guide.md`
3. Local business constraints:
   - product name / repo name
   - PRD-ID / overlay roots
   - domain contract locations
   - CI strictness and delivery profile defaults

## File Classes
- `safe-overwrite`
  - Template-generic scripts, schemas, docs, and tests with no project naming or domain binding.
- `merge-carefully`
  - Entry docs, AGENTS routing, CI workflows, README Quick Links, and any file already customized in the business repo.
- `localize-required`
  - Files containing repo name, solution name, product ID, PRD-ID, overlay root, export path, or project-specific runtime paths.
- `project-specific-do-not-copy`
  - Domain contracts, real gameplay overlays, real task triplet data, release identifiers, environment secrets, and store/platform metadata.
- `generated-or-ephemeral`
  - `logs/**`, temporary reports, replay outputs, generated baselines unless the protocol explicitly says to promote them.

## Migration Order
1. Baseline and identity
   - Confirm the target repo already builds and that solution/project names are known.
   - Confirm whether `.taskmaster/tasks/*.json` are real or still template fallback.
2. Script/runtime foundation
   - Sync reusable `scripts/python/**`, `scripts/sc/**`, schemas, and helper tests.
   - Bring over any new dependencies referenced by those scripts in the same batch.
3. Recovery and sidecar protocol
   - Sync `latest.json` producers/consumers, `inspect_run.py`, `resume_task.py`, `active-task` behavior, marathon state, and repair-guide sidecars.
4. Workflow and CI surface
   - Sync workflow changes only after local scripts are present.
   - Rebind paths, solution names, secrets, and delivery/security defaults.
5. Docs and routing
   - Update `AGENTS.md`, `README.md`, docs indexes, and workflow docs so operators can discover the new behavior.
6. Business-local adaptation
   - Rename project references, update overlay roots, adapt domain contract paths, and remove template fallback assumptions.
7. Validation and stop-loss
   - Run the minimum validation bundle before opening a PR.

## Required Localization Checklist
- Replace template repo name with the business repo name.
- Replace solution / csproj names and runtime paths.
- Replace `PRD-Example` or template overlay roots with the business PRD IDs.
- Replace template fallback assumptions with real `.taskmaster/tasks/*.json` once the business repo has them.
- Re-check any script that references domain contracts, test roots, or project-relative resources.

## Validation Sequence
1. Deterministic local checks
   - `py -3 scripts/python/dev_cli.py run-local-hard-checks --godot-bin $env:GODOT_BIN`
2. Task-scoped review pipeline on at least one real task
   - `py -3 scripts/sc/run_review_pipeline.py --task-id <id> --godot-bin $env:GODOT_BIN`
3. Task metadata / overlay / contract integrity
   - `py -3 scripts/python/validate_task_master_triplet.py`
   - `py -3 scripts/python/check_tasks_all_refs.py`
   - `py -3 scripts/python/validate_contracts.py`
4. Delivery-profile-sensitive checks when enabled
   - `py -3 scripts/python/run_gate_bundle.py --mode hard`

## Stop-Loss Rules
- Do not copy compare-specific conclusions into stable docs without extracting the durable rule first.
- Do not overwrite business task triplet files with template examples.
- Do not copy project names, PRD IDs, or solution paths blindly.
- Do not wire new workflows until all referenced local scripts exist.
- If a copied script introduces a new dependency, copy or adapt that dependency in the same migration step.

## Relationship To Compare Reports
- `template-upgrade-protocol.md`
  - Stable SSoT for **how** to upgrade.
- `business-repo-upgrade-guide.md`
  - Time-bound record of **what changed in one compare range**.
