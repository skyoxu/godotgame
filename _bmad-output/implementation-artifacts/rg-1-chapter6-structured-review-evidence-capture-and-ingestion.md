# Story RG-1: Chapter 6 Structured Review Evidence Capture And Ingestion

Status: ready-for-dev

## Story

作为 review-evidence 维护者，
我希望 Chapter 6 的每个 LLM reviewer 输出都能被仓库策略约束、解析为 canonical evidence sidecar，并由确定性逻辑派生 verdict，
从而让后续兼容投影只消费可核查 finding，而不是继续信任终端 Markdown verdict。

## Phase And Ownership

- RG phase: `RG-1`
- Requirement IDs: `RGR-007`, `RGR-008`, `RGR-009`, `RGR-010`, `RGR-011`, `RGR-012`, `RGR-015`, `RGR-016`
- Implementation owner: review-evidence maintainer
- Independent reviewer: phase-exit reviewer
- Rollback owner: review-pipeline maintainer
- Compatibility mode: preserve `playable-ea=legacy-observe`, `fast-ship=advisory`, `standard=advisory`
- Expected evidence: `logs/ci/<YYYY-MM-DD>/review-evidence-rg1-chapter6-capture/`

## Acceptance Criteria

1. Repository-owned prompt policy is appended after external/project agent prompt content for every Chapter 6 LLM reviewer and cannot be removed by lower-precedence prompt text. It requires exact anchors, concrete failure chain, surrounding context, defensible severity, the P0/P1 proof set, legitimate zero findings, Unknown for missing input, the false-positive catalog, one terminal structured block, and one diagnostic raw verdict.
2. Each completed reviewer output retains raw Markdown and produces exactly one task/run/reviewer-scoped `review-evidence-<agent>.json` sidecar that validates through `scripts/sc/_review_evidence_schema.py` against the protected v1 schema.
3. Missing, malformed, duplicate, or unparseable structured output derives `Unknown`; it cannot derive clean and cannot create an actionable product finding.
4. The minimum RG-1 validator resolves repository-relative anchors, checks line/heading/field bounds and quote/snippet agreement, applies severity proof requirements, records disposition/reason codes, derives summary counts from final dispositions, and derives `OK | Needs Fix | Unknown` without another LLM call.
5. Zero surviving actionable findings derives `OK`; a raw `Needs Fix` with zero surviving findings cannot create a compatibility finding or `Needs Fix` projection.
6. Every derived `Needs Fix` exposes at least one validated or demoted actionable finding. Compatibility output creates one finding per surviving actionable finding and never creates the current generic fixed-medium finding.
7. Derived verdict ingestion is additive and backward compatible: existing producer-owned pipeline `summary.json` fields and semantics remain unchanged; raw output paths remain readable; evidence pointers/counts/version fields are additive only.
8. Derived projection follows ADR-0032 and book 06 exactly: `OK -> pass/none`, actionable `Needs Fix -> needs-fix` with existing action policy, and zero-actionable `Unknown -> block/resume` as an evidence-inspection action rather than a product defect.
9. Timeout with no usable evidence derives `Unknown`; timeout with a complete structured block validates normally while timeout remains a separate observation.
10. All edited/new Python implementation modules remain below 400 lines. Existing oversized `_llm_review_engine.py` must be reduced by extraction rather than enlarged; `agent_to_agent_review.py` must not grow beyond its current boundary.
11. Focused prompt, parser, validator, sidecar, summary, and compatibility tests pass, followed by the repository review-pipeline regression set. Evidence is written under `logs/**`.
12. This story does not change residual routing, residual persistence/idempotency, Chapter 5 semantics, Chapter 3/4/7 profiles, recovery routing, `warn/require` promotion, or runtime enforcement outside the Chapter 6 capture/ingestion boundary.

## Tasks / Subtasks

- [ ] Task 1: Add failing prompt-policy tests (AC: 1, 11)
  - [ ] Cover all Chapter 6 reviewer profiles: code, security, test, semantic, architecture, performance.
  - [ ] Prove external/user agent prompt content cannot remove the repository fact gate or zero-findings rule.
  - [ ] Prove the structured block is terminal and singular.
