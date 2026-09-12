#!/usr/bin/env python3
"""Loopback-only Project Health HTTP host with fixed Knowledge endpoints."""
from __future__ import annotations

import argparse
import json
import secrets
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from project_health_knowledge import (
    latest_state,
    load_config,
    query,
    runtime_verify,
    save_config,
    scan,
    task_detail,
    tasks_page,
)

HOST = "127.0.0.1"
MAX_BODY = 256 * 1024


class ProjectHealthHandler(BaseHTTPRequestHandler):
    server_version = "ProjectHealth/1"

    @property
    def repo_root(self) -> Path:
        return self.server.repo_root  # type: ignore[attr-defined]

    @property
    def session_token(self) -> str:
        return self.server.session_token  # type: ignore[attr-defined]

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _origin(self) -> str:
        return f"http://{self.headers.get('Host', '')}"

    def _guard_host(self) -> bool:
        host = self.headers.get("Host", "")
        expected = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}  # type: ignore[attr-defined]
        if host not in expected:
            self._json({"status": "error", "error": "invalid Host"}, HTTPStatus.FORBIDDEN)
            return False
        return True

    def _guard_write(self) -> bool:
        if not self._guard_host():
            return False
        origin = self.headers.get("Origin")
        if origin and origin not in {self._origin(), f"http://localhost:{self.server.server_port}"}:  # type: ignore[attr-defined]
            self._json({"status": "error", "error": "cross-origin request rejected"}, HTTPStatus.FORBIDDEN)
            return False
        if self.headers.get("X-Project-Health-Token", "") != self.session_token:
            self._json({"status": "error", "error": "invalid session token"}, HTTPStatus.FORBIDDEN)
            return False
        return True

    def _json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _file(self, path: Path, content_type: str) -> None:
        try:
            data = path.read_bytes()
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND.value)
            return
        self.send_response(HTTPStatus.OK.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _body(self) -> dict[str, object]:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_length)
        except ValueError as exc:
            raise ValueError("invalid Content-Length") from exc
        if length <= 0 or length > MAX_BODY:
            raise ValueError("request body size is invalid")
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def do_GET(self) -> None:  # noqa: N802
        if not self._guard_host():
            return
        parsed = urlparse(self.path)
        path = parsed.path
        static_root = self.repo_root / "scripts" / "python"
        dashboard = self.repo_root / "logs" / "ci" / "project-health" / "latest.html"
        if path in ("/", "/latest.html"):
            self._file(dashboard, "text/html; charset=utf-8")
            return
        if path in ("/knowledge", "/knowledge/"):
            self._file(static_root / "project_health_knowledge.html", "text/html; charset=utf-8")
            return
        if path == "/knowledge/style.css":
            self._file(static_root / "project_health_knowledge.css", "text/css; charset=utf-8")
            return
        if path == "/knowledge/app.js":
            self._file(static_root / "project_health_knowledge.js", "text/javascript; charset=utf-8")
            return
        if path == "/api/knowledge/session":
            self._json({"status": "ok", "token": self.session_token})
            return
        if path == "/api/knowledge/status":
            self._json(latest_state(self.repo_root))
            return
        if path == "/api/knowledge/config":
            self._json(load_config(self.repo_root))
            return
        if path == "/api/knowledge/tasks":
            page = int(parse_qs(parsed.query).get("page", ["1"])[0])
            self._json(tasks_page(self.repo_root, page))
            return
        if path == "/api/knowledge/task":
            task_id = parse_qs(parsed.query).get("id", [""])[0]
            self._json(task_detail(self.repo_root, task_id))
            return
        self.send_error(HTTPStatus.NOT_FOUND.value)

    def do_POST(self) -> None:  # noqa: N802
        if not self._guard_write():
            return
        try:
            payload = self._body()
            path = urlparse(self.path).path
            if path == "/api/knowledge/scan":
                result = scan(self.repo_root, fetch=bool(payload.get("fetch", True)))
            elif path == "/api/knowledge/query":
                result = query(self.repo_root, payload)
            elif path == "/api/knowledge/config":
                result = save_config(self.repo_root, payload)
            elif path == "/api/knowledge/runtime":
                task_ids = payload.get("task_ids", [])
                if not isinstance(task_ids, list) or len(task_ids) > 100:
                    raise ValueError("task_ids must be an array with at most 100 items")
                result = runtime_verify(self.repo_root, [str(value) for value in task_ids])
            else:
                self.send_error(HTTPStatus.NOT_FOUND.value)
                return
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
            self._json({"status": "error", "error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        self._json(result)


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve Project Health and Knowledge on loopback only")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    server = ThreadingHTTPServer((HOST, args.port), ProjectHealthHandler)
    server.repo_root = root  # type: ignore[attr-defined]
    server.session_token = secrets.token_urlsafe(24)  # type: ignore[attr-defined]
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
