#!/usr/bin/env python3
"""Loopback-only Project Health host with Knowledge + Impact APIs."""
from __future__ import annotations

import argparse
import json
import os
import secrets
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from impact_analyzer import ImpactAnalyzer
from knowledge_locator import CONSUMERS, locate
from project_health_godot import build_navigation
from project_health_knowledge import (
    latest,
    load_config,
    main_revision,
    query,
    safe_file,
    save_config,
    scan,
    snapshot_bytes,
    snapshot_text,
    task_details,
    task_rows,
)
from project_health_runtime import eligibility, verify

IMAGE_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}
REPORT_TYPES = {".json": "application/json; charset=utf-8", ".md": "text/markdown; charset=utf-8", ".txt": "text/plain; charset=utf-8"}


def _snapshot_status(root: Path) -> dict:
    state = dict(latest(root))
    current_main = main_revision(root)
    state["current_main_revision"] = current_main
    state["snapshot_fresh"] = current_main is None or state.get("revision") == current_main
    state["template_state"] = {"task_data_initialized": bool(task_rows(root, state))}
    return state


def _tasks(root: Path) -> list[dict]:
    state = latest(root)
    rows = task_rows(root, state)
    config = state.get("config") or load_config(root)
    bindings = config.get("task_scene_bindings", [])
    runtime = {str(row.get("id")): row for row in eligibility(root)["tasks"]}
    result: list[dict] = []
    for row in rows:
        task_id = str(row["id"])
        runtime_row = runtime.get(task_id, {})
        has_mapping = any(str(item.get("task_id", item.get("taskmaster_id", ""))).strip() == task_id for item in bindings)
        if has_mapping or runtime_row.get("eligible"):
            navigation = build_navigation(root, task_id, task=row.get("task"), mappings=row.get("mappings"), bindings=bindings, state=state)
            static_status = navigation.get("static", {}).get("status", "unmapped")
        else:
            static_status = "unmapped"
        item = {key: row.get(key) for key in ("id", "title", "status", "dependencies", "recommendedSubtasks", "sources")}
        item["godot"] = {"status": static_status, "runtime_eligible": bool(runtime_row.get("eligible"))}
        result.append(item)
    return result


def _optional_json(path: Path):
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None


def _task(root: Path, task_id: str) -> dict:
    state = latest(root)
    row = next((item for item in task_rows(root, state) if item["id"] == str(task_id)), None)
    runtime = next((item for item in eligibility(root)["tasks"] if item["id"] == str(task_id)), None)
    knowledge = task_details(root, task_id)
    config = state.get("config") or load_config(root)
    navigation = build_navigation(
        root, task_id, task=row.get("task") if row else None, mappings=row.get("mappings") if row else None,
        bindings=config.get("task_scene_bindings", []), state=state,
    )
    semantic = _optional_json(root / "docs/knowledge/generated" / f"task-{task_id}-semantic.json")
    reviewed_resources = _optional_json(root / "docs/knowledge/generated" / f"task-{task_id}-resources.json")
    links_payload = _optional_json(root / "docs/knowledge/generated/task-resource-links.json") or {}
    generated_links = [
        item for item in links_payload.get("generated", [])
        if isinstance(item, dict) and str(item.get("task_id")) == str(task_id)
    ]
    return {
        "schema": "godot-project-health.task.v5",
        "revision": state.get("revision"),
        "task": {key: row.get(key) for key in ("id", "title", "status", "dependencies", "recommendedSubtasks", "sources")} if row else None,
        "runtime": runtime,
        "knowledge": knowledge,
        "navigation": navigation,
        "semantic": semantic,
        "resource_knowledge": generated_links,
        "reviewed_resources": reviewed_resources,
    }


def _source(root: Path, rel: str) -> dict:
    state = latest(root)
    text = snapshot_text(root, rel, state)
    return {"schema": "godot-project-health.source.v2", "path": rel, "revision": state.get("revision"), "text": text[:200000], "content": text[:200000]}


