# Phase 9: Signal System / 信号系统规范（CloudEvents → Godot Signals）

> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成

---

## 鐩爣

灏?vitegame 鐨?CloudEvents 浜嬩欢绯荤粺杩佺Щ鍒?godotgame 鐨?Godot Signals锛屽缓绔嬬被鍨嬪畨鍏ㄧ殑淇″彿鏋舵瀯涓庤法鍦烘櫙閫氫俊妯″紡銆?

---

## 鎶€鏈爤瀵规瘮

| 鍔熻兘 | vitegame (CloudEvents) | godotgame (Godot Signals) |
|-----|----------------------|--------------------------|
| 浜嬩欢瀹氫箟 | TypeScript 鎺ュ彛 + CloudEvent<T> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
| 浜嬩欢鍙戝皠 | eventBus.publish() | EmitSignal() |
| 浜嬩欢璁㈤槄 | eventBus.subscribe() | Connect() |
| 鍙傛暟浼犻€?| CloudEvent data 瀛楁 | Signal 鏂规硶鍙傛暟 |
| 绫诲瀷瀹夊叏 | TypeScript 娉涘瀷 | C# Delegate 绛惧悕 |
| 瑙ｈ€︽ā寮?| EventBus 涓粙 | Direct Signals + EventBus |
| 璺ㄥ満鏅€氫俊 | 鍏ㄥ眬 EventBus | Autoload EventBus + Signals |

---

## CloudEvents 瑙勮寖鍥為【 (vitegame)

### CloudEvents 缁撴瀯

```typescript
// src/shared/contracts/events.ts

import type { CloudEvent } from 'cloudevents';

// 鍩虹浜嬩欢缁撴瀯
interface CeBase {
  specversion: '1.0';
  id: string;
  source: string;
  type: string;
  time: string;
  datacontenttype?: string;
}

// 娉涘瀷 CloudEvent
type AppEvent<T> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成

// 鍏蜂綋浜嬩欢绀轰緥
interface PlayerDamagedData {
  playerId: string;
  damage: number;
  remainingHealth: number;
  damageSource: string;
}

type PlayerDamagedEvent = AppEvent<PlayerDamagedData>;

// 宸ュ巶鍑芥暟
export function createPlayerDamagedEvent(
  data: PlayerDamagedData
): PlayerDamagedEvent {
  return {
    specversion: '1.0',
    id: crypto.randomUUID(),
    source: 'https://app.game.local/player-service',
    type: 'app.player.damaged',
    time: new Date().toISOString(),
    data,
  };
}
```

### EventBus 浣跨敤 (vitegame)

```typescript
// src/services/EventBus.ts

class EventBus {
  private handlers = new Map<string, Set<(event: CloudEvent<any>) => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成

  subscribe<T>(eventType: string, handler: (event: CloudEvent<T>) => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType)!.add(handler);

    // 杩斿洖鍙栨秷璁㈤槄鍑芥暟
    return () => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
  }

  publish<T>(event: CloudEvent<T>): void {
    const handlers = this.handlers.get(event.type);
    if (handlers) {
      handlers.forEach(handler => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
    }
  }

  unsubscribe<T>(eventType: string, handler: (event: CloudEvent<T>) => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
    this.handlers.get(eventType)?.delete(handler);
  }
}

export const eventBus = new EventBus();
```

### 浣跨敤绀轰緥 (vitegame)

```typescript
// src/entities/Player.ts

import { eventBus } from '@/services/EventBus';
import { createPlayerDamagedEvent } from '@/shared/contracts/events';

export class Player {
  private health: number;

  constructor(maxHealth: number) {
    this.health = maxHealth;

    // 璁㈤槄浼ゅ浜嬩欢
    eventBus.subscribe('app.player.damaged', (event) => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
      console.log(`Player damaged: ${event.data.damage} damage`);
    });
  }

  takeDamage(amount: number, source: string): void {
    this.health -= amount;

    // 鍙戝竷浜嬩欢
    const event = createPlayerDamagedEvent({
      playerId: this.id,
      damage: amount,
      remainingHealth: this.health,
      damageSource: source,
    });

    eventBus.publish(event);
  }
}
```

---

## Godot Signals 鏍稿績姒傚康

### Signal 瀹氫箟鏂瑰紡

```csharp
// Game.Godot/Scripts/PlayerController.cs

using Godot;

namespace Game.Godot.Scripts;

public partial class PlayerController : CharacterBody2D
{
    // 鏂瑰紡 1: 鏃犲弬鏁颁俊鍙?
    [Signal]
    public delegate void DeathEventHandler();

    // 鏂瑰紡 2: 鍗曞弬鏁颁俊鍙?
    [Signal]
    public delegate void HealthChangedEventHandler(int newHealth);

    // 鏂瑰紡 3: 澶氬弬鏁颁俊鍙?
    [Signal]
    public delegate void DamagedEventHandler(int damage, string source, int remainingHealth);

    // 鏂瑰紡 4: 澶嶆潅鍙傛暟淇″彿锛堜娇鐢ㄧ被锛?
    [Signal]
    public delegate void StateChangedEventHandler(PlayerState oldState, PlayerState newState);

    private int _health = 100;
    private int _maxHealth = 100;

    public void TakeDamage(int amount, string source)
    {
        int oldHealth = _health;
        _health = Mathf.Max(0, _health - amount);

        // 鍙戝皠淇″彿锛堟柟寮?1锛氬懡鍚嶅弬鏁帮級
        EmitSignal(SignalName.Damaged, amount, source, _health);

        // 鍙戝皠淇″彿锛堟柟寮?2锛氬瓧绗︿覆鍚嶇О锛?
        // EmitSignal("damaged", amount, source, _health);

        // 鍙戝皠淇″彿锛堟柟寮?3锛歯ameof锛?
        // EmitSignal(nameof(Damaged), amount, source, _health);

        // 鍋ュ悍鍊煎彉鍖栦俊鍙?
        if (_health != oldHealth)
        {
            EmitSignal(SignalName.HealthChanged, _health);
        }

        // 姝讳骸淇″彿
        if (_health == 0)
        {
            EmitSignal(SignalName.Death);
        }
    }

    public void Heal(int amount)
    {
        int oldHealth = _health;
        _health = Mathf.Min(_maxHealth, _health + amount);

        if (_health != oldHealth)
        {
            EmitSignal(SignalName.HealthChanged, _health);
        }
    }
}
```

