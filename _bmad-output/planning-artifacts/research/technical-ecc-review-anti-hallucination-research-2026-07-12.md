---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments: []
workflowType: 'research'
lastStep: 1
research_type: 'technical'
research_topic: 'ECC review anti-hallucination engineering and repository applicability'
research_goals: 'Verify ECC review evidence gates and false-positive controls, measure local review noise, and recommend a repository-specific implementation.'
user_name: 'Weiruan'
date: '2026-07-12'
web_research_enabled: true
source_verification: true
---

# Research Report: ECC Review Anti-Hallucination Engineering

**Date:** 2026-07-12
**Author:** Weiruan
**Research Type:** Technical

---

## Research Overview

This research verifies the anti-hallucination review policy in ECC 2.0 against the canonical `affaan-m/ECC` repository at commit `40927950c49f6e742d341e20ff7b9b7e1e7bfff5`, then compares that policy with this repository's Chapter 3-7 workflow and review harness. It distinguishes ECC's actual implementation, a prompt-level pre-output self-check protected by a CI contract test, from a runtime fact-verification gate.

The local analysis covers prompt loading, LLM execution, verdict parsing, sidecar projection, residual routing, and chapter-specific deterministic validators. With user authorization, it also audits historical review evidence from the sibling `newrouge-github-main`, `lastking`, and `sanguo` business repositories. The evidence shows material review churn and evidence incompleteness, especially in Chapter 6, while also showing that Chapters 3, 4, 5, and 7 require domain-specific evidence profiles rather than a copied code-review template. See the Research Synthesis section for the final decision and implementation priorities.

## Technical Research Scope Confirmation

**Research Topic:** ECC review anti-hallucination engineering and repository applicability
**Research Goals:** Verify ECC review evidence gates and false-positive controls, measure local review noise, and recommend a repository-specific implementation.

**Technical Research Scope:**

- Architecture Analysis - review pipeline structure, evidence gates, and output contracts
- Implementation Approaches - prompt rules, deterministic validation, and severity handling
- Technology Stack - ECC source files and this repository's Python review harness
- Integration Patterns - reviewer prompts, JSON sidecars, repair guides, and task recovery
- Performance Considerations - noise, rerun cost, reviewer trust, and stop-loss behavior

**Research Methodology:**

- Current web data with rigorous source verification
- Source-level verification against a fixed ECC commit
- Local repository and review-artifact inspection
- Confidence levels for uncertain or incomplete evidence

**Scope Confirmed:** 2026-07-12

---

<!-- Content will be appended sequentially through research workflow steps -->

## Technology Stack Analysis

### Source Repository and Version Pinning

ECC 2.0 uses `affaan-m/ECC` as its canonical GitHub repository. The former `everything-claude-code` name was replaced during the 2.0 migration. This research pins all ECC claims to commit `40927950c49f6e742d341e20ff7b9b7e1e7bfff5` rather than citing the moving `main` branch.

_Source: https://github.com/affaan-m/ECC/blob/40927950c49f6e742d341e20ff7b9b7e1e7bfff5/README.md#L321-L329_

_Source: https://github.com/affaan-m/ECC/blob/40927950c49f6e742d341e20ff7b9b7e1e7bfff5/docs/MIGRATION-1X-TO-2.0.md#L1-L3_

### ECC Review Implementation

ECC implements the anti-hallucination review policy primarily as a Markdown agent prompt in `agents/code-reviewer.md`. The prompt directs the model to inspect the diff, surrounding files, dependencies, callers, and tests; apply a confidence threshold; run a four-question pre-output fact check; require stronger proof for HIGH/CRITICAL findings; accept zero findings; and filter known false-positive patterns.

This is a prompt-level self-check, not a runtime fact verifier. ECC does not parse every emitted finding and independently prove that its line number, failure scenario, or missing guard is valid.

_Source: https://github.com/affaan-m/ECC/blob/40927950c49f6e742d341e20ff7b9b7e1e7bfff5/agents/code-reviewer.md#L19-L74_

### ECC Regression Protection

ECC uses a JavaScript CI test, `tests/ci/code-reviewer-false-positive-guard.test.js`, to assert that the reviewer prompt still contains the required headings and representative policy phrases. This protects the prompt contract from accidental deletion, but it does not validate the factual quality of real review outputs.

_Source: https://github.com/affaan-m/ECC/blob/40927950c49f6e742d341e20ff7b9b7e1e7bfff5/tests/ci/code-reviewer-false-positive-guard.test.js#L8-L35_

_Source: https://github.com/affaan-m/ECC/blob/40927950c49f6e742d341e20ff7b9b7e1e7bfff5/tests/ci/code-reviewer-false-positive-guard.test.js#L58-L75_

### Local Review Orchestration

This repository's review harness is implemented in Python. `scripts/sc/_llm_review_engine.py` assembles task context, acceptance evidence, threat-model guidance, security-profile guidance, optional review templates, the diff, and an agent prompt. It writes the composed prompt and reviewer output to `logs/**`.

The LLM backend supports `codex-cli` and the OpenAI Python SDK. The CLI path runs in read-only mode; the API path uses the Responses API. The orchestration layer recognizes a final `Verdict: OK | Needs Fix` line with a regular expression.

_Local sources: `scripts/sc/_llm_backend.py`, `scripts/sc/_llm_review_engine.py`, `scripts/sc/_llm_review_prompting.py`_

### Local Prompt Sources

The default local prompt already says to avoid speculative claims and to return OK when deterministic gates are green and no concrete missing behavior or weak test can be identified. The semantic-equivalence reviewer has a similar stop-loss rule for missing obligations.

