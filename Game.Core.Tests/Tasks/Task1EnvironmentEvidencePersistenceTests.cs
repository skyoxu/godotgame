using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using FluentAssertions;
using Xunit;

namespace Game.Core.Tests.Tasks;

public sealed class Task1EnvironmentEvidencePersistenceTests
{
    private static readonly string[] RequiredEvidenceFiles =
    {
        "godot-bin-env.txt",
        "godot-version.txt",
        "godot-bin-version.txt",
        "dotnet-version.txt",
        "dotnet-sdks.txt",
        "dotnet-restore.txt",
        "packages-lock-exists.txt",
        "windows-only-check.txt",
        "utf8-check.txt",
    };

    private static readonly string[] RequiredAdrs = { "ADR-0031", "ADR-0011" };

    // ACC:T1.1
    // ACC:T1.2
    // ACC:T1.6
    [Fact]
    public void ShouldPersistEvidenceFilesAndUtf8References_WhenTask1PreflightHasRun()
    {
        if (!Task1PreflightEvidenceGuard.TryGetTodayArtifact(out var artifact, out var missingReason))
        {
            Task1PreflightEvidenceGuard.EnsureOrSkip(missingReason);
            return;
        }

        using var document = JsonDocument.Parse(File.ReadAllText(artifact.TaskJsonPath, Encoding.UTF8));
        var root = document.RootElement;

        root.TryGetProperty("evidence_paths", out var evidencePaths).Should().BeTrue();
        var relPaths = evidencePaths.EnumerateArray().Select(x => x.GetString() ?? string.Empty).Where(x => !string.IsNullOrWhiteSpace(x)).ToArray();
        relPaths.Should().NotBeEmpty();

        foreach (var fileName in RequiredEvidenceFiles)
        {
            relPaths.Should().Contain(path => path.EndsWith(fileName, StringComparison.OrdinalIgnoreCase));
            File.Exists(Path.Combine(artifact.RepoRoot, relPaths.First(path => path.EndsWith(fileName, StringComparison.OrdinalIgnoreCase)).Replace('/', Path.DirectorySeparatorChar))).Should().BeTrue();
        }

        root.TryGetProperty("utf8_check", out var utf8Check).Should().BeTrue();
        utf8Check.GetProperty("result").GetString().Should().Be("pass");
        var checkedFiles = utf8Check.GetProperty("checked_files").EnumerateArray().Select(x => x.GetString() ?? string.Empty).Where(x => !string.IsNullOrWhiteSpace(x)).ToArray();
        checkedFiles.Should().Contain(path => path.EndsWith("task-0001.json", StringComparison.OrdinalIgnoreCase));

        root.TryGetProperty("acceptance_checklist", out var checklist).Should().BeTrue();
        checklist.GetProperty("exists").GetBoolean().Should().BeTrue();
        var checklistRel = checklist.GetProperty("path").GetString();
        checklistRel.Should().NotBeNullOrWhiteSpace();
        checkedFiles.Should().Contain(path => string.Equals(path, checklistRel, StringComparison.OrdinalIgnoreCase));

        foreach (var relPath in checkedFiles)
        {
            var fullPath = Path.Combine(artifact.RepoRoot, relPath.Replace('/', Path.DirectorySeparatorChar));
            File.Exists(fullPath).Should().BeTrue($"checked UTF-8 file should exist: {relPath}");
            var bytes = File.ReadAllBytes(fullPath);
            Action act = () => new UTF8Encoding(false, true).GetString(bytes);
            act.Should().NotThrow();
        }

        root.TryGetProperty("adr_refs", out var adrRefs).Should().BeTrue();
        var actualAdrs = adrRefs.EnumerateArray().Select(x => x.GetString() ?? string.Empty).ToArray();
        actualAdrs.Should().Contain(RequiredAdrs);
    }
}
