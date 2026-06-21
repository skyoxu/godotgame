# Chapter 3-7 Component Routing Preferences

Purpose: define the soft architecture preference used by formal Chapter 3-7 task generation, overlay/contract alignment, semantics stabilization, Chapter 6 implementation/repair, and Chapter 7 UI wiring.

This document does not apply to prototype lane routing. It is not a hard gate unless a task, ADR, or reviewer explicitly promotes one item into an acceptance criterion.

## Scope

Applies to:

- Chapter 3 task intent and task triplet wording.
- Chapter 4 overlay and contract placement language.
- Chapter 5 semantic stabilization when wording drifts toward the wrong layer.
- Chapter 6 implementation and Needs Fix repair preferences.
- Chapter 7 UI wiring GDD, candidate sidecars, and generated UI wiring tasks.

Does not apply to:

- Prototype lane scaffolds or exploratory prototype records.
- One-off asset generation, GDD drafting, or chat output unless that output is being converted into formal Chapter 3-7 work.
- ECS migration decisions. ECS or a data-oriented simulation layer requires explicit task or ADR scope.

## Terms

`Component` in Chapter 3-7 means a Godot Node/Scene Component:

- a standalone `.tscn` plus a small script; or
- a child `Node` plus one responsibility script; or
- a reusable UI/control scene with a narrow public API.

It does not mean an ECS component. Do not introduce ECS naming, ECS storage, or ECS system scheduling unless the task or an accepted ADR explicitly asks for a data-oriented simulation change.

## Layer Ownership

Godot-side scripts should own:

- lifecycle and scene-tree wiring;
- presentation and UI updates;
- input collection and command dispatch;
- animation/audio/visual feedback;
- adapter glue to Autoloads, resources, and Godot APIs.

`Game.Core` should own:

- gameplay rules;
- state mutation;
- deterministic simulation;
- validation and command results;
- domain services, systems, ports, contracts, repositories, and state machines.

If a formal task needs large-scale entity simulation later, prefer a lightweight data-oriented model inside `Game.Core` first. Do not recast the Godot scene tree as an ECS runtime by default.

## Generation Preferences

Use these as Codex and workflow generation preferences for Chapter 3-7:

- One script should primarily own one view, adapter, gameplay system, or task slice.
- UI updates belong in `*View.cs`, `*Panel.cs`, or thin Godot UI scripts.
- Gameplay calculation belongs in `Game.Core` `*System.cs`, `*Service.cs`, or another pure C# class.
- Scene roots and screen roots coordinate flow and dependencies; they should not accumulate concrete combat, reward, map, economy, or config rules.
- Godot Node/Scene Components should communicate through explicit public methods, exported references, Godot signals, or C# events.
- Components should avoid reaching across the tree with global `GetNode("/root/...")` calls unless they are intentionally accessing a documented Autoload boundary.
- Fast delivery may temporarily violate these preferences, but Chapter 6 repair should prefer splitting the code back toward these boundaries.

## NodePath And Scene Wiring

For new or repaired formal Chapter 6/7 scene wiring, prefer exported paths or node references over deep hard-coded paths.

Preferred shape:

```csharp
[Export] public NodePath HudPath { get; set; } = default!;
private HudView _hud = default!;
```

Use hard-coded child paths only when they are shallow, local to the scene, and unlikely to be touched by UI wiring tasks. If a repair is caused by scene-tree rename, missing node, or path drift, first consider replacing the brittle path with an exported path/reference before adding another string path.

## Event Routing

Default routing for formal Chapter 3-7 work:

- Same UI slice or same scene: direct method calls are acceptable.
- Child UI component to parent/root: use Godot signals or C# events.
- Cross-scene, Autoload-level, audit/observability, or formal domain events: use EventBus only when the event follows ADR-0022 and `Game.Core/Contracts/**` SSoT.
- Do not use EventBus to hide simple local control flow inside one screen or one task slice.

## Chapter-Specific Use

<!-- chapter7-generated-summary:start -->
- This is a soft generation and repair preference for formal Chapter 3-7 work; it is not a hard gate.
- `Component` means a Godot Node/Scene Component: a standalone `.tscn` plus a small script, or a child Node plus one responsibility script.
- Godot Node/Scene Components are not ECS components. Do not introduce an ECS model unless a task or ADR explicitly scopes a data-oriented simulation change.
- Godot scripts own lifecycle, presentation, input, scene wiring, and adapter glue; domain rules, state mutation, and simulation logic should stay in `Game.Core`.
- Prefer one script per view, adapter, gameplay system, or task slice. UI updates belong in `*View.cs`, `*Panel.cs`, or thin Godot UI scripts.
- Gameplay calculation belongs in `Game.Core` `*System.cs`, `*Service.cs`, or other pure C# classes.
- Scene roots and screen roots should coordinate dependencies and flow; they should not accumulate concrete combat, reward, map, or economy rules.
- New or repaired scene wiring should prefer exported `NodePath` or exported node references, for example `[Export] public NodePath HudPath { get; set; }`, over deep hard-coded paths.
- Prefer direct method calls inside one UI slice or scene, and Godot signals or C# events from child UI components to parent roots.
- Use EventBus for cross-scene, Autoload-level, audit/observability, or formal domain events that follow ADR-0022 and `Game.Core/Contracts/**` SSoT.
- Asset and GDD outputs should reference target slots such as `MapView`, `BattleView`, `HudView`, and `RewardView`; they do not need to depend on a component framework.
- If a fast delivery change violates this preference, Chapter 6 repair should prefer splitting it back toward the documented boundaries.
- See `docs/workflows/chapter3-7-component-routing.md` for the full formal workflow routing rule.
<!-- chapter7-generated-summary:end -->

Chapter 3:

- Task candidates should describe view/surface work separately from Core rules when both are present.
- Do not generate generic "Component architecture" tasks that only create reusable components without player-facing or system-facing value.

Chapter 4:

- Overlay and contract text should cite Core contracts and Godot surfaces separately.
- Feature slices should not copy concrete rules into UI components when the rule belongs in `Game.Core`.

Chapter 5:

- Semantic stabilization should fix wording that implies ECS or Godot-owned domain state unless the task explicitly asks for that architecture.
- Acceptance refs should distinguish Core behavior evidence from Godot scene wiring evidence.

Chapter 6:

- During implementation and repair, move rules/state/simulation into `Game.Core` when they appear in Godot scripts without a clear adapter reason.
- Repair brittle deep `GetNode` paths with exported `NodePath` or references when the change is already touching that scene wiring.
- Keep EventBus out of simple local UI control flow unless a formal contract boundary is involved.

Chapter 7:

- UI wiring should describe target slots such as `MapView`, `BattleView`, `HudView`, `RewardView`, `SettingsPanel`, or equivalent business-repo names.
- Asset, GDD, and task outputs can reference those slots without depending on a component framework.
- Generated candidates should keep the screen/surface contract separate from Core state transitions and validation rules.

## Non-Goals

- No full-repo ECS migration.
- No hard CI gate for file names like `*View.cs` or `*System.cs`.
- No mandatory rewrite of existing working code solely to satisfy naming preferences.
- No prototype-lane policy changes.