However, the active `code-reviewer` prompt is normally loaded from `.claude/agents/lst97/code-reviewer.md` or the user's `~/.claude/agents/lst97/code-reviewer.md`. In the current environment, the active file is user-scoped and contains broad checklist-driven guidance such as DRY, SOLID, naming, documentation, N+1, caching, scalability, positive observations, and suggestions. It requires locations and examples, but it does not contain ECC's four-question gate, HIGH/CRITICAL proof triplet, zero-findings rule, or false-positive catalog.

_Local sources: `scripts/sc/_llm_review_prompting.py`, `C:/Users/weiruan/.claude/agents/lst97/code-reviewer.md`_

### Local Structured Artifacts

The post-review `agent-review.json` contract is stronger than ECC's plain Markdown output in one respect: it requires structured findings with severity, category, owner step, evidence path, message, suggested fix, and commands. Empty findings are explicitly supported and render as `No findings.`

The current schema does not require an exact source line, code snippet, input/state/outcome failure scenario, surrounding-context evidence, confidence score, or explanation of why existing safeguards fail. Therefore it structures findings without yet proving them.

_Local source: `scripts/sc/_agent_review_contract.py`_

### Storage, Infrastructure, and Deployment Relevance

No database, cloud platform, container runtime, or deployment service is intrinsic to this review mechanism. The durable state is file-based: Markdown prompts and reports, JSON summaries and sidecars, and log artifacts under `logs/**`. The relevant adoption boundary is prompt and artifact governance, not infrastructure selection.

### Technology Adoption Assessment

ECC's design is portable because it relies on model instructions plus a small regression test. This repository already has the more substantial orchestration and structured-artifact foundation needed for a stronger implementation. The technical gap is not a missing review framework; it is the absence of evidence-completeness fields and output validation at the point where LLM prose becomes a trusted finding.

**Confidence:** High for repository structure and fixed-commit ECC claims; high for the current local harness; medium for environment-wide prompt behavior because the active reviewer prompt is user-scoped rather than repository-owned.

## Integration Patterns Analysis

### Current End-to-End Review Flow

The local review path is a file-based integration pipeline:

1. Python composes a prompt from an agent prompt, task context, deterministic evidence, threat/security context, an optional structured template, and a diff.
2. Codex CLI or the OpenAI Responses API writes one Markdown report per reviewer.
3. The harness extracts only the terminal `Verdict: OK | Needs Fix` value into the LLM review summary.
4. `agent_to_agent_review.py` converts every non-OK reviewer result into one generic medium finding whose evidence is the reviewer Markdown path.
5. Recovery, repair, routing, and stop-loss logic consume the generic sidecar finding.

This preserves reviewer identity and verdict but discards the internal finding evidence before the result becomes a stable machine contract.

_Local sources: `scripts/sc/_llm_review_engine.py`, `scripts/sc/_llm_review_prompting.py`, `scripts/sc/agent_to_agent_review.py`_

### Recommended Integration Boundary

ECC's self-check should be integrated at two distinct boundaries:

- **Prompt boundary:** a repository-owned common evidence policy appended to every relevant reviewer, independent of the user-scoped `~/.claude` agent file.
- **Output-ingestion boundary:** a deterministic validator should accept, demote, or drop individual findings before deriving the final verdict and before `agent-review.json` is generated.

Only implementing the prompt boundary would reproduce ECC's design. Adding output-ingestion validation would go beyond ECC and close the local trust gap created by downstream automation.

### Reviewer Output Protocol

Each LLM reviewer should produce a small machine-readable finding collection in addition to its human-readable Markdown. A finding should carry at least:

- stable finding ID
- reviewer and review domain (`code`, `documentation`, `semantics`, or `security`)
- claimed severity and confidence
- exact evidence anchor
- quoted snippet or exact source statement
- concrete failure or consequence chain
- surrounding context inspected
- existing safeguard analysis
- recommended disposition (`keep`, `demote`, or `drop`)
- final severity after validation

The terminal verdict should be derived from validated findings. A reviewer should not be able to emit `Needs Fix` with zero surviving actionable findings.

### Code Review Evidence Contract

For code findings, the evidence gate should use the ECC-shaped contract:

- exact repository-relative file and line number or narrow line span
- exact relevant code snippet
- input -> state/precondition -> bad result
- callers/imports/tests or equivalent surrounding context inspected
- explanation of why types, validation, framework behavior, or existing tests do not prevent the result
- defensible severity tied to impact and reachability

HIGH/CRITICAL, or the local P0/P1 equivalents, should require all proof fields. Missing proof should cause deterministic demotion or removal.

_ECC source: https://github.com/affaan-m/ECC/blob/40927950c49f6e742d341e20ff7b9b7e1e7bfff5/agents/code-reviewer.md#L39-L64_

### Documentation Review Evidence Contract

ECC has no dedicated document reviewer, so a direct copy of its code rule would be incorrect. Documentation findings need a parallel but domain-specific proof contract:

- exact file, line, and heading or structured field
- exact quoted statement
- authoritative source or conflicting statement
- contradiction, omission, ambiguity, or stale-reference chain
- downstream consumer affected, such as a task generator, validator, developer, release gate, or runtime contract
- concrete bad decision or unverifiable obligation caused by the defect
- explanation of why existing indexes, validators, schemas, or cross-references do not catch it

For cross-document inconsistencies, two or more exact anchors may be valid evidence. A document issue should not be forced into an artificial runtime `input/state/result` format when the actual failure is a contradictory SSoT or an untestable requirement.