### Signal 杩炴帴鏂瑰紡

```csharp
// Game.Godot/Scripts/HealthBarUI.cs

using Godot;

namespace Game.Godot.Scripts;

public partial class HealthBarUI : Control
{
    private ProgressBar _progressBar = null!;
    private Label _healthLabel = null!;
    private PlayerController _player = null!;

    public override void _Ready()
    {
        _progressBar = GetNode<ProgressBar>("ProgressBar");
        _healthLabel = GetNode<Label>("HealthLabel");
        _player = GetNode<PlayerController>("/root/Main/Player");

        // 鏂瑰紡 1: 鐩存帴杩炴帴鍒版柟娉曪紙鎺ㄨ崘锛?
        _player.HealthChanged += OnPlayerHealthChanged;

        // 鏂瑰紡 2: 浣跨敤 Callable.From 鍖呰 Lambda
        _player.Damaged += Callable.From<int, string, int>((damage, source, remaining) =>
        {
            GD.Print($"Player took {damage} damage from {source}");
            AnimateDamage();
        });

        // 鏂瑰紡 3: 浣跨敤 Connect 鏂规硶锛堝瓧绗︿覆鍚嶇О锛?
        _player.Connect(PlayerController.SignalName.Death, Callable.From(OnPlayerDeath));

        // 鏂瑰紡 4: 浣跨敤 Connect 鏂规硶锛堝甫 flags锛?
        _player.Connect(
            PlayerController.SignalName.StateChanged,
            Callable.From<PlayerState, PlayerState>(OnPlayerStateChanged),
            (uint)ConnectFlags.OneShot // 涓€娆℃€ц繛鎺?
        );
    }

    private void OnPlayerHealthChanged(int newHealth)
    {
        _progressBar.Value = newHealth;
        _healthLabel.Text = $"{newHealth}/{_player.MaxHealth}";
    }

    private void OnPlayerDeath()
    {
        GD.Print("Player has died!");
        GetTree().ChangeSceneToFile("res://Scenes/GameOver.tscn");
    }

    private void OnPlayerStateChanged(PlayerState oldState, PlayerState newState)
    {
        GD.Print($"Player state changed: {oldState} -> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
    }

    private void AnimateDamage()
    {
        // 浼ゅ闂儊鍔ㄧ敾
        var tween = CreateTween();
        tween.TweenProperty(_progressBar, "modulate", Colors.Red, 0.1);
        tween.TweenProperty(_progressBar, "modulate", Colors.White, 0.1);
    }

    public override void _ExitTree()
    {
        // 鏂紑淇″彿杩炴帴锛堥槻姝㈠唴瀛樻硠婕忥級
        if (IsInstanceValid(_player))
        {
            _player.HealthChanged -= OnPlayerHealthChanged;
        }
    }
}
```

### Signal 涓庢柟娉曡皟鐢ㄧ殑閫夋嫨

| 鍦烘櫙 | 浣跨敤 Signal | 浣跨敤鏂规硶璋冪敤 |
|-----|-----------|------------|
| 鐖惰妭鐐硅皟鐢ㄥ瓙鑺傜偣 | 鍚?| 鏄紙鐩存帴璋冪敤锛?|
| 瀛愯妭鐐归€氱煡鐖惰妭鐐?| 鏄?| 鍚︼紙杩濆弽渚濊禆鏂瑰悜锛?|
| 鍚岀骇鑺傜偣閫氫俊 | 鏄?| [璀﹀憡]锛堥渶閫氳繃鍏卞悓鐖惰妭鐐癸級 |
| 璺ㄥ満鏅€氫俊 | 鏄紙閫氳繃 EventBus锛?| 鍚?|
| 涓€瀵瑰閫氱煡 | 鏄?| 鍚?|
| 瑙ｈ€︽ā鍧?| 鏄?| 鍚?|
| 鎬ц兘鍏抽敭璺緞 | [璀﹀憡]锛堟湁寮€閿€锛?| 鏄?|

---

## CloudEvents 鈫?Signals 杩佺Щ妯″紡

### 妯″紡 1: 绠€鍗曚簨浠惰縼绉?

**CloudEvents (vitegame)**:

```typescript
// 浜嬩欢瀹氫箟
interface CoinCollectedData {
  coinId: string;
  value: number;
}

type CoinCollectedEvent = AppEvent<CoinCollectedData>;

// 鍙戝竷浜嬩欢
eventBus.publish(createCoinCollectedEvent({ coinId: '123', value: 10 }));

// 璁㈤槄浜嬩欢
eventBus.subscribe('app.game.coin.collected', (event) => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
  score += event.data.value;
});
```

**Godot Signals (godotgame)**:

