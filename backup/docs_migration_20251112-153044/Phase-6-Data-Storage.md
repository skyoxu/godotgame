# Phase 6: SQLite 鏁版嵁灞傝縼绉?
> 鐘舵€? 瀹炴柦闃舵
> 棰勪及宸ユ椂: 5-7 澶?> 椋庨櫓绛夌骇: 涓?> 鍓嶇疆鏉′欢: Phase 1-5 瀹屾垚

---

## 鐩爣

灏?vitegame 鐨?better-sqlite3 鏁版嵁搴撹縼绉诲埌 godotgame 鐨?godot-sqlite锛屽缓绔嬬被鍨嬪畨鍏ㄧ殑浠撳偍灞傚拰杩佺Щ绯荤粺銆?
---

## 鎶€鏈爤瀵规瘮

| 鍔熻兘 | vitegame (Node.js) | godotgame (Godot) |
|-----|-------------------|------------------|
| 搴?| better-sqlite3 | godot-sqlite (GDNative) |
| 鍒濆鍖?| `new Database('game.db')` | `SQLite.new() + open_db()` |
| 鏌ヨ | `.prepare().all()` | `.query() + .query_result` |
| 鍙傛暟鍖?| `stmt.bind(params)` | 瀛楃涓叉彃鍊硷紙娉ㄦ剰娉ㄥ叆锛?|
| 浜嬪姟 | `.transaction()` | 鎵嬪姩 BEGIN/COMMIT |
| 绫诲瀷 | JavaScript 瀵硅薄 | Godot.Collections.Dictionary |

---

## 鏁版嵁搴撴灦鏋?
### 褰撳墠 Schema (vitegame)

```sql
-- 鐢ㄦ埛鏁版嵁
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    created_at INTEGER NOT NULL,
    last_login INTEGER
);

-- 鐜╁瀛樻。
CREATE TABLE saves (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    slot_number INTEGER NOT NULL,
    data TEXT NOT NULL, -- JSON 搴忓垪鍖?    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, slot_number)
);

-- 娓告垙缁熻
CREATE TABLE statistics (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    stat_key TEXT NOT NULL,
    stat_value REAL NOT NULL,
    recorded_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Schema 鐗堟湰鎺у埗
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at INTEGER NOT NULL,
    description TEXT
);
```

### 鐩爣 Schema (godotgame)

淇濇寔鐩稿悓缁撴瀯锛屼絾娣诲姞锛?
```sql
-- 鏂板锛氭垚灏辩郴缁?CREATE TABLE achievements (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    achievement_key TEXT NOT NULL,
    unlocked_at INTEGER NOT NULL,
    progress REAL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, achievement_key)
);

-- 鏂板锛氳缃瓨鍌?CREATE TABLE settings (
    user_id TEXT PRIMARY KEY,
    audio_volume REAL DEFAULT 1.0,
    graphics_quality TEXT DEFAULT 'medium',
    language TEXT DEFAULT 'en',
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## IDataStore 瀹炵幇锛圥hase 5 鎺ュ彛锛?
### 鎺ュ彛瀹氫箟锛堝洖椤撅級

```csharp
// Game.Core/Ports/IDataStore.cs

namespace Game.Core.Ports;

public interface IDataStore
{
    void Open(string dbPath);
    void Close();
    void Execute(string sql, params object[] parameters);
    T? QuerySingle<T>(string sql, params object[] parameters) where T : class;
    List<T> Query<T>(string sql, params object[] parameters) where T : class;
}
```

### Godot SQLite 閫傞厤鍣紙澧炲己鐗堬級

```csharp
// Game.Godot/Adapters/SqliteDataStore.cs

using Godot;
using Game.Core.Ports;
using System.Reflection;

namespace Game.Godot.Adapters;

/// <summary>
/// 浣跨敤 godot-sqlite 鎻掍欢鐨勯€傞厤鍣紙澧炲己鐗堬級
/// 鏀寔鍙傛暟鍖栨煡璇€佷簨鍔°€佺被鍨嬫槧灏?/// </summary>
public class SqliteDataStore : IDataStore
{
    private SQLite? _db;
    private bool _inTransaction = false;

