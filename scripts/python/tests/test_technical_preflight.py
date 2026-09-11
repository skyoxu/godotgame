#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PYTHON_DIR = REPO_ROOT / "scripts" / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))


def _load_module(name: str, relative_path: str):
    path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"failed to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class TechnicalPreflightTests(unittest.TestCase):
    def test_ui_state_driven_gdd_should_not_request_engine_change(self) -> None:
        mod = _load_module("run_technical_preflight_ui_test", "scripts/python/run_technical_preflight.py")

        result = mod.evaluate_text(
            "The run uses card choices, map route buttons, combat settlement UI, rewards, and save metadata.",
            source_kind="gdd",
            source_path="docs/gdd/ui-flow.md",
        )

        route = result["technical_preflight"]["engine_route"]
        self.assertEqual("no_engine_change", route["recommended_action"])
        self.assertEqual("none", route["candidate_backend"])
        self.assertIn("ui_state_driven", route["reason_codes"])
        self.assertEqual([], route["chapter3_task_hints"])

    def test_ordinary_2d_collision_should_use_default_backend_without_adr(self) -> None:
        mod = _load_module("run_technical_preflight_2d_test", "scripts/python/run_technical_preflight.py")

        result = mod.evaluate_text(
            "2D platformer movement uses CharacterBody2D, Area2D hitboxes, jump arcs, simple collisions, and hazards.",
            source_kind="prototype",
            source_path="docs/prototypes/platformer.md",
        )

        route = result["technical_preflight"]["engine_route"]
        self.assertEqual("use_default_backend", route["recommended_action"])
        self.assertEqual("godot_physics_2d", route["candidate_backend"])
        self.assertFalse(route["adr_required"])
        self.assertIn("collision_light", route["reason_codes"])

    def test_web_wasm_deterministic_large_physics_should_require_spike_and_adr(self) -> None:
        mod = _load_module("run_technical_preflight_rapier_test", "scripts/python/run_technical_preflight.py")

        result = mod.evaluate_text(
            "Browser Web/WASM physics sandbox with hundreds of rigid bodies, deterministic replay, rollback sync, and Rapier candidate.",
            source_kind="prototype",
            source_path="docs/prototypes/physics-sandbox.md",
        )

        route = result["technical_preflight"]["engine_route"]
        self.assertEqual("engine_spike_required", route["recommended_action"])
        self.assertEqual("rapier_2d", route["candidate_backend"])
        self.assertTrue(route["adr_required"])
        self.assertIn("determinism_required", route["reason_codes"])
        self.assertIn("web_wasm_target", route["reason_codes"])
        self.assertTrue(any("physics backend spike" in hint.lower() for hint in route["chapter3_task_hints"]))
        self.assertIn("Chapter 4", route["chapter4_overlay_hints"][0])

    def test_mixed_2d_and_3d_heavy_physics_should_not_select_a_2d_backend(self) -> None:
        mod = _load_module("run_technical_preflight_mixed_dimensions_test", "scripts/python/run_technical_preflight.py")
        result = mod.evaluate_text(
            "The Web game combines CharacterBody2D collisions with a deterministic 3D physics sandbox and many rigid bodies.",
            source_kind="gdd",
            source_path="docs/gdd/mixed-dimensions.md",
        )

        route = result["technical_preflight"]["engine_route"]
        self.assertEqual("engine_spike_required", route["recommended_action"])
        self.assertEqual("undecided_physics_backend", route["candidate_backend"])
        self.assertFalse(route["requires_plugin"])

    def test_deterministic_card_replay_without_physics_should_not_request_rapier(self) -> None:
        mod = _load_module("run_technical_preflight_determinism_test", "scripts/python/run_technical_preflight.py")

        result = mod.evaluate_text(
            "Card combat needs deterministic replay, seeded RNG restore, rollback-safe run state, and deck shuffle audit.",
            source_kind="gdd",
            source_path="docs/gdd/card-replay.md",
        )

        route = result["technical_preflight"]["engine_route"]
        self.assertEqual("no_engine_change", route["recommended_action"])
        self.assertEqual("none", route["candidate_backend"])
        self.assertFalse(route["adr_required"])
        self.assertIn("determinism_required", route["reason_codes"])

    def test_chinese_web_deterministic_physics_should_require_rapier_spike(self) -> None:
        mod = _load_module("run_technical_preflight_chinese_physics_test", "scripts/python/run_technical_preflight.py")

        result = mod.evaluate_text(
            "\u6d4f\u89c8\u5668\u7f51\u9875\u7269\u7406\u6c99\u76d2\uff0c\u6570\u767e\u4e2a\u521a\u4f53\uff0c\u786e\u5b9a\u6027\u56de\u653e\u548c\u56de\u6eda\u540c\u6b65\u3002",
            source_kind="prototype",
            source_path="docs/prototypes/physics-sandbox.md",
        )

        route = result["technical_preflight"]["engine_route"]
        self.assertEqual("engine_spike_required", route["recommended_action"])
        self.assertEqual("rapier_2d", route["candidate_backend"])
        self.assertIn("physics_core_loop", route["reason_codes"])
        self.assertIn("determinism_required", route["reason_codes"])
        self.assertIn("web_wasm_target", route["reason_codes"])

    def test_auto_source_kind_should_infer_prototype_path(self) -> None:
        mod = _load_module("run_technical_preflight_source_kind_test", "scripts/python/run_technical_preflight.py")

        result = mod.evaluate_text(
            "Simple UI prototype.",
            source_kind="auto",
            source_path="docs/prototypes/hud-loop.md",
        )

        self.assertEqual("prototype", result["source"]["kind"])

    def test_capability_snapshot_should_contribute_web_target_risk(self) -> None:
        mod = _load_module("run_technical_preflight_capability_test", "scripts/python/run_technical_preflight.py")

        result = mod.evaluate_text(
            "2D physics sandbox with many rigid bodies.",
            source_kind="gdd",
            source_path="docs/gdd/sandbox.md",
            capability_snapshot={
                "target_platforms": ["web", "desktop"],
                "plugins": {"rapier_present": True},
            },
        )

        route = result["technical_preflight"]["engine_route"]
        self.assertEqual("engine_spike_required", route["recommended_action"])
        self.assertEqual("high", route["web_export_risk"])
        self.assertIn("web_wasm_target", route["reason_codes"])
        self.assertIn("plugin_present", route["reason_codes"])

    def test_english_terms_should_match_tokens_instead_of_substrings(self) -> None:
        mod = _load_module("run_technical_preflight_token_boundary_test", "scripts/python/run_technical_preflight.py")
        result = mod.evaluate_text(
            "Async statements use websocket transport for estate updates.",
            source_kind="gdd",
            source_path="docs/gdd/networking.md",
        )

        route = result["technical_preflight"]["engine_route"]
        self.assertEqual("no_engine_change", route["recommended_action"])
        self.assertEqual(["no_physics_signal"], route["reason_codes"])

    def test_disabled_plugin_strings_should_not_count_as_present(self) -> None:
        mod = _load_module("run_technical_preflight_plugin_state_test", "scripts/python/run_technical_preflight.py")
        for value in ("false", "disabled", "0"):
            with self.subTest(value=value):
                result = mod.evaluate_text(
                    "Simple 2D collisions.",
                    source_kind="gdd",
                    source_path="docs/gdd/collision.md",
                    capability_snapshot={"plugins": {"rapier": value}},
                )
                self.assertNotIn("plugin_present", result["technical_preflight"]["engine_route"]["reason_codes"])

    def test_enabled_plugin_strings_should_count_as_present(self) -> None:
        mod = _load_module("run_technical_preflight_enabled_plugin_state_test", "scripts/python/run_technical_preflight.py")
        result = mod.evaluate_text(
            "Simple 2D collisions.",
            source_kind="gdd",
            source_path="docs/gdd/collision.md",
            capability_snapshot={"plugins": {"rapier": "enabled"}},
        )

        self.assertIn("plugin_present", result["technical_preflight"]["engine_route"]["reason_codes"])

    def test_json_snapshot_reader_should_report_non_object_payload(self) -> None:
        mod = _load_module("run_technical_preflight_snapshot_shape_test", "scripts/python/run_technical_preflight.py")
        with tempfile.TemporaryDirectory() as td:
            snapshot = Path(td) / "snapshot.json"
            snapshot.write_text("[]\n", encoding="utf-8")
            result = mod._read_json_if_present(str(snapshot))

        self.assertEqual("invalid_shape", result["snapshot_error"])
        self.assertEqual("invalid_shape", mod.capability_snapshot_status(result))

    def test_generic_vehicle_physics_should_not_bind_rapier_without_stronger_signal(self) -> None:
        mod = _load_module("run_technical_preflight_vehicle_test", "scripts/python/run_technical_preflight.py")

        result = mod.evaluate_text(
            "Vehicle physics with collisions and mobile export risk.",
            source_kind="prototype",
            source_path="docs/prototypes/vehicle.md",
        )

        route = result["technical_preflight"]["engine_route"]
        self.assertEqual("engine_spike_required", route["recommended_action"])
        self.assertEqual("undecided_physics_backend", route["candidate_backend"])
        self.assertFalse(route["requires_plugin"])

    def test_main_should_write_json_summary(self) -> None:
        mod = _load_module("run_technical_preflight_main_test", "scripts/python/run_technical_preflight.py")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "docs" / "prototypes" / "vehicle.md"
            out = root / "logs" / "technical-preflight.json"
            source.parent.mkdir(parents=True)
            source.write_text("Vehicle physics with collisions and mobile export risk.", encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                rc = mod.main(["--source", str(source), "--source-kind", "prototype", "--out-json", str(out)])

            self.assertEqual(0, rc)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual("technical-preflight.v1", payload["schema"])
            self.assertEqual(str(source), payload["source"]["path"])
            self.assertIn("engine_route", payload["technical_preflight"])

    def test_main_should_write_resolved_source_path_for_relative_source(self) -> None:
        mod = _load_module("run_technical_preflight_relative_source_test", "scripts/python/run_technical_preflight.py")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "docs" / "prototypes" / "relative.md"
            out = root / "logs" / "technical-preflight.json"
            source.parent.mkdir(parents=True)
            source.write_text("Simple UI prototype.", encoding="utf-8")
            old_cwd = Path.cwd()
            try:
                import os

                os.chdir(root)
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = mod.main(["--source", "docs/prototypes/relative.md", "--out-json", str(out)])
            finally:
                os.chdir(old_cwd)

            payload = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(0, rc)
        self.assertEqual(str(source.resolve()), payload["source"]["path"])

    def test_main_should_warn_when_capability_snapshot_is_missing(self) -> None:
        mod = _load_module("run_technical_preflight_missing_snapshot_test", "scripts/python/run_technical_preflight.py")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "docs" / "prototypes" / "ui.md"
            missing_snapshot = root / "logs" / "missing-snapshot.json"
            source.parent.mkdir(parents=True)
            source.write_text("Simple UI prototype.", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                rc = mod.main(
                    [
                        "--source",
                        str(source),
                        "--capability-snapshot",
                        str(missing_snapshot),
                        "--recommendation-only",
                    ]
                )

            result = mod.evaluate_text(
                "Simple UI prototype.",
                source_kind="prototype",
                source_path=str(source),
                capability_snapshot={"missing": str(missing_snapshot)},
            )

        self.assertEqual(0, rc)
        self.assertIn("TECHNICAL_PREFLIGHT WARNING", stderr.getvalue())
        self.assertEqual("missing", result["capability_snapshot_status"])

    def test_python_sources_should_keep_chinese_terms_ascii_escaped(self) -> None:
        checked = [
            REPO_ROOT / "scripts" / "python" / "run_technical_preflight.py",
            REPO_ROOT / "scripts" / "python" / "tests" / "test_technical_preflight.py",
        ]
        offenders: list[str] = []
        for path in checked:
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if any(ord(ch) > 127 for ch in line):
                    offenders.append(f"{path.relative_to(REPO_ROOT).as_posix()}:{line_no}")

        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