```csharp
// Game.Godot/Scripts/Coin.cs

public partial class Coin : Area2D
{
    [Signal]
    public delegate void CollectedEventHandler(string coinId, int value);

    [Export]
    public string CoinId { get; set; } = Guid.NewGuid().ToString();

    [Export]
    public int Value { get; set; } = 10;

    public override void _Ready()
    {
        BodyEntered += OnBodyEntered;
    }

    private void OnBodyEntered(Node2D body)
    {
        if (body is PlayerController)
        {
            // 鍙戝皠淇″彿
            EmitSignal(SignalName.Collected, CoinId, Value);
            QueueFree();
        }
    }
}

// Game.Godot/Scripts/ScoreManager.cs

public partial class ScoreManager : Node
{
    private int _score = 0;

    public override void _Ready()
    {
        // 璁㈤槄鎵€鏈夐噾甯佺殑鏀堕泦淇″彿
        var coins = GetTree().GetNodesInGroup("coins");
        foreach (Node coin in coins)
        {
            if (coin is Coin coinScript)
            {
                coinScript.Collected += OnCoinCollected;
            }
        }
    }

    private void OnCoinCollected(string coinId, int value)
    {
        _score += value;
        GD.Print($"Coin collected: {coinId}, Total score: {_score}");
    }
}
```

### 妯″紡 2: 澶嶆潅浜嬩欢鏁版嵁杩佺Щ

**CloudEvents (vitegame)**:

```typescript
// 澶嶆潅浜嬩欢鏁版嵁
interface EnemyDefeatedData {
  enemyId: string;
  enemyType: string;
  position: { x: number; y: number };
  rewards: {
    experience: number;
    gold: number;
    items: string[];
  };
  killedBy: string;
}

type EnemyDefeatedEvent = AppEvent<EnemyDefeatedData>;

// 鍙戝竷
eventBus.publish(createEnemyDefeatedEvent({
  enemyId: 'enemy-123',
  enemyType: 'goblin',
  position: { x: 100, y: 200 },
  rewards: { experience: 50, gold: 25, items: ['sword'] },
  killedBy: 'player-456',
}));
```

**Godot Signals (godotgame)**:

```csharp
// Game.Godot/Scripts/EnemyRewards.cs

public class EnemyRewards
{
    public int Experience { get; set; }
    public int Gold { get; set; }
    public List<string> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
}

// Game.Godot/Scripts/Enemy.cs

public partial class Enemy : CharacterBody2D
{
    [Signal]
    public delegate void DefeatedEventHandler(
        string enemyId,
        string enemyType,
        Vector2 position,
        EnemyRewards rewards,
        string killedBy
    );

    [Export]
    public string EnemyId { get; set; } = Guid.NewGuid().ToString();

    [Export]
    public string EnemyType { get; set; } = "goblin";

    [Export]
    public int Experience { get; set; } = 50;

    [Export]
    public int Gold { get; set; } = 25;

    private int _health = 100;

    public void TakeDamage(int amount, string attackerId)
    {
        _health -= amount;

        if (_health <= 0)
        {
            // 鏋勯€犲鍔辨暟鎹?
            var rewards = new EnemyRewards
            {
                Experience = Experience,
                Gold = Gold,
                Items = new List<string> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
            };

            // 鍙戝皠淇″彿
            EmitSignal(SignalName.Defeated, EnemyId, EnemyType, Position, rewards, attackerId);
            QueueFree();
        }
    }
}

// Game.Godot/Scripts/RewardManager.cs

public partial class RewardManager : Node
{
    public override void _Ready()
    {
        var enemies = GetTree().GetNodesInGroup("enemies");
        foreach (Node enemy in enemies)
        {
            if (enemy is Enemy enemyScript)
            {
                enemyScript.Defeated += OnEnemyDefeated;
            }
        }
    }

    private void OnEnemyDefeated(
        string enemyId,
        string enemyType,
        Vector2 position,
        EnemyRewards rewards,
        string killedBy
    )
    {
        GD.Print($"Enemy {enemyId} ({enemyType}) defeated at {position}");
        GD.Print($"Rewards: {rewards.Experience} XP, {rewards.Gold} gold");

        // 搴旂敤濂栧姳鍒扮帺瀹?
        var player = GetNode<PlayerController>($"/root/Main/Players/{killedBy}");
        if (player != null)
        {
            player.AddExperience(rewards.Experience);
            player.AddGold(rewards.Gold);
        }
    }
}
```

### 妯″紡 3: EventBus 璺ㄥ満鏅€氫俊

**CloudEvents EventBus (vitegame)**:

```typescript
// 鍏ㄥ眬浜嬩欢鎬荤嚎
export const globalEventBus = new EventBus();

// 鍦烘櫙 A 鍙戝竷
globalEventBus.publish(createGameStateChangedEvent({ state: 'paused' }));

// 鍦烘櫙 B 璁㈤槄
globalEventBus.subscribe('app.game.state.changed', (event) => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
  console.log('Game state:', event.data.state);
});
```

**Godot EventBus Autoload (godotgame)**:

