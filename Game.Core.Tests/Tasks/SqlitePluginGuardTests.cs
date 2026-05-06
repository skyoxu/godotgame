using System.IO;
using Xunit;

namespace Game.Core.Tests.Tasks;

public sealed class SqlitePluginGuardTests
{
    [Fact]
    public void SqliteDataStore_ShouldCheckClassExists_BeforeInstantiatingPluginClass()
    {
        var repoRoot = Path.GetFullPath(Path.Combine(System.AppContext.BaseDirectory, "..", "..", "..", ".."));
        var sourcePath = Path.Combine(repoRoot, "Game.Godot", "Adapters", "SqliteDataStore.cs");
        var source = File.ReadAllText(sourcePath);

        var classExistsIndex = source.IndexOf("ClassDB.ClassExists(\"SQLite\")", System.StringComparison.Ordinal);
        var instantiateIndex = source.IndexOf("ClassDB.Instantiate(\"SQLite\")", System.StringComparison.Ordinal);

        Assert.True(classExistsIndex >= 0, "Expected SQLite class existence guard in SqliteDataStore.");
        Assert.True(instantiateIndex >= 0, "Expected SQLite instantiation path in SqliteDataStore.");
        Assert.True(classExistsIndex < instantiateIndex, "SQLite class existence guard must run before instantiate.");
    }

    [Fact]
    public void SqliteDataStore_ShouldOnlyProbePlugin_WhenPluginBackendIsExplicitlyRequested()
    {
        var repoRoot = Path.GetFullPath(Path.Combine(System.AppContext.BaseDirectory, "..", "..", "..", ".."));
        var sourcePath = Path.Combine(repoRoot, "Game.Godot", "Adapters", "SqliteDataStore.cs");
        var source = File.ReadAllText(sourcePath);

        Assert.Contains("var forcePlugin = prefer == \"plugin\";", source);
        Assert.DoesNotContain("if (!forceManaged && TryOpenPlugin(_dbPath!))", source);
        Assert.Contains("if (forcePlugin && TryOpenPlugin(_dbPath!))", source);
    }
}
