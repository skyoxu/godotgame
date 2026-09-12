from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from _knowledge_catalog_builder import canonical_bytes
from _knowledge_locator_core import locate
from build_knowledge_catalog import build
from project_health_knowledge import write_json

POLICY_PATH = Path("knowledge/policies/consumer-policies.v1.json")
EXCLUSIONS_PATH = Path("knowledge/policies/source-exclusions.v1.json")
SUITE_PATH = Path("knowledge/evaluation/queries.v1.json")
CANONICAL = {
    "snapshot": Path("knowledge/snapshots/repository-source-snapshot.v1.json"),
    "catalog": Path("knowledge/catalogs/repository-knowledge-catalog.v1.json"),
    "projections": Path("knowledge/projections/consumer-projections.v1.json"),
}
INDEX_ROOT = Path("knowledge/indexes")
ARTIFACTS = ("snapshot", "catalog", "projections", "policies", "exclusions", "query_suite", "evaluation")
CONTROL_PLANE_PATHS = (
    "knowledge/policies", "knowledge/evaluation",
    "scripts/python/_knowledge_catalog_builder.py", "scripts/python/_knowledge_locator_core.py",
    "scripts/python/build_knowledge_catalog.py", "scripts/python/knowledge_locator.py",
    "scripts/python/publish_knowledge_catalog.py", "scripts/python/prepare_knowledge_context.py",
    "scripts/python/freeze_knowledge_context.py",
)


class PublicationBlocked(ValueError):
    def __init__(self, reason: str, details: dict[str, Any] | None = None):
        super().__init__(reason)
        self.reason = reason
        self.details = details


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _control_plane_clean(root: Path) -> bool:
    completed = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--", *CONTROL_PLANE_PATHS],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    return completed.returncode == 0 and not completed.stdout.strip()


def _evaluate(catalog: dict[str, Any], projections: dict[str, Any], policies: dict[str, Any], suite: dict[str, Any]) -> dict[str, Any]:
    policy_by = {item.get("consumer"): item for item in policies.get("policies", []) if isinstance(item, dict)}
    projection_by = {item.get("consumer"): item for item in projections.get("projections", []) if isinstance(item, dict)}
    failures: list[dict[str, Any]] = []
    cases = list(suite.get("cases", []))
    for case in cases:
        consumer = case.get("consumer")
        policy = policy_by.get(consumer)
        projection = projection_by.get(consumer)
        if not policy or not projection:
            failures.append({"id": case.get("id"), "reason": "consumer_policy_or_projection_missing"})
            continue
        result = locate({"query": case.get("query")}, catalog, policy, set(projection.get("eligible_module_ids", [])), int(policy.get("max_candidates", 12)))
        paths = {item.get("path") for item in result.get("candidates", [])}
        expected = set(case.get("must_include_paths", []))
        forbidden = set(case.get("forbidden_paths", []))
        if result.get("status") != case.get("expected_status", "matched") or not expected <= paths or forbidden & paths:
            failures.append({"id": case.get("id"), "reason": "query_expectation_failed", "candidate_paths": sorted(path for path in paths if path)})
    return {"schema": "godot-project-knowledge.evaluation-report.v1", "status": "passed" if not failures else "failed", "passed": len(cases) - len(failures), "total": len(cases), "failures": failures}


def _manifest(artifacts: dict[str, dict[str, Any]], authority_ref: str, commit: str) -> dict[str, Any]:
    hashes = {name: _hash(value) for name, value in sorted(artifacts.items())}
    basis = {"authority_ref": authority_ref, "main_commit": commit, "source_snapshot_id": artifacts["snapshot"]["snapshot_id"], "artifacts": hashes}
    generation_id = hashlib.sha256(canonical_bytes(basis)).hexdigest()
    return {"schema": "godot-project-knowledge.publication-generation.v1", "generation_id": generation_id, **basis}


def _pointer(manifest: dict[str, Any]) -> dict[str, Any]:
    return {"schema": "godot-project-knowledge.index-pointer.v1", "generation_id": manifest["generation_id"], "generation_sha256": _hash(manifest), "source_snapshot_id": manifest["source_snapshot_id"], "authority_ref": manifest["authority_ref"], "main_commit": manifest["main_commit"]}


def _generation_dir(root: Path, generation_id: str) -> Path:
    return root / INDEX_ROOT / "generations" / generation_id