```csharp
// Game.Godot/Autoloads/EventBus.cs

using Godot;
using System;
using System.Collections.Generic;

namespace Game.Godot.Autoloads;

/// <summary>
/// 鍏ㄥ眬浜嬩欢鎬荤嚎锛圓utoload 鍗曚緥锛?
/// 鐢ㄤ簬璺ㄥ満鏅€氫俊鍜屾澗鑰﹀悎
/// </summary>
public partial class EventBus : Node
{
    public static EventBus Instance { get; private set; } = null!;

    // 娓告垙鐘舵€佷簨浠?
    [Signal]
    public delegate void GameStateChangedEventHandler(string newState);

    // 鐜╁鍏ㄥ眬浜嬩欢
    [Signal]
    public delegate void PlayerLevelUpEventHandler(string playerId, int newLevel);

    // 鎴愬氨瑙ｉ攣浜嬩欢
    [Signal]
    public delegate void AchievementUnlockedEventHandler(string achievementId, string title);

    // 绯荤粺閫氱煡浜嬩欢
    [Signal]
    public delegate void SystemNotificationEventHandler(string message, string severity);

    public override void _EnterTree()
    {
        Instance = this;
    }

    // 杈呭姪鏂规硶锛氬彂甯冩父鎴忕姸鎬佸彉鍖?
    public void PublishGameStateChanged(string newState)
    {
        EmitSignal(SignalName.GameStateChanged, newState);
    }

    // 杈呭姪鏂规硶锛氬彂甯冪帺瀹跺崌绾?
    public void PublishPlayerLevelUp(string playerId, int newLevel)
    {
        EmitSignal(SignalName.PlayerLevelUp, playerId, newLevel);
    }

    // 杈呭姪鏂规硶:鍙戝竷鎴愬氨瑙ｉ攣
    public void PublishAchievementUnlocked(string achievementId, string title)
    {
        EmitSignal(SignalName.AchievementUnlocked, achievementId, title);
    }

    // 杈呭姪鏂规硶:鍙戝竷绯荤粺閫氱煡
    public void PublishSystemNotification(string message, string severity = "info")
    {
        EmitSignal(SignalName.SystemNotification, message, severity);
    }
}
```

**鍦?project.godot 涓敞鍐?*:

```ini
[autoload]

EventBus="*res://Autoloads/EventBus.cs"
ServiceLocator="*res://Autoloads/ServiceLocator.cs"
```

**浣跨敤 EventBus**:

```csharp
// Game.Godot/Scripts/GameStateManager.cs

public partial class GameStateManager : Node
{
    private string _currentState = "playing";

    public void PauseGame()
    {
        _currentState = "paused";
        GetTree().Paused = true;

        // 閫氳繃 EventBus 鍙戝竷鍏ㄥ眬浜嬩欢
        EventBus.Instance.PublishGameStateChanged("paused");
    }

    public void ResumeGame()
    {
        _currentState = "playing";
        GetTree().Paused = false;

        EventBus.Instance.PublishGameStateChanged("playing");
    }
}

// Game.Godot/Scripts/UI/PauseMenuUI.cs

public partial class PauseMenuUI : Control
{
    public override void _Ready()
    {
        // 璁㈤槄 EventBus 鍏ㄥ眬浜嬩欢
        EventBus.Instance.GameStateChanged += OnGameStateChanged;
    }

    private void OnGameStateChanged(string newState)
    {
        Visible = (newState == "paused");
        GD.Print($"Pause menu visibility: {Visible}");
    }

    public override void _ExitTree()
    {
        EventBus.Instance.GameStateChanged -= OnGameStateChanged;
    }
}

// Game.Godot/Scripts/UI/NotificationManager.cs

public partial class NotificationManager : Control
{
    private Label _notificationLabel = null!;

    public override void _Ready()
    {
        _notificationLabel = GetNode<Label>("NotificationLabel");

        // 璁㈤槄绯荤粺閫氱煡
        EventBus.Instance.SystemNotification += OnSystemNotification;
        EventBus.Instance.AchievementUnlocked += OnAchievementUnlocked;
    }

    private void OnSystemNotification(string message, string severity)
    {
        _notificationLabel.Text = message;
        _notificationLabel.Modulate = severity switch
        {
            "error" => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
            "warning" => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
            _ => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
        };

        ShowNotification();
    }

    private void OnAchievementUnlocked(string achievementId, string title)
    {
        _notificationLabel.Text = $"Achievement Unlocked: {title}";
        _notificationLabel.Modulate = Colors.Gold;
        ShowNotification();
    }

    private async void ShowNotification()
    {
        _notificationLabel.Visible = true;
        await ToSignal(GetTree().CreateTimer(3.0), Timer.SignalName.Timeout);
        _notificationLabel.Visible = false;
    }

    public override void _ExitTree()
    {
        EventBus.Instance.SystemNotification -= OnSystemNotification;
        EventBus.Instance.AchievementUnlocked -= OnAchievementUnlocked;
    }
}
```

---

## Signal 鎬ц兘浼樺寲

### 浼樺寲 1: 閬垮厤棰戠箒鐨?Connect/Disconnect

```csharp
// FAIL 閿欒锛氭瘡甯ч兘杩炴帴鍜屾柇寮€
public override void _Process(double delta)
{
    _player.HealthChanged += OnHealthChanged;
    // ... 澶勭悊閫昏緫
    _player.HealthChanged -= OnHealthChanged;
}

// 姝ｇ‘锛氬湪 _Ready 鍜?_ExitTree 涓鐞嗚繛鎺?
public override void _Ready()
{
    _player.HealthChanged += OnHealthChanged;
}

public override void _ExitTree()
{
    if (IsInstanceValid(_player))
    {
        _player.HealthChanged -= OnHealthChanged;
    }
}
```

### 浼樺寲 2: 浣跨敤 OneShot 杩炴帴锛堜竴娆℃€т簨浠讹級

```csharp
// 涓€娆℃€ц繛鎺ワ紙鑷姩鏂紑锛?
_enemy.Defeated += Callable.From(() =>
{
    GD.Print("Enemy defeated once!");
});
_enemy.Connect(
    Enemy.SignalName.Defeated,
    Callable.From(OnEnemyDefeated),
    (uint)ConnectFlags.OneShot
);
```

### 浼樺寲 3: 浣跨敤 Deferred 寤惰繜澶勭悊

