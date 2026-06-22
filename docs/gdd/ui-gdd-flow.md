---
GDD-ID: GDD-TEMPLATE-UI-FLOW-V1
Title: Template UI Wiring Flow GDD
Status: Template
Owner: template-owner
Last Updated: 2026-06-22
Encoding: UTF-8
Applies-To:
  - .taskmaster/tasks/tasks.json
  - .taskmaster/tasks/tasks_back.json
  - .taskmaster/tasks/tasks_gameplay.json
ADR-Refs:
  - ADR-0010
  - ADR-0011
  - ADR-0019
  - ADR-0025
---

# Template UI Wiring Flow GDD

This file is the Chapter 7 UI wiring and UI/UX retrofit SSoT template. Business repositories should replace the placeholder rows with their own player-facing UI flow, scenes, contracts, tests, screenshot evidence, accessibility checks, and localization checks.

## 1. Scope And Goal

Chapter 7 does not rewrite PRD, GDD, or architecture overlays. It converts completed domain and gameplay capabilities into player-facing UI wiring and finishes the UI/UX retrofit required for acceptable player-facing delivery.

Use this document after the relevant backlog slice has completed Chapter 6 and no unrecorded P0/P1 Needs Fix remains.

Formal Chapter 7 UI wiring follows `docs/workflows/chapter3-7-component-routing.md`: components are Godot Node/Scene Components, not ECS components; Godot scripts own lifecycle/presentation/input/wiring while `Game.Core` owns rules, state mutation, and simulation.

Formal Chapter 7 UI/UX retrofit follows `docs/workflows/ui-ux-implementation-policy.md`: Chapter 3 provides lightweight UI/UX intent seed, Chapter 7 provides screen contracts, theme tokens, component kit planning, screenshot acceptance, accessibility checks, and localization checks. Do not defer required UI closure to a formal Chapter 8.

## 2. Player Loop Backbone

Describe the playable loop from the player's point of view.

Example structure:

1. Main menu.
2. New run or continue.
3. Character or setup selection.
4. Core gameplay screen.
5. Reward, event, shop, rest, or summary surfaces.
6. Return, fail, win, or continue boundary.

## 3. Completed Capability Groups

Group completed tasks by player-facing capability, not by implementation module.

| Capability Group | Task IDs | Player-Facing Meaning | Primary UI Need |
| --- | --- | --- | --- |
| Example runtime foundation | T0 | Player can start the project | Main scene enters a visible shell |

## 4. Player Experience Flows

Document the concrete flows the player should experience.

### 4.1 Main Entry Flow

Describe how the player reaches the first meaningful interaction.

### 4.2 Core Gameplay Flow

Describe the main loop and state transitions.

### 4.3 Secondary Surface Flow

Describe supporting screens such as reward, rest, shop, event, inventory, settings, or run summary.

## 5. UI Wiring Matrix

Every completed feature that needs a player-facing surface should appear here.

| Feature | Task IDs | UI Surface | Player Action | System Response | State Boundary | Test Refs |
| --- | --- | --- | --- | --- | --- | --- |
| Example completed feature | T0 | `Game.Godot/Scenes/Main.tscn` | Start | Show first playable screen | Does not mutate save data | `TODO` |

## 6. Screen Contracts

Define the UI contract for each major surface. A completed `status = done` feature that touches the player should either appear in a screen contract or carry an explicit no-UI rationale.

### 6.1 Main Menu

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

### 6.2 Core Gameplay Screen

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

## 7. Theme Tokens And Component Kit

Record the visual system and reusable UI/control scenes needed to make Chapter 7 work consistent.

### 7.1 Theme Tokens

| Token Area | Decision | Evidence Or Asset |
| --- | --- | --- |
| Colors | TODO | TODO |
| Typography | TODO | TODO |
| Spacing | TODO | TODO |
| Focus style | TODO | TODO |
| Disabled state | TODO | TODO |
| Danger/warning/success states | TODO | TODO |
| HUD styling | TODO | TODO |
| Modal styling | TODO | TODO |

### 7.2 Component Kit