### Data Format and Sidecar Evolution

The existing `agent-review.json` should remain a stable consumer contract, consistent with repository policy. Evidence-rich LLM findings should first be added as a new sidecar, for example a versioned per-agent findings JSON or a review-evidence JSON. The existing agent review builder can then consume the validated sidecar and project a smaller compatibility view into `agent-review.json`.

This follows the repository's established sidecar pattern and avoids destabilizing `summary.json`.

_Local sources: `docs/agents/07-agent-to-agent-review.md`, `scripts/sc/_agent_review_contract.py`, `AGENTS.md`_

### Severity Interoperability

The current stack has multiple severity vocabularies:

- LLM Markdown: P0/P1/P2/P3
- stable agent-review contract: high/medium/low
- ECC prompt: CRITICAL/HIGH/MEDIUM/LOW

A single explicit mapping is required before applying proof thresholds. Recommended mapping for compatibility is P0 -> critical, P1 -> high, P2 -> medium, P3 -> low, with the stable sidecar retaining the original and normalized values. Without this mapping, severity demotion cannot be deterministic or auditable.

### Zero-Finding Interoperability

The existing structured contract already accepts an empty findings array and renders `No findings.` ECC's stronger rule should be placed upstream: zero validated findings must produce `Verdict: OK`, and reviewers must be told that a clean review is expected when the change is small, typed, tested, and aligned with established patterns.

_ECC source: https://github.com/affaan-m/ECC/blob/40927950c49f6e742d341e20ff7b9b7e1e7bfff5/agents/code-reviewer.md#L66-L74_

### False-Positive Catalog Integration

The catalog should be repository-owned and split into:

- general LLM review false positives adapted from ECC
- Godot/C# false positives tied to this repository's architecture and test model
- document-review false positives, such as reporting intentional templates, referenced thresholds, generated indexes, or explicitly scoped omissions as defects
- security-profile false positives, extending the existing deterministic host-safe anti-tamper normalization

A small CI contract test should assert that the prompt evidence gate, zero-findings rule, and representative catalog entries remain present. Separate validator tests should prove that malformed or under-evidenced findings are actually demoted or dropped.

_ECC source: https://github.com/affaan-m/ECC/blob/40927950c49f6e742d341e20ff7b9b7e1e7bfff5/agents/code-reviewer.md#L76-L111_

### Security and Trust Boundary

The LLM remains an untrusted evidence proposer. It may identify a real defect, but its severity and proof should not be trusted merely because the prose sounds specific. The deterministic layer should verify schema completeness, file existence, line/quote agreement, changed-scope relevance, and proof-field requirements. Semantic truth still requires review judgment; the validator should reject unsupported claims rather than pretend to prove behavior mechanically.

### Integration Assessment

The most compatible design is a layered gate:

`repo-owned prompt policy -> structured reviewer finding -> deterministic evidence validation -> normalized verdict -> agent-review compatibility sidecar -> recovery/repair routing`

This preserves the current pipeline and stop-loss machinery while preventing generic `Needs Fix` prose from automatically becoming trusted work.

**Confidence:** High for the current integration flow and information-loss point; high for the proposed sidecar compatibility approach; medium for the exact finding schema until historical noise samples are analyzed.

## Architectural Patterns and Design

### Recommended System Architecture

Use a layered evidence-gate architecture:

`repository review policy -> structured LLM findings -> deterministic evidence validator -> normalized findings and verdict -> agent-review compatibility projection -> recovery and repair routing`

This retains the current Python orchestration, log artifacts, delivery profiles, and sidecar recovery model. The architectural change is localized to the boundary where reviewer prose becomes trusted workflow state.

### Architecture Options

#### Prompt-Only Policy

Add ECC-style rules to reviewer prompts and rely on the model to enforce them.

- Lowest implementation cost
- Compatible with every backend
- Improves behavior but remains non-deterministic
- Cannot prevent malformed or unsupported findings from entering downstream automation
- Vulnerable to drift when active reviewer prompts live in a user directory

This is useful as a first prompt improvement but insufficient as the final architecture.

#### Prompt Plus Advisory Validation

Require structured findings, validate evidence fields, and record whether each finding was kept, demoted, or dropped without failing the delivery pipeline.

- Produces measurable noise data
- Preserves current ADR-0005 advisory LLM posture
- Allows schema and thresholds to stabilize before enforcement
- Supports explicit rollback

This is the recommended initial deployment architecture.

#### Prompt Plus Required Validation

Use the same validator as a required gate under selected delivery profiles.

- Prevents under-evidenced findings from affecting workflow routing
- Makes severity inflation auditable
- Risks treating reviewer formatting failures as product failures unless failure semantics are carefully separated

Required mode should enforce reviewer-output quality, not claim to prove the underlying program semantics.

### Validation Boundary

The deterministic validator may safely verify:

- finding schema completeness
- repository-relative file existence
- line number or structured anchor validity
- quoted snippet or document statement agreement
- changed-scope relevance where required
- presence of the required proof fields for elevated severity
- duplicate or near-identical finding identity
- consistency between surviving findings and the final verdict

It should not claim to mechanically prove that a complex behavior will fail. The LLM remains an evidence proposer; human or workflow judgment remains responsible for semantic truth.

### Finding State Machine

Each proposed finding should move through explicit states:

`proposed -> validated | demoted | dropped | unknown`

