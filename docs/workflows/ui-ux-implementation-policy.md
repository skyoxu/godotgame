# UI/UX Implementation Policy

## Purpose

This document defines how this repository turns game UX intent into Godot UI implementation work. It adds a lightweight UI/UX seed to Chapter 3 and a full UI/UX retrofit and acceptance layer to Chapter 7.

The policy is adapted from a comparison of this repository with Claude Code Game Studios, AlterLab GameForge, and OpenCode Game Studios. Those projects are used as selective design references only. This repository keeps its BMAD/GDS, Chapter 3-7, Taskmaster, architecture overlay, CI, and recovery workflow as the controlling flow.

## Upstream Inspiration Baseline

Reviewed upstream projects:

| Source | Repository | Baseline | Useful UI/UX Idea | Adopted As |
| --- | --- | --- | --- | --- |
| Claude Code Game Studios | <https://github.com/Donchitos/Claude-Code-Game-Studios> | `main` at `984023ddac0d5e27624f2baacde6105e45de375f`, checked 2026-06-22 | Explicit UX, HUD, UI programming, and accessibility responsibilities | Role responsibility cues for screen contracts and implementation review |
| AlterLab GameForge | <https://github.com/AlterLab-IEU/AlterLab_GameForge> | `main` at `5f5148d61986b32299070e87fcd4a1ab3718eacf`, checked 2026-06-22 | Accessibility, localization, and UI checklist material | Automatable or semi-automatable checks only |
| OpenCode Game Studios | <https://github.com/striderZA/OpenCodeGameStudios> | `master` at `3f0085d509eb3881c136385ac90b4c867c9ff326`, checked 2026-06-22 | Pre-workflow prototyping, phase gates, and discovery-to-production transition | Chapter 3 UI/UX seed and Chapter 7 readiness gates |

Do not import their studio hierarchies, installation commands, generic agent routing, or full workflow systems. If concrete wording, tables, formulas, or templates are adapted later, cite the upstream repository and checked commit in the receiving document, decision log, execution plan, or attribution record.

## Chapter Placement

Use this split:

| Stage | UI/UX Responsibility | Output Strength | Non-Goal |
| --- | --- | --- | --- |
| Chapter 3 | UI/UX Intent Seed | Enough structure to prevent throwaway UI architecture | Final art direction or polished layout |
| Chapter 6 | Functional implementation | Working UI can remain rough if structure is stable | Full visual polish |
| Chapter 7 | UI/UX Retrofit, wiring closure, and acceptance | Player-facing UI is coherent, testable, and screenshot-backed | New core gameplay scope |
| Post-Chapter-7 Polish Lane | Optional release polish | Final screenshot regression and small visual cleanup | A formal Chapter 8 or new feature phase |

Do not create a formal Chapter 8 for UI/UX by default. Chapter 7 must close the UI to an acceptable level; the post-Chapter-7 polish lane is only for release polish and debt cleanup.

## Chapter 3 UI/UX Intent Seed

Chapter 3 should add roughly 20 percent of UI/UX planning before task generation becomes implementation work. The goal is to protect downstream scene structure, input naming, screen ownership, and player-facing state visibility.

When a feature has a player-facing surface, Chapter 3 task candidates should include or reference:

- `screen_inventory_seed`: the likely screens or panels touched by the feature.
- `player_flow_map`: the entry, success, failure, cancel, and return paths visible to the player.
- `hud_priority`: always-visible, contextual, and feedback-only data categories.
- `input_model`: keyboard, mouse, controller, and action-map expectations.
- `state_visibility`: loading, empty, disabled, error, hover, focus, active, success, and failure states that matter.
- `localization_seed`: player-visible text should be planned as localization keys when feasible, not source text embedded in scripts.
- `accessibility_baseline`: focus visibility, no color-only state, text overflow risk, motion or screen-shake settings when relevant, and readable text sizing.
- `ui_risk_notes`: screens likely to need a later Chapter 7 retrofit, screenshot check, or component extraction.

Chapter 3 does not need final theme tokens, complete component kits, high-fidelity mockups, or screenshot evidence.

## Chapter 6 Structural Expectations

Chapter 6 can ship rough UI, but it should avoid choices that make Chapter 7 expensive:

- Keep screen roots, scene paths, state names, and input actions stable once a feature is accepted.
- Prefer thin `*View.cs`, `*Panel.cs`, or equivalent Godot UI scripts for presentation and input wiring.
- Keep gameplay rules and deterministic state mutation in `Game.Core`.
- Avoid one-off UI roots for major screens when a reusable screen or panel component is already implied.
- Avoid hardcoded player-facing text when the project has or expects localization.
- Preserve enough scene structure for later screenshot, focus, and layout checks.

