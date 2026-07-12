# Review Evidence Gate Hardening Execution Plan

- Title: review-evidence-gate-hardening
- Status: paused
- Branch: fix/chapter3-add-task-numbering
- Git Head: 21f7b1edf51f5b4ecf5c336bccfc7f437ecb83bf
- Goal: introduce chapter-aware, evidence-gated LLM review so unsupported findings cannot create trusted Needs Fix state, repeated reruns, or empty residual closure work.
- Scope: Chapter 3-7 review policy, structured review evidence, Chapter 6 LLM ingestion and residual routing, Chapter 5 semantic findings, Chapter 3/4/7 document profiles, replay metrics, tests, ADR/workflow updates, and compatible sidecars.
- Current step: split implementation plan authored; implementation is paused pending explicit authorization and ADR ownership.
- Last completed step: completed ECC fixed-commit research and business-repository evidence audit, then split the implementation design into owner books and control ledgers.
- Stop-loss: do not change `summary.json`; do not enable a required LLM gate before advisory replay evidence is stable; do not treat reviewer formatting failure as a product defect; do not generate residual records from an empty validated finding set.
- Next action: approve RG-0, create or update the governing ADR, freeze the evidence schema and reason-code catalog, and assign implementation owner and reviewer.
- Recovery command: `py -3 -c "from pathlib import Path; print(Path(r'execution-plans/2026-07-12-phase-review-evidence-gate-hardening-execution-plan/00-index.md').read_text(encoding='utf-8'))"`
- Open questions: final ADR ownership; whether the first schema is JSON-only or Markdown plus fenced JSON; initial retention period for compressed evidence metrics; delivery profiles allowed to move from advisory to warn or require.
- Exit criteria: all RG phases exit sequentially; every Needs Fix has at least one validated actionable finding; P0/P1 proof is complete; unparseable output is Unknown; zero surviving findings is OK; empty residual creation is impossible; Chapter 3-7 profiles and replay tests are green; durable rules move to ADR/workflow/docs.
- Related ADRs: `docs/adr/ADR-0005-quality-gates.md`, `docs/adr/ADR-0017-quality-intelligence-dashboard-and-governance.md` (Proposed); a new accepted review-evidence ADR or ADR-0005 addendum is required before enforcement.
- Related decision logs: pending RG-0 policy decision log.
- Related task id(s): n/a (phase-wide workflow hardening plan; implementation tasks have not been created).
- Related run id: n/a (planning only).
- Related latest.json: n/a (planning only).
- Related pipeline artifacts: `_bmad-output/planning-artifacts/research/technical-ecc-review-anti-hallucination-research-2026-07-12.md`; future evidence under `logs/ci/<date>/review-evidence-*`.

## Authority

- This top-level file owns recovery metadata, Gate summary, global order, and global completion only.
- Detailed implementation authority is the same-name split directory.
- ECC is an external design source, not repository policy. Fixed source commit: `40927950c49f6e742d341e20ff7b9b7e1e7bfff5`.
- The completed local research report owns the empirical baseline; this plan owns future implementation sequencing.
- Implemented durable rules must move to accepted ADRs, `docs/agents/**`, `docs/workflows/**`, schemas, and tested code. Execution plans are not the final policy SSoT.

## Gate Summary

| Gate | Required condition | Work allowed after exit |
| --- | --- | --- |
| RG-HANDOFF | Research report complete, ECC source pinned, NewRouge/LastKing/Sanguo evidence limitations recorded, split plan passes document validation | RG-0 planning task may be created |
| RG-0 | Accepted policy decision, schema owner, severity mapping, reason-code catalog, retention and compatibility rules frozen | Schema and advisory capture implementation |
| RG-1 | Chapter 6 structured capture, derived verdict, compatibility projection, empty-residual and idempotency fixes pass tests | Advisory live capture and replay |
| RG-2 | Expanded validation, replay corpus, metrics and mutation tests are stable with no unresolved P0/P1 | Chapter 5 semantic integration |
| RG-3 | Chapter 5 obligation/acceptance evidence profile passes fixtures and stop-loss tests | Chapter 3/4/7 profile integration |
| RG-4 | Chapter 3/4/7 profiles preserve deterministic-first authority and pass chapter-specific false-positive fixtures | Profile-specific warn trial |
| RG-5 | Advisory trial is accepted, rollback is proven, durable docs/ADR are updated, and selected profiles meet promotion criteria | Approved warn/require enforcement and closure |

## Implementation Books

1. [Split Index](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/00-index.md)
2. [Authority, Scope, And Invariants](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/01-authority-scope-and-invariants.md)
3. [Review Evidence Contracts And Severity](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/02-review-evidence-contracts-and-severity.md)
4. [Chapter 3-5 Evidence Profiles](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/03-chapter3-5-evidence-profiles.md)
5. [Chapter 6 Review Ingestion And Residual Closure](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/04-chapter6-review-ingestion-and-residual-closure.md)
6. [Chapter 7 UI Review Evidence](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/05-chapter7-ui-review-evidence.md)
7. [Pipeline Integration, Recovery, And Compatibility](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/06-pipeline-integration-recovery-and-compatibility.md)
8. [Observability, Replay, And Performance](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/07-observability-replay-and-performance.md)
9. [Implementation Phases](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/08-implementation-phases.md)
10. [Risks, Definition Of Done, And Glossary](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/09-risks-dod-and-glossary.md)
11. [Global Review And Split Validation](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/96-global-review-and-split-validation.md)
12. [Post-Split Requirements Ledger](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/97-post-split-requirements-ledger.md)
13. [Research-To-Split Audit](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/98-research-to-split-audit.md)
14. [Source Coverage](2026-07-12-phase-review-evidence-gate-hardening-execution-plan/99-source-coverage.md)

## Global Order

```text
RG-HANDOFF research and split-plan closure
  -> RG-0 policy, ADR, schema and compatibility freeze
  -> RG-1 Chapter 6 capture, verdict derivation and residual correctness
  -> RG-2 expanded validation, replay corpus and advisory metrics
  -> RG-3 Chapter 5 semantic evidence integration
  -> RG-4 Chapter 3/4/7 domain profiles
  -> RG-5 profile promotion, durable policy migration and closure
```

Only one RG phase may be active. A later phase cannot start from prose approval alone; it requires predecessor exit evidence and the same active schema/policy version.

## Global Completion

- Repository-owned evidence policy cannot be weakened by user-scoped agent prompts.
- Raw reviewer prose is untrusted until parsed and validated.
- A derived reviewer `Needs Fix` and its compatibility projection cannot survive without an actionable finding; producer-owned status may be retained only as declared compatibility data.
- P0/P1 cannot survive without exact evidence, failure/consequence chain, safeguard-gap explanation, and severity rationale.
- `Unknown` remains distinct from clean.
- `summary.json` remains producer-owned and schema-stable.
- `agent-review.json` remains a compatibility projection until a separately approved version change.
- Empty residual decisions and plans cannot be created.
- Chapter 3, 4, and 7 remain deterministic-first.
- Chapter 5 and 6 LLM findings use domain-specific evidence profiles.
- Replay, observability, retention, rollback, and profile promotion evidence are durable under `logs/**`.