- `validated`: evidence is complete enough for its normalized severity
- `demoted`: evidence supports a real concern but not the claimed severity
- `dropped`: missing anchor, missing failure/consequence chain, duplicate, known false positive, or no actionable change
- `unknown`: output cannot be parsed or required evidence cannot be inspected

Only `validated` and `demoted` findings may influence `Needs Fix`. If no actionable findings survive, the derived verdict is `OK`. `Unknown` is an observation gap and must not be interpreted as clean.

### Severity Architecture

Normalize the existing vocabularies into a single internal scale:

- P0 -> critical
- P1 -> high
- P2 -> medium
- P3 -> low

Retain the original severity for audit. Critical/high findings require the full proof contract. A missing proof field causes deterministic demotion or removal rather than an automatic pipeline failure.

### Sidecar Data Architecture

Preserve `summary.json` and the existing `agent-review.json` schema. Add a versioned evidence sidecar containing:

- proposed and normalized findings
- validation disposition and reason codes
- evidence anchors and proof fields
- original and normalized severity
- reviewer verdict and derived verdict
- aggregate counts for kept, demoted, dropped, duplicate, and unknown findings

`agent_to_agent_review.py` should consume the validated sidecar and project a compatibility finding rather than reducing raw reviewer prose directly to a generic medium finding.

### Chapter 3-7 Architectural Scope

The gate should be a shared workflow service with domain-specific evidence profiles, not a code-review-only component:

- **Chapter 3:** task triplet consistency, requirement traceability, acceptance falsifiability, and duplicate-task review
- **Chapter 4:** overlay/base/ADR references, contract ownership, copied-policy detection, and architecture placement review
- **Chapter 5:** semantic equivalence, obligation preservation, task-view drift, and stable-ID/contract consistency
- **Chapter 6:** code, tests, acceptance, security, performance, deterministic evidence, and reviewer closure
- **Chapter 7:** UI intent, scene/control wiring, GDD/backlog alignment, accessibility, localization, and runtime evidence

Each chapter needs its own proof profile. Requiring code snippets for a Chapter 3 task-semantic finding or an input/state/result scenario for a Chapter 4 source-placement defect would create new false positives.

### Security and Trust Architecture

Repository-owned policies must take precedence over user-scoped agent prompts. User prompts may add expertise but cannot weaken evidence requirements. The LLM output remains untrusted until validated, and all disposition decisions are written under `logs/**` for recovery and audit.

### Performance and Cost Architecture

Prompt rules are cheap compared with repeated reviewer reruns. Structured evidence adds output tokens but enables downstream deduplication and targeted reruns. The architecture should reduce total review cost by preventing vague findings from reopening Chapter 6 or causing repeated Chapter 3-7 repair loops.

### Deployment Strategy

Follow ADR-0005 and ADR-0017's staged-governance direction:

1. repository prompt policy and structured-output capture
2. advisory validation with noise metrics
3. profile-specific warn thresholds
4. required evidence validation only after historical measurements establish acceptable false-drop and unknown rates

The initial hard rule may be limited to this invariant: a reviewer result with no surviving actionable findings cannot produce `Needs Fix`.

_Local architecture sources: `docs/adr/ADR-0005-quality-gates.md`, `docs/adr/ADR-0017-quality-intelligence-dashboard-and-governance.md`, `docs/agents/07-agent-to-agent-review.md`_

_ECC source: https://github.com/affaan-m/ECC/blob/40927950c49f6e742d341e20ff7b9b7e1e7bfff5/agents/code-reviewer.md#L39-L74_

**Confidence:** High for the layered architecture and compatibility boundary; high for advisory-first rollout alignment; medium for chapter-specific proof fields until the Chapter 3-7 review implementations and historical artifacts are sampled.

## Implementation Approaches and Technology Adoption

### Empirical Noise Baseline

The template repository contains self-check and prompts-only artifacts but no usable population of real reviewer outputs. The user authorized read-only analysis of the sibling business repositories `newrouge-github-main`, `lastking`, and `sanguo`.

The evidence proves substantial review-operational noise and evidence incompleteness. It does not prove that every `Needs Fix` was a false positive.

#### Sanguo

Using only canonical Chapter 6 child LLM summaries under `logs/ci/<date>/sc-review-pipeline*/child-artifacts/sc-llm-review/summary.json`:

- 361 LLM review runs across 113 tasks
- 68.7% of runs were additional runs for a previously reviewed task
- 1,100 reviewer results: 399 OK, 463 Needs Fix, and 238 without a terminal verdict
- 217 of the 238 no-verdict results were intentional deferred semantic reviewers; 21 were genuine unresolved/no-verdict observations
- 78 reviewer timeouts; timeout and a retained textual verdict were not always mutually exclusive
- 456 complete pipeline runs represented about 34.2 hours from run start to first completion event
- 207 runs that explicitly completed the LLM step represented about 23.6 hours, with a median of 366 seconds

For the 463 `Needs Fix` outputs:

- 98.7% named a file path
- 25.7% contained an exact line anchor
- 93.7% contained an ACC or equivalent acceptance anchor
- 37.1% described an input, trigger, state, or bad-result condition
- 99.1% mentioned tests, context, or a dependency chain
- 94.6% contained a P0-P3 marker
- 0% explicitly explained why the existing safeguard, validator, type system, or test gate failed to prevent the problem

Across 355 task-reviewer combinations, 146 combinations, or 41.1%, produced both OK and Needs Fix across different rounds. Some flips reflect real code changes, but the rate is still a material reviewer-stability and rerun-cost signal.

