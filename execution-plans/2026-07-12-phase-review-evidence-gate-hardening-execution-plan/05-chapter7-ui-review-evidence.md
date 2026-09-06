# Chapter 7 UI Review Evidence

## Purpose

Define evidence requirements for UI GDD, wiring candidates, screenshot readiness, accessibility, localization, backlog gaps, and task-status review without turning visual preference into a hard defect.

## Existing Decision Sources

- Chapter 7 input collector
- UI GDD writer
- UI wiring validator
- candidate sidecar
- backlog-gap and duplicate audit
- artifact manifest and hash validator
- hard-gate summary
- task-status patch preview and explicit apply

These deterministic artifacts remain authoritative for structure, identity, hashes, and declared required sections.

## Evidence Profile

A Chapter 7 finding requires the relevant subset of:

- screen or surface ID
- UI GDD section, matrix row, or candidate ID
- related task ID and Chapter 3 `ui_ux_seed` category
- scene path and NodePath/control identity
- state/input/localization/accessibility condition
- screenshot artifact and viewport for visual claims
- expected criterion and observed mismatch
- player-facing consequence
- existing validator or manifest gap
- suggested bounded UI-wiring change

## Visual Findings

Visual readiness findings require inspectable image evidence. A reviewer must record:

- screenshot path and hash
- viewport and scale
- surface/state under review
- objective acceptance criterion
- observed region or comparison

Without screenshot evidence, return Unknown or request evidence. Do not guess.

## Accessibility Findings

Require:

- control/surface identity
- input method or assistive condition
- expected focus, label, contrast, text-fit, or navigation behavior
- observed failure and affected user action
- existing automated or manual check gap

## Localization Findings

Require:

- localization key or visible text anchor
- language/locale
- surface and state
- missing, clipped, stale, or hardcoded behavior
- screenshot or deterministic translation evidence when applicable

## False-Positive Exclusions

- rough Chapter 6 UI before its Chapter 7 retrofit task is active
- subjective aesthetic preference without acceptance or comparison evidence
- backend selection or new gameplay scope
- duplicate candidate already covered by an existing task or closure row
- missing screenshot treated as proof of visual failure
- final art direction demanded from a Chapter 3 seed
- a soft Node/Scene component preference treated as a hard violation without promotion

## Generated Task Boundary

Chapter 7 planning review does not replace implementation review. Generated tasks return to Chapter 6 and use the Chapter 6 evidence profiles for code, tests, security, and semantics.

Chapter 7 evidence must remain attached to generated task acceptance through:

- candidate source ID
- UI GDD section
- screen/surface ID
- expected screenshot/accessibility/localization artifact
- related Chapter 3 seed category

## Task Status Patch Review

Status patch review requires:

- current and proposed status
- closure evidence path
- mismatch reason
- operator intent check
- affected active implementation task

No LLM may directly apply a status patch. The existing preview/apply boundary remains explicit.

## Tests

- missing screenshot -> Unknown
- objective screenshot mismatch -> validated finding
- subjective style preference -> dropped
- duplicate covered candidate -> dropped
- missing localization key with exact surface -> validated finding
- inaccessible focus path with control/state evidence -> validated finding
- status patch conflict -> explicit review stop
- Chapter 6 rough UI deferred to Chapter 7 -> false-positive drop

## Acceptance

- Chapter 7 deterministic gates remain authoritative.
- Visual Needs Fix cannot exist without inspectable visual evidence.
- UI findings identify a surface, state, criterion, and player consequence.
- Duplicate tasks are not created from review prose.
- Status mutations retain explicit operator review.
