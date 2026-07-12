# Risks, Definition Of Done, And Glossary

## Key Risks

| Risk | Mandatory control |
| --- | --- |
| Prompt-only policy is mistaken for a fact verifier | structured evidence plus deterministic ingestion validation |
| Validator claims semantic truth it cannot prove | separate deterministic completeness from judgment-dependent correctness |
| Reviewer formatting failure blocks product delivery | classify as Unknown, not product failure |
| Valid high-severity defect is demoted by a brittle parser | retain raw output, replay fixtures, advisory rollout, adjudication sample |
| User-scoped prompt weakens policy | repository policy appended at higher precedence and regression-tested |
| `summary.json` compatibility breaks | sidecar-only design and compatibility tests |
| `agent-review.json` loses new evidence | retain full evidence sidecar and explicit projection mapping |
| Empty residual documents continue | non-empty validated set and idempotency required before write |
| Chapter 3/4/7 become LLM-gated | deterministic-first authority invariant and chapter fixtures |
| Chapter 5 rewrites from missing input | missing input -> Unknown and stop |
| Security reviewer over-hardens host-safe tasks | threat/security-profile evidence and false-positive rule |
| Visual reviewer invents defects without images | screenshot evidence or Unknown |
| Historical metrics disappear with log cleanup | durable compressed evidence summary and retention test |
| Prompt/output size increases review cost | measure token/character growth and rerun savings |
| Large scripts grow further | split new parser, validator, metrics, and projection modules by responsibility |
| Severity vocabularies drift | one normalized mapping and mutation tests |
| Same finding creates repeated rounds | normalized family fingerprint, anchor hit, and stop-loss |
| Advisory trial silently becomes enforcement | explicit mode field, profile decision, ADR, and rollback drill |

## Global Definition Of Done

1. Policy authority and precedence are documented and tested.
2. Schema v1 and example validate.
3. Every finding has a stable state and reason codes.
4. Every Needs Fix has at least one validated/demoted actionable finding.
5. P0/P1 satisfies the full proof contract.
6. Invalid anchors and quote mismatches cannot survive.
7. Zero surviving findings derives OK.
8. Missing input and parse failure derive Unknown.
9. `summary.json` remains schema-stable.
10. `agent-review.json` compatibility tests pass.
11. Empty residual creation is impossible.
12. Repeated same-family residual writes are idempotent.
13. Chapter 5 rewrite requires validated semantic evidence.
14. Chapter 3, 4, and 7 deterministic validators remain authoritative.
15. Visual findings require visual evidence.
16. Replay corpus covers valid, invalid, false-positive, Unknown, timeout, and residual cases.
17. Metrics survive raw-output cleanup.
18. Advisory trial and adjudication are complete before promotion.
19. Rollback to advisory is tested.
20. ADR/workflow/testing/recovery docs own all implemented durable rules.
21. No unresolved P0/P1; P2 is closed or has owner/expiry/recheck.

## Glossary

| Term | Meaning |
| --- | --- |
| Proposed finding | Untrusted reviewer claim before validation |
| Actionable finding | Validated or demoted finding allowed to affect Needs Fix |
| Evidence profile | Chapter/reviewer-specific proof requirements |
| Evidence sidecar | Versioned structured finding and disposition artifact |
| Raw verdict | Terminal verdict emitted by the reviewer |
| Derived verdict | Verdict computed from validated finding states |
| Safeguard gap | Why existing types, callers, tests, validators, or profiles do not prevent the issue |
| Finding family | Normalized identity used for deduplication and rerun stop-loss |
| Unknown | Observation gap caused by missing/unparseable/unverifiable input |
| Compatibility projection | Stable smaller view written for existing consumers |
| Advisory mode | Records validation without changing delivery routing |
| Require mode | Selected profile routes from derived validated verdict |

## Review Stop Conditions

- ADR or schema owner missing.
- A task proposes changing `summary.json` without separate approval.
- A validator conflates evidence completeness with semantic truth.
- P0/P1 can survive with missing proof.
- Unknown is treated as clean or as an actionable product finding.
- Chapter 3/4/7 deterministic authority is weakened.
- Empty findings can still create residual state.
- Replay shows a known valid critical finding is silently dropped without adjudication.
- Compatibility mode or rollback is unspecified.
- Raw-log cleanup removes all durable explanation of a derived verdict.
- An implementation task exceeds scope or the 400-line guardrail without approved split.
- Profile enforcement starts before advisory evidence and rollback review.
