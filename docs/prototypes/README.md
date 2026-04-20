# Prototype Workspace

Purpose: hold lightweight, pre-task exploration records before work is promoted into the formal task pipeline.

Use this directory when the question is still whether a mechanic, UI flow, architecture option, or prompt workflow is worth turning into a formal task.

## Files
- `TEMPLATE.md`
  - Copy this when starting a new prototype.
- `<date>-<slug>.md`
  - One prototype record per exploration topic.

## Recommended Start
- Create the prototype record from `TEMPLATE.md`.
- If you need a playable Godot scene scaffold, run:
  - `py -3 scripts/python/dev_cli.py create-prototype-scene --slug <slug>`

## Required Minimum Fields
Every prototype record should contain:
- hypothesis
- core player fantasy
- minimum playable loop
- scope
- success criteria
- evidence
- decision

## Decision Values
- `discard`
  - The idea is not fun enough, clear enough, or viable enough; stop here.
- `archive`
  - Keep notes/evidence because the idea has signal, but it is not ready for formal work.
- `promote`
  - Convert the result into formal task work once the core player fantasy and minimum playable loop are clear enough.

## Promotion Checklist
When a prototype is promoted, follow up outside this directory:
1. Create or update real `.taskmaster/tasks/*.json` entries.
2. Add overlay refs, test refs, and acceptance refs.
3. Add formal contracts if domain boundaries changed.
4. Run the correct `DELIVERY_PROFILE` path instead of treating the prototype as done.

## Non-Goals
- This directory is not a substitute for `execution-plans/`.
- This directory is not a substitute for `decision-logs/`.
- This directory is not where completed formal work should live.
