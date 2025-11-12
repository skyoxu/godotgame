# Phase 8: Scene Tree 涓?Node 璁捐

> 鐘舵€? 璁捐闃舵
> 棰勪及宸ユ椂: 8-12 澶?
> 椋庨櫓绛夌骇: 涓?
> 鍓嶇疆鏉′欢: Phase 1-7 瀹屾垚

---

## 鐩爣

鎺屾彙 Godot Scene Tree 鏋舵瀯锛屽缓绔?Node 缁勫悎涓庣户鎵挎ā寮忥紝瀹炵幇鍙祴璇曘€佸彲缁存姢鐨勫満鏅璁°€?

---

## Scene Tree 鏍稿績姒傚康

### Godot 鍦烘櫙鏍?vs React 缁勪欢鏍?

| 姒傚康 | React (vitegame) | Godot (godotgame) |
|-----|-----------------|------------------|
| 鍩烘湰鍗曞厓 | Component (鍑芥暟/绫? | Node (鍦烘櫙鑺傜偣) |
| 缁勭粐鏂瑰紡 | JSX 宓屽 | Scene Tree 鏍戝舰缁撴瀯 |
| 澶嶇敤鏈哄埗 | 缁勪欢瀵煎叆 | PackedScene 瀹炰緥鍖?|
| 鐢熷懡鍛ㄦ湡 | mount/unmount/render | _Ready/_Process/_ExitTree |
| 鐖跺瓙閫氫俊 | Props down/Callbacks up | Signals + GetNode |
| 鐘舵€佺鐞?| useState/Context | Node Properties + Signals |
| 浜嬩欢绯荤粺 | Synthetic Events | Godot Signals |

### Node 鍩虹姒傚康

```
Node (鍩虹被)
鈹溾攢 Node2D (2D 娓告垙瀵硅薄)
鈹? 鈹溾攢 Sprite2D (绮剧伒)
鈹? 鈹溾攢 AnimatedSprite2D (鍔ㄧ敾绮剧伒)
鈹? 鈹溾攢 CollisionShape2D (纰版挒褰㈢姸)
鈹? 鈹溾攢 Area2D (鍖哄煙妫€娴?
鈹? 鈹斺攢 CharacterBody2D (瑙掕壊鎺у埗鍣?
鈹?
鈹溾攢 Node3D (3D 娓告垙瀵硅薄)
鈹? 鈹溾攢 MeshInstance3D (缃戞牸瀹炰緥)
鈹? 鈹溾攢 Camera3D (3D 鐩告満)
鈹? 鈹斺攢 CollisionShape3D (3D 纰版挒)
鈹?
鈹溾攢 Control (UI 鑺傜偣)
鈹? 鈹溾攢 Button
鈹? 鈹溾攢 Label
鈹? 鈹斺攢 Container (VBoxContainer, HBoxContainer, etc.)
鈹?
鈹溾攢 CanvasLayer (鐢诲竷灞?
鈹溾攢 Timer (瀹氭椂鍣?
鈹溾攢 AudioStreamPlayer (闊抽鎾斁鍣?
鈹斺攢 HTTPRequest (HTTP 璇锋眰)
```

---

## 1. Scene 鏂囦欢缁撴瀯

### 鍦烘櫙鏂囦欢鏍煎紡 (.tscn)

**Player.tscn** (鏂囨湰鏍煎紡锛屼究浜庣増鏈帶鍒?:

```
[gd_scene load_steps=4 format=3 uid="uid://player_scene"]

[ext_resource type="Script" path="res://Scripts/PlayerController.cs" id="1"]
[ext_resource type="Texture2D" uid="uid://player_texture" path="res://Assets/Textures/player.png" id="2"]

[sub_resource type="RectangleShape2D" id="1"]
size = Vector2(32, 32)

[node name="Player" type="CharacterBody2D"]
script = ExtResource("1")

[node name="Sprite" type="Sprite2D" parent="."]
texture = ExtResource("2")

[node name="CollisionShape" type="CollisionShape2D" parent="."]
shape = SubResource("1")

[node name="AnimationPlayer" type="AnimationPlayer" parent="."]
```

**鍏抽敭閮ㄥ垎瑙ｆ瀽**:

1. **load_steps**: 鍦烘櫙鍔犺浇鎵€闇€鐨勮祫婧愭暟閲忥紙鑴氭湰銆佺汗鐞嗐€佸瓙璧勬簮绛夛級
2. **uid**: 鍏ㄥ眬鍞竴鏍囪瘑绗︼紝鐢ㄤ簬璺ㄥ満鏅紩鐢?
3. **ext_resource**: 澶栭儴璧勬簮寮曠敤锛堣剼鏈€佺汗鐞嗐€侀煶棰戠瓑锛?
4. **sub_resource**: 鍐呰仈璧勬簮瀹氫箟锛堝舰鐘躲€佸姩鐢汇€佹潗璐ㄧ瓑锛?
5. **node**: 鑺傜偣瀹氫箟锛屽寘鎷被鍨嬨€佺埗鑺傜偣銆佸睘鎬?

### Scene 缁ф壙 vs 缁勫悎

**缁ф壙妯″紡** (閫傚悎鍙樹綋璁捐):

```
BaseEnemy.tscn
鈹溾攢 Sprite2D
鈹溾攢 CollisionShape2D
鈹斺攢 HealthBar

缁ф壙 鈫?

FlyingEnemy.tscn (缁ф壙鑷?BaseEnemy.tscn)
鈹斺攢 娣诲姞 WingAnimation 鑺傜偣
```

**缁勫悎妯″紡** (閫傚悎鍔熻兘缁勫悎):

```
Player.tscn
鈹溾攢 Sprite2D
鈹溾攢 CollisionShape2D
鈹溾攢 InventoryComponent (瀹炰緥鍖栫殑鍦烘櫙)
鈹溾攢 HealthComponent (瀹炰緥鍖栫殑鍦烘櫙)
鈹斺攢 MovementComponent (瀹炰緥鍖栫殑鍦烘櫙)
```

---

## 2. Node 鐢熷懡鍛ㄦ湡

### 鏍稿績鐢熷懡鍛ㄦ湡鏂规硶

```csharp
// Game.Godot/Scripts/PlayerController.cs

using Godot;

namespace Game.Godot.Scripts;

public partial class PlayerController : CharacterBody2D
{
    // 1. _EnterTree: 鑺傜偣杩涘叆鍦烘櫙鏍戞椂璋冪敤锛堟渶鏃╋級
    public override void _EnterTree()
    {
        GD.Print("PlayerController: _EnterTree - Node added to tree");
        // 閫傜敤鍦烘櫙锛氭敞鍐屽叏灞€鐩戝惉鍣ㄣ€佸垵濮嬪寲闈欐€佽祫婧?
    }

    // 2. _Ready: 鑺傜偣鍙婂叾瀛愯妭鐐归兘鍔犺浇瀹屾垚鍚庤皟鐢紙鍒濆鍖栵級
    public override void _Ready()
    {
        GD.Print("PlayerController: _Ready - Scene fully loaded");

        // 鑾峰彇瀛愯妭鐐瑰紩鐢紙姝ゆ椂瀛愯妭鐐瑰凡瀛樺湪锛?
        _sprite = GetNode<Sprite2D>("Sprite");
        _collisionShape = GetNode<CollisionShape2D>("CollisionShape");

        // 杩炴帴淇″彿
        BodyEntered += OnBodyEntered;

        // 鍒濆鍖栫姸鎬?
        Health = MaxHealth;

        GD.Print("PlayerController initialized successfully");
    }

    // 3. _Process: 姣忓抚璋冪敤锛堢敤浜庢父鎴忛€昏緫鏇存柊锛?
    public override void _Process(double delta)
    {
        // 閫傜敤鍦烘櫙锛氳緭鍏ュ鐞嗐€佸姩鐢绘洿鏂般€乁I 鏇存柊
        HandleInput(delta);
        UpdateAnimation();
    }

    // 4. _PhysicsProcess: 鐗╃悊甯ц皟鐢紙鍥哄畾鏃堕棿姝ラ暱锛?
    public override void _PhysicsProcess(double delta)
    {
        // 閫傜敤鍦烘櫙锛氱墿鐞嗙Щ鍔ㄣ€佺鎾炴娴?
        var velocity = Velocity;

        // 搴旂敤閲嶅姏
        if (!IsOnFloor())
        {
            velocity.Y += Gravity * (float)delta;
        }

        // 澶勭悊绉诲姩
        var inputDirection = Input.GetAxis("move_left", "move_right");
        velocity.X = inputDirection * Speed;

        Velocity = velocity;
        MoveAndSlide();
    }

    // 5. _ExitTree: 鑺傜偣浠庡満鏅爲绉婚櫎鍓嶈皟鐢紙娓呯悊锛?
    public override void _ExitTree()
    {
        GD.Print("PlayerController: _ExitTree - Cleanup before removal");

        // 鏂紑淇″彿杩炴帴
        if (IsInstanceValid(this))
        {
            BodyEntered -= OnBodyEntered;
        }

        // 閲婃斁闈炴墭绠¤祫婧?
        // 娉ㄦ剰锛欸odot 绠＄悊鐨勮祫婧愪細鑷姩閲婃斁
    }

    // 6. _Notification: 鎺ユ敹绯荤粺閫氱煡锛堥珮绾х敤娉曪級
    public override void _Notification(int what)
    {
        switch (what)
        {
            case NotificationEnterTree:
                GD.Print("Notification: Enter Tree");
                break;
            case NotificationExitTree:
                GD.Print("Notification: Exit Tree");
                break;
            case NotificationPaused:
                GD.Print("Notification: Paused");
                break;
            case NotificationUnpaused:
                GD.Print("Notification: Unpaused");
                break;
        }
    }

    private Sprite2D _sprite = null!;
    private CollisionShape2D _collisionShape = null!;

    [Export]
    public int MaxHealth { get; set; } = 100;

    [Export]
    public float Speed { get; set; } = 200f;

    [Export]
    public float Gravity { get; set; } = 980f;

    public int Health { get; private set; }

    private void HandleInput(double delta)
    {
        // 杈撳叆澶勭悊閫昏緫
    }

    private void UpdateAnimation()
    {
        // 鍔ㄧ敾鏇存柊閫昏緫
    }

    private void OnBodyEntered(Node2D body)
    {
        GD.Print($"Player collided with: {body.Name}");
    }
}
```

**鐢熷懡鍛ㄦ湡椤哄簭鎬荤粨**:

```
鍦烘櫙鍔犺浇鏃?
1. _EnterTree (鐖惰妭鐐瑰厛浜庡瓙鑺傜偣)
2. _Ready (瀛愯妭鐐瑰厛浜庣埗鑺傜偣)

姣忓抚鏇存柊:
3. _Process (娓叉煋甯э紝甯х巼涓嶅浐瀹?
4. _PhysicsProcess (鐗╃悊甯э紝榛樿 60 FPS)

鍦烘櫙绉婚櫎鏃?
5. _ExitTree (鐖惰妭鐐瑰厛浜庡瓙鑺傜偣)
```

---

## 3. 鐖跺瓙鑺傜偣鍏崇郴涓庤妭鐐硅矾寰?

### 鑾峰彇瀛愯妭鐐?(GetNode)

```csharp
// Game.Godot/Scripts/UIController.cs

public partial class UIController : Control
{
    private Label _scoreLabel = null!;
    private Button _startButton = null!;
    private VBoxContainer _menu = null!;

    public override void _Ready()
    {
        // 鏂瑰紡 1: 鐩存帴璺緞锛堟帹鑽愶紝绫诲瀷瀹夊叏锛?
        _scoreLabel = GetNode<Label>("HUD/ScoreLabel");

        // 鏂瑰紡 2: 缁濆璺緞锛堜粠鏍硅妭鐐瑰紑濮嬶級
        _startButton = GetNode<Button>("/root/Main/UI/Menu/StartButton");

        // 鏂瑰紡 3: 鐩稿璺緞锛?./ 琛ㄧず鐖惰妭鐐癸級
        _menu = GetNode<VBoxContainer>("../Menu");

        // 鏂瑰紡 4: 浣跨敤 % 璁块棶鍞竴鍚嶇О鑺傜偣锛圙odot 4.0+锛?
        var uniqueNode = GetNode<Control>("%UniqueNodeName");

        // 鏂瑰紡 5: 妫€鏌ヨ妭鐐规槸鍚﹀瓨鍦?
        if (HasNode("HUD/HealthBar"))
        {
            var healthBar = GetNode<Control>("HUD/HealthBar");
        }

        // 鏂瑰紡 6: 浣跨敤 NodePath 鍙橀噺锛堝彲鍦?Inspector 涓厤缃級
        var customPath = new NodePath("HUD/ScoreLabel");
        _scoreLabel = GetNode<Label>(customPath);
    }
}
```

### Export NodePath 妯″紡锛堟帹鑽愮敤浜庤法鍦烘櫙寮曠敤锛?

```csharp
// Game.Godot/Scripts/PlayerController.cs

public partial class PlayerController : CharacterBody2D
{
    // 鍦?Inspector 涓彲鎷栨嫿閰嶇疆鑺傜偣璺緞
    [Export]
    public NodePath HealthBarPath { get; set; } = new NodePath("../UI/HealthBar");

    [Export]
    public NodePath CameraPath { get; set; } = new NodePath("Camera2D");

    private Control _healthBar = null!;
    private Camera2D _camera = null!;

    public override void _Ready()
    {
        // 杩愯鏃惰В鏋愯矾寰?
        if (!HealthBarPath.IsEmpty)
        {
            _healthBar = GetNode<Control>(HealthBarPath);
        }

        if (!CameraPath.IsEmpty)
        {
            _camera = GetNode<Camera2D>(CameraPath);
        }
    }
}
```

**NodePath 鏈€浣冲疄璺?*:

1. **纭紪鐮佽矾寰?*锛氶€傚悎鍦烘櫙鍐呴儴鍥哄畾缁撴瀯鐨勮妭鐐?
2. **Export NodePath**锛氶€傚悎闇€瑕佸湪 Inspector 涓厤缃殑鑺傜偣寮曠敤
3. **鍞竴鍚嶇О (%)**锛氶€傚悎璺ㄥ満鏅殑鍏ㄥ眬璁块棶锛堥渶鍦ㄧ紪杈戝櫒涓爣璁颁负 Unique锛?
4. **淇″彿閫氫俊**锛氶€傚悎鏉捐€﹀悎鐨勮妭鐐归€氫俊锛堜笉渚濊禆璺緞锛?

---

## 4. Scene 瀹炰緥鍖栦笌绠＄悊

### PackedScene 鍔犺浇涓庡疄渚嬪寲

```csharp
// Game.Godot/Scripts/EnemySpawner.cs

using Godot;
using System.Collections.Generic;

namespace Game.Godot.Scripts;

public partial class EnemySpawner : Node2D
{
    [Export]
    public PackedScene EnemyScene { get; set; } = null!;

    [Export]
    public float SpawnInterval { get; set; } = 2.0f;

    [Export]
    public int MaxEnemies { get; set; } = 10;

    private Timer _spawnTimer = null!;
    private List<Node2D> _activeEnemies = new();

    public override void _Ready()
    {
        // 鏂瑰紡 1: 鍦?Inspector 涓厤缃?PackedScene
        // (鎺ㄨ崘锛屼究浜庡彲瑙嗗寲閰嶇疆)

        // 鏂瑰紡 2: 浠ｇ爜鍔犺浇鍦烘櫙
        // EnemyScene = GD.Load<PackedScene>("res://Scenes/Enemies/BasicEnemy.tscn");

        // 璁剧疆瀹氭椂鍣?
        _spawnTimer = new Timer
        {
            WaitTime = SpawnInterval,
            Autostart = true
        };
        _spawnTimer.Timeout += OnSpawnTimerTimeout;
        AddChild(_spawnTimer);
    }

    private void OnSpawnTimerTimeout()
    {
        if (_activeEnemies.Count >= MaxEnemies) return;

        SpawnEnemy();
    }

    public void SpawnEnemy()
    {
        if (EnemyScene == null)
        {
            GD.PushError("EnemyScene is not set!");
            return;
        }

        // 瀹炰緥鍖栧満鏅?
        var enemy = EnemyScene.Instantiate<Node2D>();

        // 璁剧疆浣嶇疆
        enemy.Position = Position + new Vector2(
            GD.Randf() * 100 - 50,
            GD.Randf() * 100 - 50
        );

        // 娣诲姞鍒板満鏅爲锛堜綔涓哄綋鍓嶈妭鐐圭殑鍏勫紵鑺傜偣锛?
        GetParent().AddChild(enemy);

        // 杩借釜鏁屼汉瀹炰緥
        _activeEnemies.Add(enemy);

        // 鐩戝惉鏁屼汉姝讳骸淇″彿
        if (enemy.HasSignal("defeated"))
        {
            enemy.Connect("defeated", Callable.From(() => OnEnemyDefeated(enemy)));
        }
    }

    private void OnEnemyDefeated(Node2D enemy)
    {
        _activeEnemies.Remove(enemy);

        // 寤惰繜绉婚櫎锛堢瓑寰呮浜″姩鐢伙級
        enemy.QueueFree();
    }

    public override void _ExitTree()
    {
        // 娓呯悊鎵€鏈夋晫浜?
        foreach (var enemy in _activeEnemies)
        {
            if (IsInstanceValid(enemy))
            {
                enemy.QueueFree();
            }
        }
        _activeEnemies.Clear();
    }
}
```

### 鍦烘櫙鍒囨崲 (SceneTree.ChangeSceneToFile)

```csharp
// Game.Godot/Scripts/SceneManager.cs

using Godot;

namespace Game.Godot.Scripts;

public partial class SceneManager : Node
{
    [Signal]
    public delegate void SceneChangedEventHandler(string oldScene, string newScene);

    private string _currentScene = string.Empty;

    public override void _Ready()
    {
        _currentScene = GetTree().CurrentScene?.SceneFilePath ?? string.Empty;
    }

    /// <summary>
    /// 鍒囨崲鍒版柊鍦烘櫙锛堢珛鍗冲垏鎹級
    /// </summary>
    public void ChangeScene(string scenePath)
    {
        var oldScene = _currentScene;

        var error = GetTree().ChangeSceneToFile(scenePath);
        if (error != Error.Ok)
        {
            GD.PushError($"Failed to change scene to {scenePath}: {error}");
            return;
        }

        _currentScene = scenePath;
        EmitSignal(SignalName.SceneChanged, oldScene, scenePath);
    }

    /// <summary>
    /// 鍒囨崲鍒版柊鍦烘櫙锛堝甫杩囨浮鏁堟灉锛?
    /// </summary>
    public async void ChangeSceneWithTransition(string scenePath, float fadeTime = 0.5f)
    {
        // 鍒涘缓杩囨浮灞?
        var transition = new ColorRect
        {
            Color = Colors.Black,
            Modulate = new Color(1, 1, 1, 0)
        };
        transition.SetAnchorsPreset(Control.LayoutPreset.FullRect);

        GetTree().Root.AddChild(transition);

        // 娣″嚭
        var tween = CreateTween();
        tween.TweenProperty(transition, "modulate:a", 1.0f, fadeTime);
        await ToSignal(tween, Tween.SignalName.Finished);

        // 鍒囨崲鍦烘櫙
        ChangeScene(scenePath);

        // 娣″叆
        tween = CreateTween();
        tween.TweenProperty(transition, "modulate:a", 0.0f, fadeTime);
        await ToSignal(tween, Tween.SignalName.Finished);

        // 绉婚櫎杩囨浮灞?
        transition.QueueFree();
    }

    /// <summary>
    /// 棰勫姞杞藉満鏅紙鍚庡彴鍔犺浇锛屼笉闃诲锛?
    /// </summary>
    public async void PreloadSceneAsync(string scenePath)
    {
        var loader = ResourceLoader.LoadThreadedRequest(scenePath);

        while (true)
        {
            var status = ResourceLoader.LoadThreadedGetStatus(scenePath);

            if (status == ResourceLoader.ThreadLoadStatus.Loaded)
            {
                var scene = ResourceLoader.LoadThreadedGet(scenePath);
                GD.Print($"Scene preloaded: {scenePath}");
                break;
            }
            else if (status == ResourceLoader.ThreadLoadStatus.Failed ||
                     status == ResourceLoader.ThreadLoadStatus.InvalidResource)
            {
                GD.PushError($"Failed to preload scene: {scenePath}");
                break;
            }

            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        }
    }

    /// <summary>
    /// 閲嶆柊鍔犺浇褰撳墠鍦烘櫙
    /// </summary>
    public void ReloadCurrentScene()
    {
        GetTree().ReloadCurrentScene();
    }

    /// <summary>
    /// 娣诲姞瀛愬満鏅紙涓嶅垏鎹紝鍙犲姞鏄剧ず锛?
    /// </summary>
    public Node? AddSubScene(string scenePath)
    {
        var packedScene = GD.Load<PackedScene>(scenePath);
        if (packedScene == null)
        {
            GD.PushError($"Failed to load scene: {scenePath}");
            return null;
        }

        var instance = packedScene.Instantiate();
        GetTree().Root.AddChild(instance);

        return instance;
    }
}
```

---

## 5. Node Groups 涓?Tags

### 浣跨敤 Groups 瀹炵幇鎵归噺鎿嶄綔

```csharp
// Game.Godot/Scripts/Enemy.cs

public partial class Enemy : CharacterBody2D
{
    public override void _Ready()
    {
        // 娣诲姞鍒?"enemies" 缁?
        AddToGroup("enemies");
        AddToGroup("damageable");
    }
}

// Game.Godot/Scripts/Player.cs

public partial class Player : CharacterBody2D
{
    public override void _Ready()
    {
        AddToGroup("player");
        AddToGroup("damageable");
    }

    public void AttackAllEnemies(int damage)
    {
        // 鑾峰彇鎵€鏈?"enemies" 缁勭殑鑺傜偣
        var enemies = GetTree().GetNodesInGroup("enemies");

        foreach (Node enemy in enemies)
        {
            if (enemy is Enemy enemyScript)
            {
                enemyScript.TakeDamage(damage);
            }
        }
    }

    public void HealAllDamageableUnits(int healAmount)
    {
        // 鑾峰彇鎵€鏈?"damageable" 缁勭殑鑺傜偣
        var damageableUnits = GetTree().GetNodesInGroup("damageable");

        foreach (Node unit in damageableUnits)
        {
            if (unit.HasMethod("Heal"))
            {
                unit.Call("Heal", healAmount);
            }
        }
    }
}

// Game.Godot/Scripts/GameManager.cs

public partial class GameManager : Node
{
    public void PauseAllEnemies()
    {
        // 鏆傚仠鎵€鏈夋晫浜?
        GetTree().CallGroup("enemies", "set_process", false);
        GetTree().CallGroup("enemies", "set_physics_process", false);
    }

    public void ResumeAllEnemies()
    {
        // 鎭㈠鎵€鏈夋晫浜?
        GetTree().CallGroup("enemies", "set_process", true);
        GetTree().CallGroup("enemies", "set_physics_process", true);
    }

    public int CountActiveEnemies()
    {
        return GetTree().GetNodesInGroup("enemies").Count;
    }
}
```

**Groups 浣跨敤鍦烘櫙**:

1. **鎵归噺鎺у埗**锛氭殏鍋?鎭㈠涓€缁勮妭鐐?
2. **纰版挒绛涢€?*锛氬揩閫熻瘑鍒鎾炲璞＄被鍨?
3. **浜嬩欢骞挎挱**锛氬悜鐗瑰畾缁勫彂閫佹秷鎭?
4. **鏌ヨ缁熻**锛氱粺璁＄壒瀹氱被鍨嬭妭鐐规暟閲?

---

## 6. Autoload (鍗曚緥妯″紡)

### 娉ㄥ唽鍏ㄥ眬鍗曚緥

**project.godot**:

```ini
[autoload]

ServiceLocator="*res://Autoloads/ServiceLocator.cs"
EventBus="*res://Autoloads/EventBus.cs"
GameState="*res://Autoloads/GameState.cs"
AudioManager="*res://Autoloads/AudioManager.cs"
```

**ServiceLocator Autoload**:

```csharp
// Game.Godot/Autoloads/ServiceLocator.cs

using Godot;
using Game.Core.Ports;
using Game.Godot.Adapters;

namespace Game.Godot.Autoloads;

/// <summary>
/// 鍏ㄥ眬鏈嶅姟瀹氫綅鍣紙Autoload 鍗曚緥锛?
/// 鍦?project.godot 涓敞鍐屼负鑷姩鍔犺浇
/// </summary>
public partial class ServiceLocator : Node
{
    // 鍗曚緥璁块棶鐐?
    public static ServiceLocator Instance { get; private set; } = null!;

    // 鏈嶅姟瀹炰緥
    public ITime Time { get; private set; } = null!;
    public IInput InputService { get; private set; } = null!;
    public IResourceLoader ResourceLoader { get; private set; } = null!;
    public IAudioPlayer AudioPlayer { get; private set; } = null!;
    public IDataStore DataStore { get; private set; } = null!;
    public ILogger Logger { get; private set; } = null!;

    public override void _EnterTree()
    {
        // 璁剧疆鍗曚緥锛堝湪 _EnterTree 涓紝纭繚鏈€鏃╁垵濮嬪寲锛?
        Instance = this;
    }

    public override void _Ready()
    {
        // 娉ㄥ唽鎵€鏈夐€傞厤鍣?
        Time = new GodotTimeAdapter();
        InputService = new GodotInputAdapter();
        ResourceLoader = new GodotResourceLoader();
        AudioPlayer = new GodotAudioPlayer();
        DataStore = new SqliteDataStore();
        Logger = new GodotLogger("Game");

        // 鍒濆鍖栨暟鎹簱
        DataStore.Open("user://game.db");

        GD.Print("ServiceLocator initialized successfully");
    }

    public override void _ExitTree()
    {
        DataStore?.Close();
    }
}
```

**EventBus Autoload**:

```csharp
// Game.Godot/Autoloads/EventBus.cs

using Godot;
using System;
using System.Collections.Generic;

namespace Game.Godot.Autoloads;

/// <summary>
/// 鍏ㄥ眬浜嬩欢鎬荤嚎锛堝彂甯?璁㈤槄妯″紡锛?
/// </summary>
public partial class EventBus : Node
{
    public static EventBus Instance { get; private set; } = null!;

    private Dictionary<string, List<Action<object>>> _eventHandlers = new();

    public override void _EnterTree()
    {
        Instance = this;
    }

    /// <summary>
    /// 璁㈤槄浜嬩欢
    /// </summary>
    public void Subscribe(string eventName, Action<object> handler)
    {
        if (!_eventHandlers.ContainsKey(eventName))
        {
            _eventHandlers[eventName] = new List<Action<object>>();
        }

        _eventHandlers[eventName].Add(handler);
    }

    /// <summary>
    /// 鍙栨秷璁㈤槄
    /// </summary>
    public void Unsubscribe(string eventName, Action<object> handler)
    {
        if (_eventHandlers.ContainsKey(eventName))
        {
            _eventHandlers[eventName].Remove(handler);
        }
    }

    /// <summary>
    /// 鍙戝竷浜嬩欢
    /// </summary>
    public void Publish(string eventName, object data)
    {
        if (_eventHandlers.ContainsKey(eventName))
        {
            foreach (var handler in _eventHandlers[eventName])
            {
                try
                {
                    handler(data);
                }
                catch (Exception ex)
                {
                    GD.PushError($"EventBus error in handler for '{eventName}': {ex.Message}");
                }
            }
        }
    }

    /// <summary>
    /// 娓呯┖鎵€鏈夎闃?
    /// </summary>
    public void Clear()
    {
        _eventHandlers.Clear();
    }
}
```

**浣跨敤 Autoload**:

```csharp
// Game.Godot/Scripts/PlayerController.cs

public partial class PlayerController : CharacterBody2D
{
    public override void _Ready()
    {
        // 璁块棶鍏ㄥ眬鏈嶅姟
        var logger = ServiceLocator.Instance.Logger;
        logger.LogInfo("PlayerController initialized");

        // 璁㈤槄鍏ㄥ眬浜嬩欢
        EventBus.Instance.Subscribe("player_damaged", OnPlayerDamaged);

        // 璁块棶鍏ㄥ眬鐘舵€?
        var currentLevel = GameState.Instance.CurrentLevel;
    }

    private void OnPlayerDamaged(object data)
    {
        var damage = (int)data;
        GD.Print($"Player took {damage} damage");
    }

    public void TakeDamage(int amount)
    {
        // 鍙戝竷鍏ㄥ眬浜嬩欢
        EventBus.Instance.Publish("player_damaged", amount);
    }

    public override void _ExitTree()
    {
        // 鍙栨秷璁㈤槄
        EventBus.Instance.Unsubscribe("player_damaged", OnPlayerDamaged);
    }
}
```

---

## 7. 鍦烘櫙缁勭粐鏈€浣冲疄璺?

### 鎺ㄨ崘鐩綍缁撴瀯

```
Game.Godot/Scenes/
鈹溾攢鈹€ Main.tscn                      # 涓诲満鏅紙鍚姩鍏ュ彛锛?
鈹?
鈹溾攢鈹€ UI/                            # UI 鍦烘櫙
鈹?  鈹溾攢鈹€ MainMenu.tscn
鈹?  鈹溾攢鈹€ HUD.tscn
鈹?  鈹溾攢鈹€ PauseMenu.tscn
鈹?  鈹溾攢鈹€ SettingsMenu.tscn
鈹?  鈹斺攢鈹€ Components/                # 鍙鐢?UI 缁勪欢
鈹?      鈹溾攢鈹€ PrimaryButton.tscn
鈹?      鈹溾攢鈹€ TextInput.tscn
鈹?      鈹斺攢鈹€ HealthBar.tscn
鈹?
鈹溾攢鈹€ Game/                          # 娓告垙瀹炰綋鍦烘櫙
鈹?  鈹溾攢鈹€ Player/
鈹?  鈹?  鈹溾攢鈹€ Player.tscn
鈹?  鈹?  鈹斺攢鈹€ PlayerCamera.tscn
鈹?  鈹溾攢鈹€ Enemies/
鈹?  鈹?  鈹溾攢鈹€ BaseEnemy.tscn        # 鏁屼汉鍩虹被鍦烘櫙
鈹?  鈹?  鈹溾攢鈹€ FlyingEnemy.tscn      # 缁ф壙鑷?BaseEnemy
鈹?  鈹?  鈹斺攢鈹€ GroundEnemy.tscn      # 缁ф壙鑷?BaseEnemy
鈹?  鈹溾攢鈹€ Items/
鈹?  鈹?  鈹溾攢鈹€ Coin.tscn
鈹?  鈹?  鈹溾攢鈹€ HealthPotion.tscn
鈹?  鈹?  鈹斺攢鈹€ Weapon.tscn
鈹?  鈹斺攢鈹€ Effects/
鈹?      鈹溾攢鈹€ Explosion.tscn
鈹?      鈹溾攢鈹€ HitEffect.tscn
鈹?      鈹斺攢鈹€ Particle.tscn
鈹?
鈹溾攢鈹€ Levels/                        # 鍏冲崱鍦烘櫙
鈹?  鈹溾攢鈹€ Level1.tscn
鈹?  鈹溾攢鈹€ Level2.tscn
鈹?  鈹溾攢鈹€ BossLevel.tscn
鈹?  鈹斺攢鈹€ Tilemap/                   # 鍦板浘鐩稿叧
鈹?      鈹溾攢鈹€ GroundTileset.tres
鈹?      鈹斺攢鈹€ WallTileset.tres
鈹?
鈹斺攢鈹€ Components/                    # 鍔熻兘缁勪欢锛堝彲闄勫姞鍒颁换浣曡妭鐐癸級
    鈹溾攢鈹€ HealthComponent.tscn
    鈹溾攢鈹€ MovementComponent.tscn
    鈹溾攢鈹€ InventoryComponent.tscn
    鈹斺攢鈹€ AIComponent.tscn
```

### 鍦烘櫙鍛藉悕绾﹀畾

1. **PascalCase**: `PlayerController.tscn`, `MainMenu.tscn`
2. **璇箟鍖?*: 鍚嶇О浣撶幇鍔熻兘锛屽 `HealthBar.tscn`, `EnemySpawner.tscn`
3. **缁勪欢鍚庣紑**: 鍔熻兘缁勪欢浣跨敤 `Component` 鍚庣紑锛屽 `HealthComponent.tscn`
4. **Base 鍓嶇紑**: 鎶借薄鍩虹被浣跨敤 `Base` 鍓嶇紑锛屽 `BaseEnemy.tscn`

### 鍦烘櫙璁捐鍘熷垯

1. **鍗曚竴鑱岃矗**锛氭瘡涓満鏅彧璐熻矗涓€涓姛鑳芥ā鍧?
2. **缁勫悎浼樹簬缁ф壙**锛氫紭鍏堜娇鐢ㄥ満鏅疄渚嬪寲缁勫悎鍔熻兘
3. **鏈€灏忓寲鑰﹀悎**锛氶€氳繃 Signals 鍜?EventBus 瑙ｈ€﹀満鏅?
4. **鍙祴璇曟€?*锛氬満鏅簲鑳界嫭绔嬫祴璇曪紝涓嶄緷璧栫壒瀹氱埗鍦烘櫙

---

## 8. 娴嬭瘯鍦烘櫙鏋舵瀯

### GdUnit4 鍦烘櫙娴嬭瘯

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

### xUnit 鍦烘櫙閫昏緫娴嬭瘯

```csharp
// Game.Core.Tests/Scenes/SceneManagerTests.cs

using FluentAssertions;
using Game.Core.Tests.Fakes;
using Game.Godot.Scripts;
using Xunit;

namespace Game.Core.Tests.Scenes;

public class SceneManagerTests
{
    [Fact]
    public void ChangeScene_ShouldEmitSceneChangedSignal()
    {
        // Arrange
        var fakeSceneTree = new FakeSceneTree();
        var sceneManager = new FakeSceneManager(fakeSceneTree);

        string? emittedOldScene = null;
        string? emittedNewScene = null;

        sceneManager.SceneChangedEvent += (oldScene, newScene) =>
        {
            emittedOldScene = oldScene;
            emittedNewScene = newScene;
        };

        // Act
        sceneManager.ChangeScene("res://Scenes/Levels/Level2.tscn");

        // Assert
        emittedOldScene.Should().Be("res://Scenes/Levels/Level1.tscn");
        emittedNewScene.Should().Be("res://Scenes/Levels/Level2.tscn");
    }

    [Fact]
    public void PreloadSceneAsync_ShouldLoadSceneInBackground()
    {
        // Arrange
        var fakeResourceLoader = new FakeResourceLoader();
        var sceneManager = new FakeSceneManager(fakeResourceLoader);

        // Act
        sceneManager.PreloadSceneAsync("res://Scenes/Levels/Level3.tscn");
        fakeResourceLoader.SimulateLoadComplete();

        // Assert
        fakeResourceLoader.IsSceneLoaded("res://Scenes/Levels/Level3.tscn").Should().BeTrue();
    }
}
```

---

## 9. CI 闆嗘垚

### 鍦烘櫙缁撴瀯楠岃瘉 (GitHub Actions)

```yaml
# .github/workflows/scene-validation.yml

name: Scene Validation

on: [push, pull_request]

jobs:
  validate-scenes:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Godot
        uses: chickensoft-games/setup-godot@v1
        with:
          version: 4.5.0
          use-dotnet: true

      - name: Validate Scene Structure
        run: |
          # 妫€鏌ユ墍鏈夊満鏅枃浠惰娉?
          godot --headless --script scripts/validate_scenes.cs

      - name: Run GdUnit4 Scene Tests
        run: |
          godot --headless --path . `
            --script res://addons/gdUnit4/bin/GdUnitCmdTool.cs `
            --conf res://GdUnitRunner.cfg `
            --output ./TestResults/scene-tests.xml

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: scene-test-results
          path: TestResults/scene-tests.xml
```

**鍦烘櫙楠岃瘉鑴氭湰** (`scripts/validate_scenes.cs`):

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

---

## 瀹屾垚鏍囧噯

- [ ] 鐞嗚В Scene Tree 鏋舵瀯涓?Node 鐢熷懡鍛ㄦ湡
- [ ] 鎺屾彙鍦烘櫙缁ф壙涓庣粍鍚堟ā寮?
- [ ] 鐔熺粌浣跨敤 GetNode 鍜?NodePath
- [ ] 瀹炵幇 PackedScene 瀹炰緥鍖栦笌鍦烘櫙鍒囨崲
- [ ] 浣跨敤 Groups 瀹炵幇鎵归噺鎿嶄綔
- [ ] 鍒涘缓 Autoload 鍏ㄥ眬鍗曚緥 (ServiceLocator/EventBus)
- [ ] 鍦烘櫙缁勭粐閬靛惊鏈€浣冲疄璺碉紙鐩綍缁撴瀯涓庡懡鍚嶏級
- [ ] GdUnit4 鍦烘櫙娴嬭瘯瑕嗙洊涓昏鍦烘櫙
- [ ] xUnit 閫昏緫娴嬭瘯瑕嗙洊鍦烘櫙绠＄悊閫昏緫
- [ ] CI 闆嗘垚鍦烘櫙缁撴瀯楠岃瘉

---

## 涓嬩竴姝?

瀹屾垚鏈樁娈靛悗锛岀户缁細

鉃★笍 [Phase-9-Signal-System.md](Phase-9-Signal-System.md) 鈥?CloudEvents 鈫?Godot Signals 杩佺Щ

## Root 分层建议 / Root Layering

- 推荐主场景分层：
  - `ScreenRoot`（动态屏幕挂载点）
  - `HUD`（常驻 UI）
  - `Overlays`（Modal/Toast 等叠加）
  - 引导节点：`ThemeApplier`、`SettingsLoader`、`InputMapper`

## 导航器 / Screen Navigator

- 组件：`Game.Godot/Scripts/Navigation/ScreenNavigator.cs`
- 用法：在主场景挂 `ScreenNavigator`，设置 `ScreenRootPath` 指向容器节点
- 切换：`nav.SwitchTo("res://Game.Godot/Scenes/Screens/StartScreen.tscn")`

### 与 MainMenu 联动

- Main 监听 `ui.menu.start`：优先加载示例 `DemoScreen`（当 `TEMPLATE_DEMO=1`），否则尝试加载 `Scenes/Screens/StartScreen.tscn`（若存在）


## Overlays 层用法 / Overlays Layer

- 在主场景下新增 `Overlays`（Control）：用于承载 Modal/Toast 等叠加层，避免与 ScreenRoot 互相影响。
- 使用方式：在需要时 `Overlays.AddChild(instance)`；示例组件位于 `Game.Godot/Examples/Components/**`。

## Screen 生命周期与信号约定 / Lifecycle & Signals

- 生命周期（推荐钩子）:
  - `Enter()`：Screen 被导航器实例化并即将显示（可选自定义方法）
  - `Exit()`：Screen 被替换前触发（释放资源/断开信号）（可选自定义方法）
- 信号命名：`screen.<name>.<action>`，例如 `screen.start.loaded`、`screen.settings.saved`
- 领域事件仍通过 `/root/EventBus`，UI 层尽量发布语义清晰的 screen 事件供上层协调。


### Overlays 节点（已添加）

- 主场景 `Main.tscn` 已添加 `Overlays` 容器节点（Control，锚定全屏），用于承载 Modal/Toast 等叠加层。

### 导航钩子（Enter/Exit）

- `ScreenNavigator.SwitchTo(...)` 会在卸载旧 Screen 前调用其 `Exit()`（若存在），在加载新 Screen 后调用其 `Enter()`（若存在），便于管理资源/信号。


### Overlays 用法示例

```csharp
// 在 Screen 中将 Modal/Toast 挂到 Overlays
var overlays = GetNodeOrNull<Control>("/root/Main/Overlays");
var ps = ResourceLoader.Load<PackedScene>("res://Game.Godot/Examples/Components/Modal.tscn");
if (overlays != null && ps != null) {
    var modal = ps.Instantiate<Control>();
    overlays.AddChild(modal);
    modal.Call("Open", "Message");
}
```


## Screen 过渡 / Screen Transitions

- 导航器支持淡入淡出过渡：`UseFadeTransition=true`，`FadeDurationSec` 可配置。
- 过渡期间 Overlays 会生成全屏 `ColorRect`（拦截输入），切换完成后移除。
- 可按需替换为自定义过渡（AnimationPlayer/Shader）。

## Z 次序与输入遮罩 / Z-Order & Input Mask

- `Overlays.z_index=100`，默认 `mouse_filter=Ignore`（1），需要阻塞输入的叠加层自行设置 `Stop`。
- 过渡遮罩自动设置为 `Stop`，确保切换时屏幕不接收输入。


### Enter/Exit 示例 / Example

```csharp
// Game.Godot/Scripts/Screens/StartScreen.cs
public void Enter() { GD.Print("[StartScreen] Enter"); }
public void Exit()  { GD.Print("[StartScreen] Exit"); }
```


## 跨 Screen 导航示例 / Cross-Screen Navigation

- 示例：`Examples/Screens/DemoScreen.tscn` 按钮导航到 `Scenes/Screens/SettingsScreen.tscn`；Settings 有 Back 返回 `StartScreen`。
- 观察日志：Enter/Exit 钩子、淡入淡出过渡遮罩。

## Screen 规范与模板 / Screen Guidelines & Template

- 路径与命名：
  - 路径：`Game.Godot/Scenes/Screens/<Name>.tscn` 与 `Game.Godot/Scripts/Screens/<Name>.cs` 一一对应。
  - 命名：`<Name>` 使用 PascalCase，节点名称与文件名一致，便于查找与导航。
- 资源管理：
  - 在 `_Ready` 仅做轻量初始化；重型加载放到 `Enter()` 或异步流程中（如 `CallDeferred`/Tween）。
  - 在 `Exit()` 里面释放订阅、断开信号、停止计时器、保存必要状态，避免泄漏。
  - Overlays 场景请添加到 `/root/Main/Overlays`，不要直接挂在 ScreenRoot，避免层级干扰。
- 事件与通信：
  - UI 内部事件：`screen.<name>.<action>` 命名（screen.start.loaded / screen.settings.saved）。
  - 领域事件：统一走 `/root/EventBus`，UI 层仅转换语义并发布。
- 模板（C#）：
```csharp
// Game.Godot/Scripts/Screens/MyScreen.cs
using Godot;
namespace Game.Godot.Scripts.Screens;
public partial class MyScreen : Control
{
    public override void _Ready() { GD.Print("[MyScreen] _Ready"); }
    public void Enter() => GD.Print("[MyScreen] Enter");
    public void Exit()  => GD.Print("[MyScreen] Exit");
}
```
- 模板（.tscn）：
```ini
[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://Game.Godot/Scripts/Screens/MyScreen.cs" id="1"]
[node name="MyScreen" type="Control"]
script = ExtResource("1")
```
- 脚手架：`./scripts/scaffold/new_screen.ps1 -Name MyScreen`（已包含 Enter/Exit 钩子）。