    public void Open(string dbPath)
    {
        _db = new SQLite();
        _db.Path = dbPath;

        if (!_db.OpenDb())
        {
            throw new InvalidOperationException($"Failed to open database: {dbPath}");
        }

        // 鍚敤澶栭敭绾︽潫
        Execute("PRAGMA foreign_keys = ON;");

        // 鎬ц兘浼樺寲
        Execute("PRAGMA journal_mode = WAL;"); // Write-Ahead Logging
        Execute("PRAGMA synchronous = NORMAL;");
    }

    public void Close()
    {
        _db?.CloseDb();
        _db = null;
    }

    public void Execute(string sql, params object[] parameters)
    {
        if (_db == null)
            throw new InvalidOperationException("Database not opened");

        // 鍙傛暟鍖栨煡璇紙绠€鍖栫増锛岀敓浜х幆澧冮渶鏇翠弗鏍硷級
        string parameterizedSql = FormatSqlWithParameters(sql, parameters);

        var success = _db.Query(parameterizedSql);
        if (!success)
        {
            throw new InvalidOperationException($"SQL execution failed: {sql}");
        }
    }

    public T? QuerySingle<T>(string sql, params object[] parameters) where T : class
    {
        var results = Query<T>(sql, parameters);
        return results.FirstOrDefault();
    }

    public List<T> Query<T>(string sql, params object[] parameters) where T : class
    {
        if (_db == null)
            throw new InvalidOperationException("Database not opened");

        string parameterizedSql = FormatSqlWithParameters(sql, parameters);
        _db.Query(parameterizedSql);

        var results = new List<T>();

        for (int i = 0; i < _db.QueryResult.Length; i++)
        {
            var row = _db.QueryResult[i].As<Godot.Collections.Dictionary>();
            var instance = MapToObject<T>(row);
            if (instance != null)
            {
                results.Add(instance);
            }
        }

        return results;
    }

    /// <summary>
    /// 寮€濮嬩簨鍔?    /// </summary>
    public void BeginTransaction()
    {
        if (_inTransaction)
            throw new InvalidOperationException("Transaction already in progress");

        Execute("BEGIN TRANSACTION;");
        _inTransaction = true;
    }

    /// <summary>
    /// 鎻愪氦浜嬪姟
    /// </summary>
    public void CommitTransaction()
    {
        if (!_inTransaction)
            throw new InvalidOperationException("No transaction in progress");

        Execute("COMMIT;");
        _inTransaction = false;
    }

    /// <summary>
    /// 鍥炴粴浜嬪姟
    /// </summary>
    public void RollbackTransaction()
    {
        if (!_inTransaction)
            throw new InvalidOperationException("No transaction in progress");

        Execute("ROLLBACK;");
        _inTransaction = false;
    }

    /// <summary>
    /// 绠€鍖栧弬鏁板寲锛堢敓浜х幆澧冮渶浣跨敤 Prepared Statements锛?    /// </summary>
    private string FormatSqlWithParameters(string sql, object[] parameters)
    {
        if (parameters == null || parameters.Length == 0)
            return sql;

        // 绠€鍗曟浛鎹紙璀﹀憡锛氫笉闃?SQL 娉ㄥ叆锛屼粎鐢ㄤ簬婕旂ず锛?        for (int i = 0; i < parameters.Length; i++)
        {
            var param = parameters[i];
            string value = param switch
            {
                string s => $"'{EscapeSqlString(s)}'",
                int n => n.ToString(),
                long l => l.ToString(),
                double d => d.ToString(System.Globalization.CultureInfo.InvariantCulture),
                bool b => b ? "1" : "0",
                _ => "NULL"
            };

            sql = sql.Replace($"@{i}", value);
        }

        return sql;
    }

#### 瀹夊叏鎻愮ず涓庡噯澶囪鍙ュ缓璁?
> 閲嶈锛氫互涓?`FormatSqlWithParameters` 浠呬负鏁欏绀轰緥锛屾棤娉曢槻寰″鏉傛敞鍏ュ満鏅€傜敓浜у疄鐜板簲浼樺厛閲囩敤鈥滈缂栬瘧璇彞/缁戝畾鍙傛暟鈥濊兘鍔涳紱鑻ユ墍鐢ㄧ殑 `godot-sqlite` 鐗堟湰鏀寔 Prepared Statement锛岃鍙傝€冨畼鏂规帴鍙ｄ娇鐢ㄧ粦瀹氬弬鏁帮紙濡?`?1, ?2 ...`锛夛紝骞堕€氳繃鏄惧紡绫诲瀷缁戝畾锛堝瓧绗︿覆杞箟銆佹暟鍊兼枃鍖栨棤鍏虫牸寮忥級鍐欏叆銆?
寤鸿鍋氭硶锛?- 鍦ㄩ€傞厤灞備负鈥滃彧璇绘煡璇?鍐欏叆鎿嶄綔鈥濆垎鍒彁渚涘皝瑁咃紝鍐呴儴闆嗕腑鍋氬弬鏁扮粦瀹氫笌閿欒澶勭悊锛?- 涓衡€滃姩鎬佹瀯閫?SQL鈥濈殑鍦烘櫙锛岀粺涓€璧扳€滅櫧鍚嶅崟瀛楁鍚?+ 缁戝畾鍊尖€濈殑绛栫暐锛岄伩鍏嶇洿鎺ユ嫾鎺ワ紱
- 浣跨敤鍗曞厓娴嬭瘯瑕嗙洊鈥滄敞鍏ュ皾璇?寮傚父璺緞/浜嬪姟鍥炴粴鈥濈瓑杈圭晫锛?- 灏嗏€滃弬鏁板寲寮€鍏?闄嶇骇绛栫暐鈥濇毚闇蹭负閰嶇疆椤癸紝CI 涓姝㈤檷绾ц繍琛屻€?
    /// <summary>
    /// 杞箟 SQL 瀛楃涓诧紙鍩虹鐗堟湰锛?    /// </summary>
    private string EscapeSqlString(string input)
    {
        return input.Replace("'", "''");
    }

