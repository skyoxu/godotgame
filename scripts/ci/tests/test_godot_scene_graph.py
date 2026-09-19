from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/python"))

from _godot_scene_graph import build_scene_graph


class GodotSceneGraphTests(unittest.TestCase):
    def test_main_and_packed_child_are_confirmed(self) -> None:
        graph = build_scene_graph({
            "project.godot": '[application]\nrun/main_scene="res://Scenes/Main.tscn"\n',
            "Scenes/Main.tscn": '[gd_scene]\n[ext_resource type="PackedScene" path="res://Scenes/Panel.tscn" id="1"]\n[node name="Main" type="Node"]\n[node name="Panel" parent="." instance=ExtResource("1")]\n',
            "Scenes/Panel.tscn": '[gd_scene]\n[node name="Panel" type="Control"]\n',
        })
        self.assertEqual(graph["main_scene"], "Scenes/Main.tscn")
        self.assertEqual(graph["nodes"]["Scenes/Main.tscn"]["classification"], "confirmed-reachable")
        self.assertEqual(graph["nodes"]["Scenes/Panel.tscn"]["classification"], "confirmed-reachable")
        edge = next(item for item in graph["edges"] if item["target"] == "Scenes/Panel.tscn")
        self.assertEqual(edge["evidence_level"], "effective")

    def test_possible_literal_does_not_make_scene_reachable(self) -> None:
        graph = build_scene_graph({
            "project.godot": '[application]\nrun/main_scene="res://Main.tscn"\n',
            "Main.tscn": '[gd_scene]\n[ext_resource type="Script" path="res://Main.gd" id="1"]\n[node name="Main" type="Node"]\nscript = ExtResource("1")\n',
            "Main.gd": 'const NEXT_SCENE = "res://Other.tscn"\n',
            "Other.tscn": '[gd_scene]\n[node name="Other" type="Node"]\n',
        })
        edge = next(item for item in graph["edges"] if item.get("kind") == "script-reference")
        self.assertEqual(edge["evidence_level"], "possible")
        self.assertEqual(graph["nodes"]["Other.tscn"]["classification"], "unreachable-candidate")

    def test_explicit_switch_makes_scene_reachable(self) -> None:
        graph = build_scene_graph({
            "project.godot": '[application]\nrun/main_scene="res://Main.tscn"\n',
            "Main.tscn": '[gd_scene]\n[ext_resource type="Script" path="res://Main.gd" id="1"]\n[node name="Main" type="Node"]\nscript = ExtResource("1")\n',
            "Main.gd": 'func go():\n    change_scene_to_file("res://Other.tscn")\n',
            "Other.tscn": '[gd_scene]\n[node name="Other" type="Node"]\n',
        })
        edge = next(item for item in graph["edges"] if item.get("kind") == "script-reference")
        self.assertEqual(edge["evidence_level"], "effective")
        self.assertEqual(graph["nodes"]["Other.tscn"]["classification"], "confirmed-reachable")

    def test_scene_constant_used_by_switch_is_effective(self) -> None:
        graph = build_scene_graph({
            "project.godot": '[application]\nrun/main_scene="res://Main.tscn"\n',
            "Main.tscn": '[gd_scene]\n[ext_resource type="Script" path="res://Main.gd" id="1"]\n[node name="Main" type="Node"]\nscript = ExtResource("1")\n',
            "Main.gd": 'const NEXT_SCENE = "res://Other.tscn"\nfunc go():\n    _switch_to(NEXT_SCENE)\n',
            "Other.tscn": '[gd_scene]\n[node name="Other" type="Node"]\n',
        })
        edge = next(item for item in graph["edges"] if item.get("kind") == "script-reference")
        self.assertEqual(edge["evidence_level"], "effective")
        self.assertEqual(graph["nodes"]["Other.tscn"]["classification"], "confirmed-reachable")

    def test_dynamic_load_is_unknown_and_cycle_is_bounded(self) -> None:
        dynamic = build_scene_graph({
            "project.godot": "",
            "Unused.tscn": "[gd_scene]\n",
            "Loader.gd": "var scene = load(scene_path)\n",
        })
        self.assertTrue(any(item.get("classification") == "dynamic-unknown" for item in dynamic["code_references"]))
        cycle = build_scene_graph({
            "project.godot": 'run/main_scene="res://A.tscn"',
            "A.tscn": '[gd_scene]\n[ext_resource type="PackedScene" path="res://B.tscn" id="1"]\n[node name="A" type="Node"]\n[node name="B" parent="." instance=ExtResource("1")]',
            "B.tscn": '[gd_scene]\n[ext_resource type="PackedScene" path="res://A.tscn" id="1"]\n[node name="B" type="Node"]\n[node name="A" parent="." instance=ExtResource("1")]',
        })
        self.assertTrue(any(item.get("kind") == "cycle" for item in cycle["diagnostics"]))

    def test_static_config_and_asset_references_are_preserved(self) -> None:
        graph = build_scene_graph({
            "project.godot": '[application]\nrun/main_scene="res://Main.tscn"\n',
            "Main.tscn": '[gd_scene]\n[ext_resource type="Script" path="res://Main.gd" id="1"]\n[node name="Main" type="Node"]\nscript = ExtResource("1")\n',
            "Main.gd": 'var cfg = load("res://Data/feature.json")\nvar icon = load("res://Assets/icon.png")\n',
        }, known_paths=["project.godot", "Main.tscn", "Main.gd", "Data/feature.json", "Assets/icon.png"])
        refs = graph["code_references"]
        self.assertTrue(any(item.get("kind") == "config-reference" and item.get("target") == "Data/feature.json" for item in refs))
        self.assertTrue(any(item.get("kind") == "asset-reference" and item.get("target") == "Assets/icon.png" for item in refs))

    def test_event_route_is_effective(self) -> None:
        graph = build_scene_graph({
            "project.godot": '[application]\nrun/main_scene="res://Main.tscn"\n',
            "Main.tscn": '[gd_scene]\n[ext_resource type="PackedScene" path="res://Menu.tscn" id="1"]\n[node name="Main" type="Node"]\n[node name="Menu" parent="." instance=ExtResource("1")]\n',
            "Menu.tscn": '[gd_scene]\n[ext_resource type="Script" path="res://Menu.gd" id="1"]\n[node name="Menu" type="Control"]\nscript = ExtResource("1")\n',
            "Menu.gd": 'func activate():\n    EventBus.PublishSimple("ui.feature.open", "ui", "{}")\n',
            "Controller.gd": 'func handle(kind):\n    if kind == "ui.feature.open":\n        change_scene_to_file("res://Feature.tscn")\n',
            "Feature.tscn": '[gd_scene]\n[node name="Feature" type="Control"]\n',
        })
        route = next(item for item in graph["edges"] if item.get("kind") == "event-route")
        self.assertEqual(route["source"], "Menu.tscn")
        self.assertEqual(route["target"], "Feature.tscn")
        self.assertEqual(route["evidence_level"], "effective")
        self.assertEqual(graph["nodes"]["Feature.tscn"]["classification"], "confirmed-reachable")


if __name__ == "__main__":
    unittest.main()
