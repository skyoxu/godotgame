#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sc-llm-generate-tests-from-acceptance-refs

Generate missing test files referenced by acceptance "Refs:" using Codex CLI (LLM),
then run deterministic tests (scripts/sc/test.py) to verify.

This tool is intentionally conservative:
  - It only creates files explicitly referenced by acceptance Refs.
  - It does not invent new paths.
  - It writes prompts/traces/outputs to logs/ci/<date>/sc-llm-acceptance-tests/.

Usage (Windows):
  py -3 scripts/sc/llm_generate_tests_from_acceptance_refs.py --task-id 11 --verify unit
  py -3 scripts/sc/llm_generate_tests_from_acceptance_refs.py --task-id 10 --verify all --godot-bin "$env:GODOT_BIN"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _bootstrap_imports() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))


_bootstrap_imports()

from _taskmaster import resolve_triplet  # noqa: E402
from _util import ci_dir, repo_root, run_cmd, write_json, write_text  # noqa: E402


REFS_RE = re.compile(r"\bRefs\s*:\s*(.+)$", flags=re.IGNORECASE)

AUTO_BEGIN = "<!-- BEGIN AUTO:TEST_ORG_NAMING_REFS -->"
AUTO_END = "<!-- END AUTO:TEST_ORG_NAMING_REFS -->"


