#!/usr/bin/env python3
"""Loopback-only Project Health host with Knowledge + Impact APIs."""
from __future__ import annotations

import argparse
import hashlib
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
from project_health_knowledge import load_config, latest, query, safe_file, save_config, scan, task_details
from project_health_runtime import eligibility, verify

IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def _walk_tasks(value):
    if isinstance(value, dict):
        if "id" in value and ("title" in value or "status" in value):
            yield value
        for child in value.values():
            yield from _walk_tasks(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_tasks(child)


def _tasks(root: Path) -> list[dict]:
    task_dir = root / ".taskmaster/tasks"
    rows: dict[str, dict] = {}
    if not task_dir.exists():
        return []
    for file in sorted(task_dir.glob("*.json")):
        try:
            data = json.loads(file.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        for task in _walk_tasks(data):
            task_id = str(task.get("id") or "").strip()
            if not task_id:
                continue
            row = rows.setdefault(task_id, {"id": task_id, "title": "", "status": "", "dependencies": [], "sources": []})
            row["title"] = row["title"] or str(task.get("title") or "")
            row["status"] = row["status"] or str(task.get("status") or "")
            deps = task.get("dependencies") or []
            if isinstance(deps, list):
                row["dependencies"] = sorted({*row["dependencies"], *(str(x) for x in deps)})
            row["sources"].append(file.relative_to(root).as_posix())
    return sorted(rows.values(), key=lambda item: (not item["id"].isdigit(), int(item["id"]) if item["id"].isdigit() else item["id"]))


def _task(root: Path, task_id: str) -> dict:
    rows = _tasks(root)
    match = next((row for row in rows if row["id"] == str(task_id)), None)
    runtime = next((row for row in eligibility(root)["tasks"] if row["id"] == str(task_id)), None)
    knowledge = task_details(root, task_id)
    return {"schema": "godot-project-health.task.v3", "task": match, "runtime": runtime, "knowledge": knowledge}


def _source(root: Path, rel: str) -> dict:
    path = safe_file(root, rel)
    manifest = {str(item.get("path")): item for item in latest(root).get("records", [])}
    if rel not in manifest or not path.is_file():
        raise ValueError("source path is not in the scanned manifest")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest[rel].get("sha256"):
        raise ValueError("source changed after scan; scan again")
    return {"schema": "godot-project-health.source.v1", "path": rel, "revision": latest(root).get("revision"), "text": raw.decode("utf-8-sig")[:200000]}


def _image(root: Path, rel: str) -> tuple[bytes, str]:
    path = safe_file(root, rel)
    mime = IMAGE_TYPES.get(path.suffix.lower())
    if not mime:
        raise ValueError("unsupported image type")
    manifest = {str(item.get("path")): item for item in latest(root).get("records", [])}
    record = manifest.get(rel)
    if record is None or not path.is_file():
        raise ValueError("image is not in the scanned manifest")
    raw = path.read_bytes()
    if len(raw) > 16 * 1024 * 1024:
        raise ValueError("image exceeds 16 MiB preview limit")
    if hashlib.sha256(raw).hexdigest() != record.get("sha256"):
        raise ValueError("image changed after scan; scan again")
    return raw, mime


def handler_factory(root: Path):
    token = secrets.token_urlsafe(32)
    operation_lock = threading.Lock()
    operation_state = {"active": False, "action": None, "started_at": None, "task_ids": [], "verification_mode": None}

    def operation_snapshot() -> dict:
        return {"schema": "godot-project-health.operation.v1", **operation_state}

    def begin_operation(action: str, *, task_ids: list[str] | None = None, verification_mode: str | None = None) -> bool:
        if not operation_lock.acquire(blocking=False):
            return False
        operation_state.update({
            "active": True,
            "action": action,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "task_ids": task_ids or [],
            "verification_mode": verification_mode,
        })
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
            if isinstance(payload, bytes):
                body = payload
            elif isinstance(payload, str):
                body = payload.encode("utf-8")
            else:
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self'; object-src 'none'; frame-ancestors 'none'")
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
            parsed = urlsplit(self.path)
            path = parsed.path
            params = parse_qs(parsed.query)
            try:
                if path == "/api/knowledge/session":
                    self.send({"token": token, "service": "godot-project-health-knowledge-v1"})
                elif path == "/api/knowledge/operation":
                    self.send(operation_snapshot())
                elif path == "/api/knowledge/status":
                    state = latest(root)
                    task_root = root / ".taskmaster/tasks"
                    state["template_state"] = {"task_data_initialized": task_root.exists() and any(task_root.glob("*.json"))}
                    self.send(state)
                elif path == "/api/knowledge/config":
                    self.send(load_config(root))
                elif path == "/api/knowledge/tasks":
                    self.send({"schema": "godot-project-health.tasks.v1", "tasks": _tasks(root)})
                elif path == "/api/knowledge/task":
                    self.send(_task(root, params.get("id", [""])[0]))
                elif path == "/api/knowledge/source":
                    self.send(_source(root, params.get("path", [""])[0]))
                elif path == "/api/knowledge/runtime-eligibility":
                    self.send(eligibility(root))
                elif path == "/api/knowledge/runtime-latest":
                    runtime_path = root / "logs/ci/project-health-knowledge/runtime/latest.json"
                    self.send(json.loads(runtime_path.read_text(encoding="utf-8")) if runtime_path.exists() else {"schema": "godot-project-health.runtime-index.v1", "tasks": [], "summary": {}})
                elif path == "/api/knowledge/image":
                    data, mime = _image(root, params.get("path", [""])[0])
                    self.send(data, content_type=mime)
                elif path in ("/knowledge", "/knowledge/"):
                    self.send(Path(__file__).with_name("project_health_knowledge.html").read_text(encoding="utf-8"), content_type="text/html; charset=utf-8")
                elif path == "/knowledge/app.js":
                    self.send(Path(__file__).with_name("project_health_knowledge.js").read_text(encoding="utf-8"), content_type="text/javascript; charset=utf-8")
                elif path == "/knowledge/style.css":
                    self.send(Path(__file__).with_name("project_health_knowledge.css").read_text(encoding="utf-8"), content_type="text/css; charset=utf-8")
                elif path in ("/", "/latest.html"):
                    self.send((root / "logs/ci/project-health/latest.html").read_text(encoding="utf-8"), content_type="text/html; charset=utf-8")
                else:
                    self.send({"reason": "Not found"}, 404)
            except Exception as exc:
                self.send({"status": "failed", "reason": str(exc)}, 422)

        def do_POST(self):
            if not self.require_post_auth():
                self.send({"reason": "Same-origin session token required"}, 403)
                return
            path = urlsplit(self.path).path
            try:
                request = self.read_request()
                action = {
                    "/api/knowledge/scan": "scan",
                    "/api/knowledge/config": "save-config",
                    "/api/knowledge/runtime-verify": "runtime-verify",
                }.get(path)
                task_ids = []
                if path == "/api/knowledge/runtime-verify":
                    if request.get("task_id") is not None:
                        task_ids = [str(request.get("task_id"))]
                    elif isinstance(request.get("task_ids"), list):
                        task_ids = [str(value) for value in request["task_ids"]]
                if action and not begin_operation(action, task_ids=task_ids, verification_mode=str(request.get("mode") or "") or None):
                    self.send({"status": "busy", "reason": "Another Project Health write operation is active", "operation": operation_snapshot()}, 409)
                    return
                try:
                    if path == "/api/knowledge/scan":
                        state = scan(root)
                        task_root = root / ".taskmaster/tasks"
                        state["template_state"] = {"task_data_initialized": task_root.exists() and any(task_root.glob("*.json"))}
                        self.send(state)
                    elif path == "/api/knowledge/query":
                        search = query(root, str(request.get("query") or ""))
                        consumer = str(request.get("consumer") or "repository-session")
                        if consumer not in CONSUMERS:
                            raise ValueError("unknown consumer")
                        search["consumer"] = consumer
                        search["locator"] = locate(root, consumer=consumer, text=str(request.get("query") or ""), task_id=str(request.get("task_id")) if request.get("task_id") is not None else None)
                        self.send(search)
                    elif path == "/api/knowledge/impact":
                        self.send(ImpactAnalyzer(root).analyze(str(request.get("target") or ""), strict=bool(request.get("strict", False))))
                    elif path == "/api/knowledge/config":
                        self.send({"status": "saved", "config": save_config(root, request)})
                    elif path == "/api/knowledge/runtime-verify":
                        godot_bin = str(request.get("godot_bin") or os.environ.get("GODOT_BIN") or "").strip()
                        if not godot_bin:
                            raise ValueError("GODOT_BIN is not configured; set it in the server environment or provide godot_bin")
                        ids = request.get("task_ids")
                        selected_ids = [str(value) for value in ids] if isinstance(ids, list) else None
                        self.send(verify(
                            root,
                            godot_bin,
                            timeout=int(request.get("timeout_sec", 600)),
                            task_id=str(request.get("task_id")) if request.get("task_id") is not None else None,
                            task_ids=selected_ids,
                            all_eligible=bool(request.get("all_eligible", False)),
                            global_timeout=int(request.get("global_timeout_sec", 3600)),
                            mode=str(request.get("mode") or "main"),
                        ))
                    else:
                        self.send({"reason": "Not found"}, 404)
                finally:
                    if action:
                        end_operation()
            except Exception as exc:
                self.send({"status": "failed", "reason": str(exc)}, 422)

    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args(argv)
    ThreadingHTTPServer(("127.0.0.1", args.port), handler_factory(args.repo_root.resolve())).serve_forever()


if __name__ == "__main__":
    main()
