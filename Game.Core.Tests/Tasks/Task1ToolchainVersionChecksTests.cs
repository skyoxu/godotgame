using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using FluentAssertions;
using Xunit;

namespace Game.Core.Tests.Tasks;

public sealed class Task1ToolchainVersionChecksTests
{
    // ACC:T1.4
    // ACC:T1.5
    // ACC:T1.7
    // ACC:T1.8
    [Fact]
    public void ShouldValidatePinnedToolchainEvidence_WhenTask1PreflightHasRun()
    {
        if (!Task1PreflightEvidenceGuard.TryGetTodayArtifact(out var artifact, out var missingReason))
        {
            Task1PreflightEvidenceGuard.EnsureOrSkip(missingReason);
            return;
        }

        using var document = JsonDocument.Parse(File.ReadAllText(artifact.TaskJsonPath, Encoding.UTF8));
        var root = document.RootElement;

        root.GetProperty("godot_version").GetString().Should().Be("4.5.1");

        var godotBin = root.GetProperty("godot_bin").GetString();
        godotBin.Should().NotBeNullOrWhiteSpace();
        Path.IsPathRooted(godotBin!).Should().BeTrue();
        File.Exists(godotBin!).Should().BeTrue();

        var godotBinCheck = root.GetProperty("godot_bin_check");
        godotBinCheck.GetProperty("is_absolute").GetBoolean().Should().BeTrue();
        godotBinCheck.GetProperty("installation_verification_result").GetString().Should().Be("pass");

        var commands = root.GetProperty("godot_commands");
        ValidateGodotCommand(commands, artifact, "godot_version_command");
        ValidateGodotCommand(commands, artifact, "godot_bin_version_command");

        var sdkCheck = root.GetProperty("dotnet_sdk_check");
        sdkCheck.GetProperty("exit_code").GetInt32().Should().Be(0);
        sdkCheck.GetProperty("has_dotnet8_sdk").GetBoolean().Should().BeTrue();
        var sdkVersions = sdkCheck.GetProperty("detected_sdk_versions").EnumerateArray().Select(x => x.GetString() ?? string.Empty).ToArray();
        sdkVersions.Should().Contain(version => version.StartsWith("8.", StringComparison.Ordinal));
        ResolveEvidencePath(artifact, sdkCheck.GetProperty("evidence_file").GetString()).Exists.Should().BeTrue();

        root.GetProperty("dotnet_version").GetString().Should().StartWith("8.");

        var restore = root.GetProperty("dotnet_restore");
        restore.GetProperty("exit_code").GetInt32().Should().Be(0);
        var solutionName = Task1PreflightEvidenceGuard.ResolvePrimarySolutionName(artifact.RepoRoot);
        restore.GetProperty("command").GetString().Should().Contain(solutionName);
        ResolveEvidencePath(artifact, restore.GetProperty("evidence_file").GetString()).Exists.Should().BeTrue();
    }

    private static void ValidateGodotCommand(JsonElement commands, Task1PreflightArtifact artifact, string commandKey)
    {
        var entry = commands.GetProperty(commandKey);
        entry.GetProperty("exit_code").GetInt32().Should().Be(0);
        entry.GetProperty("parsed_version").GetString().Should().Be("4.5.1");
        ResolveEvidencePath(artifact, entry.GetProperty("evidence_file").GetString()).Exists.Should().BeTrue();
    }

    private static FileInfo ResolveEvidencePath(Task1PreflightArtifact artifact, string? relPath)
    {
        relPath.Should().NotBeNullOrWhiteSpace();
        return new FileInfo(Path.Combine(artifact.RepoRoot, relPath!.Replace('/', Path.DirectorySeparatorChar)));
    }
}