## Chapter 7 UI/UX Retrofit Layer

Chapter 7 owns the remaining 80 percent of UI/UX work. It converts completed capabilities and rough UI into a coherent player-facing experience.

Chapter 7 should produce or update:

- Screen contracts for every major player-facing surface.
- A UI wiring matrix that maps completed features to surfaces and player actions.
- Theme tokens for colors, typography, spacing, focus style, disabled state, danger/warning/success states, HUD styling, and modal styling.
- A UI component kit plan or implementation tasks for common controls and HUD elements.
- Screenshot acceptance requirements for key resolutions and key UI states.
- Accessibility and localization checks tied to concrete artifacts.
- A post-Chapter-7 polish lane only when the remaining work is release polish rather than missing UI closure.

## Screen Contract Template

Use this shape for each major screen or panel:

```md
# Screen Contract: <screen-id>

- Scene path:
- Owner script:
- Entry conditions:
- Exit paths:
- Primary player goal:
- Required visible data:
- Required commands:
- Required states:
- Input actions:
- Focus order:
- Localization keys:
- Accessibility checks:
- Screenshot baselines:
- Acceptance criteria:
- No-UI rationale, if applicable:
```

A completed `status = done` feature that touches the player should either appear in a screen contract or carry an explicit no-UI rationale.

## Component Kit Expectations

Prefer reusable Godot UI/control scenes for repeated controls. Start small and expand only when the same pattern appears on multiple screens.

Expected component families:

- Button, icon button, and toggle.
- Panel, section header, footer, and divider.
- Modal, confirmation dialog, tooltip, and toast.
- Tab, segmented control, list item, and card.
- HUD meter, stat row, resource counter, reward card, and inventory slot.
- Settings row, slider row, keybind row, and volume row.
- Focus frame and input prompt.

Each reusable component should define public API, exported references, signals/events, disabled state, focus behavior, localization handling, and minimal screenshot or scene-test expectations when feasible.

## Screenshot Acceptance

Chapter 7 acceptance should prefer screenshot-backed evidence when a UI change claims visual readiness.

Minimum screenshot set for major screens:

- `1280x720` default layout.
- `1920x1080` default layout.
- Small-window layout such as `960x540` when the game supports window resizing.
- Focus-visible state.
- Hover, pressed, selected, and disabled state when relevant.
- Long-text or pseudolocalization state when localization is relevant.

Screenshot checks may begin as manual evidence and later become automated. The acceptance record should store the screenshot paths under `logs/` or another agreed evidence directory.

## Accessibility And Localization Checks

Adopt only checks that can be tied to artifacts, scripts, scene inspection, screenshots, or explicit acceptance notes:

- No player-critical information conveyed by color alone.
- Focus path exists for keyboard/controller flows.
- Focus state is visible.
- Player-visible text uses localization keys when localization is in scope.
- Placeholder integrity is preserved across localized strings.
- Text does not overflow its intended container in required screenshots.
- Readable text size and line height are suitable for target resolutions.
- Separate volume channels exist when audio settings are in scope.
- Subtitles, screen-shake reduction, motion reduction, hold-toggle alternatives, and rebindable input exist when the feature requires them.

Subjective playtest feedback remains useful, but it is not a Chapter 7 hard gate unless converted into a concrete artifact, check, or acceptance criterion.

## Post-Chapter-7 Polish Lane

Use this optional lane only after Chapter 7 has produced an acceptable UI closure. It may handle:

- final screenshot regression,
- small spacing and alignment fixes,
- final icon or art replacement,
- accessibility debt cleanup,
- localization debt cleanup,
- release candidate visual review.

It must not add new core gameplay scope, replace screen contracts wholesale, or defer required Chapter 7 UI closure.

## Upgrade Procedure

When refreshing this policy against newer upstream versions:

1. Re-check the current upstream branch, tag or release, commit, check date, and license status.
2. Review only UI/UX implementation, accessibility, localization, screenshot evidence, prototyping gate, and phase-gate material.
3. Reject upstream material that remains only coaching, roleplay, generic studio hierarchy, or non-Godot workflow routing.
4. Convert accepted material into repository-owned Chapter 3 seed rules, Chapter 7 retrofit rules, screen contracts, component kit expectations, checks, or validation evidence.
5. Record accepted upgrades in this document, an execution plan, or a decision log when they affect future workflow behavior.