- [ ] Task 2: Implement repository-owned prompt-policy composition (AC: 1, 10)
  - [ ] Prefer a new focused `scripts/sc/_review_evidence_prompt_policy.py` module.
  - [ ] Integrate through `scripts/sc/_llm_review_prompting.py`; do not duplicate canonical schema fields in prose beyond the output contract required by the prompt.
- [ ] Task 3: Add failing structured capture and parse tests (AC: 2, 3, 9, 11)
  - [ ] Cover valid block, zero findings, missing block, malformed JSON, duplicate terminal blocks, timeout without evidence, and timeout with complete evidence.
  - [ ] Assert raw Markdown retention and deterministic sidecar naming.
- [ ] Task 4: Implement parser and sidecar writer in new focused modules (AC: 2, 3, 9, 10)
  - [ ] Suggested boundaries: `_review_evidence_capture.py` for extraction/retention and `_review_evidence_sidecar.py` for identity/path/write behavior.
  - [ ] Use repository UTF-8/JSON helpers and write only beneath the task-scoped LLM review output directory.
  - [ ] Do not write or mutate residual decision logs, execution plans, active-task route fields, or pipeline `summary.json`.
- [ ] Task 5: Add failing minimum-validator and derived-verdict tests (AC: 4, 5, 6, 8, 11)
  - [ ] Cover exact repository anchor, line/heading bounds, quote mismatch, elevated proof removal, reason codes, demotion/drop, summary consistency, and zero findings.
  - [ ] Cover raw/derived disagreement and the complete `OK | Needs Fix | Unknown` matrix.
- [ ] Task 6: Implement RG-1 minimum runtime validation and derivation (AC: 3, 4, 5, 9, 10)
  - [ ] Reuse `scripts/sc/_review_evidence_schema.py`; do not fork or copy the schema.
  - [ ] Keep judgment-dependent defect truth outside deterministic validation; validate evidence completeness, reachability inputs, and contract consistency only.
  - [ ] Do not implement RG-2 cross-run deduplication, replay metrics, expanded false-positive adjudication, or retention reporting.
- [ ] Task 7: Integrate capture into the LLM review producer without increasing oversized modules (AC: 2, 7, 9, 10)
  - [ ] Extract orchestration from `scripts/sc/_llm_review_engine.py` into focused modules before adding capture behavior; the edited engine must end below 400 lines.
  - [ ] Add additive evidence metadata to each `ReviewResult.details` and the LLM review summary without changing existing field meanings.
  - [ ] Preserve prompt budget, reviewer deferral, timeout, host-safe normalization, and raw output behavior.
- [ ] Task 8: Replace generic reviewer ingestion with validated evidence ingestion (AC: 5, 6, 7, 8, 10)
  - [ ] Extract evidence-projection logic from `agent_to_agent_review.py` into a new focused module so the entry file remains below 400 lines.
  - [ ] Use `_agent_review_contract.py` only for backward-compatible helpers; do not change its public schema version or allowed verdict/action vocabulary.
  - [ ] Preserve deterministic/artifact-integrity findings as higher-priority independent blocks.
- [ ] Task 9: Run focused and integration verification and write evidence (AC: 11, 12)
  - [ ] Run schema, prompt shaping, runtime budget, agent-review contract, and agent-to-agent review tests.
  - [ ] Add `scripts/sc/tests/test_review_evidence_pipeline_integration.py`; use `scripts/sc/tests/_taskmaster_fixture.py` to stage all three task views outside the real repository task directory, inject `SC_TASKMASTER_TASKS_JSON_PATH`, `SC_TASKMASTER_TASKS_BACK_PATH`, and `SC_TASKMASTER_TASKS_GAMEPLAY_PATH` into direct calls and subprocesses, and restore the environment after the test.
  - [ ] The integration test must invoke the production `scripts/sc/run_review_pipeline.py` entry path, not only capture/ingestion helpers. Stub only external LLM/Godot execution boundaries; assert per-agent evidence sidecars and summary pointers are emitted, `agent-review.json` consumes the derived verdict, and producer `summary.json` status/fields remain unchanged.
  - [ ] Run the full local review-pipeline regression set through `test_run_review_pipeline_delivery_profile.py` plus the production-entry evidence integration test.
  - [ ] Confirm no changed implementation module exceeds 400 lines, `summary.json` is unchanged, profile modes are unchanged, and no residual/route file was modified.