    /// <summary>
    /// 鏄犲皠 Dictionary 鍒?C# 瀵硅薄锛堝弽灏勭増鏈級
    /// </summary>
    private T? MapToObject<T>(Godot.Collections.Dictionary row) where T : class
    {
        var instance = Activator.CreateInstance<T>();
        var properties = typeof(T).GetProperties(BindingFlags.Public | BindingFlags.Instance);

        foreach (var prop in properties)
        {
            // 灏濊瘯澶氱鍛藉悕绾﹀畾
            string[] possibleKeys = {
                prop.Name,                           // UserId
                ToSnakeCase(prop.Name),              // user_id
                prop.Name.ToLower()                  // userid
            };

            foreach (var key in possibleKeys)
            {
                if (row.ContainsKey(key))
                {
                    try
                    {
                        var value = row[key];

                        // 绫诲瀷杞崲
                        if (value != null && prop.CanWrite)
                        {
                            object convertedValue = prop.PropertyType.Name switch
                            {
                                nameof(String) => value.ToString() ?? string.Empty,
                                nameof(Int32) => Convert.ToInt32(value),
                                nameof(Int64) => Convert.ToInt64(value),
                                nameof(Double) => Convert.ToDouble(value),
                                nameof(Boolean) => Convert.ToBoolean(value),
                                nameof(DateTime) => DateTimeOffset.FromUnixTimeSeconds(Convert.ToInt64(value)).DateTime,
                                _ => value
                            };

                            prop.SetValue(instance, convertedValue);
                        }
                    }
                    catch (Exception ex)
                    {
                        GD.PrintErr($"Failed to map property {prop.Name}: {ex.Message}");
                    }

                    break;
                }
            }
        }

        return instance;
    }

    /// <summary>
    /// PascalCase 鈫?snake_case
    /// </summary>
    private string ToSnakeCase(string input)
    {
        return string.Concat(input.Select((x, i) =>
            i > 0 && char.IsUpper(x) ? "_" + x.ToString() : x.ToString()
        )).ToLower();
    }
}
```

---

## 棰嗗煙妯″瀷 (C# DTOs)

### 鐢ㄦ埛瀹炰綋

```csharp
// Game.Core/Domain/Entities/User.cs

namespace Game.Core.Domain.Entities;

public class User
{
    public string Id { get; set; } = string.Empty;
    public string Username { get; set; } = string.Empty;
    public long CreatedAt { get; set; }
    public long? LastLogin { get; set; }

    public User() { }

    public User(string username)
    {
        Id = Guid.NewGuid().ToString();
        Username = username;
        CreatedAt = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
    }
}
```

### 瀛樻。瀹炰綋

```csharp
// Game.Core/Domain/Entities/SaveGame.cs

namespace Game.Core.Domain.Entities;

public class SaveGame
{
    public string Id { get; set; } = string.Empty;
    public string UserId { get; set; } = string.Empty;
    public int SlotNumber { get; set; }
    public string Data { get; set; } = string.Empty; // JSON
    public long CreatedAt { get; set; }
    public long UpdatedAt { get; set; }

