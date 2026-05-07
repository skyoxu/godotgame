# Prototype: <slug>

- Status: active | promoted | archived | discarded
- Owner: <name or agent>
- Date: <YYYY-MM-DD>
- Related formal task ids: none yet | <id list>

## Hypothesis
- <你想验证什么>

## Core Player Fantasy
- <玩家在第一分钟内应该感受到什么，或看懂什么>

## Minimum Playable Loop
- <玩家必须能够完整走通的最小闭环>

## Game Feature
- <这个 prototype 最有辨识度的玩法特色>

## Core Gameplay Loop
- <重复发生的核心游戏循环>

## Win / Fail Conditions
- <玩家如何获胜，如何失败>

## Game Type Specifics
- Game Type: <docs/game-type-guides 中的 canonical id，例如 rpg>
- Guide Path: docs/game-type-guides/<game-type>.md
- <Step07-lite 原型 1>: <玩家对该小节的回答>
- <Step07-lite 原型 2>: <玩家对该小节的回答>
- <Step07-lite 原型 3>: <玩家对该小节的回答>

## Implementation Skill
- Name: <仓内 prototype skill 名称，例如 prototype-rpg-godot-zh>
- Path: .agents/skills/<skill-name>/SKILL.md
- Contract Path: .agents/skills/<skill-name>/references/<contract-file>.md

## Prototype Type Kit
- Game Type: <docs/prototype-type-kits 中的 canonical id，例如 rpg>
- Kit Path: docs/prototype-type-kits/<game-type>.md
- Manifest Path: docs/prototype-type-kits/default-rpg-template.manifest.json

### Gameplay Flow / GDD Route
- 使用随机遇怪、地图撞怪，还是二者都支持？ <player answer>
- 战斗是回合制指令，还是即时碰撞/自动战斗？ <player answer>
- 胜利后回到地图，还是进入结算后结束 prototype？ <player answer>

### Prototype Scene UI
- 战斗场景需要哪些 UI：HP、指令按钮、战斗日志、技能栏？ <player answer>
- 地图场景需要哪些 UI：HP、任务提示、小地图、遇怪提示？ <player answer>
- 失败后是直接 Game Over，还是允许 Retry？ <player answer>

## Prototype Spec Sidecar
- Spec Path: docs/prototypes/<slug>.prototype.json
- Consumer: project-health and prototype TDD
- Rule: Markdown is for humans; the sidecar JSON is the stable script contract.
- Required JSON fields:
  - prototype_core.game_feature
  - prototype_core.core_gameplay_loop
  - prototype_core.win_fail_conditions
  - prototype_type_kit.gameplay_flow
  - prototype_type_kit.prototype_scene_ui
  - tdd.red / tdd.green / tdd.refactor

## Scope
- In:
  - <包含内容>
- Out:
  - <排除内容>

## Success Criteria
- <可观察的成功判断 1>
- <可观察的成功判断 2>

## Promote Signals
- <什么证据说明它值得进入正式任务>

## Archive Signals
- <什么证据说明它有信号，但暂时不适合正式交付>

## Discard Signals
- <什么证据说明它应该停在 prototype 阶段>

## Evidence
- Code paths:
  - <path>
- Logs / media / notes:
  - <path or note>

## Decision
- discard | archive | promote

## Next Step
- <如果 promote，下一步进入什么正式任务 / overlay / test>
