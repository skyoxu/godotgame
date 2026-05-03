# RPG Prototype Type Kit

## 用途

本文件用于 RPG 类型的 prototype lane。它不是完整 GDD，也不处理数值平衡、长期成长、装备经济、任务系统或边界情况。它只定义 1-2 个场景内可以完成的最小核心游玩闭环，让玩家能从地图移动进入战斗，并在胜利或失败后得到明确反馈。

## 适用范围

- 游戏类型：rpg
- Prototype 目标：验证探索到战斗再到结算的核心体验是否成立
- 推荐场景数量：2 个
  - Map Scene：地图探索场景
  - Battle Scene：战斗场景
- 推荐实现粒度：可玩优先，表现和数值从简

## Gameplay Flow / GDD Route

### 默认最小游玩动线

1. 玩家进入地图场景。
2. 玩家使用 WASD 在地图上上下左右自由移动。
3. 地图中存在一种触发战斗的方式：随机遇怪，或地图刷怪后与怪物碰撞。
4. 触发战斗后，游戏切换到 RPG 战斗场景。
5. 战斗场景采用简单回合制：玩家选择一个指令，怪物随后行动。
6. 玩家默认至少拥有 `Attack` 指令；可选加入 `Skill`、`Item`、`Defend`。
7. 玩家行动会降低怪物 HP；怪物行动会降低玩家 HP。
8. 怪物 HP 降至 0 时，触发胜利结算。
9. 胜利结算后，玩家回到地图场景，可以继续移动或触发下一次战斗。
10. 玩家 HP 降至 0 时，触发失败结算或 Game Over。
11. 失败后允许玩家选择 Retry 或返回地图，具体由本 prototype 的目标决定。

### 最小闭环判定

这个 RPG prototype 至少应能完成以下闭环：

`进入地图 -> 移动 -> 遇敌 -> 进入战斗 -> 选择攻击 -> 怪物受伤 -> 怪物反击 -> 胜利或失败 -> 显示结算`

如果时间只允许实现一个结局，优先实现胜利闭环：

`地图移动 -> 触发战斗 -> 击败怪物 -> 胜利结算 -> 回到地图`

### 推荐默认假设

- 遇敌方式：地图刷怪并碰撞触发，优先于随机遇怪，因为更直观、便于测试。
- 战斗方式：回合制指令战斗，优先于即时战斗，因为更符合 RPG 原型的最小表达。
- 地图规模：一个小房间或一条短路径即可。
- 怪物数量：1 个怪物即可。
- 玩家属性：只需要 HP 和 Attack。
- 怪物属性：只需要 HP 和 Attack。
- 结算内容：只需要 Victory / Defeat 文本和 Continue / Retry 按钮。

## Prototype Scene UI

### Map Scene UI

地图场景 UI 只显示能支撑探索到遇敌闭环的信息：

- Player HP：显示当前玩家 HP。
- Input Hint：显示 `WASD Move`。
- Quest Hint：可选显示一个极简任务提示，例如 `Find an enemy`。
- Mini Map：可选显示小地图；第一版默认不做，除非用户明确需要。
- Encounter Hint：遇怪提示。当靠近怪物或触发区域时，显示 `Encounter!` 或 `Press Enter`。
- Optional Debug Text：显示当前场景、遇敌状态或坐标，仅用于 prototype 调试。

不建议在 RPG prototype 第一版加入：

- 完整小地图
- 任务追踪器
- 背包入口
- 角色面板
- 复杂技能栏
- 商店、装备、经验条

### Battle Scene UI

战斗场景 UI 只显示能完成一场战斗的信息：

- Player HP：玩家当前 HP。
- Enemy HP：怪物当前 HP。
- Command Panel：至少包含 `Attack`。
- Battle Log：显示最近一条战斗反馈，例如 `Player attacks for 3 damage.`。
- Turn Indicator：显示当前是 Player Turn 还是 Enemy Turn。
- Result Panel：胜利或失败时显示 `Victory` / `Defeat`。
- Continue / Retry Button：结算后继续或重试。

可选但非必须：

- Skill 按钮
- Defend 按钮
- Item 按钮
- 简单动画状态文本
- 敌人名称

### UI 最小可用标准

- 玩家能看懂自己是否在地图或战斗中。
- 玩家能看懂自己当前 HP 和怪物 HP。
- 玩家能知道现在能按什么键或点什么按钮。
- 玩家每次行动后能看到反馈。
- 玩家能明确知道胜利或失败。

## 两轮确认问题

### Round 1：Gameplay Flow / GDD Route

请用户确认或修改以下问题。用户输入任何非空内容都可以保存并继续。

1. 使用随机遇怪、地图撞怪，还是二者都支持？
2. 战斗是回合制指令，还是即时碰撞/自动战斗？
3. 胜利后回到地图，还是进入结算后结束 prototype？
4. 玩家失败后是直接 Game Over、Retry 当前战斗，还是回到地图？

### Round 2：Prototype Scene UI

请用户确认或修改以下问题。用户输入任何非空内容都可以保存并继续。

1. 战斗场景需要哪些 UI：HP、指令按钮、战斗日志、技能栏？
2. 地图场景需要哪些 UI：HP、任务提示、小地图、遇怪提示？
3. 失败后是直接 Game Over，还是允许 Retry？
4. 结算 UI 需要哪些按钮：Continue、Retry、Back to Map、End Prototype？
5. 是否需要保留任何调试 UI 帮助快速验证 prototype？

## 建议保存字段

路由器可以将确认后的信息保存为：

```json
{
  "prototype_type_kit": {
    "game_type": "rpg",
    "kit_path": "docs/prototype-type-kits/rpg.md",
    "gameplay_flow": {
      "default_route": [
        "Enter map scene",
        "Move with WASD",
        "Trigger encounter",
        "Enter turn-based battle",
        "Resolve victory or defeat",
        "Return to map or show game over"
      ],
      "user_notes": []
    },
    "prototype_scene_ui": {
      "default_ui": [
        "Map: Player HP, input hint, encounter hint",
        "Battle: Player HP, Enemy HP, command panel, battle log, turn indicator",
        "Result: Victory/Defeat panel with continue or retry"
      ],
      "user_notes": []
    }
  }
}
```

## 不进入本 Prototype Kit 的内容

以下内容应留给后续 GDD、正式任务或 Chapter6 流程，不应成为本 prototype 的前置条件：

- 等级成长曲线
- 经验值和升级公式
- 装备、背包、商店
- 多角色队伍
- 多怪物编队
- 技能树
- 任务系统
- 长期存档
- 完整剧情演出
- 完整美术 UI 规范
- 边界条件和异常输入处理