Representative evidence includes `sanguo/logs/ci/2026-04-03/sc-review-pipeline-task-66-*/child-artifacts/sc-llm-review/`, where different rounds reached materially different semantic conclusions and at least one reviewer repeated deterministic failure information rather than producing an independent review finding.

#### NewRouge

The current repository snapshot retains only three small `logs/ci/evidence/task-*.json` files; all referenced raw pipeline and reviewer artifacts have been removed. Durable Chapter 6 records still show:

- 166 Chapter 6 decision logs across 83 tasks
- 38 tasks had two or more Chapter 6 decision records
- 83 decision records existed beyond the first record for their task
- task 111 had 14 records; task 37 had 9; tasks 48 and 78 had 7 each
- 155 of 166 decisions stated that no low-priority findings were captured
- the paired execution plans repeated the same empty scope while requiring residual findings to be closed
- at least 310 durable decision/plan documents were created for these empty-finding closure states
- exact file-line evidence in the durable decisions: zero
- complete input/state/result/guard proof chains: zero

The implementation cause is directly visible in the workflow code: raw non-OK reviewer results are reduced to generic medium findings, and residual recording may continue when the detailed low-priority finding collection is empty.

#### LastKing

The current repository snapshot also lacks the original pipeline and reviewer sidecars. Durable records show:

- 106 Chapter 6 residual or stop-loss decisions across 50 tasks
- 27 tasks had repeated decisions, creating 56 additional decision artifacts
- 100 paired residual execution plans
- 95 of 106 decisions did not preserve a concrete finding
- 151 unique referenced `logs/ci/**` paths are now missing
- the first Chapter 7-generated UI task group, T41-T46, produced 21 residual decisions; T43 alone produced 9

The one remaining raw reviewer sample acknowledged that deterministic evidence was green and acceptance metadata was missing, stated that the result could not directly prove a code defect, and still emitted `Verdict: Needs Fix`. This is a direct example of incomplete input failing to downgrade to Unknown.

### Adoption Strategy

Adopt the mechanism incrementally, with Chapter 6 first. The chapters do not all contain the same kind of review, so a single code-review prompt should not be applied across the workflow.

### Chapter 3 Implementation Profile

Chapter 3 is primarily a structured generation and deterministic validation workflow. Its review points are task-intent quality, coverage, duplicate candidates, patch inspection, triplet consistency, references, and semantic review tier.

Recommended implementation:

- retain deterministic coverage, triplet, refs, and semantic-tier validators as the decision source
- give LLM- or human-generated candidate-review notes a task-planning evidence profile
- require candidate ID, requirement ID, exact source reference, conflicting task ID when claiming duplication, and a concrete coverage or implementation consequence
- keep patch review explicit before `compile_task_triplet.py --write`
- do not add a broad code reviewer to Chapter 3

Chapter 3 false-positive exclusions:

- missing Chapter 4 overlay or final contract detail is not a Chapter 3 defect
- missing final theme tokens, screenshots, or component kits is not a Chapter 3 defect
- a soft component-routing preference is not a blocking violation unless promoted by a task or ADR
- mature Chapter 4-7 metadata should not be required merely because a historical business task contains it

### Chapter 4 Implementation Profile

Chapter 4 already uses structured JSON generation, parser validation, dry-run/simulate/apply separation, overlay execution validation, contract validation, and tests.

Recommended implementation:

- keep model-output schema and deterministic validators as hard gates
- add evidence-gated semantic review only for outliers, proposed apply patches, or conflicts that deterministic validators cannot resolve
- require overlay file and heading, exact quoted text, authoritative Base/ADR/task source, contradiction or ownership error, and downstream consequence
- do not allow the review step to rewrite acceptance during overlay generation

Chapter 4 false-positive exclusions:

- referencing Base or ADR policy instead of copying thresholds is correct
- feature slices belong in the overlay, not Base chapter 08
- absence of acceptance rewrites is intentional in the overlay-only phase
- an incomplete first scaffold is not a final-document defect before the bounded repair/apply sequence completes

### Chapter 5 Implementation Profile

Chapter 5 contains the second-highest LLM risk because obligation extraction, acceptance alignment, coverage, and semantic gates can form repeated review/rewrite loops.

Recommended implementation:

- each Needs Fix finding must cite the exact task field or source obligation and the exact acceptance item or missing acceptance location
- require the chain `source obligation -> current acceptance representation -> missing or distorted behavior -> downstream test/delivery consequence`
- classify missing or insufficient input as Unknown, not Needs Fix
- stop after extraction failure instead of adding downstream review
- retain rewrite-ratio, failure-family, timeout, and batch stop-loss controls
- store structured semantic findings before any acceptance rewrite is applied

Chapter 5 false-positive exclusions:

- do not restate deterministic refs, anchor, schema, ADR, or static-scan failures
- do not invent obligations that are not implied by the authoritative task sources
- do not rewrite acceptance merely for preferred wording
- do not report two differently worded but equivalent acceptance statements as a semantic gap
- do not treat a deliberately deferred Chapter 7 visual obligation as a Chapter 5 delivery defect

### Chapter 6 Implementation Profile

Chapter 6 is the immediate priority and the closest match to ECC.

Recommended implementation:

- add a repository-owned evidence policy after the loaded agent prompt so user-scoped prompts cannot weaken it
- require structured findings rather than parsing only the terminal verdict
- use code, semantic, security, architecture, performance, and test-specific finding profiles
- apply the ECC four-question gate to code findings
- require the full proof triplet for P0/P1
- derive the final verdict from surviving validated findings
- prohibit residual recording when the validated low-priority finding list is empty
- make residual recording idempotent by task, run, reviewer, and normalized finding family
- preserve the original severity and normalized severity
- route Unknown separately from clean
- use sanitized historical Sanguo outputs as replay fixtures