def _image(root: Path, rel: str, revision: str | None = None) -> tuple[bytes, str]:
    mime = IMAGE_TYPES.get(Path(rel).suffix.casefold())
    if not mime:
        raise ValueError("unsupported image type")
    state = latest(root)
    if revision and revision != state.get("revision"):
        raise ValueError("image snapshot changed; reopen the task or scan again")
    data = snapshot_bytes(root, rel, state)
    if len(data) > 16 * 1024 * 1024:
        raise ValueError("image exceeds 16 MiB preview limit")
    return data, mime


def _report(root: Path, request_path: str) -> tuple[str, str]:
    relative = request_path.lstrip("/")
    report_root = (root / "logs/ci/project-health").resolve()
    target = safe_file(report_root, relative)
    content_type = REPORT_TYPES.get(target.suffix.casefold())
    if not content_type or not target.is_file():
        raise FileNotFoundError(relative)
    return target.read_text(encoding="utf-8"), content_type


def handler_factory(root: Path):
    token = secrets.token_urlsafe(32)
    operation_lock = threading.Lock()
    operation_state = {"active": False, "action": None, "started_at": None, "task_ids": [], "verification_mode": None}

    def operation_snapshot() -> dict:
        return {"schema": "godot-project-health.operation.v1", **operation_state}

    def begin_operation(action: str, *, task_ids: list[str] | None = None, verification_mode: str | None = None) -> bool:
        if not operation_lock.acquire(blocking=False):
            return False
        operation_state.update({"active": True, "action": action, "started_at": datetime.now(timezone.utc).isoformat(), "task_ids": task_ids or [], "verification_mode": verification_mode})
        return True

    def end_operation() -> None:
        operation_state.update({"active": False, "action": None, "started_at": None, "task_ids": [], "verification_mode": None})
        operation_lock.release()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def allowed_host(self) -> bool:
            return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

        def send(self, payload, code=200, content_type="application/json; charset=utf-8"):
            body = payload if isinstance(payload, bytes) else payload.encode("utf-8") if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            dashboard = urlsplit(self.path).path in ("/", "/latest.html")
            inline = " 'unsafe-inline'" if dashboard else ""
            self.send_header("Content-Security-Policy", f"default-src 'self'; script-src 'self'{inline}; style-src 'self'{inline}; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def require_post_auth(self) -> bool:
            origin = f"http://127.0.0.1:{self.server.server_port}"
            return self.allowed_host() and self.headers.get("Origin") == origin and secrets.compare_digest(self.headers.get("X-Project-Health-Token", ""), token)

        def read_request(self):
            length = int(self.headers.get("Content-Length", "0") or 0)
            if not 0 < length <= 65536:
                raise ValueError("Expected bounded JSON request")
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("Expected application/json")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("Expected JSON object")
            return payload

        def do_GET(self):
            if not self.allowed_host():
                self.send({"reason": "Invalid Host"}, 403)
                return
            parsed = urlsplit(self.path); path = parsed.path; params = parse_qs(parsed.query)
            try:
                if path == "/api/knowledge/session": self.send({"token": token, "service": "godot-project-health-knowledge-v1"})
                elif path == "/api/knowledge/operation": self.send(operation_snapshot())
                elif path == "/api/knowledge/status": self.send(_snapshot_status(root))
                elif path == "/api/knowledge/config": self.send(load_config(root))
                elif path == "/api/knowledge/tasks": self.send({"schema": "godot-project-health.tasks.v2", "revision": latest(root).get("revision"), "tasks": _tasks(root)})
                elif path == "/api/knowledge/task": self.send(_task(root, params.get("id", [""])[0]))
                elif path == "/api/knowledge/source": self.send(_source(root, params.get("path", [""])[0]))
                elif path == "/api/knowledge/runtime-eligibility": self.send(eligibility(root))
                elif path == "/api/knowledge/runtime-latest":
                    runtime_path = root / "logs/ci/project-health-knowledge/runtime/latest.json"
                    self.send(json.loads(runtime_path.read_text(encoding="utf-8")) if runtime_path.exists() else {"schema": "godot-project-health.runtime-index.v2", "tasks": [], "summary": {}})
                elif path == "/api/knowledge/image":
                    data, mime = _image(root, params.get("path", [""])[0], params.get("revision", [None])[0])
                    self.send(data, content_type=mime)
                elif path in ("/knowledge", "/knowledge/"): self.send(Path(__file__).with_name("project_health_knowledge.html").read_text(encoding="utf-8"), content_type="text/html; charset=utf-8")
                elif path == "/knowledge/app.js": self.send(Path(__file__).with_name("project_health_knowledge.js").read_text(encoding="utf-8"), content_type="text/javascript; charset=utf-8")
                elif path == "/knowledge/style.css": self.send(Path(__file__).with_name("project_health_knowledge.css").read_text(encoding="utf-8"), content_type="text/css; charset=utf-8")
                elif path in ("/", "/latest.html"): self.send((root / "logs/ci/project-health/latest.html").read_text(encoding="utf-8"), content_type="text/html; charset=utf-8")
                elif path.startswith("/api/"): self.send({"reason": "Not found"}, 404)
                else:
                    try:
                        body, mime = _report(root, path)
                        self.send(body, content_type=mime)
                    except (FileNotFoundError, ValueError):
                        self.send({"reason": "Not found"}, 404)
            except Exception as exc:
                self.send({"status": "failed", "reason": str(exc)}, 422)

        def do_POST(self):
            if not self.require_post_auth():
                self.send({"reason": "Same-origin session token required"}, 403); return
            path = urlsplit(self.path).path
            try:
                request = self.read_request()
                action = {"/api/knowledge/scan": "scan", "/api/knowledge/config": "save-config", "/api/knowledge/runtime-verify": "runtime-verify"}.get(path)
                task_ids: list[str] = []
                if path == "/api/knowledge/runtime-verify":
                    if request.get("task_id") is not None: task_ids = [str(request.get("task_id"))]
                    elif isinstance(request.get("task_ids"), list): task_ids = [str(value) for value in request["task_ids"]]
                if action and not begin_operation(action, task_ids=task_ids, verification_mode=str(request.get("mode") or "") or None):
                    self.send({"status": "busy", "reason": "Another Project Health write operation is active", "operation": operation_snapshot()}, 409); return
                try:
                    if path == "/api/knowledge/scan": scan(root); self.send(_snapshot_status(root))
                    elif path == "/api/knowledge/query":
                        search = query(root, str(request.get("query") or "")); consumer = str(request.get("consumer") or "repository-session")
                        if consumer not in CONSUMERS: raise ValueError("unknown consumer")
                        search["consumer"] = consumer
                        search["locator"] = locate(root, consumer=consumer, text=str(request.get("query") or ""), task_id=(str(request.get("task_id")) if request.get("task_id") is not None else None))
                        self.send(search)
                    elif path == "/api/knowledge/impact": self.send(ImpactAnalyzer(root).analyze(str(request.get("target") or ""), strict=bool(request.get("strict", False))))
                    elif path == "/api/knowledge/config": self.send({"status": "saved", "config": save_config(root, request)})
                    elif path == "/api/knowledge/runtime-verify":
                        godot_bin = str(request.get("godot_bin") or os.environ.get("GODOT_BIN") or "").strip()
                        if not godot_bin: raise ValueError("GODOT_BIN is not configured; set it in the server environment or provide godot_bin")
                        ids = request.get("task_ids"); selected_ids = [str(value) for value in ids] if isinstance(ids, list) else None
                        self.send(verify(root, godot_bin, timeout=int(request.get("timeout_sec", 600)), task_id=(str(request.get("task_id")) if request.get("task_id") is not None else None), task_ids=selected_ids, all_eligible=bool(request.get("all_eligible", False)), all_gameplay=bool(request.get("all_gameplay", False)), global_timeout=int(request.get("global_timeout_sec", 3600)), mode=str(request.get("mode") or "main")))
                    else: self.send({"reason": "Not found"}, 404)
                finally:
                    if action: end_operation()
            except Exception as exc:
                self.send({"status": "failed", "reason": str(exc)}, 422)

    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser(); parser.add_argument("--repo-root", type=Path, required=True); parser.add_argument("--port", type=int, required=True); args = parser.parse_args(argv)
    ThreadingHTTPServer(("127.0.0.1", args.port), handler_factory(args.repo_root.resolve())).serve_forever()


if __name__ == "__main__": main()
