#!/usr/bin/env python3
"""Create a minimal Godot prototype scene scaffold under Game.Godot/Prototypes."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8", newline="\n")


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_rel(path: Path, *, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def sanitize_slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", str(value or "").strip())
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-_")
    return cleaned or "prototype"


def slug_to_pascal(slug: str) -> str:
    parts = [part for part in re.split(r"[-_]+", slug) if part]
    return "".join(part[:1].upper() + part[1:] for part in parts) or "Prototype"


def render_script(*, class_name: str, scene_root: str) -> str:
    return "\n".join(
        [
            "using Godot;",
            "",
            "namespace Game.Godot.Prototypes;",
            "",
            f"public partial class {class_name} : {scene_root}",
            "{",
            "    public override void _Ready()",
            "    {",
            '        GD.Print("Prototype scaffold ready: replace this scene with the minimum playable loop.");',
            "    }",
            "}",
            "",
        ]
    )


def render_scene(*, class_name: str, scene_root: str, script_res_path: str) -> str:
    lines = [
        "[gd_scene load_steps=2 format=3]",
        "",
        f'[ext_resource type="Script" path="{script_res_path}" id="1"]',
        "",
        f'[node name="{class_name}" type="{scene_root}"]',
        'script = ExtResource("1")',
    ]
    if scene_root == "Control":
        lines += [
            "layout_mode = 3",
            "anchors_preset = 15",
            "anchor_right = 1.0",
            "anchor_bottom = 1.0",
            "grow_horizontal = 2",
            "grow_vertical = 2",
            "",
            '[node name="PrototypeHint" type="Label" parent="."]',
            "layout_mode = 0",
            "offset_left = 24.0",
            "offset_top = 24.0",
            "offset_right = 640.0",
            "offset_bottom = 80.0",
            'text = "Replace this scaffold with your minimum playable loop."',
        ]
    else:
        lines += [
            "",
            '[node name="PrototypeLoop" type="Node2D" parent="."]',
        ]
    lines.append("")
    return "\n".join(lines)


def _replace_template_tokens(path: Path, *, old_slug: str, new_slug: str, old_class: str, new_class: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(old_slug, new_slug)
    text = text.replace(old_class, new_class)
    write_text(path, text)


def create_from_template_manifest(
    *,
    root: Path,
    slug: str,
    prototype_root: str,
    manifest_path: Path,
    force: bool,
) -> int:
    manifest = read_json(manifest_path)
    paths = manifest.get("paths") if isinstance(manifest.get("paths"), dict) else {}
    source_root_rel = str(paths.get("scene_template_root") or "").strip()
    if not source_root_rel:
        print("PROTOTYPE_SCENE ERROR: template manifest missing paths.scene_template_root.", file=sys.stderr)
        return 2

    source_root = (root / source_root_rel).resolve()
    if not source_root.exists() or not source_root.is_dir():
        print(f"PROTOTYPE_SCENE ERROR: template root not found: {repo_rel(source_root, root=root)}", file=sys.stderr)
        return 2

    old_slug = source_root.name
    default_scene_rel = str(paths.get("default_scene") or "").strip()
    default_script_rel = str(paths.get("default_script") or "").strip()
    old_scene_name = Path(default_scene_rel).stem if default_scene_rel else ""
    old_script_name = Path(default_script_rel).stem if default_script_rel else ""
    old_class = old_script_name or old_scene_name or f"{slug_to_pascal(old_slug)}Prototype"
    new_class = f"{slug_to_pascal(slug)}Prototype"
    target_root = root / prototype_root / slug
    target_scene = target_root / f"{new_class}.tscn"
    target_script = target_root / "Scripts" / f"{new_class}.cs"

    if target_root.exists() and not force:
        print(
            f"PROTOTYPE_SCENE ERROR: scaffold already exists for slug={slug}; pass --force to overwrite.",
            file=sys.stderr,
        )
        return 1

    if target_root.exists():
        shutil.rmtree(target_root)
    shutil.copytree(source_root, target_root)

    old_scene = target_root / f"{old_class}.tscn"
    old_script = target_root / "Scripts" / f"{old_class}.cs"
    if old_scene.exists() and old_scene != target_scene:
        old_scene.rename(target_scene)
    if old_script.exists() and old_script != target_script:
        old_script.rename(target_script)

    for item in target_root.rglob("*"):
        if item.is_file() and item.suffix.lower() in {".tscn", ".cs", ".gd", ".tres", ".md", ".json"}:
            _replace_template_tokens(item, old_slug=old_slug, new_slug=slug, old_class=old_class, new_class=new_class)

    print(
        "PROTOTYPE_SCENE created_from_template "
        f"scene={repo_rel(target_scene, root=root)} "
        f"script={repo_rel(target_script, root=root)} "
        f"template={repo_rel(source_root, root=root)}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Create a minimal prototype scene scaffold.")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--prototype-root", default="Game.Godot/Prototypes")
    ap.add_argument("--scene-root", default="Control", choices=["Control", "Node2D"])
    ap.add_argument("--template-manifest", default="", help="Copy a prototype template described by a manifest instead of creating a blank scaffold.")
    ap.add_argument("--force", action="store_true", help="Overwrite the scaffold when files already exist.")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = (Path(args.repo_root).resolve() if str(args.repo_root or "").strip() else repo_root())
    slug = sanitize_slug(args.slug)
    pascal = slug_to_pascal(slug)
    class_name = f"{pascal}Prototype"
    if str(args.template_manifest or "").strip():
        manifest_path = Path(str(args.template_manifest))
        if not manifest_path.is_absolute():
            manifest_path = root / manifest_path
        return create_from_template_manifest(
            root=root,
            slug=slug,
            prototype_root=str(args.prototype_root),
            manifest_path=manifest_path.resolve(),
            force=bool(args.force),
        )

    prototype_dir = root / args.prototype_root / slug
    scene_path = prototype_dir / f"{class_name}.tscn"
    script_path = prototype_dir / "Scripts" / f"{class_name}.cs"
    assets_dir = prototype_dir / "Assets"

    if (scene_path.exists() or script_path.exists()) and not args.force:
        print(
            f"PROTOTYPE_SCENE ERROR: scaffold already exists for slug={slug}; pass --force to overwrite.",
            file=sys.stderr,
        )
        return 1

    ensure_dir(assets_dir)
    script_res_path = f"res://{args.prototype_root.strip('/').replace(chr(92), '/')}/{slug}/Scripts/{class_name}.cs"
    write_text(script_path, render_script(class_name=class_name, scene_root=str(args.scene_root)))
    write_text(
        scene_path,
        render_scene(
            class_name=class_name,
            scene_root=str(args.scene_root),
            script_res_path=script_res_path,
        ),
    )
    print(
        "PROTOTYPE_SCENE created "
        f"scene={scene_path.relative_to(root).as_posix()} "
        f"script={script_path.relative_to(root).as_posix()}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