## Dev Notes

### Protected Inputs

- `docs/adr/ADR-0032-review-evidence-gate.md` is Accepted and must not be weakened or rewritten in this story.
- `scripts/sc/schemas/review-evidence.v1.schema.json` is the only executable schema authority. Treat it as read-only; any required contract change stops this story and requires a separately reviewed schema-version task.
- `scripts/sc/_review_evidence_schema.py` and `_review_evidence_schema_fallback.py` are RG-0 protected validation inputs. Reuse their public behavior; do not relax proof, identity, disposition, summary, or verdict invariants.
- `summary.json` remains producer-owned. No compatibility shortcut may overwrite its status.

### Current State And Required Delta

- `_llm_review_prompting.py` currently emits Markdown instructions ending in a regex-parsed `Verdict: OK | Needs Fix`; add the higher-precedence repository evidence policy through a separate focused module.
- `_llm_review_engine.py` currently writes prompt/raw review/trace artifacts, parses only the terminal raw verdict, performs host-safe normalization, and serializes `ReviewResult`. Add capture through extracted helpers; preserve timeout budgets, deferred semantic execution, prompt shaping, and existing summary fields.
- `agent_to_agent_review.py` currently converts every non-OK LLM result into one generic medium finding via `_build_llm_findings`. Replace only this LLM path with sidecar-backed projection; preserve step-failure, artifact-integrity, approval, latest-index, and deterministic finding behavior.
- `_agent_review_contract.py` already freezes `pass | needs-fix | block` and `none | resume | refresh | fork`. Do not introduce a new compatibility value or schema version.
- Existing focused tests establish prompt shaping, runtime budget, agent-review contract, and generic ingestion behavior. Convert the generic-ingestion expectation to canonical actionable-finding projection while retaining all unrelated assertions.

### Architecture And File Boundaries

- NEW preferred: `scripts/sc/_review_evidence_prompt_policy.py`.
- NEW preferred: `scripts/sc/_review_evidence_capture.py`.
- NEW preferred: `scripts/sc/_review_evidence_sidecar.py`.
- NEW preferred: `scripts/sc/_review_evidence_runtime.py`.
- NEW preferred: `scripts/sc/_agent_review_evidence.py`.
- UPDATE: `scripts/sc/_llm_review_prompting.py`.
- UPDATE with mandatory extraction: `scripts/sc/_llm_review_engine.py`.
- UPDATE without net growth beyond 400 lines: `scripts/sc/agent_to_agent_review.py`.
- UPDATE only for compatible helpers when necessary: `scripts/sc/_agent_review_contract.py`.
- UPDATE/NEW focused tests under `scripts/sc/tests/`.

Do not touch `scripts/python/chapter6_route.py`, `scripts/sc/llm_review_needs_fix_fast.py`, residual/technical-debt writers, Chapter 3/4/5/7 workflows, delivery-profile promotion values, or `summary.json` schemas in this task.

### Testing Requirements

- Red first: every implementation behavior begins with a failing focused test.
- Required focused areas:
  - `test_review_evidence_schema.py`
  - `test_llm_review_prompt_shaping.py`
  - `test_llm_review_runtime_budget.py`
  - `test_agent_review_contract.py`
  - `test_agent_to_agent_review.py`
  - `test_review_evidence_prompt_policy.py`
  - `test_review_evidence_capture.py`
  - `test_review_evidence_runtime.py`
  - `test_review_evidence_pipeline_integration.py`