```csharp
// 寤惰繜鍒扮┖闂插抚澶勭悊锛堥伩鍏嶅湪鐗╃悊甯т腑淇敼鍦烘櫙鏍戯級
_player.Connect(
    PlayerController.SignalName.Death,
    Callable.From(OnPlayerDeath),
    (uint)ConnectFlags.Deferred
);

private void OnPlayerDeath()
{
    // 姝ゆ柟娉曚細鍦ㄧ┖闂插抚璋冪敤锛屽畨鍏ㄥ湴淇敼鍦烘櫙鏍?
    GetTree().ChangeSceneToFile("res://Scenes/GameOver.tscn");
}
```

### 浼樺寲 4: 閬垮厤杩囧鍙傛暟浼犻€?

```csharp
// FAIL 閿欒锛氫紶閫掕繃澶氬弬鏁?
[Signal]
public delegate void ComplexEventEventHandler(
    string id, string name, int value, float time, Vector2 pos, Vector2 vel, Color color, bool flag
);

// 姝ｇ‘锛氫娇鐢ㄦ暟鎹被
public class EventData
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public int Value { get; set; }
    public float Time { get; set; }
    public Vector2 Position { get; set; }
    public Vector2 Velocity { get; set; }
    public Color Color { get; set; }
    public bool Flag { get; set; }
}

[Signal]
public delegate void ComplexEventEventHandler(EventData data);
```

---

## Signal 鍛藉悕绾﹀畾

### 鍛藉悕瑙勫垯

```csharp
// 1. 浜嬩欢鍚嶇О锛歅ascalCase + 鍔ㄨ瘝杩囧幓寮?
[Signal]
public delegate void HealthChangedEventHandler(int newHealth);

[Signal]
public delegate void DamagedEventHandler(int amount);

[Signal]
public delegate void StateEnteredEventHandler(string stateName);

// 2. Handler 鍚庣紑锛欵ventHandler
public delegate void CollectedEventHandler(string itemId);

// 3. 淇″彿鍙傛暟锛氭弿杩版€у懡鍚?
[Signal]
public delegate void ItemPickedUpEventHandler(string itemId, string itemName, int quantity);

// 4. 甯冨皵鐘舵€佸彉鍖栵細浣跨敤 Toggled/Changed
[Signal]
public delegate void VisibilityToggledEventHandler(bool isVisible);

[Signal]
public delegate void EnabledChangedEventHandler(bool isEnabled);

// 5. 鐢熷懡鍛ㄦ湡浜嬩欢锛氫娇鐢ㄥ姩浣滆瘝
[Signal]
public delegate void SpawnedEventHandler();

[Signal]
public delegate void DestroyedEventHandler();

[Signal]
public delegate void InitializedEventHandler();
```

### 浜嬩欢绫诲瀷鍒嗙被

```csharp
// Game.Godot/Scripts/EventCategories.cs

namespace Game.Godot.Scripts;

/// <summary>
/// 鐜╁鐩稿叧浜嬩欢
/// </summary>
public partial class PlayerEvents
{
    [Signal] public delegate void HealthChangedEventHandler(int newHealth);
    [Signal] public delegate void DamagedEventHandler(int damage, string source);
    [Signal] public delegate void HealedEventHandler(int amount);
    [Signal] public delegate void DeathEventHandler();
    [Signal] public delegate void RespawnedEventHandler(Vector2 position);
    [Signal] public delegate void LevelUpEventHandler(int newLevel);
    [Signal] public delegate void ExperienceGainedEventHandler(int amount);
}

/// <summary>
/// 娓告垙鐘舵€佷簨浠?
/// </summary>
public partial class GameStateEvents
{
    [Signal] public delegate void GameStartedEventHandler();
    [Signal] public delegate void GamePausedEventHandler();
    [Signal] public delegate void GameResumedEventHandler();
    [Signal] public delegate void GameOverEventHandler(int finalScore);
    [Signal] public delegate void LevelCompletedEventHandler(int levelId);
}

/// <summary>
/// 鐗╁搧/鑳屽寘浜嬩欢
/// </summary>
public partial class InventoryEvents
{
    [Signal] public delegate void ItemAddedEventHandler(string itemId, int quantity);
    [Signal] public delegate void ItemRemovedEventHandler(string itemId, int quantity);
    [Signal] public delegate void ItemUsedEventHandler(string itemId);
    [Signal] public delegate void InventoryFullEventHandler();
}

/// <summary>
/// UI 浜嬩欢
/// </summary>
public partial class UIEvents
{
    [Signal] public delegate void ButtonClickedEventHandler(string buttonName);
    [Signal] public delegate void MenuOpenedEventHandler(string menuName);
    [Signal] public delegate void MenuClosedEventHandler(string menuName);
    [Signal] public delegate void DialogueStartedEventHandler(string dialogueId);
    [Signal] public delegate void DialogueCompletedEventHandler(string dialogueId);
}
```

---

## Signal 娴嬭瘯绛栫暐

### GdUnit4 Signal 娴嬭瘯

```csharp
// C# equivalent (Godot 4 + C# + GdUnit4)
using Godot;
using System.Threading.Tasks;

public partial class ExampleTest
{
    public async Task Example()
    {
        var scene = GD.Load<PackedScene>("res://Game.Godot/Scenes/MainScene.tscn");
        var inst = scene?.Instantiate();
        var tree = (SceneTree)Engine.GetMainLoop();
        tree.Root.AddChild(inst);
        await ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        inst.QueueFree();
    }
}
```

### xUnit Signal 娴嬭瘯锛堜娇鐢?Fake锛?

