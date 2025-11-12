# Phase 10: Jest 鈫?xUnit 鍗曞厓娴嬭瘯杩佺Щ

> 鐘舵€? 璁捐闃舵
> 棰勪及宸ユ椂: 8-12 澶?
> 椋庨櫓绛夌骇: 涓?
> 鍓嶇疆鏉′欢: Phase 1-9 瀹屾垚

---

## 鐩爣

灏?vitegame 鐨?Jest + TypeScript 鍗曞厓娴嬭瘯杩佺Щ鍒?godotgame 鐨?xUnit + C# 鍗曞厓娴嬭瘯锛屽缓绔嬬被鍨嬪畨鍏ㄧ殑娴嬭瘯濂椾欢涓?AI-first 瑕嗙洊鐜囬棬绂併€?

---

## 鎶€鏈爤瀵规瘮

| 鍔熻兘 | vitegame (Node.js) | godotgame (.NET 8) |
|-----|-------------------|-------------------|
| 娴嬭瘯妗嗘灦 | Jest 29 | xUnit 2.x |
| 鏂█搴?| Jest expect() | FluentAssertions |
| 娴嬭瘯闅旂 | describe/it 宓屽 | [Fact]/[Theory] 鎵佸钩 |
| 娴嬭瘯鍙?| jest.mock / jest.fn | Moq / NSubstitute / Fakes |
| 鍙傛暟鍖栨祴璇?| test.each() | [Theory] + [InlineData] |
| 鐢熷懡鍛ㄦ湡 | beforeEach/afterEach | Constructor/IDisposable |
| 瑕嗙洊鐜?| c8 / istanbul | coverlet |
| 杩愯鍣?| jest CLI | dotnet test |
| CI 闆嗘垚 | npm test | dotnet test --logger trx |

---

## Jest 娴嬭瘯缁撴瀯鍥為【

### 鍏稿瀷 Jest 娴嬭瘯 (vitegame)

```typescript
// src/domain/entities/Player.test.ts

import { Player } from './Player';
import { FakeTime } from '@/tests/fakes/FakeTime';

describe('Player', () => {
  let player: Player;
  let fakeTime: FakeTime;

  beforeEach(() => {
    fakeTime = new FakeTime();
    player = new Player(fakeTime);
  });

  describe('constructor', () => {
    it('should initialize with default health', () => {
      expect(player.health).toBe(100);
      expect(player.maxHealth).toBe(100);
    });

    it('should initialize at position (0, 0)', () => {
      expect(player.position).toEqual({ x: 0, y: 0 });
    });
  });

  describe('takeDamage', () => {
    it('should reduce health by damage amount', () => {
      player.takeDamage(30);
      expect(player.health).toBe(70);
    });

    it('should not reduce health below zero', () => {
      player.takeDamage(150);
      expect(player.health).toBe(0);
    });

    it('should emit damaged event', () => {
      const mockHandler = jest.fn();
      player.on('damaged', mockHandler);

      player.takeDamage(20);

      expect(mockHandler).toHaveBeenCalledWith({
        damage: 20,
        remainingHealth: 80,
      });
    });
  });

  describe('move', () => {
    it('should update position', () => {
      player.move(10, 15);
      expect(player.position).toEqual({ x: 10, y: 15 });
    });

    it('should clamp position to bounds', () => {
      player.move(1000, 2000);
      expect(player.position).toEqual({ x: 800, y: 600 });
    });
  });

  describe('heal', () => {
    beforeEach(() => {
      player.takeDamage(40);
    });

    it('should increase health', () => {
      player.heal(20);
      expect(player.health).toBe(80);
    });

    it('should not exceed max health', () => {
      player.heal(100);
      expect(player.health).toBe(100);
    });
  });
});
```

---

## xUnit 娴嬭瘯缁撴瀯

### 绛変环 xUnit 娴嬭瘯 (godotgame)

