from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _knowledge_catalog_builder import GitSnapshot, build_layers
from project_health_knowledge import write_json

OUTPUT_PATHS = {
    "snapshot": Path("knowledge/snapshots/repository-source-snapshot.v1.json"),
    "catalog": Path("knowledge/catalogs/repository-knowledge-catalog.v1.json"),
    "projections": Path("knowledge/projections/consumer-projections.v1.json"),
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def build(root: Path, authority_ref: str = "refs/heads/main") -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    policies = _load(root / "knowledge/policies/consumer-policies.v1.json")
    exclusions = _load(root / "knowledge/policies/source-exclusions.v1.json")
    return build_layers(GitSnapshot(root, authority_ref), exclusions, policies)


def check_outputs(root: Path, outputs: dict[Path, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    for relative, expected in outputs.items():
        path = root / relative
        if not path.is_file():
            issues.append(f"missing:{relative.as_posix()}")
            continue
        try:
            current = _load(path)
        except (OSError, json.JSONDecodeError):
            issues.append(f"invalid:{relative.as_posix()}")
            continue
        if current != expected:
            issues.append(f"stale:{relative.as_posix()}")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build repository Knowledge catalog layers from a trusted Git ref.")
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--authority-ref", default="refs/heads/main")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = args.repository_root.resolve()
    snapshot, catalog, projections = build(root, args.authority_ref)
    outputs = {OUTPUT_PATHS["snapshot"]: snapshot, OUTPUT_PATHS["catalog"]: catalog, OUTPUT_PATHS["projections"]: projections}
    if args.write:
        for relative, value in outputs.items():
            write_json(root / relative, value)
    issues = check_outputs(root, outputs) if args.check else []
    print(json.dumps({
        "status": "stale" if issues else "ok", "authority_ref": args.authority_ref,
        "commit": snapshot["commit"], "sources": len(snapshot["sources"]), "modules": len(catalog["modules"]),
        "written": args.write, "checked": args.check, "issues": issues,
    }, ensure_ascii=False, sort_keys=True))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
