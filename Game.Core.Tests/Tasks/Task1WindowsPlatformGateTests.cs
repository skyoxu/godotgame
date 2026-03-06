using System;
using System.IO;
using System.Text;
using System.Text.Json;
using FluentAssertions;
using Xunit;

namespace Game.Core.Tests.Tasks;

public sealed class Task1WindowsPlatformGateTests
{
    // ACC:T1.13
    // ACC:T1.14
    [Fact]
    public void ShouldValidateWindowsOnlyEvidence_WhenTask1PreflightHasRun()
    {
        if (!Task1PreflightEvidenceGuard.TryGetTodayArtifact(out var artifact, out var missingReason))
        {
            Task1PreflightEvidenceGuard.EnsureOrSkip(missingReason);
            return;
        }

        using var document = JsonDocument.Parse(File.ReadAllText(artifact.TaskJsonPath, Encoding.UTF8));
        var root = document.RootElement;

        root.GetProperty("os_platform").GetString().Should().Be("Windows");

        var check = root.GetProperty("windows_only_check");
        check.GetProperty("result").GetString().Should().Be("pass");
        check.GetProperty("platform_evidence").GetString().Should().NotBeNullOrWhiteSpace();
        check.GetProperty("reason").GetString().Should().BeEmpty();

        var evidenceRel = check.GetProperty("evidence_file").GetString();
        evidenceRel.Should().NotBeNullOrWhiteSpace();
        var evidencePath = Path.Combine(artifact.RepoRoot, evidenceRel!.Replace('/', Path.DirectorySeparatorChar));
        File.Exists(evidencePath).Should().BeTrue();

        var content = File.ReadAllText(evidencePath, Encoding.UTF8);
        content.Should().Contain("result=pass");
        content.Should().Contain("platform=");
    }
}