    public SaveGame() { }

    public SaveGame(string userId, int slotNumber, string data)
    {
        Id = Guid.NewGuid().ToString();
        UserId = userId;
        SlotNumber = slotNumber;
        Data = data;
        CreatedAt = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        UpdatedAt = CreatedAt;
    }
}
```

---

## 浠撳偍灞傚疄鐜?
### 鐢ㄦ埛浠撳偍鎺ュ彛

```csharp
// Game.Core/Domain/Repositories/IUserRepository.cs

namespace Game.Core.Domain.Repositories;

public interface IUserRepository
{
    User? GetById(string id);
    User? GetByUsername(string username);
    List<User> GetAll();
    void Create(User user);
    void Update(User user);
    void Delete(string id);
}
```

### 鐢ㄦ埛浠撳偍瀹炵幇

```csharp
// Game.Godot/Repositories/UserRepository.cs

using Game.Core.Domain.Entities;
using Game.Core.Domain.Repositories;
using Game.Core.Ports;

namespace Game.Godot.Repositories;

public class UserRepository : IUserRepository
{
    private readonly IDataStore _dataStore;

    public UserRepository(IDataStore dataStore)
    {
        _dataStore = dataStore ?? throw new ArgumentNullException(nameof(dataStore));
    }

    public User? GetById(string id)
    {
        const string sql = "SELECT id, username, created_at, last_login FROM users WHERE id = @0";
        return _dataStore.QuerySingle<User>(sql, id);
    }

    public User? GetByUsername(string username)
    {
        const string sql = "SELECT id, username, created_at, last_login FROM users WHERE username = @0";
        return _dataStore.QuerySingle<User>(sql, username);
    }

    public List<User> GetAll()
    {
        const string sql = "SELECT id, username, created_at, last_login FROM users ORDER BY created_at DESC";
        return _dataStore.Query<User>(sql);
    }

    public void Create(User user)
    {
        const string sql = @"
            INSERT INTO users (id, username, created_at, last_login)
            VALUES (@0, @1, @2, @3)";

        _dataStore.Execute(sql, user.Id, user.Username, user.CreatedAt, user.LastLogin ?? (object)DBNull.Value);
    }

    public void Update(User user)
    {
        const string sql = @"
            UPDATE users
            SET username = @0, last_login = @1
            WHERE id = @2";

        _dataStore.Execute(sql, user.Username, user.LastLogin ?? (object)DBNull.Value, user.Id);
    }

    public void Delete(string id)
    {
        const string sql = "DELETE FROM users WHERE id = @0";
        _dataStore.Execute(sql, id);
    }
}
```

---

## 鏁版嵁搴撹縼绉荤郴缁?
### 杩佺Щ绠＄悊鍣?
```csharp
// Game.Core/Infrastructure/DatabaseMigration.cs

using Game.Core.Ports;

namespace Game.Core.Infrastructure;

public class DatabaseMigration
{
    private readonly IDataStore _dataStore;
    private readonly ILogger _logger;

    public DatabaseMigration(IDataStore dataStore, ILogger logger)
    {
        _dataStore = dataStore;
        _logger = logger;
    }

    /// <summary>
    /// 杩愯鎵€鏈夋湭搴旂敤鐨勮縼绉?    /// </summary>
    public void Migrate()
    {
        EnsureSchemaVersionTable();

        int currentVersion = GetCurrentVersion();
        var migrations = GetMigrations();

        foreach (var migration in migrations.Where(m => m.Version > currentVersion))
        {
            _logger.LogInfo($"Applying migration {migration.Version}: {migration.Description}");

            try
            {
                _dataStore.BeginTransaction();
                migration.Up(_dataStore);
                RecordMigration(migration);
                _dataStore.CommitTransaction();

                _logger.LogInfo($"Migration {migration.Version} applied successfully");
            }
            catch (Exception ex)
            {
                _dataStore.RollbackTransaction();
                _logger.LogError($"Migration {migration.Version} failed", ex);
                throw;
            }
        }
    }

    private void EnsureSchemaVersionTable()
    {
        const string sql = @"
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at INTEGER NOT NULL,
                description TEXT
            )";