| Component | Scene Or Script | Public API | Required States | Test Or Screenshot Refs |
| --- | --- | --- | --- | --- |
| Button / icon button / toggle | TODO | TODO | default, focus, hover, pressed, disabled | TODO |
| Panel / modal / tooltip / toast | TODO | TODO | open, close, disabled where relevant | TODO |
| HUD meter / stat row / resource counter | TODO | TODO | default, warning, critical | TODO |
| Reward card / inventory slot / list item | TODO | TODO | default, selected, disabled | TODO |
| Settings row / slider row / keybind row | TODO | TODO | default, focus, editing, disabled | TODO |

## 8. Validation Plan

List automated or manual validation for each flow.

| Flow | Validation Type | Test Refs Or Manual Evidence |
| --- | --- | --- |
| Main entry | automated or manual | TODO |

### 8.1 Screenshot Acceptance

Major screens should include screenshot-backed evidence when a UI change claims visual readiness.

| Screen | Resolution Or State | Evidence Path | Notes |
| --- | --- | --- | --- |
| Main menu | `1280x720` | TODO | TODO |
| Main menu | `1920x1080` | TODO | TODO |
| Main menu | focus-visible | TODO | TODO |
| Core gameplay screen | `1280x720` | TODO | TODO |
| Core gameplay screen | `1920x1080` | TODO | TODO |
| Core gameplay screen | long-text or pseudolocalization, if relevant | TODO | TODO |

### 8.2 Accessibility And Localization Checks

| Check | Applies To | Evidence |
| --- | --- | --- |
| No player-critical information conveyed by color alone | TODO | TODO |
| Keyboard/controller focus path exists | TODO | TODO |
| Focus state is visible | TODO | TODO |
| Player-visible text uses localization keys when localization is in scope | TODO | TODO |
| Text does not overflow required screenshots | TODO | TODO |
| Readable text size and line height are suitable for target resolutions | TODO | TODO |
| Audio, subtitles, motion, screen-shake, hold-toggle, or rebind settings exist when required | TODO | TODO |

## 9. Risks And Stop-Loss

List UI wiring risks that should stop Chapter 7.

- A completed `status = done` task has no UI surface or explicit no-UI rationale.
- A UI surface bypasses the domain/service boundary.
- Player-visible text bypasses localization rules when the project has i18n requirements.
- UI actions mutate deterministic state during preview, hover, refresh, or open-panel behavior.
- A major screen has no screen contract.
- A UI readiness claim has no screenshot, scene test, manual evidence, or explicit waiver.
- A major screen has no keyboard/controller focus path when keyboard/controller input is in scope.

## 10. Chapter 3-7 Component Routing Preferences

Apply `docs/workflows/chapter3-7-component-routing.md` as a soft preference for formal Chapter 7 UI wiring. This is not a hard gate and does not apply to prototype-lane work.

- Treat Component as a Godot Node/Scene Component, not an ECS component.
- Keep Godot scripts focused on lifecycle, presentation, input, and wiring.
- Keep gameplay rules, state mutation, and simulation logic in `Game.Core` unless the task or ADR explicitly scopes otherwise.
- Prefer exported `NodePath` wiring over deep hardcoded paths when the UI surface depends on child nodes.
- Prefer direct calls, Godot signals, or C# events inside one UI wiring slice; use EventBus only for global services or formal feature boundaries.
- If a UI wiring slice treats Component as ECS or moves gameplay rules/state mutation from `Game.Core` into Godot scripts without explicit task or ADR scope, treat it as a repair preference rather than a Chapter 7 hard gate by default.
- Apply `docs/workflows/ui-ux-implementation-policy.md` for UI/UX retrofit, screenshot acceptance, accessibility checks, localization checks, and post-Chapter-7 polish boundaries.

## 11. Unwired UI Feature List

List completed features that are not wired to UI yet, or explicitly mark them as no-UI-needed.

| Task IDs | Capability | Missing UI Surface | Reason | Next Action |
| --- | --- | --- | --- | --- |
| T0 | Example completed feature | Main surface | Template placeholder | Replace in business repo |

## 12. Next UI Wiring Task Candidates

Generate follow-up tasks from this section only after the matrix and unwired list are current.

| Candidate | Source Matrix Row | Scope | Suggested Test Refs |
| --- | --- | --- | --- |
| Wire first playable surface | Example completed feature | Add visible scene and command binding | TODO |
