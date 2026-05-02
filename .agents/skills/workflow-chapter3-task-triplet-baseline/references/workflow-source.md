# Workflow Source Summary: Chapter 3

Generated from the template repo `workflow.md` by `scripts/python/update_workflow_chapter_skills.py`.

- Canonical English name: Phase 1: Task Triplet Initialization
- Source line span: 168-326
- Heading count: 11
- Command-like line count: 14
- Artifact/reference line count: 0

## Headings

- 3. Phase 1: Task Triplet Initialization
- 3.0 Choose the Chapter 3 route first
- 3.1 Prepare planning inputs
- 3.2 Extract requirement anchors
- 3.3 Generate task candidates
- 3.4 Audit the coverage matrix
- 3.5 Compile a task triplet patch
- 3.6 Build the authoritative triplet
- 3.7 Validate the triplet baseline
- 3.8 Standardize semantic review tier early
- 3.9 Chapter 3 stop-loss

## Command And Artifact Signals

- `py -3 scripts/python/extract_requirement_anchors.py --mode init`
- `py -3 scripts/python/extract_requirement_anchors.py --mode add --source-glob <changed-doc-or-glob>`
- `py -3 scripts/python/generate_task_candidates_from_sources.py --mode init --id-prefix GEN`
- `py -3 scripts/python/generate_task_candidates_from_sources.py --mode add --id-prefix <SG|NG|GM|GEN>`
- `py -3 scripts/python/audit_task_candidate_coverage.py`
- `py -3 scripts/python/compile_task_triplet.py --mode init`
- `py -3 scripts/python/compile_task_triplet.py --mode add`
- `py -3 scripts/python/compile_task_triplet.py --mode <init|add> --write`
- `py -3 scripts/python/build_taskmaster_tasks.py`
- `py -3 scripts/python/task_links_validate.py`
- `py -3 scripts/python/check_tasks_all_refs.py`
- `py -3 scripts/python/validate_task_master_triplet.py`
- `py -3 scripts/python/backfill_semantic_review_tier.py --mode conservative --write`
- `py -3 scripts/python/validate_semantic_review_tier.py --mode conservative`