        _dataStore.Execute(sql);
    }

    private int GetCurrentVersion()
    {
        const string sql = "SELECT MAX(version) as version FROM schema_version";

        try
        {
            var result = _dataStore.QuerySingle<VersionRow>(sql);
            return result?.Version ?? 0;
        }
        catch
        {
            return 0;
        }
    }

    private void RecordMigration(Migration migration)
    {
        const string sql = @"
            INSERT INTO schema_version (version, applied_at, description)
            VALUES (@0, @1, @2)";

        _dataStore.Execute(sql, migration.Version, DateTimeOffset.UtcNow.ToUnixTimeSeconds(), migration.Description);
    }

    private List<Migration> GetMigrations()
    {
        return new List<Migration>
        {
            new Migration001_InitialSchema(),
            new Migration002_AddAchievements(),
            new Migration003_AddSettings()
        };
    }

    private class VersionRow
    {
        public int Version { get; set; }
    }
}
```

### 杩佺Щ鍩虹被

```csharp
// Game.Core/Infrastructure/Migration.cs

using Game.Core.Ports;

namespace Game.Core.Infrastructure;

public abstract class Migration
{
    public abstract int Version { get; }
    public abstract string Description { get; }
    public abstract void Up(IDataStore dataStore);
    public abstract void Down(IDataStore dataStore);
}
```

### 鍏蜂綋杩佺Щ绀轰緥

```csharp
// Game.Core/Infrastructure/Migrations/Migration001_InitialSchema.cs

using Game.Core.Ports;

namespace Game.Core.Infrastructure.Migrations;

public class Migration001_InitialSchema : Migration
{
    public override int Version => 1;
    public override string Description => "Initial database schema";

    public override void Up(IDataStore dataStore)
    {
        // Users 琛?        dataStore.Execute(@"
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                created_at INTEGER NOT NULL,
                last_login INTEGER
            )");

        // Saves 琛?        dataStore.Execute(@"
            CREATE TABLE saves (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                slot_number INTEGER NOT NULL,
                data TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, slot_number)
            )");

        // Statistics 琛?        dataStore.Execute(@"
            CREATE TABLE statistics (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                stat_key TEXT NOT NULL,
                stat_value REAL NOT NULL,
                recorded_at INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )");

        // 绱㈠紩
        dataStore.Execute("CREATE INDEX idx_saves_user_id ON saves(user_id)");
        dataStore.Execute("CREATE INDEX idx_statistics_user_id ON statistics(user_id)");
    }

    public override void Down(IDataStore dataStore)
    {
        dataStore.Execute("DROP TABLE IF EXISTS statistics");
        dataStore.Execute("DROP TABLE IF EXISTS saves");
        dataStore.Execute("DROP TABLE IF EXISTS users");
    }
}
```

```csharp
// Game.Core/Infrastructure/Migrations/Migration002_AddAchievements.cs

using Game.Core.Ports;

namespace Game.Core.Infrastructure.Migrations;

public class Migration002_AddAchievements : Migration
{
    public override int Version => 2;
    public override string Description => "Add achievements system";

    public override void Up(IDataStore dataStore)
    {
        dataStore.Execute(@"
            CREATE TABLE achievements (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                achievement_key TEXT NOT NULL,
                unlocked_at INTEGER NOT NULL,
                progress REAL DEFAULT 0.0,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, achievement_key)
            )");

        dataStore.Execute("CREATE INDEX idx_achievements_user_id ON achievements(user_id)");
    }

    public override void Down(IDataStore dataStore)
    {
        dataStore.Execute("DROP TABLE IF EXISTS achievements");
    }
}
```

---

## 鍚姩鏃跺垵濮嬪寲

### ServiceLocator 闆嗘垚

```csharp
// Game.Godot/Autoloads/ServiceLocator.cs (鎵╁睍)

public partial class ServiceLocator : Node
{
    public static ServiceLocator Instance { get; private set; } = null!;

    public IDataStore DataStore { get; private set; } = null!;
    public IUserRepository UserRepository { get; private set; } = null!;
    // ... 鍏朵粬鏈嶅姟

    public override void _Ready()
    {
        Instance = this;

        // 鍒濆鍖栨暟鎹瓨鍌?        DataStore = new SqliteDataStore();
        DataStore.Open("user://game.db");

        // 杩愯杩佺Щ
        var logger = new GodotLogger("Migration");
        var migration = new DatabaseMigration(DataStore, logger);
        migration.Migrate();

        // 鍒濆鍖栦粨鍌?        UserRepository = new UserRepository(DataStore);

        GD.Print("Database initialized and migrated successfully");
    }