```csharp
// Game.Core.Tests/Fakes/FakeSignalEmitter.cs

using System;
using System.Collections.Generic;

namespace Game.Core.Tests.Fakes;

public class FakeSignalEmitter
{
    private Dictionary<string, List<Delegate>> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成

    public void Connect(string signalName, Delegate handler)
    {
        if (!_handlers.ContainsKey(signalName))
        {
            _handlers[signalName] = new List<Delegate>();
        }
        _handlers[signalName].Add(handler);
    }

    public void Disconnect(string signalName, Delegate handler)
    {
        _handlers[signalName]?.Remove(handler);
    }

    public void Emit(string signalName, params object[] args)
    {
        if (_handlers.ContainsKey(signalName))
        {
            foreach (var handler in _handlers[signalName])
            {
                handler.DynamicInvoke(args);
            }
        }
    }
}

// Game.Core.Tests/Signals/PlayerSignalTests.cs

using FluentAssertions;
using Game.Core.Tests.Fakes;
using Xunit;

namespace Game.Core.Tests.Signals;

public class PlayerSignalTests
{
    [Fact]
    public void HealthChanged_ShouldEmitCorrectValue()
    {
        // Arrange
        var emitter = new FakeSignalEmitter();
        int receivedHealth = 0;

        emitter.Connect("health_changed", (int newHealth) =>
        {
            receivedHealth = newHealth;
        });

        // Act
        emitter.Emit("health_changed", 75);

        // Assert
        receivedHealth.Should().Be(75);
    }

    [Fact]
    public void Damaged_ShouldEmitAllParameters()
    {
        // Arrange
        var emitter = new FakeSignalEmitter();
        int receivedDamage = 0;
        string receivedSource = string.Empty;
        int receivedRemaining = 0;

        emitter.Connect("damaged", (int damage, string source, int remaining) =>
        {
            receivedDamage = damage;
            receivedSource = source;
            receivedRemaining = remaining;
        });

        // Act
        emitter.Emit("damaged", 30, "enemy", 70);

        // Assert
        receivedDamage.Should().Be(30);
        receivedSource.Should().Be("enemy");
        receivedRemaining.Should().Be(70);
    }

    [Fact]
    public void MultipleSubscribers_ShouldAllReceiveSignal()
    {
        // Arrange
        var emitter = new FakeSignalEmitter();
        int subscriber1Count = 0;
        int subscriber2Count = 0;

        emitter.Connect("test_signal", () => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
        emitter.Connect("test_signal", () => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成

        // Act
        emitter.Emit("test_signal");
        emitter.Emit("test_signal");

        // Assert
        subscriber1Count.Should().Be(2);
        subscriber2Count.Should().Be(2);
    }

    [Fact]
    public void Disconnect_ShouldStopReceivingSignals()
    {
        // Arrange
        var emitter = new FakeSignalEmitter();
        int callCount = 0;
        Action handler = () => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成

        emitter.Connect("test_signal", handler);

        // Act
        emitter.Emit("test_signal");
        emitter.Disconnect("test_signal", handler);
        emitter.Emit("test_signal");

        // Assert
        callCount.Should().Be(1);
    }
}
```

---

## Signal 鏂囨。鍖?

### XML 鏂囨。娉ㄩ噴

```csharp
// Game.Godot/Scripts/PlayerController.cs

namespace Game.Godot.Scripts;

public partial class PlayerController : CharacterBody2D
{
    /// <summary>
    /// 褰撶帺瀹剁敓鍛藉€煎彂鐢熷彉鍖栨椂鍙戝皠銆?
    /// </summary>
    /// <param name="newHealth">鏂扮殑鐢熷懡鍊硷紙0 鍒?MaxHealth锛?/param>
    /// <example>
    /// <code>
    /// player.HealthChanged += (newHealth) => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
    ///     GD.Print($"Player health: {newHealth}");
    /// };
    /// </code>
    /// </example>
    [Signal]
    public delegate void HealthChangedEventHandler(int newHealth);

    /// <summary>
    /// 褰撶帺瀹跺彈鍒颁激瀹虫椂鍙戝皠锛堝湪 HealthChanged 涔嬪墠锛夈€?
    /// </summary>
    /// <param name="damage">浼ゅ鏁板€?/param>
    /// <param name="source">浼ゅ鏉ユ簮锛堝 "enemy", "trap", "fall"锛?/param>
    /// <param name="remainingHealth">鍓╀綑鐢熷懡鍊?/param>
    /// <remarks>
    /// 姝や俊鍙烽€傜敤浜庢挱鏀句激瀹抽煶鏁堛€佹樉绀轰激瀹虫暟瀛椼€佽Е鍙戝彈鍑诲姩鐢荤瓑銆?
    /// </remarks>
    [Signal]
    public delegate void DamagedEventHandler(int damage, string source, int remainingHealth);

    /// <summary>
    /// 褰撶帺瀹舵浜℃椂鍙戝皠锛堢敓鍛藉€奸檷鑷?0锛夈€?
    /// </summary>
    /// <remarks>
    /// 姝や俊鍙峰彧浼氬湪鐢熷懡鍊奸娆￠檷鑷?0 鏃跺彂灏勪竴娆°€?
    /// 閫傜敤浜庤Е鍙戞浜″姩鐢汇€佹樉绀烘父鎴忕粨鏉熺晫闈€佽褰曟浜＄粺璁＄瓑銆?
    /// </remarks>
    [Signal]
    public delegate void DeathEventHandler();

    /// <summary>
    /// 褰撶帺瀹剁姸鎬佸彂鐢熷彉鍖栨椂鍙戝皠锛堝 Idle 鈫?Running 鈫?Jumping锛夈€?
    /// </summary>
    /// <param name="oldState">鏃х姸鎬?/param>
    /// <param name="newState">鏂扮姸鎬?/param>
    /// <example>
    /// <code>
    /// player.StateChanged += (oldState, newState) => 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
    ///     GD.Print($"Player state: {oldState} -> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
    ///     AnimationPlayer.Play(newState.ToString());
    /// };
    /// </code>
    /// </example>
    [Signal]
    public delegate void StateChangedEventHandler(PlayerState oldState, PlayerState newState);
}
```