Chapter 6 false-positive exclusions should include ECC's catalog plus local cases:

- host-safe anti-tamper over-hardening when the task does not require strict tamper resistance
- web threat-model findings in an offline single-player path without an applicable boundary
- rough but structurally stable UI intentionally deferred to Chapter 7
- deterministic gate failures merely restated by an LLM as independent findings
- missing runtime evidence caused by absent review input rather than a product defect
- suggestions that do not identify an acceptance obligation or reachable bad result
- repeated finding families with no new source anchor or changed evidence
- obsolete absolute paths or unavailable evidence locations

### Chapter 7 Implementation Profile

Chapter 7 is primarily a governed document and deterministic artifact workflow: collector, UI GDD, candidate sidecar, backlog-gap analysis, manifest validation, hard gates, and task-status patch preview.

Recommended implementation:

- keep deterministic validators and manifest hashes as the hard decision source
- retain explicit human review of task-status patch previews
- add evidence-gated review only for UI intent, visual readiness, accessibility, localization, or task-candidate conflicts
- require screen/surface identity, GDD section or matrix row, task ID, scene/NodePath where relevant, viewport/screenshot artifact for visual claims, and a concrete player-facing consequence
- route generated implementation tasks back through the Chapter 6 evidence-gated reviewer profile

Chapter 7 false-positive exclusions:

- rough Chapter 6 UI is not itself a Chapter 7 defect until the corresponding retrofit acceptance is active
- subjective visual preference is not blocking without an acceptance criterion or screenshot comparison
- backend selection and new gameplay scope are outside Chapter 7
- already-covered candidate gaps should not generate duplicate tasks
- missing screenshot evidence should produce Unknown or an evidence request, not a guessed visual defect

### Shared Evidence Sidecar

Introduce a versioned review-evidence sidecar with fields for:

- workflow chapter and review domain
- reviewer identity
- proposed finding ID
- original and normalized severity
- confidence
- exact anchors and quoted evidence
- failure or consequence chain
- surrounding context inspected
- existing safeguard gap
- suggested change
- validation disposition and reason code
- derived verdict

The stable `agent-review.json` remains a compatibility projection.

### Testing and Quality Assurance

Add four test layers:

1. Prompt contract regression tests modeled on ECC, asserting that the evidence gate, zero-findings rule, elevated-severity proof, and representative false-positive entries remain present.
2. Schema and validator unit tests for invalid paths, invalid lines, quote mismatch, missing proof, severity demotion, duplicate findings, Unknown output, and zero-findings verdict derivation.
3. Chapter-specific false-positive fixtures for task planning, overlays, semantics, code/security, and UI wiring.
4. Historical replay fixtures built from sanitized Sanguo reviewer outputs and durable NewRouge/LastKing residual states.

Critical invariants:

- Needs Fix requires at least one surviving actionable finding
- P0/P1 requires complete elevated-severity proof
- invalid source anchors cannot survive validation
- zero surviving findings derives OK
- unparseable output derives Unknown
- empty low-priority findings cannot create a residual decision or execution plan

### Deployment and Operations

Roll out in advisory mode first, consistent with ADR-0005 and ADR-0017:

1. capture structured findings and metrics without changing delivery results
2. compare raw and validated verdicts
3. measure keep, demote, drop, duplicate, Unknown, flip, and repeated-family rates by chapter and reviewer
4. enable warn behavior by delivery profile
5. enable required evidence validation only after replay tests and live measurements are stable

The retained aggregate artifact must survive raw log cleanup so future analysis does not repeat the NewRouge and LastKing observability gap.

### Cost Optimization

The primary savings come from preventing invalid findings from opening another Chapter 6 round or generating empty residual records. Structured evidence adds some output tokens, but it enables targeted reviewer reruns, finding deduplication, idempotent residual recording, and chapter-specific reviewer selection.

Do not set speculative numeric blocking thresholds yet. Begin with invariant violations and observe the baseline before choosing drop-rate or flip-rate policy thresholds.

### Architecture Decision Requirement

Implementation changes the review-output contract and quality-gate policy. It should cite ADR-0005 and either update its addendum or add a new accepted ADR for evidence-gated LLM review, sidecar ownership, severity normalization, and advisory-to-required rollout.

### Success Metrics

Track at least:

- exact-anchor completeness
- failure/consequence-chain completeness
- existing-safeguard-gap completeness
- keep, demote, and drop rates
- raw-to-derived verdict changes
- OK/Needs Fix flip rate by task-reviewer pair
- repeated finding-family rate
- empty residual count
- reviewer timeout and Unknown rates
- LLM review time and rerun count by chapter
- retained evidence availability after raw-log cleanup

**Confidence:** High that Chapter 6 has material evidence-quality and workflow-churn problems; high that NewRouge and LastKing contain empty residual-recording defects; medium when classifying individual historical findings as false positives because most raw evidence is missing in those two repositories.

## Research Synthesis

### Executive Summary

ECC's reviewer policy is a strong and practical prompt design. Before emitting a finding, the model must verify an exact location, a concrete failure mode, surrounding context, and a defensible severity. Elevated findings require a code/line anchor, an input-state-outcome scenario, and an explanation of why existing safeguards do not prevent the problem. ECC explicitly permits a zero-finding review and contains a catalog of common LLM false positives.