    public override void _ExitTree()
    {
        DataStore?.Close();
    }
}
```

---

## 娴嬭瘯绛栫暐

### 鍗曞厓娴嬭瘯锛堝唴瀛?SQLite锛?
```csharp
// Game.Core.Tests/Infrastructure/UserRepositoryTests.cs

using FluentAssertions;
using Game.Core.Domain.Entities;
using Game.Core.Tests.Fakes;
using Game.Godot.Repositories;
using Xunit;

namespace Game.Core.Tests.Infrastructure;

public class UserRepositoryTests : IDisposable
{
    private readonly FakeDataStore _dataStore;
    private readonly UserRepository _repository;

    public UserRepositoryTests()
    {
        _dataStore = new FakeDataStore();
        _dataStore.Open(":memory:");

        // 鍒濆鍖?Schema
        _dataStore.Execute(@"
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                created_at INTEGER NOT NULL,
                last_login INTEGER
            )");

        _repository = new UserRepository(_dataStore);
    }

    [Fact]
    public void Create_ShouldAddUserToDatabase()
    {
        // Arrange
        var user = new User("test_user");

        // Act
        _repository.Create(user);

        // Assert
        var retrieved = _repository.GetById(user.Id);
        retrieved.Should().NotBeNull();
        retrieved!.Username.Should().Be("test_user");
    }

    [Fact]
    public void GetByUsername_ShouldReturnCorrectUser()
    {
        // Arrange
        var user = new User("alice");
        _repository.Create(user);

        // Act
        var retrieved = _repository.GetByUsername("alice");

        // Assert
        retrieved.Should().NotBeNull();
        retrieved!.Id.Should().Be(user.Id);
    }

    [Fact]
    public void Update_ShouldModifyExistingUser()
    {
        // Arrange
        var user = new User("bob");
        _repository.Create(user);

        // Act
        user.LastLogin = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        _repository.Update(user);

        // Assert
        var retrieved = _repository.GetById(user.Id);
        retrieved!.LastLogin.Should().Be(user.LastLogin);
    }

    [Fact]
    public void Delete_ShouldRemoveUser()
    {
        // Arrange
        var user = new User("charlie");
        _repository.Create(user);

        // Act
        _repository.Delete(user.Id);

        // Assert
        var retrieved = _repository.GetById(user.Id);
        retrieved.Should().BeNull();
    }

    public void Dispose()
    {
        _dataStore.Close();
    }
}
```

### 杩佺Щ娴嬭瘯

```csharp
// Game.Core.Tests/Infrastructure/DatabaseMigrationTests.cs

using FluentAssertions;
using Game.Core.Infrastructure;
using Game.Core.Tests.Fakes;
using Xunit;

namespace Game.Core.Tests.Infrastructure;

public class DatabaseMigrationTests : IDisposable
{
    private readonly FakeDataStore _dataStore;
    private readonly FakeLogger _logger;
    private readonly DatabaseMigration _migration;

    public DatabaseMigrationTests()
    {
        _dataStore = new FakeDataStore();
        _dataStore.Open(":memory:");

        _logger = new FakeLogger();
        _migration = new DatabaseMigration(_dataStore, _logger);
    }

    [Fact]
    public void Migrate_ShouldApplyAllMigrations()
    {
        // Act
        _migration.Migrate();

        // Assert
        var tables = _dataStore.Query<TableInfo>("SELECT name FROM sqlite_master WHERE type='table'");
        var tableNames = tables.Select(t => t.Name).ToList();

        tableNames.Should().Contain("users");
        tableNames.Should().Contain("saves");
        tableNames.Should().Contain("achievements");
        tableNames.Should().Contain("schema_version");
    }

    [Fact]
    public void Migrate_ShouldNotReapplyMigrations()
    {
        // Arrange
        _migration.Migrate();

        // Act
        _migration.Migrate();

        // Assert锛堟病鏈夋姏鍑哄紓甯革級
        var version = _dataStore.QuerySingle<VersionRow>("SELECT MAX(version) as version FROM schema_version");
        version!.Version.Should().BeGreaterThan(0);
    }

    public void Dispose()
    {
        _dataStore.Close();
    }

    private class TableInfo
    {
        public string Name { get; set; } = string.Empty;
    }