---

## 杩佺Щ妫€鏌ユ竻鍗?

### 浜嬩欢瀹氫箟杩佺Щ

- [ ] CloudEvents 绫诲瀷瀹氫箟 鈫?[Signal] delegate 瀹氫箟
- [ ] CloudEvent<T> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
- [ ] 浜嬩欢宸ュ巶鍑芥暟 鈫?EmitSignal() 璋冪敤
- [ ] 浜嬩欢鍛藉悕瑙勮寖锛坅pp.entity.action 鈫?EntityActionEventHandler锛?

### 浜嬩欢鍙戝皠杩佺Щ

- [ ] eventBus.publish() 鈫?EmitSignal(SignalName.XXX, ...)
- [ ] 浜嬩欢鍙傛暟搴忓垪鍖?鈫?鐩存帴浼犻€掑弬鏁帮紙鎴栦娇鐢ㄦ暟鎹被锛?
- [ ] 浜嬩欢婧?(source) 鈫?闅愬紡锛堥€氳繃鍙戝皠鑺傜偣锛夋垨鏄惧紡浼犻€?

### 浜嬩欢璁㈤槄杩佺Щ

- [ ] eventBus.subscribe() 鈫?signal += handler
- [ ] 璁㈤槄鍙栨秷 (unsubscribe) 鈫?signal -= handler
- [ ] 璁㈤槄鐢熷懡鍛ㄦ湡绠＄悊锛坃Ready 璁㈤槄锛宊ExitTree 鍙栨秷锛?

### EventBus 杩佺Щ

- [ ] 鍏ㄥ眬 EventBus 鈫?Autoload EventBus.cs
- [ ] 璺ㄥ満鏅簨浠?鈫?EventBus.Instance.XXXChanged 淇″彿
- [ ] EventBus.publish/subscribe 鈫?EventBus.EmitSignal/Connect

### 娴嬭瘯杩佺Щ

- [ ] Jest 浜嬩欢娴嬭瘯 鈫?GdUnit4 GdUnitSignalSpy
- [ ] 娴嬭瘯浜嬩欢鍙戝皠 鈫?signal_spy.is_emitted()
- [ ] 娴嬭瘯浜嬩欢鍙傛暟 鈫?signal_spy.get_last_args()
- [ ] xUnit 閫昏緫娴嬭瘯 鈫?FakeSignalEmitter

### 鏂囨。杩佺Щ

- [ ] CloudEvents 濂戠害鏂囨。 鈫?Signal XML 鏂囨。娉ㄩ噴
- [ ] 浜嬩欢鍙傛暟璇存槑 鈫?<param> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成
- [ ] 浣跨敤绀轰緥 鈫?<example> 状态: 模板规范（最小集已落地）`n> 前置: Phase 1-8 完成

---

## 鎬ц兘鍩哄噯

### Signal 鎬ц兘娴嬭瘯

```csharp
// Game.Godot.Tests/Performance/SignalPerformanceTest.cs

using Godot;
using System.Diagnostics;

namespace Game.Godot.Tests.Performance;

public partial class SignalPerformanceTest : Node
{
    [Signal]
    public delegate void TestSignalEventHandler(int value);

    public override void _Ready()
    {
        // 娴嬭瘯 1: 鍗曡闃呰€呮€ц兘
        TestSingleSubscriber();

        // 娴嬭瘯 2: 澶氳闃呰€呮€ц兘
        TestMultipleSubscribers();

        // 娴嬭瘯 3: 鍙傛暟浼犻€掓€ц兘
        TestParameterPassing();
    }

    private void TestSingleSubscriber()
    {
        TestSignal += OnTestSignal;

        var sw = Stopwatch.StartNew();
        for (int i = 0; i < 100000; i++)
        {
            EmitSignal(SignalName.TestSignal, i);
        }
        sw.Stop();

        GD.Print($"Single subscriber: {sw.ElapsedMilliseconds}ms for 100k emissions");

        TestSignal -= OnTestSignal;
    }

    private void TestMultipleSubscribers()
    {
        for (int i = 0; i < 10; i++)
        {
            TestSignal += OnTestSignal;
        }

        var sw = Stopwatch.StartNew();
        for (int i = 0; i < 100000; i++)
        {
            EmitSignal(SignalName.TestSignal, i);
        }
        sw.Stop();

        GD.Print($"10 subscribers: {sw.ElapsedMilliseconds}ms for 100k emissions");

        // 娓呯悊
        for (int i = 0; i < 10; i++)
        {
            TestSignal -= OnTestSignal;
        }
    }

    private void TestParameterPassing()
    {
        TestSignal += OnTestSignal;

        var sw = Stopwatch.StartNew();
        for (int i = 0; i < 100000; i++)
        {
            EmitSignal(SignalName.TestSignal, i);
        }
        sw.Stop();

        GD.Print($"Parameter passing: {sw.ElapsedMilliseconds}ms for 100k emissions");

        TestSignal -= OnTestSignal;
    }

