# AlterLab Patch Policy

## Purpose

This document records how this repository may use content from the public AlterLab GameForge project as a selective patch source.

AlterLab GameForge is not a replacement for this repository's BMAD/GDS-derived design flow, Chapter 3-7 workflow, Taskmaster integration, architecture overlays, CI gates, or local recovery pipeline. It is treated as an external reference for narrowly scoped game-development knowledge that can be converted into repository-owned rules, templates, checks, simulations, or tests.

## Source

Primary upstream source:

- Repository: <https://github.com/AlterLab-IEU/AlterLab_GameForge>
- Relevant upstream areas as of the initial review:
  - `skills/workflows/game-localization-manager/`
  - `skills/workflows/game-balance-check/`
  - `skills/agents/game-economy-designer/`
  - `skills/agents/game-ux-designer/`
  - `skills/agents/game-accessibility-specialist/`
  - `genre-packs/roguelike/`
  - `genre-packs/narrative/`

The initial policy decision was based on the public AlterLab GameForge repository observed in June 2026. Future updates must re-check the current upstream state before changing this repository.

## Baseline And Attribution

Initial upstream baseline:

- Date checked: 2026-06-22
- Branch checked: `main`
- Commit checked: `5f5148d61986b32299070e87fcd4a1ab3718eacf`
- Upstream license at check time: MIT License

When this repository adapts concrete wording, tables, formulas, or templates from AlterLab rather than independently restating the idea, the receiving document, decision log, execution plan, or other attribution record must cite AlterLab GameForge and the checked commit or release. Prefer paraphrased repository-owned rules over copied upstream prose.

Do not vendor AlterLab files directly unless the user explicitly asks for that import and the resulting license/attribution obligations are recorded in the same change.

## Integration Rule

Adopt only material that can become one of the following:

- A repository-owned engineering rule.
- A deterministic validation check.
- A code or data test.
- A reusable template field.
- A simulation model or measurable tuning metric.
- A concise checklist that can be tied to a gate, acceptance note, or implementation artifact.

Do not adopt material that remains only facilitation, coaching, roleplay, brainstorming, or human-only instruction.

## Allowed Patch Areas

### Localization Engineering

This is the highest-value AlterLab patch area for this repository.

Allowed ideas to adapt:

- Externalize all player-facing strings from code and scenes.
- Use stable hierarchical localization keys, not source text as keys.
- Forbid programmatic sentence concatenation for player-facing text.
- Prefer parameterized strings with reorderable placeholders.
- Add pseudolocalization checks to catch hardcoded strings, overflow, encoding issues, and layout assumptions.
- Validate placeholder integrity across localized strings.
- Reserve design rules for CJK font fallback, line height, line breaking, text input, and IME behavior.
- Track translator context metadata when real localization begins: screen, speaker, tone, maximum length, and screenshot reference.

Repository direction:

- Convert these into Godot/C# i18n conventions, validation scripts, and CI-friendly checks when localization work starts.
- Keep translation quality review, cultural review, and LQA as human processes outside the automated gate unless concrete checks exist.

### Economy And Balance Modeling

Allowed ideas to adapt:

- Faucet/sink resource flow models.
- Run economy tables.
- Upgrade cost and reward curves.
- Drop-rate and pity-system validation.
- Time-to-kill targets.
- Win-rate ranges for simulated archetypes.
- Reward gap analysis.
- Currency surplus/deficit tracking.
- Monte Carlo simulation for randomized systems.
- Percentile reporting such as P5/P50/P95 for unlucky, median, and lucky paths.
- Dominant-strategy detection through pick-rate, win-rate, or expected-value analysis.

Repository direction:

- Prefer `Game.Core` formulas, xUnit tests, deterministic fixture data, and Python simulation scripts over prose-only balance advice.
- Balance claims should become numbers, assertions, or repeatable reports before they are treated as repository policy.

### Game Type Template Enhancements

Do not import AlterLab genre packs as a second game-type system. This repository already carries the BMAD/GDS 24 game-type template set.

Allowed narrow enhancements:

- For roguelike templates:
  - Run-length targets.
  - First power-spike timing.
  - Meta-progression warnings that permanent upgrades must not flatten difficulty.
  - Pity-system and false-randomness notes.
  - Item pick-rate boundaries.
  - Build entropy or build-diversity metrics.
  - Shop price versus income ratio checks.
  - Death should teach; avoid death-tax design.
- For narrative or visual-novel templates:
  - Branch architecture categories.
  - Active-branch budget.
  - State-variable budget.
  - Consequence mapping tables.
  - Authored-word versus read-word ratio.
  - Choice split ratio checks.
  - Invisible-consequence and exposition-dump anti-pattern checks.

Repository direction:

- Add only concise, executable checks or fields to the existing BMAD/GDS game-type templates.
- Update the canonical BMAD/GDS source template first, then sync any docs-side mirror so `docs/game-type-guides/` does not drift from the active BMAD/GDS game-type source path recorded in this repository at upgrade time.
- Do not add AlterLab as a parallel routing layer.

### UX And Accessibility Checks

Allowed ideas to adapt only when they can become automated or semi-automated checks:

- Minimum readable text size rules.
- No information conveyed by color alone.
- Keyboard or controller focus path coverage.
- Text overflow detection from screenshots or UI scene inspection.
- Separate volume-channel settings.
- Subtitle settings presence.
- Screen-shake and motion-effect reduction settings.
- Toggle alternatives for held inputs.
- Centralized and rebindable input mapping.

Repository direction:

- Treat purely subjective usability review as human feedback, not as an automated quality gate.
- Prefer Godot scene scans, config checks, screenshot checks, and scripted navigation checks when feasible.

## Excluded Patch Areas

The following AlterLab areas are not planned for adoption as repository workflow rules:

- Playtest facilitation templates that depend on human players and observers.
- Market research workflows.
- Studio-agent role systems.
- AlterLab command or installation routing.
- General engine specialists for Unity, Unreal, or multi-engine support.
- AlterLab CI pipeline templates that conflict with this repository's existing Windows/Godot/C# pipeline.
- Full genre-pack imports.
- Prompt-only guidance that cannot be tied to artifacts, checks, tests, simulations, or implementation rules.

## Upgrade Procedure

When the user asks to refresh this repository against a newer AlterLab GameForge version:

1. Check the current upstream repository and release state.
2. Record the upstream branch, tag or release, commit, check date, and license status in the proposed change.
3. Review only the allowed patch areas listed in this document.
4. Compare upstream changes against the current repository-owned rules, templates, scripts, and tests.
5. Propose a narrow upgrade plan that separates:
   - localization engineering changes,
   - economy/balance modeling changes,
   - game-type template enhancements,
   - UX/accessibility check changes.
6. Reject upstream changes that remain coaching-only or duplicate existing BMAD/GDS coverage.
7. Preserve this repository's Chapter 3-7 workflow, architecture invariants, CI gates, and recovery protocol.
8. Record any accepted upgrade as repository-owned documentation, code, tests, or scripts, not as a blind copy of AlterLab routing.
9. Add attribution when adapted content is more specific than a general idea or design principle.
10. Record accepted upgrades in the changed document, an execution plan, or a decision log when the change affects future workflow behavior.

## Decision Summary

AlterLab GameForge is useful here as a selective external patch source, not as a workflow dependency. The preferred adoption path is:

1. Localization engineering checks.
2. Economy and balance simulations/tests.
3. Small roguelike and narrative template enhancements.
4. UX/accessibility checks that can become automated or semi-automated.

Everything else remains outside the main flow unless a future upstream version adds concrete, automatable, repository-compatible material.
