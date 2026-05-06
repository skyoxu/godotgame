# Prototype: default-rpg-template

- Status: active
- Owner: prototype-lane
- Date: 2026-05-04
- Related formal task ids: none yet

## Hypothesis
- éªè¯é»è®¤ RPG æ¨¡æ¿æ¯å¦è½å¨ 1 å° 2 ä¸ªåºæ¯åæä¾æ¸æ°ãå¯æ©å±ãå¯å¤ç¨çæå°æ ¸å¿æ¸¸ç©é­ç¯ã

## Core Player Fantasy
- ç©å®¶å¨ç¬¬ä¸åéåè½çæå°å¾æ¢ç´¢ãé­éææãæåç»ç®ä¸æ®µå¼å¾ªç¯ï¼å¹¶æåå°ç»å¸ RPG ååçæ¨è¿èå¥ã

## Minimum Playable Loop
- å°å¾ç§»å¨ï¼è§¦åé­éï¼è¿å¥ææï¼å®æèå©æå¤±è´¥ç»ç®ï¼åè¿åå°å¾æç»æ prototypeã

## Game Feature
- ä½¿ç¨å¯å¤ç¨çé»è®¤ RPG æ¨¡æ¿èµäº§ãå°å¾åºæ¯ãææåºæ¯åå¥å±åè·¯ï¼ä½ä¸ºåç»­ RPG ååçåºç¡èµ·ç¹ã

## Core Gameplay Loop
- å°å¾æ¢ç´¢ -> è§¦åé­é -> ææç»ç® -> å¥å±æå¤±è´¥åé¦ -> è¿åå°å¾ç»§ç»­æ¨è¿ã

## Win / Fail Conditions
- å»è´¥å½åé­éæäººè§ä¸ºååºææèå©ï¼ç©å®¶çå½å½é¶è§ä¸ºå¤±è´¥ï¼å»è´¥æç»é¦é¢å prototype éå³ã

## Game Type Specifics
- Game Type: rpg
- Guide Path: docs/game-type-guides/rpg.md
- Character System: è§è²è³å°åå« HPãæ»å»ãé²å¾¡ãæ´å»çåé¡¹æå°ææå±æ§ã
- World and Exploration: ä½¿ç¨åå¼ å°å°å¾æ¿è½½æ¢ç´¢ä¸é­éå¥å£ï¼ä¸æ©å±é¿æä»»å¡ãç»æµæåéç³»ç»ã
- Combat System: ä½¿ç¨æå°å¯ç©ç RPG ææé­ç¯ï¼åè®¸åç»­é¡¹ç®æ¿æ¢ä¸ºæä»¤å¼ãèªå¨å¼æåèªå¨å¼ææã

## Implementation Skill
- Name: prototype-rpg-godot-zh
- Path: .agents/skills/prototype-rpg-godot-zh/SKILL.md
- Contract Path: .agents/skills/prototype-rpg-godot-zh/references/rpg-prototype-contract.md

## Prototype Type Kit
- Game Type: rpg
- Kit Path: docs/prototype-type-kits/rpg.md
- Manifest Path: docs/prototype-type-kits/default-rpg-template.manifest.json

### Gameplay Flow / GDD Route
- ä½¿ç¨éæºéæªãå°å¾ææªï¼è¿æ¯äºèé½æ¯æï¼ é»è®¤æ¯æå°å¾è§¦åé­éï¼éè¦æ¶å¯æ¿æ¢ä¸ºéæºéæªææ··åæ¨¡å¼ã
- æææ¯ååå¶æä»¤ï¼è¿æ¯å³æ¶ç¢°æ/èªå¨ææï¼ é»è®¤ä½¿ç¨æå°å¯ç©çååæ¨è¿å¼ææï¼ä¹å¯ä»¥è¢«é¡¹ç®æ¿æ¢ä¸ºèªå¨ææè¡¨ç°ã
- èå©ååå°å°å¾ï¼è¿æ¯è¿å¥ç»ç®åç»æ prototypeï¼ é»è®¤å°æªåç²¾è±èå©ååå°å°å¾ï¼å»è´¥æç»é¦é¢åç»æ prototypeã