- Minimum final commands:
  - `py -3 -m unittest scripts.sc.tests.test_review_evidence_schema scripts.sc.tests.test_review_evidence_prompt_policy scripts.sc.tests.test_review_evidence_capture scripts.sc.tests.test_review_evidence_runtime scripts.sc.tests.test_review_evidence_pipeline_integration`
  - `py -3 -m unittest scripts.sc.tests.test_llm_review_prompt_shaping scripts.sc.tests.test_llm_review_runtime_budget scripts.sc.tests.test_agent_review_contract scripts.sc.tests.test_agent_to_agent_review scripts.sc.tests.test_run_review_pipeline_delivery_profile`
  - `py -3 -m unittest discover -s scripts/sc/tests -p "test_review_evidence_*.py"`
  - `py -3 -m compileall -q scripts/sc scripts/sc/tests`
  - `git diff --check`

The integration test owns fixture creation and chooses the temporary task ID. Do not hard-code or borrow a task ID from NewRouge, LastKing, Sanguo, or another business repository. Before and after the test, assert that the real `.taskmaster/tasks` files were neither created nor changed and that every task/output artifact remains under the temporary fixture/output roots.

### Stop-Loss

- If derived ingestion requires changing residual creation, route precedence, repair-guide semantics, or needs-fix-fast behavior, stop and create the separate RG-1 residual-routing task.
- If the v1 schema or ADR-0032 must change, stop; do not modify protected inputs inside this story.
- If a required extraction would broaden into unrelated engine refactoring, keep the smallest interface-preserving split and record the remainder as a separately scoped task.
- If a reviewer claim cannot cite an exact anchor, failure chain, context, and defensible severity, demote/drop it; zero findings remains legal.

### References

- [ADR-0032 Decision](../../docs/adr/ADR-0032-review-evidence-gate.md#decision)
- [Shared Finding Contract](../../execution-plans/2026-07-12-phase-review-evidence-gate-hardening-execution-plan/02-review-evidence-contracts-and-severity.md#shared-finding-contract)
- [Chapter 6 Target Flow](../../execution-plans/2026-07-12-phase-review-evidence-gate-hardening-execution-plan/04-chapter6-review-ingestion-and-residual-closure.md#target-flow)
- [Parser And Validator](../../execution-plans/2026-07-12-phase-review-evidence-gate-hardening-execution-plan/04-chapter6-review-ingestion-and-residual-closure.md#parser-and-validator)
- [Agent-Review Projection Matrix](../../execution-plans/2026-07-12-phase-review-evidence-gate-hardening-execution-plan/06-pipeline-integration-recovery-and-compatibility.md#agent-review-projection-matrix)
- [RG-1 Phase](../../execution-plans/2026-07-12-phase-review-evidence-gate-hardening-execution-plan/08-implementation-phases.md#phase-rg-1-chapter-6-capture-and-residual-correctness)
- [LLM Review Prompting](../../scripts/sc/_llm_review_prompting.py)
- [LLM Review Engine](../../scripts/sc/_llm_review_engine.py)
- [Agent-To-Agent Review](../../scripts/sc/agent_to_agent_review.py)
- [Agent Review Contract](../../scripts/sc/_agent_review_contract.py)

## Out Of Scope

- Residual write suppression/idempotency implementation and all residual decision/execution-plan mutation.
- Chapter 6 route selection, repair-guide migration, active-task routing, and needs-fix-fast correction.
- RG-2 replay corpus, cross-run deduplication, advisory metrics, retention reporting, and performance smoke.
- Chapter 5 semantic integration and Chapter 3/4/7 evidence profiles.
- Any profile promotion to `warn` or `require`.
- Any breaking `agent-review.json` or producer `summary.json` schema change.

## Dev Agent Record

### Agent Model Used

Not started.

### Debug Log References

- RG-0 clean gate: `logs/ci/2026-07-13/review-evidence-rg0-final-clean-review/`

### Completion Notes List

- Ultimate context engine analysis completed; implementation has not started.

### File List

- `_bmad-output/implementation-artifacts/rg-1-chapter6-structured-review-evidence-capture-and-ingestion.md`
