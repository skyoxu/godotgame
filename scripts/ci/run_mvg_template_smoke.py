#!/usr/bin/env python3
"""Inject a neutral MVG fixture, execute the real runner, and restore the checkout."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--godot-bin", default=os.environ.get("GODOT_BIN", ""))
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    if not args.godot_bin:
        raise SystemExit("GODOT_BIN is required for the neutral MVG runtime smoke")

    fixture_files = {
        root / ".taskmaster/tasks/tasks.json": json.dumps(
            {"master": {"tasks": [{"id": 900001, "status": "done"}, {"id": 900002, "status": "done"}]}},
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        root / "Game.Core/MvgTemplateSmoke.cs": (
            "namespace Game.Core;\n"
            "public static class MvgTemplateSmoke { public static int Value => 2; }\n"
        ),
        root / "Game.Core/Contracts/MvgTemplateSmokeContract.cs": (
            "namespace Game.Core.Contracts;\n"
            "public interface IMvgTemplateSmokeContract { int Value { get; } }\n"
        ),
        root / "Game.Core.Tests/Integration/MvgTemplateSmokeTests.cs": (
            "using Xunit;\n\n"
            "namespace Game.Core.Tests.Integration;\n\n"
            "public sealed class MvgTemplateSmokeTests\n"
            "{\n"
            "    [Fact]\n"
            "    public void Neutral_contract_is_observable() => Assert.Equal(2, Game.Core.MvgTemplateSmoke.Value);\n"
            "}\n"
        ),
        root / "Tests.Godot/tests/Integration/Mvg/test_mvg_template_smoke.gd": (
            'extends "res://addons/gdUnit4/src/GdUnitTestSuite.gd"\n\n'
            "func test_neutral_runtime_contract() -> void:\n"
            "    assert_int(1 + 1).is_equal(2)\n"
        ),
    }
    manifest_path = root / ".mvg-template-smoke/manifest.json"
    manifest = {
        "schema_version": "godotgame.mvg-integration.v1",
        "mvg_id": "template-runtime-smoke",
        "coverage": {
            "mode": "pilot",
            "scope_id": "neutral-template-runtime",
            "required_flow_ids": ["neutral-cross-runtime-flow"],
            "blocking_task_ids": [],
            "excluded_claims": [
                "Runtime smoke proves template mechanics, not project-wide MVG coverage."
            ],
        },
        "flows": [{
            "id": "neutral-cross-runtime-flow",
            "task_ids": [900001, 900002],
            "outcome": "A neutral integration contract is evidenced in both dotnet and GdUnit runtimes.",
            "source_paths": ["Game.Core/MvgTemplateSmoke.cs"],
            "handoffs": [{
                "contract_ref": "Game.Core/Contracts/MvgTemplateSmokeContract.cs",
                "behavior": "The neutral producer and consumer share one explicit contract boundary.",
                "producer_task": 900001,
                "consumer_task": 900002,
                "owner_task": 900002,
                "test_ids": ["neutral-dotnet", "neutral-gdunit"],
            }],
            "test_ids": ["neutral-dotnet", "neutral-gdunit"],
        }],
        "tests": [
            {
                "id": "neutral-dotnet",
                "kind": "dotnet",
                "state": "implemented",
                "evidence_level": "domain-integration",
                "path": "Game.Core.Tests/Integration/MvgTemplateSmokeTests.cs",
                "selector": "Game.Core.Tests.Integration.MvgTemplateSmokeTests",
                "min_tests": 1,
            },
            {
                "id": "neutral-gdunit",
                "kind": "gdunit",
                "state": "implemented",
                "evidence_level": "scene-method",
                "path": "Tests.Godot/tests/Integration/Mvg/test_mvg_template_smoke.gd",
                "min_tests": 1,
            },
        ],
    }

    originals: dict[Path, bytes | None] = {}
    created_dirs: set[Path] = set()
    try:
        for path, content in fixture_files.items():
            originals[path] = path.read_bytes() if path.exists() else None
            path.parent.mkdir(parents=True, exist_ok=True)
            created_dirs.add(path.parent)
            path.write_text(content, encoding="utf-8")
        originals[manifest_path] = manifest_path.read_bytes() if manifest_path.exists() else None
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        created_dirs.add(manifest_path.parent)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        command = [
            sys.executable,
            "scripts/python/run_mvg_acceptance.py",
            "--manifest", ".mvg-template-smoke/manifest.json",
            "--mode", "run",
            "--snapshot", "workspace",
            "--revision", "HEAD",
            "--godot-bin", args.godot_bin,
            "--timeout-sec", "900",
        ]
        result = subprocess.run(command, cwd=root, check=False)
        return result.returncode
    finally:
        for path, previous in reversed(list(originals.items())):
            if previous is None:
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(previous)
        for directory in sorted(created_dirs, key=lambda p: len(p.parts), reverse=True):
            current = directory
            while current != root:
                try:
                    current.rmdir()
                except OSError:
                    break
                current = current.parent


if __name__ == "__main__":
    raise SystemExit(main())