The important qualification is that ECC does not implement a runtime fact checker. Its mechanism lives in `agents/code-reviewer.md`, and its JavaScript CI test asserts that the policy text remains present. The proposed local design should adopt ECC's prompt policy and add deterministic output-ingestion validation because local reviewer verdicts drive recovery, reruns, residual recording, and durable workflow state.

The business-repository evidence demonstrates a real need. In Sanguo, only 25.7% of 463 canonical Chapter 6 `Needs Fix` outputs contained an exact line anchor, 37.1% described a failure condition, and none explicitly explained why existing safeguards failed. NewRouge and LastKing generated large numbers of durable residual records without retaining concrete findings. This proves evidence and workflow noise; it does not prove that every historical finding was incorrect.

### Table of Contents

1. Technical Research Scope Confirmation
2. Technology Stack Analysis
3. Integration Patterns Analysis
4. Architectural Patterns and Design
5. Implementation Approaches and Technology Adoption
6. Research Synthesis
7. Strategic Recommendation
8. Chapter 3-7 Decision Matrix
9. Implementation Roadmap
10. Risks and Limitations
11. Source Verification

### Key Verified ECC Findings

- Canonical repository: `affaan-m/ECC`; the former repository name was replaced in ECC 2.0.
- Fixed research commit: `40927950c49f6e742d341e20ff7b9b7e1e7bfff5`.
- Context and confidence filtering: `agents/code-reviewer.md` lines 19-37.
- Four-question fact gate: lines 39-53.
- HIGH/CRITICAL proof triplet: lines 55-64.
- Zero-finding rule: lines 66-74 and approval rules at lines 290-297.
- Common false-positive catalog: lines 76-111.
- Prompt-regression CI contract: `tests/ci/code-reviewer-false-positive-guard.test.js`.
- ECC does not contain a dedicated document-review agent implementing the same full gate.

_Primary ECC source: https://github.com/affaan-m/ECC/blob/40927950c49f6e742d341e20ff7b9b7e1e7bfff5/agents/code-reviewer.md#L19-L111_

_ECC regression test: https://github.com/affaan-m/ECC/blob/40927950c49f6e742d341e20ff7b9b7e1e7bfff5/tests/ci/code-reviewer-false-positive-guard.test.js#L8-L75_

### Business-Repository Evidence Summary

| Repository | Usable raw reviewer evidence | Durable review-churn evidence | Main result |
|---|---:|---:|---|
| Sanguo | 361 canonical Chapter 6 LLM runs; 1,100 agent results | 463 Needs Fix outputs | Exact line 25.7%; failure-condition signal 37.1%; safeguard-gap proof 0%; 41.1% task-reviewer OK/Needs Fix flip rate |
| NewRouge | Raw pipeline artifacts removed | 166 Chapter 6 decisions across 83 tasks | 155 decisions captured no low-priority finding but still created residual closure state; at least 310 empty decision/plan documents |
| LastKing | Raw pipeline artifacts almost entirely removed | 106 decisions and 100 residual plans | 95 decisions retained no concrete finding; 27 of 50 tasks had repeated decision records |

The absence of retained raw artifacts in NewRouge and LastKing limits false-positive classification and cost reconstruction. It also establishes a requirement for a durable aggregate evidence sidecar that survives raw-log cleanup.

### Strategic Recommendation

Adopt ECC's reviewer policy, but do not stop at prompt text. Implement a repository-owned, chapter-aware evidence system:

`review policy -> structured proposed findings -> deterministic evidence validation -> normalized findings and derived verdict -> compatibility agent-review sidecar -> recovery and repair routing`

The system must enforce these invariants:

- `Needs Fix` requires at least one surviving actionable finding.
- P0/P1 requires the elevated-severity proof contract.
- Invalid or unverifiable anchors cannot survive validation.
- Zero surviving findings derives `OK`.
- Unparseable or insufficient-input output derives `Unknown`.
- Empty low-priority findings cannot create residual decisions or execution plans.

### Chapter 3-7 Decision Matrix

| Chapter | Existing review character | Recommended evidence gate | Enforcement priority |
|---|---|---|---|
| 3 | Structured task generation, coverage audit, patch review, deterministic triplet validation | Task ID, requirement/source anchor, duplicate target, concrete coverage consequence | Medium; deterministic-first |
| 4 | LLM overlay generation with JSON parsing, dry-run/simulate/apply, deterministic overlay and contract validation | Document heading/quote, Base/ADR/task authority, contradiction or ownership consequence | Medium; outliers and apply patches |
| 5 | LLM obligation extraction, acceptance alignment, coverage, semantic gate, repeated rewrite risk | Source obligation, acceptance anchor, missing-behavior chain, test/delivery consequence | High; second implementation target |
| 6 | Code, security, test, semantic, architecture, and performance reviewers affecting reruns and residual state | ECC code gate plus reviewer-specific proof profiles and deterministic ingestion validation | Critical; first implementation target |
| 7 | UI GDD, candidate sidecar, manifest, backlog-gap, hard gates, task-status preview | Screen/surface, GDD row, task/scene anchor, screenshot or accessibility/localization evidence, player consequence | Medium; deterministic-first |

### Local False-Positive Catalog

The repository should adopt ECC's catalog and add chapter-specific exclusions.

#### Cross-Chapter

- Do not restate a deterministic validator failure as an independent LLM discovery.
- Do not convert missing review input into a product defect.
- Do not repeat a finding family without a new anchor or changed evidence.
- Do not accept obsolete absolute paths or inaccessible evidence.
- Do not treat advisory component-routing preferences as hard requirements unless promoted by a task or ADR.

