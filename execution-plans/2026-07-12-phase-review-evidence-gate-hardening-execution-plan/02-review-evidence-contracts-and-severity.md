# Review Evidence Contracts And Severity

## Shared Finding Contract

Each proposed finding records:

- schema version
- workflow chapter
- review domain and reviewer
- non-empty task/run identity; non-task-scoped reviews use a stable synthetic `task_id` in the form `scope:<chapter>:<stable-scope-id>`, while every invocation receives a non-empty `run_id`
- stable proposed finding ID
- title and actionable message
- original severity and normalized severity
- confidence
- exact source anchors
- quoted evidence or snippet
- failure or consequence chain
- context inspected
- existing safeguard gap
- severity rationale
- suggested change
- validation state and reason codes
- normalized finding-family fingerprint

The canonical machine shape is defined by `scripts/sc/schemas/review-evidence.v1.schema.json`; the plan-local schema file is a non-normative pointer used by Whole-directory review.

## Anchor Types

| Anchor type | Required fields | Typical chapters |
| --- | --- | --- |
| code-line | repository path, start line, optional end line, snippet | 6 |
| document-line | repository path, line, heading, quote | 3, 4, 5, 7 |
| structured-field | repository path, JSON/YAML field path, serialized value | 3, 5, 7 |
| task | task ID, view, field or acceptance ID | 3, 5, 6, 7 |
| artifact | artifact path, artifact type, hash or stable item ID | 4, 6, 7 |
| screenshot | artifact path, viewport, surface ID, comparison criterion | 7 |

## Failure And Consequence Chains

Code profile:

`input or trigger -> state/precondition -> bad result`

Document or semantic profile:

`authoritative statement -> conflicting/missing representation -> affected consumer -> bad decision or unverifiable obligation`

UI profile:

`surface and state -> viewport/input/accessibility condition -> player-visible failure -> acceptance criterion`

## Existing Safeguard Gap

The finding must name the relevant safeguard and why it does not close the issue:

- type system or compiler
- caller validation
- framework default
- deterministic validator
- unit or integration test
- security profile normalization
- artifact manifest or hash
- human patch preview

For medium/low findings, missing safeguard analysis may cause advisory demotion. For P0/P1 it is mandatory.

## Severity Normalization

| Prompt severity | Normalized severity | Stable compatibility severity |
| --- | --- | --- |
| P0 / CRITICAL | critical | high |
| P1 / HIGH | high | high |
| P2 / MEDIUM | medium | medium |
| P3 / LOW | low | low |

The compatibility projection does not erase the normalized value; it only maps into the current `agent-review.json` vocabulary.

## Elevated-Severity Proof

Critical/high findings require all of:

1. exact source anchor and quote/snippet
2. concrete failure or consequence chain
3. surrounding context inspected
4. existing safeguard gap
5. severity rationale covering reachability, impact, and affected scope

Missing any item results in deterministic demotion or drop. It does not become a product pipeline failure.

## Finding State Machine

```text
proposed
  -> validated
  -> demoted
  -> dropped
  -> unknown
```

- `validated`: evidence satisfies its normalized severity profile.
- `demoted`: a real actionable concern survives at a lower severity.
- `dropped`: unsupported, duplicate, out of scope, known false positive, or non-actionable.
- `unknown`: evidence cannot be parsed or inspected.

Only validated and demoted findings influence `Needs Fix`.

## Reason-Code Families

- `schema.*`
- `anchor.*`
- `quote.*`
- `context.*`
- `failure_chain.*`
- `safeguard_gap.*`
- `severity.*`
- `scope.*`
- `duplicate.*`
- `false_positive.*`
- `input.*`
- `verdict.*`

Reason codes are stable machine values. Human explanations may evolve without changing recovery logic.

## Verdict Derivation

| Condition | Derived verdict |
| --- | --- |
| one or more actionable validated/demoted findings | Needs Fix |
| no actionable findings and no unknown state | OK |
| parse failure, missing required review input, or unverifiable required evidence | Unknown |

Raw reviewer verdict is retained for comparison but cannot override the derived verdict.

## Summary Derivation

Summary fields are derived only after every finding has a validation disposition:

- `proposed_count` equals the number of findings in the sidecar.
- `validated_count`, `demoted_count`, `dropped_count`, and `unknown_count` equal their corresponding validation-state counts.
- `actionable_count` equals `validated_count + demoted_count`.
- `highest_severity` is the highest `validation.final_severity` among actionable `validated|demoted` findings.
- `highest_severity` is `none` when `actionable_count` is zero.
- Pre-validation `normalized_severity` is retained for audit and proof selection but never drives recovery routing after a final disposition exists.

## False-Positive Catalog Ownership

- Shared ECC-derived catalog: this book and repository prompt policy.
- Chapter 3-5 catalog: book 03.
- Chapter 6 code/security/test/semantic/architecture/performance catalog: book 04.
- Chapter 7 UI catalog: book 05.

## Compatibility

- Do not change `summary.json`.
- Add a new versioned evidence sidecar.
- Project validated results into the current `agent-review.json` contract.
- A future breaking `agent-review.json` version requires a separate migration decision.

## Acceptance

- JSON Schema validates the example and rejects missing mandatory fields.
- Severity mapping tests prove original P0-P3/CRITICAL-LOW values normalize before proof evaluation and remain distinct from `validation.final_severity`.
- Identity tests reject empty task/run IDs and cover the synthetic non-task scope form.
- Profile ownership tests enumerate code, security, test, semantic, architecture, and performance consistently in the Chapter 6 catalog and source coverage.
- Summary consistency tests derive every count and highest actionable final severity from finding dispositions; a demoted P1 reports summary medium, not high.
- Review-domain tests distinguish Chapter 6 `architecture` from Chapter 4 `architecture-document` and from `performance`.
- Unit tests cover all finding states and reason-code families.
- P0/P1 mutation tests remove each proof element and observe demotion/drop.
- Verdict tests prove zero findings is OK and unparseable output is Unknown.
- Compatibility tests prove current consumers still read the projected sidecar.
