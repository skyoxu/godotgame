# Workflow Rule Feedback Record

## 1. Rule Identity

- Rule name: chapter6 p1 floor acceptance refs
- Workflow family: `chapter6`
- Source repository: `skyoxu/newrouge`
- Source branch: `main`
- Source commit: `444002a047f8739c7ba34c090af6d1abc3558b46`
- Date: `2026-04-19`

## 2. Problem Statement

- Some Chapter 6 runs looked like residual-only cleanup on the surface, but the underlying findings still touched acceptance refs, artifact integrity, or planned-only producer validity.
- If those findings were treated as ordinary residual debt, operators could incorrectly stop reruns and carry forward evidence from an invalid producer bundle.

## 3. Observed Symptoms

- Operator-visible symptom: a run appeared eligible for `record-residual` even though the finding family still affected task validity.
- Cost symptom: wrong residual routing caused later recovery confusion and extra inspection work.
- Quality symptom: risk of accepting invalid acceptance evidence or planned-only artifacts as if they were low-priority debt.
- Recovery symptom: `record-residual` needed a deterministic floor so high-impact workflow findings would stay above ordinary residual handling.

## 4. Artifact Evidence

- `agent-review.json`: findings with category / owner-step semantics
- `latest.json`: route and recovery signal context
- `execution-context.json`: producer-side validity context
- `repair-guide.json`: rerun / stop-loss hints
- implementation evidence:
  - `scripts/python/chapter6_route.py`
  - `_P1_FLOOR_CATEGORIES`
  - `_P1_FLOOR_OWNER_STEPS`
  - `_residual_reason_from_agent_review(...)`

## 5. Failure / Waste Pattern

- Failure family: residual misclassification
- Trigger condition: medium/low findings remain, but at least one finding still belongs to acceptance-refs / artifact-integrity / planned-only / security-boundary / false-green families
- Repeated how many times: enough to justify a dedicated deterministic floor in business-repo routing
- Affected lane or step:
  - affected lane: `record-residual`
  - protected lanes: `inspect-first`, `fix-deterministic`, fresh producer rerun

## 6. Proposed Reusable Rule

- Proposed rule in one sentence: Chapter 6 must not record residual debt when remaining findings still belong to `P1 floor` workflow-validity categories such as acceptance refs or artifact integrity.
- Proposed template target:
  - constant table
  - classifier helper
  - workflow doc
- Suggested files:
  - `scripts/python/chapter6_route.py`
  - `workflow.md`
  - `docs/workflows/run-protocol.md`

## 7. Classification

- Promotion class: `needs-cross-repo-validation`
- Why: the mechanism is reusable, but the exact category and owner-step taxonomy should ideally be confirmed across more than one business repository before expanding the default template list.

## 8. Cross-Repo Status

- Status: `single-repo`
- Other repositories checked: none at record creation time
- Matching evidence summary: `newrouge` had already hardened this as a durable Chapter 6 routing invariant

## 9. Safety Review

- Does this weaken deterministic gates? `no`
- Could this create a false-green path? `no`
- Could this hide a P1/P0 issue inside residual recording? `no`
- Could this overfit one business repository? `medium`
- Safety notes: the reusable part is the `P1 floor` mechanism; the exact category list should be promoted carefully.

## 10. Expected Benefit

- Time saved: prevents wasted residual loops that later need to be reopened
- LLM cost saved: avoids paying for the wrong closure lane
- Recovery clarity improvement: high
- False rerun reduction: medium

## 11. Validation Plan

- Required regression tests:
  - Chapter 6 route residual-eligibility tests
  - recovery-sidecar regression tests
- Required workflow docs to update:
  - `workflow.md`
  - `docs/workflows/stable-public-entrypoints.md`
  - `docs/workflows/run-protocol.md`
- Required business-repo backports after promotion:
  - align category / owner-step output in `agent-review.json`

## 12. Final Decision

- Decision: `wait-for-cross-repo-validation`
- Decision reason: the `P1 floor` mechanism should exist in the template, but the precise taxonomy should be confirmed across multiple business repositories.