```csharp
// Game.Core.Tests/Domain/Entities/PlayerTests.cs

using FluentAssertions;
using Game.Core.Domain.Entities;
using Game.Core.Tests.Fakes;
using Xunit;

namespace Game.Core.Tests.Domain.Entities;

/// <summary>
/// Player 瀹炰綋鍗曞厓娴嬭瘯
/// </summary>
public class PlayerTests : IDisposable
{
    private readonly Player _player;
    private readonly FakeTime _fakeTime;

    // Constructor = beforeEach
    public PlayerTests()
    {
        _fakeTime = new FakeTime();
        _player = new Player(_fakeTime);
    }

    // IDisposable = afterEach
    public void Dispose()
    {
        // Cleanup resources if needed
    }

    [Fact]
    public void Constructor_ShouldInitializeWithDefaultHealth()
    {
        // Arrange & Act (done in constructor)

        // Assert
        _player.Health.Should().Be(100);
        _player.MaxHealth.Should().Be(100);
    }

    [Fact]
    public void Constructor_ShouldInitializeAtOrigin()
    {
        // Arrange & Act (done in constructor)

        // Assert
        _player.Position.X.Should().Be(0);
        _player.Position.Y.Should().Be(0);
    }

    [Fact]
    public void TakeDamage_ShouldReduceHealthByDamageAmount()
    {
        // Arrange
        const int damage = 30;

        // Act
        _player.TakeDamage(damage);

        // Assert
        _player.Health.Should().Be(70);
    }

    [Fact]
    public void TakeDamage_ShouldNotReduceHealthBelowZero()
    {
        // Arrange
        const int damage = 150;

        // Act
        _player.TakeDamage(damage);

        // Assert
        _player.Health.Should().Be(0);
    }

    [Fact]
    public void TakeDamage_ShouldEmitDamagedEvent()
    {
        // Arrange
        int receivedDamage = 0;
        int receivedRemainingHealth = 0;

        _player.Damaged += (damage, remainingHealth) =>
        {
            receivedDamage = damage;
            receivedRemainingHealth = remainingHealth;
        };

        // Act
        _player.TakeDamage(20);

        // Assert
        receivedDamage.Should().Be(20);
        receivedRemainingHealth.Should().Be(80);
    }

    [Fact]
    public void Move_ShouldUpdatePosition()
    {
        // Arrange
        const double x = 10;
        const double y = 15;

        // Act
        _player.Move(x, y);

        // Assert
        _player.Position.X.Should().Be(10);
        _player.Position.Y.Should().Be(15);
    }

    [Fact]
    public void Move_ShouldClampPositionToBounds()
    {
        // Arrange
        const double x = 1000;
        const double y = 2000;

        // Act
        _player.Move(x, y);

        // Assert
        _player.Position.X.Should().Be(800);
        _player.Position.Y.Should().Be(600);
    }

    [Fact]
    public void Heal_ShouldIncreaseHealth()
    {
        // Arrange
        _player.TakeDamage(40);
        const int healAmount = 20;

        // Act
        _player.Heal(healAmount);

        // Assert
        _player.Health.Should().Be(80);
    }

    [Fact]
    public void Heal_ShouldNotExceedMaxHealth()
    {
        // Arrange
        _player.TakeDamage(40);
        const int healAmount = 100;

        // Act
        _player.Heal(healAmount);

        // Assert
        _player.Health.Should().Be(100);
    }
}
```

---

## 鏍稿績杩佺Щ妯″紡

### 1. describe/it 鈫?[Fact]/[Theory]

**Jest (宓屽缁撴瀯)**:

```typescript
describe('Player', () => {
  describe('takeDamage', () => {
    it('should reduce health', () => {
      // test
    });

    it('should not go below zero', () => {
      // test
    });
  });
});
```

**xUnit (鎵佸钩缁撴瀯 + 鍛藉悕绾﹀畾)**:

```csharp
public class PlayerTests
{
    [Fact]
    public void TakeDamage_ShouldReduceHealth()
    {
        // test
    }

    [Fact]
    public void TakeDamage_ShouldNotGoBelowZero()
    {
        // test
    }
}
```

**鍛藉悕绾﹀畾**:
- **鏍煎紡**: `MethodName_Scenario_ExpectedBehavior`
- **绀轰緥**:
  - `TakeDamage_WithNegativeAmount_ThrowsArgumentException`
  - `Constructor_WithNullTime_ThrowsArgumentNullException`
  - `Move_WithValidCoordinates_UpdatesPosition`

---

### 2. expect() 鈫?FluentAssertions

**Jest 鏂█ 鈫?FluentAssertions 鏄犲皠琛?*:

| Jest | FluentAssertions | 璇存槑 |
|------|-----------------|------|
| `expect(x).toBe(y)` | `x.Should().Be(y)` | 鍊肩浉绛?|
| `expect(x).toEqual(y)` | `x.Should().BeEquivalentTo(y)` | 娣卞害鐩哥瓑 |
| `expect(x).toBeNull()` | `x.Should().BeNull()` | Null 妫€鏌?|
| `expect(x).toBeDefined()` | `x.Should().NotBeNull()` | 闈?Null |
| `expect(x).toBeTruthy()` | `x.Should().BeTrue()` | 鐪熷€?|
| `expect(x).toBeGreaterThan(y)` | `x.Should().BeGreaterThan(y)` | 澶т簬 |
| `expect(x).toContain(y)` | `x.Should().Contain(y)` | 鍖呭惈 |
| `expect(arr).toHaveLength(n)` | `arr.Should().HaveCount(n)` | 闀垮害/鏁伴噺 |
| `expect(fn).toThrow()` | `fn.Should().Throw<Exception>()` | 寮傚父 |
| `expect(mock).toHaveBeenCalled()` | `mock.Verify(m => m.Method(), Times.Once)` | Mock 璋冪敤 |

**绀轰緥杩佺Щ**:

```typescript
// Jest
expect(player.health).toBe(100);
expect(player.position).toEqual({ x: 0, y: 0 });
expect(player.items).toHaveLength(5);
expect(() => player.takeDamage(-10)).toThrow('Damage must be positive');
```

```csharp
// xUnit + FluentAssertions
player.Health.Should().Be(100);
player.Position.Should().BeEquivalentTo(new Vector2D(0, 0));
player.Items.Should().HaveCount(5);
Action act = () => player.TakeDamage(-10);
act.Should().Throw<ArgumentException>()
   .WithMessage("Damage must be positive*");
```

---

### 3. beforeEach/afterEach 鈫?Constructor/IDisposable

**Jest 鐢熷懡鍛ㄦ湡**:

```typescript
describe('Player', () => {
  let player: Player;
  let fakeTime: FakeTime;

  beforeEach(() => {
    fakeTime = new FakeTime();
    player = new Player(fakeTime);
  });

  afterEach(() => {
    // cleanup
  });

  it('test 1', () => { /* ... */ });
  it('test 2', () => { /* ... */ });
});
```

**xUnit 鐢熷懡鍛ㄦ湡**:

