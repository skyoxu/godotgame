#!/usr/bin/env python3
"""Run the Chapter 2.5 technical preflight recommendation pass."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "technical-preflight.v1"

UI_TERMS = {
    "button",
    "buttons",
    "card",
    "cards",
    "choice",
    "choices",
    "combat settlement",
    "deck",
    "dialog",
    "hud",
    "itemlist",
    "map route",
    "menu",
    "reward",
    "rewards",
    "route buttons",
    "save metadata",
    "settlement",
    "shop",
    "state",
    "ui",
    "\u6309\u94ae",
    "\u83dc\u5355",
    "\u754c\u9762",
    "\u5361\u724c",
    "\u5546\u5e97",
    "\u5956\u52b1",
    "\u72b6\u6001",
    "\u5bf9\u8bdd",
}

TWO_D_TERMS = {
    "2d",
    "area2d",
    "characterbody2d",
    "collision",
    "collisions",
    "hitbox",
    "hitboxes",
    "jump",
    "platformer",
    "2\u7ef4",
    "\u4e8c\u7ef4",
    "\u78b0\u649e",
    "\u78b0\u649e\u4f53",
    "\u8df3\u8dc3",
    "\u5e73\u53f0\u8df3\u8dc3",
    "\u547d\u4e2d\u76d2",
}

THREE_D_TERMS = {
    "3d",
    "characterbody3d",
    "fps",
    "tps",
    "vr",
    "ragdoll",
    "rigidbody3d",
    "3\u7ef4",
    "\u4e09\u7ef4",
    "\u7b2c\u4e00\u4eba\u79f0",
    "\u7b2c\u4e09\u4eba\u79f0",
    "\u5e03\u5a03\u5a03",
}

HEAVY_PHYSICS_TERMS = {
    "hundreds of rigid bodies",
    "large physics",
    "many rigid bodies",
    "physics sandbox",
    "rigid bodies",
    "rigidbody",
    "rigidbody2d",
    "vehicle",
    "vehicles",
    "destructible",
    "\u5927\u91cf\u521a\u4f53",
    "\u591a\u4e2a\u521a\u4f53",
    "\u8bb8\u591a\u521a\u4f53",
    "\u6570\u767e\u4e2a\u521a\u4f53",
    "\u7269\u7406\u6c99\u76d2",
    "\u7269\u7406\u6838\u5fc3",
    "\u8f7d\u5177",
    "\u8f66\u8f86",
    "\u521a\u4f53",
    "\u7834\u574f",
}

DETERMINISM_TERMS = {
    "determinism",
    "deterministic",
    "lockstep",
    "replay",
    "rollback",
    "sync",
    "\u786e\u5b9a\u6027",
    "\u53ef\u590d\u73b0",
    "\u56de\u653e",
    "\u91cd\u653e",
    "\u56de\u6eda",
    "\u540c\u6b65",
}

WEB_TERMS = {
    "browser",
    "wasm",
    "web",
    "web/wasm",
    "\u6d4f\u89c8\u5668",
    "\u7f51\u9875",
    "\u7f51\u9875\u7aef",
}

RAPIER_TERMS = {"rapier"}


def _contains_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def _build_route(
    *,
    recommended_action: str,
    candidate_backend: str,
    confidence: str,
    reason_codes: list[str],
    adr_required: bool,
    web_export_risk: str,
    blocking_questions: list[str],
) -> dict[str, Any]:
    chapter3_hints: list[str] = []
    chapter4_hints: list[str] = []
    chapter5_guards = [
        "Do not introduce an engine constraint unless Chapter 2.5 or an accepted ADR marks it required.",
        "Do not remove a required engine spike or ADR constraint during semantic stabilization.",
    ]
    chapter6_gates: list[str] = []

    if recommended_action == "engine_spike_required":
        chapter3_hints.append(f"Create a physics backend spike for {candidate_backend} before implementation tasks.")
        chapter4_hints.append("Chapter 4 must record the backend decision; plugin or global backend changes require ADR or decision-log.")
        chapter6_gates.append("Chapter 6 must not install plugins or modify project.godot until spike evidence and ADR/decision-log exist.")
    elif recommended_action == "use_default_backend":
        chapter3_hints.append(f"Use {candidate_backend} as the default backend unless implementation evidence shows it is insufficient.")
        chapter4_hints.append("Chapter 4 may record an overlay note; no ADR is required for default backend use.")
        chapter6_gates.append("Chapter 6 may use built-in backend behavior but should keep gameplay rules in Game.Core.")

    return {
        "domain": "physics",
        "recommended_action": recommended_action,
        "candidate_backend": candidate_backend,
        "confidence": confidence,
        "reason_codes": sorted(set(reason_codes)),
        "adr_required": adr_required,
        "requires_plugin": candidate_backend.startswith("rapier"),
        "web_export_risk": web_export_risk,
        "apply_mode": "recommend_only",
        "blocking_questions": blocking_questions,
        "chapter3_task_hints": chapter3_hints,
        "chapter4_overlay_hints": chapter4_hints,
        "chapter5_semantic_guards": chapter5_guards,
        "chapter6_acceptance_gates": chapter6_gates,
        "chapter7_ui_notes": [
            "Chapter 7 consumes confirmed runtime state and debug surfaces; it does not choose the engine backend.",
        ],
    }


def _snapshot_has_platform(snapshot: dict[str, Any], platform: str) -> bool:
    raw = snapshot.get("target_platforms") or snapshot.get("platforms") or []
    if isinstance(raw, str):
        values = [raw]
    elif isinstance(raw, list):
        values = [str(item) for item in raw]
    else:
        values = []
    return any(platform.lower() in item.lower() for item in values)


def _snapshot_plugin_present(snapshot: dict[str, Any], name: str) -> bool:
    plugins = snapshot.get("plugins")
    if isinstance(plugins, dict):
        for key, value in plugins.items():
            if name.lower() in str(key).lower() and bool(value):
                return True
    if isinstance(plugins, list):
        return any(name.lower() in str(item).lower() for item in plugins)
    return False


def _reasoned_route(text: str, capability_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    lower = text.lower()
    snapshot = capability_snapshot or {}
    reason_codes: list[str] = []

    ui_state_driven = _contains_any(lower, UI_TERMS)
    two_d = _contains_any(lower, TWO_D_TERMS)
    three_d = _contains_any(lower, THREE_D_TERMS)
    heavy_physics = _contains_any(lower, HEAVY_PHYSICS_TERMS)
    determinism = _contains_any(lower, DETERMINISM_TERMS)
    web = _contains_any(lower, WEB_TERMS) or _snapshot_has_platform(snapshot, "web")
    rapier_named = _contains_any(lower, RAPIER_TERMS)
    rapier_present = _snapshot_plugin_present(snapshot, "rapier")

    if ui_state_driven:
        reason_codes.append("ui_state_driven")
    if two_d:
        reason_codes.append("collision_light")
    if three_d:
        reason_codes.append("physics_3d")
    if heavy_physics:
        reason_codes.append("physics_core_loop")
    if determinism:
        reason_codes.append("determinism_required")
    if web:
        reason_codes.append("web_wasm_target")
    if rapier_named:
        reason_codes.append("plugin_candidate_named")
    if rapier_present:
        reason_codes.append("plugin_present")

    physics_backend_signal = heavy_physics or two_d or three_d or rapier_named

    if heavy_physics and not (rapier_named or determinism or web) and (two_d or not three_d):
        return _build_route(
            recommended_action="engine_spike_required",
            candidate_backend="undecided_physics_backend",
            confidence="low",
            reason_codes=reason_codes or ["physics_core_loop"],
            adr_required=False,
            web_export_risk="medium",
            blocking_questions=[
                "Confirm target platforms before selecting a physics backend.",
                "Compare the built-in Godot backend against plugin candidates before implementation.",
            ],
        )

    if (heavy_physics or rapier_named or (determinism and physics_backend_signal)) and (two_d or not three_d):
        return _build_route(
            recommended_action="engine_spike_required",
            candidate_backend="rapier_2d",
            confidence="medium" if web or determinism else "low",
            reason_codes=reason_codes or ["physics_core_loop"],
            adr_required=True,
            web_export_risk="high" if web else "medium",
            blocking_questions=[
                "Confirm target platforms before selecting a plugin physics backend.",
                "Confirm whether deterministic replay or rollback is a hard requirement.",
            ],
        )

    if heavy_physics and three_d:
        return _build_route(
            recommended_action="engine_spike_required",
            candidate_backend="jolt_3d",
            confidence="medium",
            reason_codes=reason_codes or ["physics_core_loop", "physics_3d"],
            adr_required=False,
            web_export_risk="medium" if web else "low",
            blocking_questions=["Confirm whether built-in Jolt behavior is sufficient before considering plugins."],
        )

    if three_d:
        return _build_route(
            recommended_action="use_default_backend",
            candidate_backend="jolt_3d",
            confidence="medium",
            reason_codes=reason_codes or ["physics_3d"],
            adr_required=False,
            web_export_risk="medium" if web else "low",
            blocking_questions=[],
        )

    if two_d:
        return _build_route(
            recommended_action="use_default_backend",
            candidate_backend="godot_physics_2d",
            confidence="medium",
            reason_codes=reason_codes or ["collision_light"],
            adr_required=False,
            web_export_risk="low",
            blocking_questions=[],
        )

    return _build_route(
        recommended_action="no_engine_change",
        candidate_backend="none",
        confidence="high" if ui_state_driven else "medium",
        reason_codes=reason_codes or ["no_physics_signal"],
        adr_required=False,
        web_export_risk="low",
        blocking_questions=[],
    )


def evaluate_text(
    text: str,
    *,
    source_kind: str,
    source_path: str,
    capability_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_kind = infer_source_kind(source_kind=source_kind, source_path=source_path)
    snapshot = capability_snapshot or {}
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": {
            "kind": resolved_kind,
            "path": source_path,
        },
        "capability_snapshot": snapshot,
        "capability_snapshot_status": capability_snapshot_status(snapshot),
        "technical_preflight": {
            "chapter": "2.5",
            "position": "after Chapter 2 capability scan and before Chapter 3 task generation",
            "engine_route": _reasoned_route(text, snapshot),
        },
    }


def infer_source_kind(*, source_kind: str, source_path: str) -> str:
    if source_kind != "auto":
        return source_kind
    normalized = source_path.replace("\\", "/").lower()
    if "/docs/prototypes/" in normalized or normalized.startswith("docs/prototypes/"):
        return "prototype"
    if "/docs/gdd/" in normalized or normalized.startswith("docs/gdd/"):
        return "gdd"
    if "/.taskmaster/tasks/" in normalized or normalized.startswith(".taskmaster/tasks/"):
        return "task"
    return "auto"


def _read_json_if_present(path_value: str) -> dict[str, Any]:
    if not str(path_value or "").strip():
        return {}
    path = Path(path_value)
    if not path.exists():
        return {"missing": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"invalid_json": str(path), "error": str(exc)}


def capability_snapshot_status(snapshot: dict[str, Any]) -> str:
    if snapshot.get("missing"):
        return "missing"
    if snapshot.get("invalid_json"):
        return "invalid_json"
    return "provided" if snapshot else "not_provided"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Chapter 2.5 technical preflight recommendations.")
    parser.add_argument("--source", required=True, help="GDD, prototype record, or task source to inspect.")
    parser.add_argument("--source-kind", default="auto", choices=["auto", "gdd", "prototype", "task"])
    parser.add_argument("--capability-snapshot", default="", help="Optional Chapter 2 engine capability snapshot JSON.")
    parser.add_argument("--out-json", default="", help="Optional output JSON path.")
    parser.add_argument("--recommendation-only", action="store_true", help="Print compact recommendation instead of full JSON.")
    parser.add_argument("--self-check", action="store_true", help="Accepted for dev_cli parity; this command is read-only.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = Path(args.source)
    if not source.exists():
        print(f"TECHNICAL_PREFLIGHT ERROR: source not found: {source}", file=sys.stderr)
        return 2

    result = evaluate_text(
        source.read_text(encoding="utf-8"),
        source_kind=args.source_kind,
        source_path=str(source.resolve()),
        capability_snapshot=_read_json_if_present(args.capability_snapshot),
    )
    snapshot_status = result["capability_snapshot_status"]
    if snapshot_status in {"missing", "invalid_json"}:
        print(f"TECHNICAL_PREFLIGHT WARNING: capability_snapshot_status={snapshot_status}", file=sys.stderr)

    if args.out_json:
        out = Path(args.out_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    route = result["technical_preflight"]["engine_route"]
    if args.recommendation_only:
        print(
            "TECHNICAL_PREFLIGHT "
            f"action={route['recommended_action']} "
            f"backend={route['candidate_backend']} "
            f"confidence={route['confidence']} "
            f"adr_required={str(route['adr_required']).lower()}"
        )
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