def _validate_generation(root: Path, pointer: dict[str, Any], require_current_ref: bool) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    generation_id = pointer.get("generation_id")
    if not isinstance(generation_id, str) or not re.fullmatch(r"[0-9a-f]{64}", generation_id):
        raise PublicationBlocked("generation_id_invalid")
    generation = _generation_dir(root, generation_id)
    manifest = _load(generation / "manifest.json")
    if manifest.get("generation_id") != generation_id or pointer.get("generation_sha256") != _hash(manifest):
        raise PublicationBlocked("generation_manifest_binding_invalid")
    artifacts: dict[str, dict[str, Any]] = {}
    for name in ARTIFACTS:
        artifact = _load(generation / f"{name}.json")
        if manifest.get("artifacts", {}).get(name) != _hash(artifact):
            raise PublicationBlocked(f"generation_artifact_hash_invalid:{name}")
        artifacts[name] = artifact
    if require_current_ref:
        current = subprocess.run(["git", "-C", str(root), "rev-parse", str(manifest.get("authority_ref"))], capture_output=True, text=True, encoding="utf-8", check=False)
        if current.returncode or current.stdout.strip() != manifest.get("main_commit"):
            raise PublicationBlocked("authority_ref_moved")
    return manifest, artifacts


def publish(root: Path, authority_ref: str = "refs/heads/main") -> dict[str, Any]:
    if not _control_plane_clean(root):
        raise PublicationBlocked("dirty_control_plane")
    policies = _load(root / POLICY_PATH)
    exclusions = _load(root / EXCLUSIONS_PATH)
    suite = _load(root / SUITE_PATH)
    snapshot, catalog, projections = build(root, authority_ref)
    evaluation = _evaluate(catalog, projections, policies, suite)
    if evaluation["status"] != "passed":
        raise PublicationBlocked("repository_query_evaluation_failed", {"evaluation": evaluation})
    artifacts = {"snapshot": snapshot, "catalog": catalog, "projections": projections, "policies": policies, "exclusions": exclusions, "query_suite": suite, "evaluation": evaluation}
    manifest = _manifest(artifacts, authority_ref, snapshot["commit"])
    generation = _generation_dir(root, manifest["generation_id"])
    for name, value in artifacts.items():
        write_json(generation / f"{name}.json", value)
    write_json(generation / "manifest.json", manifest)
    pointer = _pointer(manifest)
    _validate_generation(root, pointer, True)
    for name in ("snapshot", "catalog", "projections"):
        write_json(root / CANONICAL[name], artifacts[name])
    write_json(root / INDEX_ROOT / "current.json", pointer)
    write_json(root / INDEX_ROOT / "last-known-good.json", pointer)
    return {"status": "published", "pointer": pointer, "evaluation": evaluation}


def check_current(root: Path) -> dict[str, Any]:
    pointer_path = root / INDEX_ROOT / "current.json"
    if not pointer_path.is_file():
        raise PublicationBlocked("current_pointer_missing")
    pointer = _load(pointer_path)
    manifest, artifacts = _validate_generation(root, pointer, True)
    for name in ("snapshot", "catalog", "projections"):
        if _load(root / CANONICAL[name]) != artifacts[name]:
            raise PublicationBlocked(f"canonical_artifact_mismatch:{name}")
    if _load(root / POLICY_PATH) != artifacts["policies"]:
        raise PublicationBlocked("current_policy_mismatch")
    if _load(root / EXCLUSIONS_PATH) != artifacts["exclusions"]:
        raise PublicationBlocked("current_exclusions_mismatch")
    if _load(root / SUITE_PATH) != artifacts["query_suite"]:
        raise PublicationBlocked("current_query_suite_mismatch")
    if artifacts["evaluation"].get("status") != "passed":
        raise PublicationBlocked("published_evaluation_not_passed")
    return {"status": "current", "pointer": pointer, "manifest": manifest}


def restore_lkg(root: Path) -> dict[str, Any]:
    path = root / INDEX_ROOT / "last-known-good.json"
    if not path.is_file():
        raise PublicationBlocked("lkg_pointer_missing")
    pointer = _load(path)
    _, artifacts = _validate_generation(root, pointer, False)
    for name in ("snapshot", "catalog", "projections"):
        write_json(root / CANONICAL[name], artifacts[name])
    write_json(root / INDEX_ROOT / "current.json", pointer)
    return {"status": "restored", "pointer": pointer}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish/check/recover validated repository Knowledge generations.")
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--authority-ref", default="refs/heads/main")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--restore-lkg", action="store_true")
    args = parser.parse_args(argv)
    root = args.repository_root.resolve()
    try:
        result = publish(root, args.authority_ref) if args.publish else check_current(root) if args.check else restore_lkg(root)
    except PublicationBlocked as exc:
        payload: dict[str, Any] = {"schema": "godot-project-knowledge.publication-result.v1", "status": "blocked", "reason": exc.reason}
        if exc.details:
            payload["details"] = exc.details
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    print(json.dumps({"schema": "godot-project-knowledge.publication-result.v1", **result}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