#### Chapter 3

- Missing Chapter 4 overlays or final contracts is not a task-planning defect.
- Missing Chapter 7 visual polish is not a task-planning defect.
- Historical mature-task metadata is not automatically required for new candidates.

#### Chapter 4

- Referencing Base/ADR policy rather than copying thresholds is correct.
- Not rewriting acceptance during overlay generation is intentional.
- A first-pass scaffold is not a final-quality document before bounded repair/apply completes.

#### Chapter 5

- Do not invent obligations absent from authoritative sources.
- Do not rewrite semantically equivalent acceptance only for style.
- Do not report refs, anchors, schemas, or static checks already enforced deterministically.
- Do not promote deliberately deferred Chapter 7 visual work into a Chapter 5 defect.

#### Chapter 6

- Do not demand strict anti-tamper under `host-safe` unless the task requires it.
- Do not apply web threat assumptions to an offline single-player path without a boundary.
- Do not treat rough but structurally stable UI as a Chapter 6 failure when Chapter 7 owns retrofit.
- Do not convert suggestions, best-practice preferences, or hypothetical edges into findings without a reachable bad result.
- Apply ECC's framework-handled errors, caller validation, magic-number, long-function, JSDoc, null-guard, N+1, missing-await, TypeScript migration, test/example hardcoding, and security-theater exclusions.

#### Chapter 7

- Subjective visual preference is not blocking without acceptance or screenshot comparison.
- Backend selection and new gameplay scope are outside Chapter 7.
- An already-covered backlog gap must not create a duplicate task.
- Missing screenshot evidence should produce `Unknown` or an evidence request, not a guessed visual defect.

### Implementation Roadmap

#### Phase 1: Chapter 6 Evidence Capture

- Add a repository-owned review evidence policy appended after external agent prompts.
- Define a versioned review-evidence schema.
- Parse structured findings before accepting the terminal verdict.
- Preserve original severity, normalized severity, anchors, proof, disposition, and derived verdict.
- Fix empty residual recording and make residual writes idempotent.

#### Phase 2: Deterministic Validation and Replay

- Validate file existence, line ranges, quotes, required proof fields, and duplicates.
- Add zero-finding, Unknown, demotion, and verdict-consistency tests.
- Build sanitized replay fixtures from Sanguo outputs.
- Add NewRouge and LastKing empty-residual regression fixtures.

#### Phase 3: Chapter 5 Semantic Findings

- Add structured obligation and acceptance anchors.
- Preserve findings before rewrites.
- Treat missing input as Unknown and extraction failure as stop-and-fix.
- Prevent deterministic-rule restatement and invented obligations.

#### Phase 4: Chapter 3, 4, and 7 Profiles

- Add task-planning, architecture-document, and UI-document evidence profiles.
- Keep existing deterministic gates authoritative.
- Apply LLM review only where deterministic validation cannot decide the issue.

#### Phase 5: Governance

- Run advisory-only measurements first.
- Track keep, demote, drop, duplicate, Unknown, flip, timeout, rerun, and empty-residual rates.
- Enable warn and require behavior by delivery profile only after replay and live evidence are stable.
- Update ADR-0005 or add a new accepted ADR before changing the hard review contract.

### Risks and Limitations

- Exact line presence is necessary for code findings but not sufficient to prove correctness.
- Document and semantic findings need structured anchors and consequence chains rather than artificial code scenarios.
- Historical code changes explain some OK/Needs Fix flips; flip rate is a stability signal, not a direct false-positive rate.
- NewRouge and LastKing raw artifact deletion prevents complete retrospective classification.
- Structured evidence increases output size, but should reduce total cost by preventing vague reruns and empty closure work.
- A strict formatter failure must be classified as reviewer `Unknown`, not as a product defect.

### Source Verification

Primary public sources were verified against a fixed ECC commit rather than the moving default branch. Local technical claims were verified against the current Python harness, prompt templates, sidecar contracts, ADRs, Chapter 3-7 workflow documentation, and read-only business-repository artifacts.

Key local sources:

- `scripts/sc/_llm_review_prompting.py`
- `scripts/sc/_llm_review_engine.py`
- `scripts/sc/_llm_backend.py`
- `scripts/sc/agent_to_agent_review.py`
- `scripts/sc/_agent_review_contract.py`
- `scripts/sc/templates/llm_review/bmad-godot-review-template.txt`
- `workflow.md`
- `docs/workflows/chapter3-7-component-routing.md`
- `docs/workflows/ui-ux-implementation-policy.md`
- `docs/adr/ADR-0005-quality-gates.md`
- `docs/adr/ADR-0017-quality-intelligence-dashboard-and-governance.md`

### Final Conclusion

The repository needs an ECC-derived anti-hallucination policy. The strongest evidence is not merely that reviewer prose can be vague; it is that vague or detail-losing verdicts currently enter automated recovery and residual workflows. Chapter 6 should be corrected first by preserving and validating individual findings before deriving workflow state. Chapter 5 should follow with semantic-specific proof. Chapters 3, 4, and 7 should remain deterministic-first and receive narrower evidence profiles for the review points they actually contain.

The target is not fewer findings at any cost. The target is fewer unsupported findings, no empty closure work, defensible severity, explicit Unknown states, and a review history that remains auditable after raw logs are removed.

**Technical Research Completion Date:** 2026-07-12

**Overall Confidence:** High for the ECC source analysis, current harness architecture, Chapter 6 priority, and empty-residual defect; medium for the historical false-positive rate because two business repositories no longer retain raw reviewer outputs.
