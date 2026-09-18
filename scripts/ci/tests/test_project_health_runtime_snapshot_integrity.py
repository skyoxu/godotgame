from __future__ import annotations

import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/python"))

from _project_health_runtime_snapshot import _is_regenerable_gdunit_import, _is_workspace_ignored, prepare_snapshot


class ProjectHealthRuntimeSnapshotIntegrityTests(unittest.TestCase):
    def test_only_gdunit_plugin_import_cache_is_regenerable(self) -> None:
        self.assertTrue(_is_regenerable_gdunit_import("Tests.Godot/addons/gdUnit4/icons/check.png.import"))
        self.assertFalse(_is_regenerable_gdunit_import("Tests.Godot/addons/gdUnit4/scripts/gdunit.gd"))
        self.assertFalse(_is_regenerable_gdunit_import("Game.Godot/Assets/player.png.import"))
        self.assertFalse(_is_regenerable_gdunit_import("../Tests.Godot/addons/gdUnit4/cache.import"))
        self.assertFalse(_is_workspace_ignored("Tests.Godot/addons/gdUnit4/bin/GdUnitCmdTool.gd"))
        self.assertTrue(_is_workspace_ignored("Game.Core/bin/Debug/Game.Core.dll"))
        self.assertTrue(_is_workspace_ignored("Game.Core/obj/project.assets.json"))

    def test_main_and_workspace_exclude_plugin_import_cache_but_keep_project_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()

            def git(*args: str) -> str:
                return subprocess.check_output(
                    ["git", "-C", str(root), *args], stderr=subprocess.DEVNULL
                ).decode().strip()

            git("init", "-b", "main")
            excluded = root / "Tests.Godot/addons/gdUnit4/icons/check.png.import"
            plugin_source = root / "Tests.Godot/addons/gdUnit4/scripts/gdunit.gd"
            plugin_bin = root / "Tests.Godot/addons/gdUnit4/bin/GdUnitCmdTool.gd"
            project_import = root / "Game.Godot/Assets/player.png.import"
            build_bin = root / "Game.Core/bin/Debug/ignored.dll"
            for path in (excluded, plugin_source, plugin_bin, project_import, build_bin):
                path.parent.mkdir(parents=True, exist_ok=True)
            excluded.write_text("derived-cache", encoding="utf-8")
            plugin_source.write_text("extends Node\n", encoding="utf-8")
            plugin_bin.write_text("extends SceneTree\n", encoding="utf-8")
            project_import.write_text("project-import", encoding="utf-8")
            build_bin.write_text("build-output", encoding="utf-8")
            git("add", ".")
            git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "fixture")
            revision = git("rev-parse", "HEAD")
            (root / ".git/info/exclude").write_text("logs/\n", encoding="utf-8")

            for mode in ("main", "workspace"):
                destination = (root / f"logs/{mode}/source").resolve()
                manifest = prepare_snapshot(root, destination, revision, mode, time.monotonic() + 30)
                excluded_rel = excluded.relative_to(root).as_posix()
                plugin_rel = plugin_source.relative_to(root).as_posix()
                plugin_bin_rel = plugin_bin.relative_to(root).as_posix()
                project_rel = project_import.relative_to(root).as_posix()
                build_bin_rel = build_bin.relative_to(root).as_posix()
                self.assertNotIn(excluded_rel, manifest["files"])
                self.assertFalse((destination / excluded_rel).exists())
                self.assertIn(plugin_rel, manifest["files"])
                self.assertIn(plugin_bin_rel, manifest["files"])
                self.assertIn(project_rel, manifest["files"])
                if mode == "workspace":
                    self.assertNotIn(build_bin_rel, manifest["files"])
                self.assertEqual((destination / plugin_rel).read_text(encoding="utf-8"), "extends Node\n")
                self.assertEqual((destination / project_rel).read_text(encoding="utf-8"), "project-import")


if __name__ == "__main__":
    unittest.main()