    private class VersionRow
    {
        public int Version { get; set; }
    }
}
```

---

## 鏁版嵁杩佺Щ鑴氭湰

### 浠?vitegame 杩佺Щ鏁版嵁

```csharp
// scripts/MigrateData.cs (CLI 宸ュ叿)

using Game.Core.Ports;
using Game.Godot.Adapters;

public class DataMigrationTool
{
    public static void Main(string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: MigrateData <source.db> <target.db>");
            return;
        }

        string sourcePath = args[0];
        string targetPath = args[1];

        Console.WriteLine($"Migrating data from {sourcePath} to {targetPath}...");

        // 鎵撳紑婧愭暟鎹簱锛堝亣璁句娇鐢?System.Data.SQLite锛?        using var sourceConn = new System.Data.SQLite.SQLiteConnection($"Data Source={sourcePath}");
        sourceConn.Open();

        // 鎵撳紑鐩爣鏁版嵁搴擄紙Godot SQLite 閫傞厤鍣級
        var targetStore = new SqliteDataStore();
        targetStore.Open(targetPath);

        // 杩佺Щ鐢ㄦ埛
        MigrateUsers(sourceConn, targetStore);

        // 杩佺Щ瀛樻。
        MigrateSaves(sourceConn, targetStore);

        // 杩佺Щ缁熻鏁版嵁
        MigrateStatistics(sourceConn, targetStore);

        Console.WriteLine("Migration completed successfully!");
    }

    private static void MigrateUsers(System.Data.SQLite.SQLiteConnection source, IDataStore target)
    {
        using var cmd = new System.Data.SQLite.SQLiteCommand("SELECT id, username, created_at, last_login FROM users", source);
        using var reader = cmd.ExecuteReader();

        int count = 0;
        while (reader.Read())
        {
            string id = reader.GetString(0);
            string username = reader.GetString(1);
            long createdAt = reader.GetInt64(2);
            long? lastLogin = reader.IsDBNull(3) ? null : reader.GetInt64(3);

            target.Execute(
                "INSERT INTO users (id, username, created_at, last_login) VALUES (@0, @1, @2, @3)",
                id, username, createdAt, lastLogin ?? (object)DBNull.Value
            );

            count++;
        }

        Console.WriteLine($"Migrated {count} users");
    }

    private static void MigrateSaves(System.Data.SQLite.SQLiteConnection source, IDataStore target)
    {
        using var cmd = new System.Data.SQLite.SQLiteCommand("SELECT id, user_id, slot_number, data, created_at, updated_at FROM saves", source);
        using var reader = cmd.ExecuteReader();

        int count = 0;
        while (reader.Read())
        {
            string id = reader.GetString(0);
            string userId = reader.GetString(1);
            int slotNumber = reader.GetInt32(2);
            string data = reader.GetString(3);
            long createdAt = reader.GetInt64(4);
            long updatedAt = reader.GetInt64(5);

            target.Execute(
                "INSERT INTO saves (id, user_id, slot_number, data, created_at, updated_at) VALUES (@0, @1, @2, @3, @4, @5)",
                id, userId, slotNumber, data, createdAt, updatedAt
            );

            count++;
        }

        Console.WriteLine($"Migrated {count} save files");
    }

    private static void MigrateStatistics(System.Data.SQLite.SQLiteConnection source, IDataStore target)
    {
        using var cmd = new System.Data.SQLite.SQLiteCommand("SELECT id, user_id, stat_key, stat_value, recorded_at FROM statistics", source);
        using var reader = cmd.ExecuteReader();

        int count = 0;
        while (reader.Read())
        {
            string id = reader.GetString(0);
            string userId = reader.GetString(1);
            string statKey = reader.GetString(2);
            double statValue = reader.GetDouble(3);
            long recordedAt = reader.GetInt64(4);

            target.Execute(
                "INSERT INTO statistics (id, user_id, stat_key, stat_value, recorded_at) VALUES (@0, @1, @2, @3, @4)",
                id, userId, statKey, statValue, recordedAt
            );

            count++;
        }

        Console.WriteLine($"Migrated {count} statistics records");
    }
}
```

---

## CI 闆嗘垚

### 鏁版嵁搴撴祴璇?(GitHub Actions)

```yaml
# .github/workflows/tests.yml

name: Tests

on: [push, pull_request]

