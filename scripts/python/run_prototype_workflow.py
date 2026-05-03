#!/usr/bin/env python3
"""Top-level router for the prototype 7-day playable Godot workflow."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def today_str() -> str:
    return dt.date.today().isoformat()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8", newline="\n")


def write_json(path: Path, payload: object) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sanitize_slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", str(value or "").strip())
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-_")
    return cleaned or "prototype"


_LIST_FIELD_ALIASES: dict[str, list[str]] = {
    "status": ["status", "状态"],
    "owner": ["owner", "负责人"],
    "date": ["date", "日期"],
    "related_formal_task_ids": ["related formal task ids", "关联正式任务 id"],
    "hypothesis": ["hypothesis", "假设"],
    "core_player_fantasy": ["core player fantasy", "核心玩家幻想"],
    "minimum_playable_loop": ["minimum playable loop", "最小可玩循环"],
    "success_criteria": ["success criteria", "成功标准"],
    "promote_signals": ["promote signals", "进入 promote 的信号"],
    "archive_signals": ["archive signals", "进入 archive 的信号"],
    "discard_signals": ["discard signals", "进入 discard 的信号"],
    "decision": ["decision", "结论"],
    "next_step": ["next step", "下一步"],
}


def _normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().strip(":：")).lower()


def parse_template_content(content: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    lines = content.splitlines()
    current_section: str | None = None
    scope_mode: str | None = None
    evidence_mode: str | None = None
    section_values: dict[str, list[str]] = {}
    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            if title.startswith("Prototype:"):
                payload["slug"] = sanitize_slug(title.split(":", 1)[1].strip())
            elif title.startswith("原型："):
                payload["slug"] = sanitize_slug(title.split("：", 1)[1].strip())
            continue
        if stripped.startswith("- "):
            entry = stripped[2:].strip()
            if current_section == "scope":
                lowered_entry = _normalize_heading(entry)
                if lowered_entry in {"in", "纳入"}:
                    scope_mode = "in"
                elif lowered_entry in {"out", "排除"}:
                    scope_mode = "out"
                elif scope_mode == "in":
                    section_values.setdefault("scope_in", []).append(entry)
                elif scope_mode == "out":
                    section_values.setdefault("scope_out", []).append(entry)
                continue
            if current_section == "evidence":
                section_values.setdefault("evidence", []).append(entry)
                continue
            matched_meta = False
            for canonical, aliases in _LIST_FIELD_ALIASES.items():
                for alias in aliases:
                    if entry.lower().startswith(alias.lower() + ":") or entry.lower().startswith(alias.lower() + "："):
                        _, value = re.split(r"[:：]", entry, maxsplit=1)
                        section_values.setdefault(canonical, []).append(value.strip())
                        matched_meta = True
                        break
                if matched_meta:
                    break
            if matched_meta and current_section is None:
                continue
            if current_section:
                section_values.setdefault(current_section, []).append(entry)
            continue
        if stripped.startswith("## "):
            heading = _normalize_heading(stripped[3:])
            current_section = None
            scope_mode = None
            evidence_mode = None
            for canonical, aliases in _LIST_FIELD_ALIASES.items():
                if heading in [_normalize_heading(item) for item in aliases]:
                    current_section = canonical
                    break
            if heading == "范围" or heading == "scope":
                current_section = "scope"
            elif heading == "证据" or heading == "evidence":
                current_section = "evidence"
            continue
        if current_section == "scope":
            lowered = _normalize_heading(stripped)
            if lowered in {"in", "纳入"}:
                scope_mode = "in"
            elif lowered in {"out", "排除"}:
                scope_mode = "out"
            continue
        if current_section == "evidence":
            lowered = _normalize_heading(stripped)
            if lowered in {"code paths", "代码路径"}:
                evidence_mode = "code"
            elif lowered in {"logs / media / notes", "日志 / 媒体 / 备注"}:
                evidence_mode = "notes"
            elif evidence_mode:
                section_values.setdefault("evidence", []).append(stripped)
            continue
    for key, values in section_values.items():
        if key == "slug":
            payload["slug"] = sanitize_slug(values[0]) if values else ""
        elif key in {"status", "owner", "date", "decision", "next_step"}:
            payload[key] = values[0] if values else ""
        else:
            payload[key] = [item for item in values if item]
    return payload


def normalize_prototype_payload(raw: dict[str, Any], *, today: str | None = None) -> dict[str, Any]:
    current_day = today or today_str()
    normalized: dict[str, Any] = {
        "slug": sanitize_slug(raw.get("slug") or "") if str(raw.get("slug") or "").strip() else "",
        "status": str(raw.get("status") or "active").strip() or "active",
        "owner": str(raw.get("owner") or "operator").strip() or "operator",
        "date": str(raw.get("date") or current_day).strip() or current_day,
        "related_formal_task_ids": list(raw.get("related_formal_task_ids") or ["none yet"]),
        "hypothesis": _first(raw.get("hypothesis")) or "",
        "core_player_fantasy": _first(raw.get("core_player_fantasy")) or "",
        "minimum_playable_loop": _first(raw.get("minimum_playable_loop")) or "",
        "scope_in": list(raw.get("scope_in") or ["TBD"]),
        "scope_out": list(raw.get("scope_out") or ["TBD"]),
        "success_criteria": list(raw.get("success_criteria") or []),
        "promote_signals": list(raw.get("promote_signals") or ["TBD"]),
        "archive_signals": list(raw.get("archive_signals") or ["TBD"]),
        "discard_signals": list(raw.get("discard_signals") or ["TBD"]),
        "evidence": list(raw.get("evidence") or ["TBD"]),
        "decision": str(raw.get("decision") or "pending").strip() or "pending",
        "next_step": str(raw.get("next_step") or "Proceed to the next prototype workflow confirmation step.").strip()
        or "Proceed to the next prototype workflow confirmation step.",
    }
    return normalized


def _first(value: Any) -> str:
    if isinstance(value, list):
        return str(value[0]).strip() if value else ""
    return str(value or "").strip()


def required_field_names(payload: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    required_scalars = ["slug", "hypothesis", "core_player_fantasy", "minimum_playable_loop"]
    for key in required_scalars:
        if not str(payload.get(key) or "").strip():
            missing.append(key)
    if not payload.get("success_criteria"):
        missing.append("success_criteria")
    return missing


def required_questions_for_missing_payload(payload: dict[str, Any]) -> list[dict[str, str]]:
    normalized = normalize_prototype_payload(payload)
    prompts = {
        "slug": "prototype slug",
        "hypothesis": "prototype hypothesis",
        "core_player_fantasy": "core player fantasy",
        "minimum_playable_loop": "minimum playable loop",
        "success_criteria": "success criteria (comma-separated if multiple)",
    }
    return [{"id": key, "prompt": prompts[key]} for key in required_field_names(normalized)]


def active_state_path(*, repo_root: Path, slug: str) -> Path:
    return repo_root / "logs" / "ci" / "active-prototypes" / f"{sanitize_slug(slug)}.active.json"


def write_active_state(*, repo_root: Path, slug: str, payload: dict[str, Any]) -> Path:
    path = active_state_path(repo_root=repo_root, slug=slug)
    write_json(path, payload)
    return path


def _score_text(value: Any) -> str:
    if isinstance(value, list):
        text = " ".join(str(item).strip() for item in value if str(item).strip())
        return text.strip()
    return str(value or "").strip()


def _has_meaningful_items(items: list[Any]) -> bool:
    meaningful = [item for item in items if _score_text(item) and _score_text(item).upper() != "TBD"]
    return bool(meaningful)


def build_prototype_intake_score(payload: dict[str, Any]) -> dict[str, Any]:
    hypothesis_text = _score_text(payload.get("hypothesis"))
    fantasy_text = _score_text(payload.get("core_player_fantasy"))
    loop_text = _score_text(payload.get("minimum_playable_loop"))
    next_step_text = _score_text(payload.get("next_step"))
    success_items = [item for item in payload.get("success_criteria") or [] if _score_text(item)]
    scope_in_items = [item for item in payload.get("scope_in") or [] if _score_text(item) and _score_text(item).upper() != "TBD"]
    scope_out_items = [item for item in payload.get("scope_out") or [] if _score_text(item) and _score_text(item).upper() != "TBD"]
    evidence_items = [item for item in payload.get("evidence") or [] if _score_text(item) and _score_text(item).upper() != "TBD"]
    promote_items = [item for item in payload.get("promote_signals") or [] if _score_text(item) and _score_text(item).upper() != "TBD"]
    archive_items = [item for item in payload.get("archive_signals") or [] if _score_text(item) and _score_text(item).upper() != "TBD"]
    discard_items = [item for item in payload.get("discard_signals") or [] if _score_text(item) and _score_text(item).upper() != "TBD"]

    feasibility_score = 0
    if len(hypothesis_text) >= 20 and len(loop_text) >= 40:
        feasibility_score += 8
    elif len(hypothesis_text) >= 10 and len(loop_text) >= 20:
        feasibility_score += 4
    if len(success_items) >= 2:
        feasibility_score += 6
    elif len(success_items) == 1:
        feasibility_score += 3
    if len(scope_in_items) >= 2 and len(scope_out_items) >= 2:
        feasibility_score += 6
    elif len(scope_in_items) >= 1 and len(scope_out_items) >= 1:
        feasibility_score += 3
    if next_step_text and next_step_text != "Proceed to the next prototype workflow confirmation step.":
        feasibility_score += 5 if len(next_step_text) >= 12 else 2
    feasibility_score = min(feasibility_score, 25)

    completeness_score = 0
    if len(hypothesis_text) >= 20:
        completeness_score += 5
    elif hypothesis_text:
        completeness_score += 2
    if len(fantasy_text) >= 30:
        completeness_score += 5
    elif fantasy_text:
        completeness_score += 2
    if len(loop_text) >= 40:
        completeness_score += 5
    elif loop_text:
        completeness_score += 2
    if len(success_items) >= 2:
        completeness_score += 4
    elif len(success_items) == 1:
        completeness_score += 2
    if len(promote_items) >= 1 and len(archive_items) >= 1 and len(discard_items) >= 1:
        completeness_score += 3
    elif len(promote_items) >= 1:
        completeness_score += 1
    if len(evidence_items) >= 1:
        completeness_score += 3
    completeness_score = min(completeness_score, 25)

    dimensions = [
        {
            "id": "prototype_feasibility",
            "label": "Prototype feasibility",
            "score": feasibility_score,
            "max_score": 25,
            "focus": "The file is concrete enough for the top-level prototype router to drive Day 1 to Day 5 with low ambiguity.",
        },
        {
            "id": "content_completeness",
            "label": "Content completeness",
            "score": completeness_score,
            "max_score": 25,
            "focus": "The prototype file contains enough structured information to avoid relying on hidden assumptions.",
        },
    ]
    total_score = sum(int(item["score"]) for item in dimensions)
    recommendation = (
        "ready-for-tdd"
        if total_score >= 36 and feasibility_score >= 18 and completeness_score >= 14
        else "refine-before-tdd"
    )
    return {
        "total_score": total_score,
        "max_score": 50,
        "recommendation": recommendation,
        "dimensions": dimensions,
    }


def _json_block(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _extract_json_object(text: str) -> dict[str, Any]:
    stripped = str(text or "").strip()
    if not stripped:
        return {}
    try:
        parsed = json.loads(stripped)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start < 0 or end <= start:
        return {}
    try:
        parsed = json.loads(stripped[start : end + 1])
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _build_llm_review_prompt(payload: dict[str, Any]) -> str:
    return (
        "You are reviewing an indie game prototype intake, not a full PRD/GDD.\n"
        "Score only the market and commercialization aspects that cannot be hard-scored reliably with deterministic rules.\n"
        "Use exactly two dimensions, 25 points each: market_potential, commercialization_cost.\n"
        "Be conservative. Do not hand out high scores just because required fields are filled.\n"
        "Market potential and commercialization cost must be judged only from statements present in the file, not from outside knowledge.\n"
        "Do not require a complete PRD, GDD, lore bible, production roadmap, economy design, or full architecture.\n"
        "Return JSON only with keys: total_score, max_score, recommendation, dimensions, top_gaps.\n"
        "recommendation must be one of: market-strong, market-cautious, commercialization-risky.\n\n"
        f"Prototype intake:\n{_json_block(payload)}\n"
    )


def _resolve_codex_command() -> str:
    if sys.platform.startswith("win"):
        return shutil.which("codex.cmd") or shutil.which("codex") or "codex"
    return shutil.which("codex") or "codex"


def build_prototype_intake_llm_review(
    payload: dict[str, Any],
    *,
    root: Path,
    score_engine: str,
    timeout_sec: int,
) -> dict[str, Any]:
    engine = str(score_engine or "deterministic").strip().lower()
    if engine == "deterministic":
        return {"engine": engine, "status": "skipped", "reason": "deterministic score engine only"}
    if engine not in {"codex", "hybrid"}:
        return {"engine": engine, "status": "skipped", "reason": f"unsupported score engine: {engine}"}

    out_path = root / "logs" / "ci" / "active-prototypes" / f"{sanitize_slug(payload.get('slug') or 'prototype')}.llm-intake-review.md"
    prompt = _build_llm_review_prompt(payload)
    cmd = [
        _resolve_codex_command(),
        "exec",
        "-s",
        "read-only",
        "-C",
        str(root),
        "--output-last-message",
        str(out_path),
        "-",
    ]
    rc, trace = _run_with_input(cmd, cwd=root, input_text=prompt, timeout_sec=timeout_sec)
    if rc != 0:
        return {"engine": engine, "status": "failed", "rc": rc, "trace": trace[-2000:]}
    review_text = out_path.read_text(encoding="utf-8") if out_path.exists() else trace
    review = _extract_json_object(review_text)
    if not review:
        return {"engine": engine, "status": "failed", "rc": rc, "trace": trace[-2000:], "error": "missing-json-review"}
    return {"engine": engine, "status": "ok", "review": review}


def _build_confirmation_message(
    payload: dict[str, Any],
    *,
    file_path: str,
    intake_score: dict[str, Any],
    llm_review: dict[str, Any] | None = None,
) -> str:
    lines = [
        "Prototype workflow paused for confirmation.",
        f"Prototype file: {file_path or 'not provided'}",
        f"Slug: {payload.get('slug') or '(missing)'}",
        f"Hypothesis: {payload.get('hypothesis') or '(missing)'}",
        f"Core player fantasy: {payload.get('core_player_fantasy') or '(missing)'}",
        f"Minimum playable loop: {payload.get('minimum_playable_loop') or '(missing)'}",
        f"Success criteria: {', '.join(payload.get('success_criteria') or []) or '(missing)'}",
        f"Hard intake score: {intake_score['total_score']}/{intake_score['max_score']}",
        f"Hard recommendation: {intake_score['recommendation']}",
    ]
    for item in intake_score["dimensions"]:
        lines.append(f"{item['label']}: {item['score']}/{item['max_score']}")
    if llm_review and llm_review.get("status") == "ok":
        review = dict(llm_review.get("review") or {})
        lines.append(f"AI market/commercial score: {review.get('total_score', 'unknown')}/{review.get('max_score', 50)}")
        lines.append(f"AI market/commercial recommendation: {review.get('recommendation', 'unknown')}")
        for item in list(review.get("dimensions") or []):
            if isinstance(item, dict):
                label = str(item.get("label") or item.get("id") or "AI dimension")
                score = item.get("score", "unknown")
                max_score = item.get("max_score", 25)
                lines.append(f"{label}: {score}/{max_score}")
            else:
                text = str(item).strip()
                if text:
                    lines.append(text)
        top_gaps = [str(item) for item in list(review.get("top_gaps") or []) if str(item).strip()]
        if top_gaps:
            lines.append(f"AI top gaps: {'; '.join(top_gaps[:3])}")
    elif llm_review and llm_review.get("status") == "skipped":
        lines.append("AI market/commercial review: not run")
    elif llm_review and llm_review.get("status") not in {"skipped", ""}:
        lines.append(f"AI market/commercial review: {llm_review.get('status')} ({llm_review.get('reason') or llm_review.get('error') or 'see active state'})")
    return "\n".join(lines)


def _run(cmd: list[str], *, cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore",
        check=False,
    )
    return proc.returncode or 0, proc.stdout or ""


def _run_with_input(cmd: list[str], *, cwd: Path, input_text: str, timeout_sec: int) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            input=input_text,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=False,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired:
        return 124, "codex exec timeout\n"
    except Exception as exc:  # noqa: BLE001
        return 1, f"codex exec failed to start: {exc}\n"
    return proc.returncode or 0, proc.stdout or ""


def _prototype_record_path(*, root: Path, slug: str) -> Path:
    return root / "docs" / "prototypes" / f"{today_str()}-{slug}.md"


def _ensure_prototype_record(root: Path, payload: dict[str, Any]) -> tuple[int, str]:
    cmd = [
        "py",
        "-3",
        "scripts/python/run_prototype_tdd.py",
        "--slug",
        str(payload["slug"]),
        "--create-record-only",
        "--owner",
        str(payload["owner"]),
        "--hypothesis",
        str(payload["hypothesis"]),
        "--core-player-fantasy",
        str(payload["core_player_fantasy"]),
        "--minimum-playable-loop",
        str(payload["minimum_playable_loop"]),
        "--decision",
        str(payload["decision"]),
        "--next-step",
        str(payload["next_step"]),
    ]
    for item in payload.get("related_formal_task_ids") or []:
        cmd += ["--related-task-id", str(item)]
    for item in payload.get("scope_in") or []:
        cmd += ["--scope-in", str(item)]
    for item in payload.get("scope_out") or []:
        cmd += ["--scope-out", str(item)]
    for item in payload.get("success_criteria") or []:
        cmd += ["--success-criteria", str(item)]
    for item in payload.get("promote_signals") or []:
        cmd += ["--promote-signal", str(item)]
    for item in payload.get("archive_signals") or []:
        cmd += ["--archive-signal", str(item)]
    for item in payload.get("discard_signals") or []:
        cmd += ["--discard-signal", str(item)]
    for item in payload.get("evidence") or []:
        cmd += ["--evidence", str(item)]
    return _run(cmd, cwd=root)


def _day_steps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    slug = str(payload["slug"])
    filter_expr = str(payload.get("test_filter") or slug.replace("-", "").replace("_", ""))
    gdunit_path = str(payload.get("gdunit_path") or f"tests/Prototype/{''.join(part.title() for part in slug.split('-'))}")
    return [
        {
            "day": 1,
            "title": "Create prototype record",
            "cmd": None,
        },
        {
            "day": 2,
            "title": "Create minimum prototype scene scaffold",
            "cmd": ["py", "-3", "scripts/python/dev_cli.py", "create-prototype-scene", "--slug", slug],
        },
        {
            "day": 3,
            "title": "Run prototype red",
            "cmd": [
                "py",
                "-3",
                "scripts/python/dev_cli.py",
                "run-prototype-tdd",
                "--slug",
                slug,
                "--stage",
                "red",
                "--dotnet-target",
                "Game.Core.Tests/Game.Core.Tests.csproj",
                "--filter",
                filter_expr,
            ],
        },
        {
            "day": 4,
            "title": "Run prototype green",
            "cmd": [
                "py",
                "-3",
                "scripts/python/dev_cli.py",
                "run-prototype-tdd",
                "--slug",
                slug,
                "--stage",
                "green",
                "--dotnet-target",
                "Game.Core.Tests/Game.Core.Tests.csproj",
                "--filter",
                filter_expr,
            ],
        },
        {
            "day": 5,
            "title": "Run Godot-side prototype verification",
            "cmd": [
                "py",
                "-3",
                "scripts/python/dev_cli.py",
                "run-prototype-tdd",
                "--slug",
                slug,
                "--stage",
                "green",
                "--gdunit-path",
                gdunit_path,
            ],
        },
    ]


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in str(value or "").split(",") if item.strip()]


def _apply_answers(payload: dict[str, Any], answers: dict[str, str]) -> dict[str, Any]:
    updated = dict(payload)
    for key, value in answers.items():
        if key == "slug":
            updated[key] = sanitize_slug(value)
        elif key == "success_criteria":
            updated[key] = _split_csv(value)
        elif key in {"scope_in", "scope_out", "related_formal_task_ids", "promote_signals", "archive_signals", "discard_signals", "evidence"}:
            updated[key] = _split_csv(value)
        else:
            updated[key] = value.strip()
    return updated


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Run the prototype 7-day top-level workflow router through Day 5.")
    ap.add_argument("--prototype-file", default="", help="Path to a prototype record filled from TEMPLATE.md / TEMPLATE.zh-CN.md.")
    ap.add_argument("--confirm", action="store_true", help="Continue after reading and confirming the prototype summary.")
    ap.add_argument("--set", action="append", default=[], help="Provide required answers in key=value form when the router asks for missing fields.")
    ap.add_argument("--godot-bin", default="", help="Required before running Day 5 Godot-side verification.")
    ap.add_argument("--stop-after-day", type=int, default=5, choices=[1, 2, 3, 4, 5], help="Stop after the selected day.")
    ap.add_argument("--resume-active", default="", help="Resume from an active prototype slug if no file is re-supplied.")
    ap.add_argument("--score-engine", default="deterministic", choices=["deterministic", "codex", "hybrid"], help="Optional prototype intake score engine. Codex is a soft second opinion, not the hard gate.")
    ap.add_argument("--score-timeout-sec", type=int, default=180, help="Timeout for optional codex intake review.")
    ap.add_argument("--self-check", action="store_true", help="Print planned behavior without executing steps.")
    return ap


def _parse_set_args(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def _resolve_file(root: Path, path_str: str) -> Path | None:
    if not str(path_str or "").strip():
        return None
    candidate = Path(path_str)
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve()


def _load_existing_active_state(root: Path, slug: str) -> dict[str, Any] | None:
    path = active_state_path(repo_root=root, slug=slug)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = repo_root()
    answers = _parse_set_args(list(args.set or []))
    prototype_file = _resolve_file(root, args.prototype_file)
    active_payload: dict[str, Any] | None = None
    if not prototype_file and args.resume_active:
        active_payload = _load_existing_active_state(root, sanitize_slug(args.resume_active))

    payload: dict[str, Any]
    file_label = ""
    if prototype_file:
        if not prototype_file.exists():
            print(f"PROTOTYPE_WORKFLOW ERROR: prototype file not found: {prototype_file}", file=sys.stderr)
            return 2
        file_label = str(prototype_file.relative_to(root)).replace("\\", "/") if prototype_file.is_relative_to(root) else str(prototype_file)
        payload = normalize_prototype_payload(parse_template_content(prototype_file.read_text(encoding="utf-8")))
    elif active_payload:
        payload = normalize_prototype_payload(active_payload.get("prototype") or {})
        file_label = active_payload.get("prototype_file") or ""
    else:
        payload = normalize_prototype_payload({})

    if answers:
        payload = normalize_prototype_payload(_apply_answers(payload, answers))

    missing = required_field_names(payload)
    if not prototype_file and not active_payload and not answers:
        questions = required_questions_for_missing_payload(payload)
        state = {
            "status": "awaiting-required-fields",
            "prototype_file": "",
            "prototype": payload,
            "missing_required_fields": missing,
            "questions": questions,
            "resume_hint": f"py -3 scripts/python/dev_cli.py run-prototype-workflow --set slug=<slug> --set hypothesis=<...> --set core_player_fantasy=<...> --set minimum_playable_loop=<...> --set success_criteria=<item1,item2>",
        }
        slug = payload.get("slug") or "prototype"
        path = write_active_state(repo_root=root, slug=str(slug), payload=state)
        print("PROTOTYPE_WORKFLOW status=needs-input")
        print(f"Active state: {path.relative_to(root).as_posix()}")
        for item in questions:
            print(f" - required {item['id']}: {item['prompt']}")
        return 0

    if missing:
        state = {
            "status": "awaiting-required-fields",
            "prototype_file": file_label,
            "prototype": payload,
            "missing_required_fields": missing,
            "questions": required_questions_for_missing_payload(payload),
            "resume_hint": "Re-run with --set key=value for each missing required field.",
        }
        path = write_active_state(repo_root=root, slug=str(payload.get("slug") or "prototype"), payload=state)
        print("PROTOTYPE_WORKFLOW status=needs-input")
        print(f"Active state: {path.relative_to(root).as_posix()}")
        print(f"Missing required fields: {', '.join(missing)}")
        return 0

    intake_score = build_prototype_intake_score(payload)
    llm_review = build_prototype_intake_llm_review(
        payload,
        root=root,
        score_engine=str(args.score_engine),
        timeout_sec=int(args.score_timeout_sec),
    )
    if not args.confirm:
        state = {
            "status": "needs-confirmation",
            "prototype_file": file_label,
            "prototype": payload,
            "missing_required_fields": [],
            "prototype_intake_score": intake_score,
            "prototype_intake_llm_review": llm_review,
            "confirmation_summary": _build_confirmation_message(
                payload,
                file_path=file_label,
                intake_score=intake_score,
                llm_review=llm_review,
            ),
            "resume_hint": f"py -3 scripts/python/dev_cli.py run-prototype-workflow {'--prototype-file ' + file_label if file_label else '--resume-active ' + str(payload['slug'])} --confirm",
        }
        path = write_active_state(repo_root=root, slug=str(payload["slug"]), payload=state)
        print("PROTOTYPE_WORKFLOW status=needs-confirmation")
        print(f"Active state: {path.relative_to(root).as_posix()}")
        print(state["confirmation_summary"])
        return 0

    if args.self_check:
        state = {
            "status": "self-check",
            "prototype_file": file_label,
            "prototype": payload,
            "prototype_intake_score": intake_score,
            "prototype_intake_llm_review": llm_review,
            "planned_days": [step["day"] for step in _day_steps(payload) if int(step["day"]) <= int(args.stop_after_day)],
        }
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0

    record_rc, record_output = _ensure_prototype_record(root, payload)
    if record_rc != 0:
        print(record_output, end="")
        return record_rc

    steps_run: list[dict[str, Any]] = []
    for step in _day_steps(payload):
        day = int(step["day"])
        if day == 1:
            steps_run.append({"day": day, "title": step["title"], "status": "ok", "record": str(_prototype_record_path(root=root, slug=str(payload["slug"])).relative_to(root)).replace("\\", "/")})
        else:
            cmd = [str(item) for item in (step["cmd"] or [])]
            if day == 5:
                if not str(args.godot_bin or "").strip():
                    state = {
                        "status": "awaiting-required-fields",
                        "prototype_file": file_label,
                        "prototype": payload,
                        "missing_required_fields": ["godot_bin"],
                        "questions": [{"id": "godot_bin", "prompt": "godot binary path required before Day 5"}],
                        "steps_run": steps_run,
                    }
                    path = write_active_state(repo_root=root, slug=str(payload["slug"]), payload=state)
                    print("PROTOTYPE_WORKFLOW status=needs-input")
                    print(f"Active state: {path.relative_to(root).as_posix()}")
                    print("Missing required fields: godot_bin")
                    return 0
                cmd += ["--godot-bin", str(args.godot_bin)]
            rc, output = _run(cmd, cwd=root)
            steps_run.append({"day": day, "title": step["title"], "status": "ok" if rc == 0 else "fail", "cmd": cmd})
            if rc != 0:
                print(output, end="")
                return rc
        if day >= int(args.stop_after_day):
            break

    state = {
        "status": "completed-through-day",
        "prototype_file": file_label,
        "prototype": payload,
        "prototype_intake_score": intake_score,
        "prototype_intake_llm_review": llm_review,
        "completed_through_day": int(args.stop_after_day),
        "steps_run": steps_run,
    }
    path = write_active_state(repo_root=root, slug=str(payload["slug"]), payload=state)
    print(f"PROTOTYPE_WORKFLOW status=ok day={args.stop_after_day} active_state={path.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
