using Game.Core.Prototypes;
using Xunit;
using Xunit.Abstractions;

namespace Game.Core.Tests.Prototypes;

public class DefaultRpgPrototypeLoopTests
{
    private readonly ITestOutputHelper _output;

    public DefaultRpgPrototypeLoopTests(ITestOutputHelper output)
    {
        _output = output;
    }

    [Fact]
    public void ShouldGenerateEncounterAndRewardSummary_WhenPrototypeLoopResolvesBattle()
    {
        var loop = new DefaultRpgPrototypeLoop();

        var result = loop.ResolveBattleAndReward(
            playerHp: 30,
            playerAttack: 12,
            playerDefense: 4,
            critRate: 0.25,
            enemyHp: 18,
            enemyAttack: 6,
            enemyDefense: 2,
            rewardSeed: 1);

        Assert.True(result.EncounterTriggered);
        Assert.True(result.BattleResolved);
        Assert.Equal("equipment", result.RewardCategory);
        Assert.True(result.PlayerHpAfterBattle > 0);
    }

    [Fact]
    public void ShouldAdvanceToRewardPhaseAfterNonBossVictory_WhenPlayerWinsEncounter()
    {
        var loop = new DefaultRpgPrototypeLoop();

        var state = loop.CreateInitialState();
        var result = loop.ResolveEncounter(state);

        Assert.Equal(2, result.NextState.StepIndex);
        Assert.Equal("reward", result.NextState.Phase);
        Assert.False(result.NextState.IsGameOver);
        Assert.False(result.NextState.IsVictory);
        Assert.Equal(3, result.RewardOptions.Count);
        Assert.All(result.RewardOptions, option => Assert.False(string.IsNullOrWhiteSpace(option.Title)));
    }

    [Fact]
    public void ShouldEndPrototypeWithVictory_WhenBossEncounterIsCleared()
    {
        var loop = new DefaultRpgPrototypeLoop();

        var state = new DefaultRpgPrototypeState(
            StepIndex: 15,
            PlayerHp: 26,
            PlayerAttack: 16,
            PlayerDefense: 6,
            CritRate: 0.35,
            PassiveSkills: ["先发制人"],
            EquippedItems: ["青铜剑"],
            Phase: "battle",
            IsGameOver: false,
            IsVictory: false);

        var result = loop.ResolveEncounter(state);

        Assert.True(result.NextState.IsVictory);
        Assert.False(result.NextState.IsGameOver);
        Assert.Equal("complete", result.NextState.Phase);
        Assert.Contains("魔王", result.Encounter.Name);
        Assert.Empty(result.RewardOptions);
    }

    [Fact]
    public void ShouldKeepEachSingleArchetypeRouteWithinPlayableRange_WhenPrototypeRunIsSimulated()
    {
        var loop = new DefaultRpgPrototypeLoop();

        var vanguard = SimulateFixedRewardRoute(loop, 0);
        var guardian = SimulateFixedRewardRoute(loop, 1);
        var hunter = SimulateFixedRewardRoute(loop, 2);

        _output.WriteLine($"Vanguard: victory={vanguard.IsVictory} hp={vanguard.PlayerHp} step={vanguard.StepIndex}");
        _output.WriteLine($"Guardian: victory={guardian.IsVictory} hp={guardian.PlayerHp} step={guardian.StepIndex}");
        _output.WriteLine($"Hunter: victory={hunter.IsVictory} hp={hunter.PlayerHp} step={hunter.StepIndex}");

        Assert.True(vanguard.IsVictory || vanguard.PlayerHp > 0);
        Assert.True(guardian.IsVictory || guardian.PlayerHp > 0);
        Assert.True(hunter.IsVictory || hunter.PlayerHp > 0);
        Assert.True(vanguard.IsVictory);
        Assert.True(guardian.IsVictory);
        Assert.True(hunter.IsVictory);
        Assert.True(vanguard.PlayerHp <= 30);
        Assert.True(guardian.PlayerHp <= 12);
        Assert.True(hunter.PlayerHp <= 8);
    }

    private static DefaultRpgPrototypeState SimulateFixedRewardRoute(DefaultRpgPrototypeLoop loop, int rewardIndex)
    {
        var state = loop.CreateInitialState();

        while (!state.IsGameOver && !state.IsVictory)
        {
            var encounter = loop.ResolveEncounter(state);
            state = encounter.NextState;

            if (state.IsGameOver || state.IsVictory)
            {
                break;
            }

            state = loop.ApplyReward(state, rewardIndex);
        }

        return state;
    }
}