    private void OnTestSignal(int value)
    {
        // 绌哄鐞嗗櫒
    }
}
```

### 鎬ц兘闃堝€?

| 鍦烘櫙 | 鐩爣闃堝€?|
|-----|---------|
| 鍗曡闃呰€?100k 鍙戝皠 | < 50ms |
| 10 璁㈤槄鑰?100k 鍙戝皠 | < 200ms |
| 鍙傛暟浼犻€?100k 鍙戝皠 | < 60ms |
| EventBus 鍏ㄥ眬浜嬩欢 1k 鍙戝皠 | < 10ms |

---

## CI 闆嗘垚

### Signal 鍚堣妫€鏌?(GitHub Actions)

```yaml
# .github/workflows/signal-compliance.yml

name: Signal Compliance

on:
  push:
    paths:
      - 'Game.Godot/Scripts/**/*.cs'
      - 'Game.Godot/Autoloads/**/*.cs'
  pull_request:
    paths:
      - 'Game.Godot/Scripts/**/*.cs'
      - 'Game.Godot/Autoloads/**/*.cs'

jobs:
  signal-compliance:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup .NET 8
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '8.0.x'

      - name: Check Signal Naming Convention
        shell: pwsh
        run: |
          # 妫€鏌?[Signal] 鍛藉悕鏄惁绗﹀悎 EventHandler 鍚庣紑
          $violations = Select-String -Path "Game.Godot/**/*.cs" -Pattern "\[Signal\].*delegate.*(?<!EventHandler)\(\);" -Encoding UTF8

          if ($violations) {
            Write-Error "Signal naming violations found:"
            $violations | ForEach-Object { Write-Host $_.Line }
            exit 1
          }

      - name: Check Signal Documentation
        shell: pwsh
        run: |
          # 妫€鏌?[Signal] 鏄惁鏈?XML 鏂囨。娉ㄩ噴
          $files = Get-ChildItem -Path "Game.Godot/Scripts" -Filter "*.cs" -Recurse
          $undocumented = @()

          foreach ($file in $files) {
            $content = Get-Content $file.FullName -Raw
            $signals = [regex]::Matches($content, '\[Signal\][^\r\n]*\r?\n\s*public delegate')

            foreach ($match in $signals) {
              $linesBefore = $content.Substring(0, $match.Index) -split '\r?\n'
              $lastLine = $linesBefore[-1]

              if ($lastLine -notmatch '///\s*<summary>') {
                $undocumented += "$($file.Name): $($match.Value)"
              }
            }
          }

          if ($undocumented.Count -gt 0) {
            Write-Error "Undocumented signals found:"
            $undocumented | ForEach-Object { Write-Host $_ }
            exit 1
          }

      - name: Run Signal Tests
        run: |
          dotnet test Game.Core.Tests/Game.Core.Tests.csproj `
            --filter "FullyQualifiedName~Signal" `
            --verbosity normal
```

---

## 瀹屾垚鏍囧噯

- [ ] 鎵€鏈?CloudEvents 浜嬩欢瀹氫箟宸茶縼绉诲埌 [Signal] delegate
- [ ] EventBus Autoload 宸插垱寤哄苟鍦?project.godot 娉ㄥ唽
- [ ] 鎵€鏈変簨浠跺彂灏勫凡浠?eventBus.publish() 杩佺Щ鍒?EmitSignal()
- [ ] 鎵€鏈変簨浠惰闃呭凡浠?eventBus.subscribe() 杩佺Щ鍒?signal += handler
- [ ] 淇″彿鍛藉悕绗﹀悎绾﹀畾锛圥ascalCase + EventHandler 鍚庣紑锛?
- [ ] 鎵€鏈変俊鍙锋湁 XML 鏂囨。娉ㄩ噴锛?summary>, <param>, <example>锛?
- [ ] GdUnit4 淇″彿娴嬭瘯瑕嗙洊涓昏鍦烘櫙锛圙dUnitSignalSpy锛?
- [ ] xUnit 閫昏緫娴嬭瘯瑕嗙洊淇″彿閫昏緫锛團akeSignalEmitter锛?
- [ ] 淇″彿鎬ц兘娴嬭瘯杈惧埌鍩哄噯闃堝€?
- [ ] CI 绠￠亾鍖呭惈淇″彿鍚堣妫€鏌?

---

## 涓嬩竴姝?

瀹屾垚鏈樁娈靛悗,缁х画:

鉃★笍 [Phase-10-Unit-Tests.md](Phase-10-Unit-Tests.md) 鈥?xUnit 鍗曞厓娴嬭瘯杩佺Щ




## 命名规范 / Naming

- Godot 信号：snake_case（`pressed`, `text_changed`）
- UI 事件（Screen 内/发布到总线）：`screen.<name>.<action>`
- 领域事件（EventBus）：`core.<context>.<event>` / 既有域名（`player.health.changed`）

## 订阅与解除订阅 / Subscriptions

- 推荐使用 `SignalScope` + `NodeWithSignals` 统一管理连接，在 `_ExitTree` 自动清理
- 示例（C#）：见 `Game.Godot/Scripts/Utils/SignalScope.cs` 与 `NodeWithSignals.cs`

## 与 EventBus 协同 / With EventBus

- UI 发布 `screen.*` 事件或调用服务；领域事件通过 `/root/EventBus` 订阅；跨边界使用 JSON 数据

## 测试建议 / Testing

- 连接→触发→断言；`queue_free`→再触发→不抛错/不泄漏；必要时采用 Headless 模式


## 示例 / Examples

- 组件：`Game.Godot/Examples/Components/EventListenerPanel.tscn`（继承 ControlWithSignals，Enter() 订阅 EventBus）
- 测试：`tests/UI/SignalScope_Tests.gd`（发布事件 → 断言收到 → 释放 → 再发布不报错）