@dataclass(frozen=True)
class GenResult:
    ref: str
    status: str  # ok|skipped|fail
    rc: int | None = None
    prompt_path: str | None = None
    trace_path: str | None = None
    output_path: str | None = None
    error: str | None = None


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _truncate(text: str, *, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def _extract_testing_framework_excerpt() -> str:
    path = repo_root() / "docs" / "testing-framework.md"
    if not path.exists():
        return ""
    text = _read_text(path)
    a = text.find(AUTO_BEGIN)
    b = text.find(AUTO_END)
    if a < 0 or b < 0 or b <= a:
        return ""
    excerpt = text[a + len(AUTO_BEGIN) : b].strip()
    return excerpt


def _split_refs_blob(blob: str) -> list[str]:
    s = str(blob or "").strip()
    s = s.replace("`", "")
    s = s.replace(",", " ")
    s = s.replace(";", " ")
    return [p.strip().replace("\\", "/") for p in s.split() if p.strip()]


def _extract_acceptance_refs(acceptance: Any) -> dict[str, list[str]]:
    # Returns mapping: ref_path -> list of acceptance texts that reference it.
    by_ref: dict[str, list[str]] = {}
    if not isinstance(acceptance, list):
        return by_ref
    for raw in acceptance:
        text = str(raw or "").strip()
        m = REFS_RE.search(text)
        if not m:
            continue
        refs = _split_refs_blob(m.group(1))
        for r in refs:
            if not r:
                continue
            by_ref.setdefault(r, []).append(text)
    return by_ref


def _run_codex_exec(*, prompt: str, out_last_message: Path, timeout_sec: int) -> tuple[int, str, list[str]]:
    exe = shutil.which("codex")
    if not exe:
        return 127, "codex executable not found in PATH\n", ["codex"]
    cmd = [
        exe,
        "exec",
        "-s",
        "read-only",
        "-C",
        str(repo_root()),
        "--output-last-message",
        str(out_last_message),
        "-",
    ]
    try:
        proc = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            encoding="utf-8",
            errors="ignore",
            cwd=str(repo_root()),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired:
        return 124, "codex exec timeout\n", cmd
    except Exception as exc:  # noqa: BLE001
        return 1, f"codex exec failed to start: {exc}\n", cmd
    return proc.returncode or 0, proc.stdout or "", cmd


def _extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError("No JSON object found in model output.")
    obj = json.loads(m.group(0))
    if not isinstance(obj, dict):
        raise ValueError("Model output JSON is not an object.")
    return obj


def _prompt_for_ref(*, task_id: str, title: str, ref: str, acceptance_texts: list[str]) -> str:
    ext = Path(ref).suffix.lower()
    if ext == ".gd":
        lang_rules = [
            "Target file type: GDScript (GdUnit4 test suite).",
            "- Must be valid .gd, English only.",
            "- Must extend a GdUnit4 suite (res://addons/gdUnit4/src/GdUnitTestSuite.gd).",
            "- Must be failing (red stage) with a deterministic failing assertion.",
            "- Do not rely on external assets; keep it self-contained.",
        ]
    else:
        lang_rules = [
            "Target file type: C# xUnit test file.",
            "- Must be valid .cs, English only.",
            "- Must compile under .NET 8.",
            "- Use FluentAssertions if possible.",
            "- Must be failing (red stage) with deterministic failing assertion.",
            "- Do not reference Godot APIs in Game.Core.Tests.",
        ]

    testing_excerpt = _extract_testing_framework_excerpt()
    testing_excerpt = _truncate(testing_excerpt, max_chars=10_000)

    acc = "\n".join([f"- {t}" for t in acceptance_texts[:20]])
    acc = acc if acc.strip() else "(no acceptance text captured for this ref)"

    constraints = "\n".join(
        [
            "Hard constraints:",
            "- Output MUST be valid JSON only (no Markdown).",
            '- The JSON MUST contain: {"file_path": "...", "content": "..."}.' ,
            f"- file_path MUST be exactly: {ref}",
            "- content MUST be a complete file content.",
            "- Do not create multiple files.",
        ]
    )

    prompt = "\n".join(
        [
            "You are a senior test engineer.",
            "Generate a missing test file referenced by acceptance Refs.",
            "",
            constraints,
            "",
            f"Task: {task_id} - {title}",
            f"Target ref: {ref}",
            "",
            "Acceptance items referencing this ref:",
            acc,
            "",
            "Repository testing framework excerpt (SSoT; may be empty):",
            testing_excerpt,
            "",
            "Language rules:",
            "\n".join(lang_rules),
            "",
            "Now output ONLY the required JSON object.",
        ]
    )
    return prompt


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate missing tests referenced by acceptance Refs using Codex CLI.")
    ap.add_argument("--task-id", required=True, help="Task id (master id, e.g. 11).")
    ap.add_argument("--timeout-sec", type=int, default=900, help="codex exec timeout in seconds (default: 900).")
    ap.add_argument("--verify", choices=["auto", "none", "unit", "all"], default="auto", help="Run deterministic verification tests after generation.")
    ap.add_argument("--godot-bin", default=None, help="Godot mono console path (required for verify=all, or set env GODOT_BIN).")
    args = ap.parse_args()

    task_id = str(args.task_id).split(".", 1)[0].strip()
    if not task_id.isdigit():
        print("SC_LLM_ACCEPTANCE_TESTS ERROR: --task-id must be a numeric master id (e.g. 11).")
        return 2

    out_dir = ci_dir("sc-llm-acceptance-tests")

    # Gate: acceptance must declare deterministic evidence mapping via "Refs:".
    gate_cmd = [
        "py",
        "-3",
        "scripts/python/validate_acceptance_refs.py",
        "--task-id",
        task_id,
        "--stage",
        "green",
        "--out",
        str(out_dir / f"acceptance-refs.{task_id}.json"),
    ]
    gate_rc, gate_out = run_cmd(gate_cmd, cwd=repo_root(), timeout_sec=60)
    write_text(out_dir / f"acceptance-refs.{task_id}.log", gate_out)
    if gate_rc != 0:
        print(f"SC_LLM_ACCEPTANCE_TESTS ERROR: acceptance refs gate failed rc={gate_rc} out={out_dir}")
        return 1

    triplet = resolve_triplet(task_id=task_id)
    if not triplet.back or not triplet.gameplay:
        write_json(out_dir / f"triplet-{task_id}.json", triplet.__dict__)
        print(f"SC_LLM_ACCEPTANCE_TESTS ERROR: task mapping missing in tasks_back/tasks_gameplay for task_id={task_id}")
        return 1

    title = str(triplet.master.get("title") or "").strip()

    by_ref: dict[str, list[str]] = {}
    for view in [triplet.back, triplet.gameplay]:
        if not isinstance(view, dict):
            continue
        for k, v in _extract_acceptance_refs(view.get("acceptance")).items():
            by_ref.setdefault(k, []).extend(v)

    refs = sorted(by_ref.keys())
    if not refs:
        write_text(out_dir / f"no-refs-{task_id}.log", "No acceptance refs found.\n")
        print(f"SC_LLM_ACCEPTANCE_TESTS status=fail refs=0 out={out_dir}")
        return 1

    results: list[GenResult] = []
    created = 0
    any_gd = False

    for ref in refs:
        ref_norm = ref.replace("\\", "/")
        disk = repo_root() / ref_norm
        if disk.exists():
            results.append(GenResult(ref=ref_norm, status="skipped", rc=0))
            continue

        if disk.suffix.lower() == ".gd":
            any_gd = True

        prompt = _prompt_for_ref(task_id=task_id, title=title, ref=ref_norm, acceptance_texts=by_ref.get(ref, []))
        prompt_path = out_dir / f"prompt-{task_id}-{Path(ref_norm).name}.txt"
        write_text(prompt_path, prompt)
        output_path = out_dir / f"codex-last-{task_id}-{Path(ref_norm).name}.txt"
        trace_path = out_dir / f"codex-trace-{task_id}-{Path(ref_norm).name}.log"

        rc, trace_out, _cmd = _run_codex_exec(prompt=prompt, out_last_message=output_path, timeout_sec=int(args.timeout_sec))
        write_text(trace_path, trace_out)
        last_msg = _read_text(output_path) if output_path.exists() else ""
        if rc != 0 or not last_msg.strip():
            results.append(
                GenResult(
                    ref=ref_norm,
                    status="fail",
                    rc=rc,
                    prompt_path=str(prompt_path),
                    trace_path=str(trace_path),
                    output_path=str(output_path),
                    error="codex exec failed/empty output",
                )
            )
            continue

        try:
            obj = _extract_json_object(last_msg)
            fp = str(obj.get("file_path") or "").replace("\\", "/")
            content = str(obj.get("content") or "")
            if fp != ref_norm:
                raise ValueError(f"unexpected file_path: {fp}")
            if not content.strip():
                raise ValueError("empty content")
            disk.parent.mkdir(parents=True, exist_ok=True)
            disk.write_text(content.replace("\r\n", "\n"), encoding="utf-8", newline="\n")
            created += 1
            results.append(
                GenResult(
                    ref=ref_norm,
                    status="ok",
                    rc=0,
                    prompt_path=str(prompt_path),
                    trace_path=str(trace_path),
                    output_path=str(output_path),
                )
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                GenResult(
                    ref=ref_norm,
                    status="fail",
                    rc=1,
                    prompt_path=str(prompt_path),
                    trace_path=str(trace_path),
                    output_path=str(output_path),
                    error=str(exc),
                )
            )

    # Sync test_refs from acceptance refs (task-level union evidence).
    sync_cmd = [
        "py",
        "-3",
        "scripts/python/update_task_test_refs_from_acceptance_refs.py",
        "--task-id",
        task_id,
        "--write",
    ]
    sync_rc, sync_out = run_cmd(sync_cmd, cwd=repo_root(), timeout_sec=60)
    write_text(out_dir / f"sync-test-refs-{task_id}.log", sync_out)

    # Decide verification mode.
    verify = args.verify
    if verify == "auto":
        verify = "all" if any_gd else "unit"

    test_step = None
    if verify != "none":
        if verify == "all":
            godot_bin = args.godot_bin or os.environ.get("GODOT_BIN")
            if not godot_bin:
                write_text(out_dir / f"verify-{task_id}.log", "ERROR: verify=all requires --godot-bin or env GODOT_BIN\n")
                test_step = {"status": "fail", "rc": 2, "error": "missing_godot_bin"}
            else:
                cmd = ["py", "-3", "scripts/sc/test.py", "--type", "all", "--godot-bin", str(godot_bin)]
                rc, out = run_cmd(cmd, cwd=repo_root(), timeout_sec=1_800)
                write_text(out_dir / f"verify-{task_id}.log", out)
                test_step = {"status": "ok" if rc == 0 else "fail", "rc": rc, "cmd": cmd}
        else:
            cmd = ["py", "-3", "scripts/sc/test.py", "--type", "unit"]
            rc, out = run_cmd(cmd, cwd=repo_root(), timeout_sec=1_800)
            write_text(out_dir / f"verify-{task_id}.log", out)
            test_step = {"status": "ok" if rc == 0 else "fail", "rc": rc, "cmd": cmd}

    summary = {
        "cmd": "sc-llm-generate-tests-from-acceptance-refs",
        "task_id": task_id,
        "title": title,
        "refs_total": len(refs),
        "created": created,
        "sync_test_refs_rc": sync_rc,
        "verify_mode": verify,
        "test_step": test_step,
        "results": [r.__dict__ for r in results],
        "out_dir": str(out_dir),
    }
    write_json(out_dir / f"summary-{task_id}.json", summary)

    hard_fail = any(r.status == "fail" for r in results) or sync_rc != 0 or (test_step and test_step.get("rc") not in (None, 0))
    print(f"SC_LLM_ACCEPTANCE_TESTS status={'fail' if hard_fail else 'ok'} created={created} out={out_dir}")
    return 1 if hard_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())