jobs:
  database-tests:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup .NET 8
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '8.0.x'

      - name: Restore dependencies
        run: dotnet restore Game.Core.Tests/Game.Core.Tests.csproj

      - name: Run database unit tests
        run: |
          dotnet test Game.Core.Tests/Game.Core.Tests.csproj `
            --filter "FullyQualifiedName~Infrastructure" `
            --no-restore `
            --verbosity normal `
            --collect:"XPlat Code Coverage"

      - name: Check migration integrity
        run: |
          # 楠岃瘉鎵€鏈夎縼绉婚兘鏈夊搴旂殑娴嬭瘯
          $migrations = Get-ChildItem -Path Game.Core/Infrastructure/Migrations/*.cs
          foreach ($migration in $migrations) {
            $testFile = "Game.Core.Tests/Infrastructure/" + $migration.BaseName + "Tests.cs"
            if (-not (Test-Path $testFile)) {
              Write-Error "Missing test for migration: $($migration.Name)"
              exit 1
            }
          }
```

---

## 瀹屾垚鏍囧噯

- [ ] IDataStore 閫傞厤鍣ㄥ畬鏁村疄鐜帮紙浜嬪姟鏀寔锛?- [ ] User/SaveGame/Statistics 瀹炰綋鍜屼粨鍌ㄥ畬鎴?- [ ] 鏁版嵁搴撹縼绉荤郴缁熷彲杩愯锛圡igration001-003锛?- [ ] 鎵€鏈変粨鍌ㄩ€氳繃鍗曞厓娴嬭瘯锛堝唴瀛?SQLite锛?- [ ] 杩佺Щ绯荤粺閫氳繃闆嗘垚娴嬭瘯
- [ ] 鏁版嵁杩佺Щ鑴氭湰鍙粠 vitegame 瀵煎叆鏁版嵁
- [ ] ServiceLocator 闆嗘垚鏁版嵁搴撳垵濮嬪寲
- [ ] CI 绠￠亾鍖呭惈鏁版嵁搴撴祴璇曞拰杩佺Щ瀹屾暣鎬ф鏌?
---

## 鎬ц兘浼樺寲寤鸿

1. **杩炴帴姹?*锛欸odot SQLite 涓嶆敮鎸佽繛鎺ユ睜锛岃€冭檻浣跨敤鍗曚緥妯″紡
2. **鎵归噺鎻掑叆**锛氫娇鐢ㄤ簨鍔″寘瑁瑰鏉?INSERT 璇彞
3. **绱㈠紩绛栫暐**锛氫负楂橀鏌ヨ瀛楁锛坲ser_id, username锛夊缓绔嬬储寮?4. **WAL 妯″紡**锛歚PRAGMA journal_mode = WAL` 鎻愬崌骞跺彂鍐欏叆
5. **鏌ヨ浼樺寲**锛氶伩鍏?SELECT \*锛屼粎鏌ヨ闇€瑕佺殑瀛楁

---

## 涓嬩竴姝?
瀹屾垚鏈樁娈靛悗锛岀户缁細

鉃★笍 [Phase-7-UI-Migration.md](Phase-7-UI-Migration.md) 鈥?React 鈫?Godot Control 杩佺Щ

### Autoload 与仓储使用 / Autoload & Repositories

- Autoload: `project.godot` 已注册 `SqlDb`，入口 `Main.gd` 调用 `SqlDb.TryOpen("user://data/game.db")`（首次运行自动执行 `scripts/db/schema.sql`）。
- C# 仓储：见 `Game.Core/Repositories/*.cs` 与 `Game.Godot/Adapters/Db/*.cs`，通过 `ISqlDatabase` 注入使用。
- 示例（C#）：
```csharp
var db = GetNode<Game.Godot.Adapters.SqliteDataStore>("/root/SqlDb");
var users = new Game.Godot.Adapters.Db.UserRepository(db);
await users.UpsertAsync(new Game.Core.Domain.Entities.User { Username = "alice" });
var u = await users.FindByUsernameAsync("alice");
```


### Inventory 持久化（过渡实现）

- 使用 saves 表 `slot_number=90` 存储 inventory 快照（JSON: `{ items: { id: qty } }`），用户为 `default`。
- 仓储：`SqlInventoryRepository`（Game.Godot/Adapters/Db/SqlInventoryRepository.cs），接口对齐 `IInventoryRepository`。
- UI 面板仍保留 JSON 存储作为演示；仓储桥接 `InventoryRepoBridge` 用于 GdUnit 测试与后续 UI 接入。