```csharp
public class PlayerTests : IDisposable
{
    private readonly Player _player;
    private readonly FakeTime _fakeTime;

    // beforeEach
    public PlayerTests()
    {
        _fakeTime = new FakeTime();
        _player = new Player(_fakeTime);
    }

    // afterEach
    public void Dispose()
    {
        // Cleanup
    }

    [Fact]
    public void Test1() { /* ... */ }

    [Fact]
    public void Test2() { /* ... */ }
}
```

**Class Fixtures (鍏变韩涓婁笅鏂?**:

```csharp
// 褰撻渶瑕佸湪澶氫釜娴嬭瘯闂村叡浜槀璐电殑鍒濆鍖栵紙濡傛暟鎹簱杩炴帴锛?
public class DatabaseFixture : IDisposable
{
    public SqliteDataStore DataStore { get; }

    public DatabaseFixture()
    {
        DataStore = new SqliteDataStore();
        DataStore.Open(":memory:");
        // Initialize schema
    }

    public void Dispose()
    {
        DataStore.Close();
    }
}

public class UserRepositoryTests : IClassFixture<DatabaseFixture>
{
    private readonly DatabaseFixture _fixture;

    public UserRepositoryTests(DatabaseFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public void GetById_ShouldReturnUser()
    {
        // Use _fixture.DataStore
    }
}
```

---

### 4. test.each() 鈫?[Theory] + [InlineData]

**Jest 鍙傛暟鍖栨祴璇?*:

```typescript
describe('Player.takeDamage', () => {
  test.each([
    [10, 90],
    [50, 50],
    [100, 0],
    [150, 0],
  ])('when damage is %i, health should be %i', (damage, expectedHealth) => {
    player.takeDamage(damage);
    expect(player.health).toBe(expectedHealth);
  });
});
```

**xUnit 鍙傛暟鍖栨祴璇?*:

```csharp
public class PlayerTests
{
    [Theory]
    [InlineData(10, 90)]
    [InlineData(50, 50)]
    [InlineData(100, 0)]
    [InlineData(150, 0)]
    public void TakeDamage_ShouldReduceHealthCorrectly(int damage, int expectedHealth)
    {
        // Arrange
        var fakeTime = new FakeTime();
        var player = new Player(fakeTime);

        // Act
        player.TakeDamage(damage);

        // Assert
        player.Health.Should().Be(expectedHealth);
    }
}
```

**MemberData (澶嶆潅鏁版嵁)**:

```csharp
public class PlayerTests
{
    public static IEnumerable<object[]> DamageTestData =>
        new List<object[]>
        {
            new object[] { 10, 90, "minor damage" },
            new object[] { 50, 50, "moderate damage" },
            new object[] { 100, 0, "lethal damage" },
            new object[] { 150, 0, "overkill damage" },
        };

    [Theory]
    [MemberData(nameof(DamageTestData))]
    public void TakeDamage_VariousScenarios(int damage, int expectedHealth, string scenario)
    {
        // Arrange
        var player = new Player(new FakeTime());

        // Act
        player.TakeDamage(damage);

        // Assert
        player.Health.Should().Be(expectedHealth, because: scenario);
    }
}
```

---

### 5. jest.mock 鈫?Moq / NSubstitute / Fakes

**Jest Mock**:

```typescript
// Jest
const mockTime = {
  getTimestamp: jest.fn(() => 1234567890),
  getDeltaTime: jest.fn(() => 0.016),
  getElapsedTime: jest.fn(() => 60.0),
};

const player = new Player(mockTime);
player.update();

expect(mockTime.getDeltaTime).toHaveBeenCalled();
```

**閫夋嫨 1: Moq (楠岃瘉琛屼负)**:

```csharp
using Moq;

// Moq
var mockTime = new Mock<ITime>();
mockTime.Setup(t => t.GetTimestamp()).Returns(1234567890);
mockTime.Setup(t => t.GetDeltaTime()).Returns(0.016);
mockTime.Setup(t => t.GetElapsedTime()).Returns(60.0);

var player = new Player(mockTime.Object);
player.Update();

mockTime.Verify(t => t.GetDeltaTime(), Times.Once);
```

**閫夋嫨 2: NSubstitute (鏇寸畝娲?**:

```csharp
using NSubstitute;

// NSubstitute
var mockTime = Substitute.For<ITime>();
mockTime.GetTimestamp().Returns(1234567890);
mockTime.GetDeltaTime().Returns(0.016);
mockTime.GetElapsedTime().Returns(60.0);

var player = new Player(mockTime);
player.Update();

mockTime.Received(1).GetDeltaTime();
```

**閫夋嫨 3: Fake 瀹炵幇 (鎺ㄨ崘鐢ㄤ簬绠€鍗曞満鏅?**:

```csharp
// Game.Core.Tests/Fakes/FakeTime.cs

public class FakeTime : ITime
{
    private double _timestamp = 1234567890;
    private double _deltaTime = 0.016;
    private double _elapsedTime = 0;

    public double GetTimestamp() => _timestamp;
    public double GetDeltaTime() => _deltaTime;
    public double GetElapsedTime() => _elapsedTime;

    public void SetTimestamp(double value) => _timestamp = value;
    public void SetDeltaTime(double value) => _deltaTime = value;
    public void AdvanceTime(double seconds) => _elapsedTime += seconds;
}

// Usage
var fakeTime = new FakeTime();
fakeTime.SetDeltaTime(0.032); // Simulate slow frame
var player = new Player(fakeTime);
player.Update();
```

**Fake vs Mock 閫夋嫨鍘熷垯**:

| 鍦烘櫙 | 浣跨敤 Fake | 浣跨敤 Mock (Moq/NSubstitute) |
|-----|----------|---------------------------|
| 绠€鍗曠姸鎬佸璞?| [OK] FakeTime, FakeInput | 鍚?|
| 闇€瑕侀獙璇佽皟鐢ㄦ鏁?椤哄簭 | 鍚?| [OK] Mock |
| 澶嶆潅渚濊禆/澶氭柟娉曡皟鐢?| 鍚?| [OK] Mock |
| 璺ㄦ祴璇曞鐢?| [OK] 鍏变韩 Fake | 鍚︼紙姣忔祴璇曞垱寤?Mock锛?|
| 鍙鎬т紭鍏?| [OK] 鏇寸洿瑙?| [璀﹀憡] 瀛︿範鏇茬嚎 |

---

## AAA 妯″紡 (Arrange-Act-Assert)

### 鏍囧噯 AAA 缁撴瀯

```csharp
[Fact]
public void TakeDamage_WithValidAmount_ShouldReduceHealth()
{
    // Arrange (鍑嗗娴嬭瘯鏁版嵁鍜屼緷璧?
    var fakeTime = new FakeTime();
    var player = new Player(fakeTime);
    const int damage = 30;
    const int expectedHealth = 70;

    // Act (鎵ц琚祴鎿嶄綔)
    player.TakeDamage(damage);

    // Assert (楠岃瘉缁撴灉)
    player.Health.Should().Be(expectedHealth);
}
```

### 澶嶆潅 AAA 绀轰緥

```csharp
[Fact]
public void Move_WithCollision_ShouldStopAtBoundary()
{
    // Arrange
    var fakeTime = new FakeTime();
    var player = new Player(fakeTime);
    var mockCollisionDetector = new Mock<ICollisionDetector>();

    // 璁剧疆纰版挒妫€娴嬪櫒鍦?x=500 澶勮繑鍥炵鎾?
    mockCollisionDetector
        .Setup(cd => cd.CheckCollision(It.IsAny<Vector2D>()))
        .Returns((Vector2D pos) => pos.X >= 500);

    player.SetCollisionDetector(mockCollisionDetector.Object);

    // Act
    player.Move(600, 100); // 灏濊瘯绉诲姩鍒?x=600

    // Assert
    player.Position.X.Should().Be(499); // 搴旇鍋滃湪杈圭晫
    player.Position.Y.Should().Be(100);
    mockCollisionDetector.Verify(
        cd => cd.CheckCollision(It.IsAny<Vector2D>()),
        Times.AtLeastOnce
    );
}
```

---

## 寮傛娴嬭瘯杩佺Щ

### Jest 寮傛娴嬭瘯

```typescript
// Jest async/await
describe('UserService', () => {
  it('should fetch user by id', async () => {
    const user = await userService.getUserById('123');
    expect(user.username).toBe('alice');
  });

  it('should throw on invalid id', async () => {
    await expect(userService.getUserById('')).rejects.toThrow('Invalid ID');
  });
});
```

### xUnit 寮傛娴嬭瘯

```csharp
// xUnit async Task
public class UserServiceTests
{
    [Fact]
    public async Task GetUserById_ShouldReturnUser()
    {
        // Arrange
        var service = new UserService(new FakeDataStore());

        // Act
        var user = await service.GetUserByIdAsync("123");

        // Assert
        user.Username.Should().Be("alice");
    }

    [Fact]
    public async Task GetUserById_WithInvalidId_ShouldThrowArgumentException()
    {
        // Arrange
        var service = new UserService(new FakeDataStore());

        // Act
        Func<Task> act = async () => await service.GetUserByIdAsync("");

        // Assert
        await act.Should().ThrowAsync<ArgumentException>()
            .WithMessage("Invalid ID*");
    }
}
```

---

## 娴嬭瘯鍒嗙被涓庤繃婊?

### [Trait] 鏍囪

```csharp
// Game.Core.Tests/Domain/Entities/PlayerTests.cs

public class PlayerTests
{
    [Fact]
    [Trait("Category", "Unit")]
    [Trait("Feature", "Player")]
    public void TakeDamage_ShouldReduceHealth()
    {
        // ...
    }

    [Fact]
    [Trait("Category", "Unit")]
    [Trait("Feature", "Player")]
    [Trait("Priority", "High")]
    public void Move_ShouldUpdatePosition()
    {
        // ...
    }

    [Fact]
    [Trait("Category", "Integration")]
    [Trait("Feature", "Player")]
    public void SaveToDatabase_ShouldPersist()
    {
        // ...
    }
}
```

### 杩愯鐗瑰畾鍒嗙被娴嬭瘯

```bash
# 鍙繍琛屽崟鍏冩祴璇?
dotnet test --filter "Category=Unit"

# 杩愯鐗瑰畾鍔熻兘鐨勬祴璇?
dotnet test --filter "Feature=Player"

# 杩愯楂樹紭鍏堢骇娴嬭瘯
dotnet test --filter "Priority=High"

# 缁勫悎杩囨护
dotnet test --filter "Category=Unit&Feature=Player"
```

---

## 瑕嗙洊鐜囬厤缃笌闂ㄧ

### coverlet 閰嶇疆 (Game.Core.Tests.csproj)

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="coverlet.collector" Version="6.0.0">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
    </PackageReference>
    <PackageReference Include="xunit" Version="2.9.3" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
    </PackageReference>
    <PackageReference Include="FluentAssertions" Version="7.0.0" />
    <PackageReference Include="Moq" Version="4.20.0" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\Game.Core\Game.Core.csproj" />
  </ItemGroup>
</Project>
```

### 瑕嗙洊鐜囧懡浠?

```bash
# 鐢熸垚瑕嗙洊鐜囨姤鍛?
dotnet test Game.Core.Tests/Game.Core.Tests.csproj \
  --collect:"XPlat Code Coverage" \
  --results-directory ./TestResults

# 浣跨敤 ReportGenerator 鐢熸垚 HTML 鎶ュ憡
dotnet tool install -g dotnet-reportgenerator-globaltool

reportgenerator \
  -reports:./TestResults/**/coverage.cobertura.xml \
  -targetdir:./TestResults/CoverageReport \
  -reporttypes:Html
```

### 瑕嗙洊鐜囬棬绂佽剼鏈?

```javascript
// scripts/quality_gates.mjs

import { readFileSync } from 'fs';
import { parseStringPromise } from 'xml2js';

const COVERAGE_LINE_THRESHOLD = 90;
const COVERAGE_BRANCH_THRESHOLD = 85;

async function checkCoverage() {
  const coverageXml = readFileSync('./TestResults/coverage.cobertura.xml', 'utf-8');
  const coverage = await parseStringPromise(coverageXml);

  const lineRate = parseFloat(coverage.coverage.$['line-rate']) * 100;
  const branchRate = parseFloat(coverage.coverage.$['branch-rate']) * 100;

  console.log(`Line Coverage: ${lineRate.toFixed(2)}%`);
  console.log(`Branch Coverage: ${branchRate.toFixed(2)}%`);

  if (lineRate < COVERAGE_LINE_THRESHOLD) {
    console.error(`FAIL Line coverage ${lineRate.toFixed(2)}% is below threshold ${COVERAGE_LINE_THRESHOLD}%`);
    process.exit(1);
  }

  if (branchRate < COVERAGE_BRANCH_THRESHOLD) {
    console.error(`FAIL Branch coverage ${branchRate.toFixed(2)}% is below threshold ${COVERAGE_BRANCH_THRESHOLD}%`);
    process.exit(1);
  }

  console.log('Coverage thresholds met');
}

checkCoverage().catch(err => {
  console.error(err);
  process.exit(1);
});
```

---

## 娴嬭瘯缁勭粐鏈€浣冲疄璺?

### 鎺ㄨ崘鐩綍缁撴瀯

```
Game.Core.Tests/
鈹溾攢鈹€ Domain/
鈹?  鈹溾攢鈹€ Entities/
鈹?  鈹?  鈹溾攢鈹€ PlayerTests.cs
鈹?  鈹?  鈹溾攢鈹€ EnemyTests.cs
鈹?  鈹?  鈹斺攢鈹€ ItemTests.cs
鈹?  鈹溾攢鈹€ ValueObjects/
鈹?  鈹?  鈹溾攢鈹€ Vector2DTests.cs
鈹?  鈹?  鈹斺攢鈹€ HealthPointsTests.cs
鈹?  鈹斺攢鈹€ Services/
鈹?      鈹溾攢鈹€ GameLogicServiceTests.cs
鈹?      鈹斺攢鈹€ ScoreServiceTests.cs
鈹溾攢鈹€ Infrastructure/
鈹?  鈹溾攢鈹€ Repositories/
鈹?  鈹?  鈹溾攢鈹€ UserRepositoryTests.cs
鈹?  鈹?  鈹斺攢鈹€ SaveGameRepositoryTests.cs
鈹?  鈹斺攢鈹€ Migrations/
鈹?      鈹斺攢鈹€ DatabaseMigrationTests.cs
鈹溾攢鈹€ Fakes/
鈹?  鈹溾攢鈹€ FakeTime.cs
鈹?  鈹溾攢鈹€ FakeInput.cs
鈹?  鈹溾攢鈹€ FakeDataStore.cs
鈹?  鈹斺攢鈹€ FakeLogger.cs
鈹斺攢鈹€ Fixtures/
    鈹斺攢鈹€ DatabaseFixture.cs
```

### 鍛藉悕绾﹀畾

```csharp
// Good: 娴嬭瘯鍛藉悕娓呮櫚
[Fact]
public void Constructor_WithValidParameters_ShouldInitializeProperties()

[Fact]
public void TakeDamage_WithNegativeAmount_ThrowsArgumentException()

[Fact]
public void Move_WhenOutOfBounds_ClampsToMaxBoundary()

// Bad: 娴嬭瘯鍛藉悕鍚硦
[Fact]
public void Test1()

[Fact]
public void ItWorks()

[Fact]
public void TestTakeDamage()
```

---

## 娴嬭瘯鏁版嵁鏋勫缓鍣ㄦā寮?

### 闂锛氬鏉傚璞″垱寤?

```csharp
// Bad: 姣忎釜娴嬭瘯閮介噸澶嶅垱寤哄鏉傚璞?
[Fact]
public void Test1()
{
    var player = new Player(new FakeTime())
    {
        Health = 100,
        MaxHealth = 100,
        Position = new Vector2D(50, 50),
        Velocity = new Vector2D(10, 0),
        Items = new List<Item>
        {
            new Item { Id = "1", Name = "Sword" },
            new Item { Id = "2", Name = "Shield" }
        }
    };
    // test...
}

[Fact]
public void Test2()
{
    var player = new Player(new FakeTime())
    {
        Health = 50,
        MaxHealth = 100,
        Position = new Vector2D(100, 100),
        // ... 閲嶅鍒涘缓
    };
    // test...
}
```

### 瑙ｅ喅鏂规锛欱uilder Pattern

```csharp
// Game.Core.Tests/Builders/PlayerBuilder.cs

public class PlayerBuilder
{
    private ITime _time = new FakeTime();
    private int _health = 100;
    private int _maxHealth = 100;
    private Vector2D _position = new Vector2D(0, 0);
    private Vector2D _velocity = new Vector2D(0, 0);
    private List<Item> _items = new();

    public static PlayerBuilder APlayer() => new();

    public PlayerBuilder WithHealth(int health)
    {
        _health = health;
        return this;
    }

    public PlayerBuilder WithMaxHealth(int maxHealth)
    {
        _maxHealth = maxHealth;
        return this;
    }

    public PlayerBuilder At(double x, double y)
    {
        _position = new Vector2D(x, y);
        return this;
    }

    public PlayerBuilder WithVelocity(double vx, double vy)
    {
        _velocity = new Vector2D(vx, vy);
        return this;
    }

    public PlayerBuilder WithItem(Item item)
    {
        _items.Add(item);
        return this;
    }

    public PlayerBuilder Injured()
    {
        _health = 30;
        return this;
    }

    public PlayerBuilder AtFullHealth()
    {
        _health = _maxHealth;
        return this;
    }

    public Player Build()
    {
        var player = new Player(_time)
        {
            Health = _health,
            MaxHealth = _maxHealth,
            Position = _position,
            Velocity = _velocity
        };

        foreach (var item in _items)
        {
            player.AddItem(item);
        }

        return player;
    }
}

// 浣跨敤绀轰緥
public class PlayerTests
{
    [Fact]
    public void TakeDamage_WhenInjured_ShouldReduceHealth()
    {
        // Arrange
        var player = PlayerBuilder.APlayer()
            .Injured()
            .At(50, 50)
            .Build();

        // Act
        player.TakeDamage(10);

        // Assert
        player.Health.Should().Be(20);
    }

    [Fact]
    public void Move_FromOrigin_ShouldUpdatePosition()
    {
        // Arrange
        var player = PlayerBuilder.APlayer()
            .AtFullHealth()
            .Build();

        // Act
        player.Move(10, 15);

        // Assert
        player.Position.Should().BeEquivalentTo(new Vector2D(10, 15));
    }
}
```

---

## 鐗瑰畾鍦烘櫙娴嬭瘯妯″紡

### 1. 寮傚父娴嬭瘯

```csharp
[Fact]
public void TakeDamage_WithNegativeAmount_ThrowsArgumentException()
{
    // Arrange
    var player = PlayerBuilder.APlayer().Build();

    // Act
    Action act = () => player.TakeDamage(-10);

    // Assert
    act.Should().Throw<ArgumentException>()
       .WithMessage("Damage must be positive*")
       .And.ParamName.Should().Be("amount");
}

[Fact]
public void Constructor_WithNullTime_ThrowsArgumentNullException()
{
    // Arrange & Act
    Action act = () => new Player(null!);

    // Assert
    act.Should().Throw<ArgumentNullException>()
       .WithParameterName("time");
}
```

### 2. 浜嬩欢/淇″彿娴嬭瘯

```csharp
[Fact]
public void TakeDamage_ShouldRaiseDamagedEvent()
{
    // Arrange
    var player = PlayerBuilder.APlayer().Build();
    int receivedDamage = 0;
    int receivedHealth = 0;

    player.Damaged += (damage, health) =>
    {
        receivedDamage = damage;
        receivedHealth = health;
    };

    // Act
    player.TakeDamage(25);

    // Assert
    receivedDamage.Should().Be(25);
    receivedHealth.Should().Be(75);
}

[Fact]
public void TakeDamage_WhenHealthReachesZero_ShouldRaiseDeathEvent()
{
    // Arrange
    var player = PlayerBuilder.APlayer().WithHealth(10).Build();
    bool deathEventRaised = false;

    player.Death += () => deathEventRaised = true;

    // Act
    player.TakeDamage(20);

    // Assert
    deathEventRaised.Should().BeTrue();
    player.Health.Should().Be(0);
}
```

### 3. 鏃堕棿渚濊禆娴嬭瘯

```csharp
[Fact]
public void Update_ShouldUseCorrectDeltaTime()
{
    // Arrange
    var fakeTime = new FakeTime();
    fakeTime.SetDeltaTime(0.032); // 30 FPS

    var player = new Player(fakeTime);
    player.Velocity = new Vector2D(100, 0); // 100 units/sec

    // Act
    player.Update(); // Should move 100 * 0.032 = 3.2 units

    // Assert
    player.Position.X.Should().BeApproximately(3.2, 0.01);
}

[Fact]
public void Cooldown_AfterElapsedTime_ShouldExpire()
{
    // Arrange
    var fakeTime = new FakeTime();
    var player = new Player(fakeTime);
    player.StartCooldown(5.0); // 5 second cooldown

    // Act
    fakeTime.AdvanceTime(6.0);
    player.Update();

    // Assert
    player.IsCooldownActive.Should().BeFalse();
}
```

### 4. 鐘舵€佽浆鎹㈡祴璇?

```csharp
[Theory]
[InlineData(PlayerState.Idle, PlayerState.Running)]
[InlineData(PlayerState.Running, PlayerState.Jumping)]
[InlineData(PlayerState.Jumping, PlayerState.Falling)]
[InlineData(PlayerState.Falling, PlayerState.Idle)]
public void TransitionTo_WithValidTransition_ShouldChangeState(
    PlayerState fromState,
    PlayerState toState)
{
    // Arrange
    var player = PlayerBuilder.APlayer().Build();
    player.SetState(fromState);

    // Act
    player.TransitionTo(toState);

    // Assert
    player.CurrentState.Should().Be(toState);
}

[Fact]
public void TransitionTo_WithInvalidTransition_ShouldThrowInvalidOperationException()
{
    // Arrange
    var player = PlayerBuilder.APlayer().Build();
    player.SetState(PlayerState.Idle);

    // Act
    Action act = () => player.TransitionTo(PlayerState.Falling);

    // Assert
    act.Should().Throw<InvalidOperationException>()
       .WithMessage("Cannot transition from Idle to Falling*");
}
```

---

## 娴嬭瘯鏇胯韩瀹屾暣绀轰緥

### FakeTime 瀹炵幇

```csharp
// Game.Core.Tests/Fakes/FakeTime.cs

using Game.Core.Ports;

namespace Game.Core.Tests.Fakes;

public class FakeTime : ITime
{
    private double _timestamp = 1234567890;
    private double _deltaTime = 0.016; // 60 FPS
    private double _elapsedTime = 0;

    public double GetTimestamp() => _timestamp;
    public double GetDeltaTime() => _deltaTime;
    public double GetElapsedTime() => _elapsedTime;

    public void SetTimestamp(double value) => _timestamp = value;
    public void SetDeltaTime(double value) => _deltaTime = value;

    public void AdvanceTime(double seconds)
    {
        _elapsedTime += seconds;
        _timestamp += seconds;
    }

    public void Reset()
    {
        _timestamp = 1234567890;
        _deltaTime = 0.016;
        _elapsedTime = 0;
    }
}
```

### FakeInput 瀹炵幇

```csharp
// Game.Core.Tests/Fakes/FakeInput.cs

using Game.Core.Ports;

namespace Game.Core.Tests.Fakes;

public class FakeInput : IInput
{
    private readonly Dictionary<string, bool> _pressedActions = new();
    private readonly Dictionary<string, bool> _justPressedActions = new();
    private readonly Dictionary<string, bool> _justReleasedActions = new();
    private Vector2D _mousePosition = Vector2D.Zero;

    public void SetActionPressed(string action, bool pressed)
    {
        _pressedActions[action] = pressed;
    }

    public void SimulateActionPress(string action)
    {
        _justPressedActions[action] = true;
        _pressedActions[action] = true;
    }

    public void SimulateActionRelease(string action)
    {
        _justReleasedActions[action] = true;
        _pressedActions[action] = false;
    }

    public void SetMousePosition(Vector2D position)
    {
        _mousePosition = position;
    }

    public bool IsActionPressed(string action)
    {
        return _pressedActions.GetValueOrDefault(action, false);
    }

    public bool IsActionJustPressed(string action)
    {
        var result = _justPressedActions.GetValueOrDefault(action, false);
        _justPressedActions[action] = false; // 娑堣垂
        return result;
    }

    public bool IsActionJustReleased(string action)
    {
        var result = _justReleasedActions.GetValueOrDefault(action, false);
        _justReleasedActions[action] = false; // 娑堣垂
        return result;
    }

    public Vector2D GetAxis(string negativeX, string positiveX, string negativeY, string positiveY)
    {
        var x = (IsActionPressed(positiveX) ? 1.0 : 0.0) - (IsActionPressed(negativeX) ? 1.0 : 0.0);
        var y = (IsActionPressed(positiveY) ? 1.0 : 0.0) - (IsActionPressed(negativeY) ? 1.0 : 0.0);
        return new Vector2D(x, y);
    }

    public Vector2D GetMousePosition()
    {
        return _mousePosition;
    }

    public void Reset()
    {
        _pressedActions.Clear();
        _justPressedActions.Clear();
        _justReleasedActions.Clear();
        _mousePosition = Vector2D.Zero;
    }
}
```

### FakeDataStore 瀹炵幇

```csharp
// Game.Core.Tests/Fakes/FakeDataStore.cs

using Game.Core.Ports;

namespace Game.Core.Tests.Fakes;

public class FakeDataStore : IDataStore
{
    private readonly Dictionary<Type, Dictionary<string, object>> _tables = new();
    private bool _isOpen = false;

    public void Open(string dbPath)
    {
        _isOpen = true;
    }

    public void Close()
    {
        _isOpen = false;
        _tables.Clear();
    }

    public void Execute(string sql, params object[] parameters)
    {
        EnsureOpen();
        // 绠€鍖栧疄鐜帮細涓嶇湡姝ｈВ鏋?SQL锛屼粎鐢ㄤ簬娴嬭瘯
    }

    public T? QuerySingle<T>(string sql, params object[] parameters) where T : class
    {
        EnsureOpen();
        var table = GetTable<T>();
        return table.Values.FirstOrDefault() as T;
    }

    public List<T> Query<T>(string sql, params object[] parameters) where T : class
    {
        EnsureOpen();
        var table = GetTable<T>();
        return table.Values.Cast<T>().ToList();
    }

    // Test helper methods
    public void Insert<T>(string id, T entity) where T : class
    {
        EnsureOpen();
        var table = GetTable<T>();
        table[id] = entity;
    }

    public void Clear<T>() where T : class
    {
        if (_tables.ContainsKey(typeof(T)))
        {
            _tables[typeof(T)].Clear();
        }
    }

    private Dictionary<string, object> GetTable<T>()
    {
        var type = typeof(T);
        if (!_tables.ContainsKey(type))
        {
            _tables[type] = new Dictionary<string, object>();
        }
        return _tables[type];
    }

    private void EnsureOpen()
    {
        if (!_isOpen)
        {
            throw new InvalidOperationException("Database not opened");
        }
    }
}
```

---

## CI 闆嗘垚

### GitHub Actions 閰嶇疆

```yaml
# .github/workflows/tests.yml

name: Unit Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  unit-tests:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup .NET 8
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '8.0.x'

      - name: Restore dependencies
        run: dotnet restore Game.Core.Tests/Game.Core.Tests.csproj

      - name: Build
        run: dotnet build Game.Core.Tests/Game.Core.Tests.csproj --no-restore

      - name: Run unit tests with coverage
        run: |
          dotnet test Game.Core.Tests/Game.Core.Tests.csproj `
            --no-build `
            --verbosity normal `
            --collect:"XPlat Code Coverage" `
            --results-directory ./TestResults `
            --logger trx

      - name: Generate coverage report
        run: |
          dotnet tool install -g dotnet-reportgenerator-globaltool
          reportgenerator `
            -reports:./TestResults/**/coverage.cobertura.xml `
            -targetdir:./TestResults/CoverageReport `
            -reporttypes:Html;Cobertura

      - name: Check coverage thresholds
        run: node scripts/quality_gates.mjs

      - name: Upload coverage report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report
          path: ./TestResults/CoverageReport

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: ./TestResults/*.trx

      - name: Publish coverage to Codecov
        if: always()
        uses: codecov/codecov-action@v3
        with:
          files: ./TestResults/**/coverage.cobertura.xml
          flags: unittests
          name: codecov-godotgame
```

---

## 瀹屾垚鏍囧噯

- [ ] 鎵€鏈?Jest 鍗曞厓娴嬭瘯宸茶縼绉诲埌 xUnit
- [ ] 浣跨敤 FluentAssertions 鏇夸唬 Jest expect()
- [ ] AAA 妯″紡鍦ㄦ墍鏈夋祴璇曚腑涓€鑷村簲鐢?
- [ ] 娴嬭瘯鍛藉悕绗﹀悎 `MethodName_Scenario_ExpectedBehavior` 绾﹀畾
- [ ] [Theory] + [InlineData] 鐢ㄤ簬鍙傛暟鍖栨祴璇?
- [ ] Fake 瀹炵幇鎻愪緵缁欐牳蹇冪鍙?(ITime, IInput, IDataStore, ILogger)
- [ ] Builder 妯″紡鐢ㄤ簬澶嶆潅瀵硅薄鍒涘缓
- [ ] 瑕嗙洊鐜囪揪鍒?鈮?0% 琛岃鐩栫巼锛屸墺85% 鍒嗘敮瑕嗙洊鐜?
- [ ] coverlet 閰嶇疆姝ｇ‘锛岀敓鎴?Cobertura 鎶ュ憡
- [ ] CI 绠￠亾鍖呭惈鍗曞厓娴嬭瘯鎵ц鍜岃鐩栫巼闂ㄧ
- [ ] 娴嬭瘯鍒嗙被浣跨敤 [Trait] 鏍囪锛圕ategory, Feature, Priority锛?

---

## 涓嬩竴姝?

瀹屾垚鏈樁娈靛悗锛岀户缁細

[鍙傝€僝 [Phase-11-Scene-Integration-Tests-REVISED.md](Phase-11-Scene-Integration-Tests-REVISED.md) 鈥?鍦烘櫙娴嬭瘯璁捐锛圙dUnit4锛?

## 模板规范 / Template Guidelines

- 结构：
  - xUnit：`Game.Core.Tests/**`（.NET 8 + xUnit + FluentAssertions）
  - GdUnit4：`tests/**`（Godot 4，示例测试默认关闭）
- 命名：文件名 `<Type>Tests.cs`，类名 `<Type>Tests`；GdUnit 用 `*_Tests.gd`
- 守卫：示例测试受 `TEMPLATE_DEMO=1` 控制，默认跳过（模板更干净）

## 快速命令 / Quick Commands

- 运行 .NET 测试：`./scripts/ci/run_dotnet_tests.ps1`
- 运行 Godot 测试：`./scripts/ci/run_gdunit_tests.ps1 -GodotBin "$env:GODOT_BIN"`
- 一键测试（可含示例）：`./scripts/test.ps1 [-GodotBin <path>] [-IncludeDemo]`

## 覆盖率 / Coverage

- 可通过引入 `coverlet.msbuild` 启用 `/p:CollectCoverage=true /p:CoverletOutputFormat=cobertura`；模板默认不强制开启（保持轻量）


## 覆盖率（coverlet.collector） / Coverage

- 已包含 `coverlet.collector`，可直接运行：
  - `dotnet test Game.sln --collect:"XPlat Code Coverage" -- DataCollectionRunSettings.DataCollectors.DataCollector.Configuration.Format=cobertura`
- 脚本：`./scripts/ci/run_dotnet_coverage.ps1` 收集并存放到 `logs/ci/<ts>/dotnet-coverage/`