### Prototype Scene UI
- ææåºæ¯éè¦åªäº UIï¼HPãæä»¤æé®ãæææ¥å¿ãæè½æ ï¼ é»è®¤åå«ç©å®¶ä¸æäººçå±æ§å±ç¤ºãHP æ¡ãæææ¥å¿åç»æåé¦ã
- å°å¾åºæ¯éè¦åªäº UIï¼HPãä»»å¡æç¤ºãå°å°å¾ãéæªæç¤ºï¼ é»è®¤åå«å°å¾ä¸»ä½ãç¶æä¿¡æ¯ãæ¨è¿æç¤ºåé­éåé¦ã
- å¤±è´¥åæ¯ç´æ¥ Game Overï¼è¿æ¯åè®¸ Retryï¼ é»è®¤ç´æ¥è¿å¥å¤±è´¥ç»ç®ï¼å·ä½é¡¹ç®å¯æ¹æ Retryã

## Scope
- In:
  - åå¼ å°å¾åºæ¯
  - ååºææåºæ¯
  - æå°èè´å¤æ­
  - åºç¡å¥å±æç»ç®åé¦
- Out:
  - é¿çº¿å§æä¸ä»»å¡ç³»ç»
  - å¤è§è²éä¼ç³»ç»
  - å¤æè£å¤ç»æµ
  - æ­£å¼ä»»å¡ refsãacceptance refsãoverlay refs

## Success Criteria
- ç©å®¶è½å¨æ¨¡æ¿ä¸­å®æä¸æ¬¡å®æ´çå°å¾å°ææå°ç»ç®é­ç¯ã
- åç»­é¡¹ç®è½å¤å¤å¶æ­¤æ¨¡æ¿å¹¶æ¿æ¢èµæºãé­éè§åå UIï¼èä¸å¿éååºç¡ååç»æã

## Promote Signals
- æ¨¡æ¿ç»æè¶³å¤æ¸æ°ï¼è½å¤æ¯æå¤ä¸ª RPG ååå¿«éèµ·æ­¥ã
- å°å¾ãææãç»ç®ä¸å±èè´£åç¦»æç¡®ï¼ä¾¿äºæ¿æ¢ç©æ³ã

## Archive Signals
- æ¨¡æ¿ç»æå¯ç¨ï¼ä½é»è®¤è¡¨ç°å±æé»è®¤æ°å¼ä»éåç»­é¡¹ç®èªè¡å¼ºåã

## Discard Signals
- é»è®¤æ¨¡æ¿æ æ³æ¯ææå° RPG é­ç¯ï¼æè¦åå°å·ä½æ ·ä¾åå®¹å¯¼è´é¾ä»¥å¤ç¨ã

## Evidence
- Code paths:
  - Game.Core/Prototypes/DefaultRpgPrototypeLoop.cs
  - Game.Godot/Prototypes/DefaultRpgTemplate/DefaultRpgPrototype.tscn
  - Game.Godot/Prototypes/DefaultRpgTemplate/Scripts/DefaultRpgPrototype.cs
  - Tests.Godot/tests/Prototype/DefaultRpgPrototype/test_default_rpg_prototype_scene.gd
- Logs / media / notes:
  - Game.Godot/Prototypes/DefaultRpgTemplate/Assets/
  - logs/ci/2026-05-04/prototype-tdd-default-rpg-template-red/

## Decision
- archive

## Next Step
- å¤å¶é»è®¤ RPG æ¨¡æ¿å°æ°ç prototype slugï¼åæ¿æ¢ç©æ³è®¾å®ãç´ æååºæ¯é»è¾ã
