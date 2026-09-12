#!/usr/bin/env python3
"""Loopback-only Project Health host with Knowledge + Impact APIs."""
from __future__ import annotations

import argparse
import json
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from impact_analyzer import ImpactAnalyzer
from project_health_knowledge import load_config, latest, query, save_config, scan


def handler_factory(root: Path):
    token = secrets.token_urlsafe(32)

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
            self.send_header("Content-Security-Policy", "default-src 'self'; object-src 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def require_post_auth(self) -> bool:
            origin = f"http://127.0.0.1:{self.server.server_port}"
            return (
                self.allowed_host()
                and self.headers.get("Origin") == origin
                and secrets.compare_digest(self.headers.get("X-Project-Health-Token", ""), token)
            )

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
            path = urlsplit(self.path).path
            try:
                if path == "/api/knowledge/session":
                    self.send({"token": token, "service": "godot-project-health-knowledge-v1"})
                elif path == "/api/knowledge/status":
                    state = latest(root)
                    task_root = root / ".taskmaster/tasks"
                    state["template_state"] = {"task_data_initialized": task_root.exists() and any(task_root.glob("*.json"))}
                    self.send(state)
                elif path == "/api/knowledge/config":
                    self.send(load_config(root))
                elif path in ("/knowledge", "/knowledge/"):
                    self.send((Path(__file__).with_name("project_health_knowledge.html")).read_text(encoding="utf-8"), content_type="text/html; charset=utf-8")
                elif path == "/knowledge/app.js":
                    self.send((Path(__file__).with_name("project_health_knowledge.js")).read_text(encoding="utf-8"), content_type="text/javascript; charset=utf-8")
                elif path == "/knowledge/style.css":
                    self.send((Path(__file__).with_name("project_health_knowledge.css")).read_text(encoding="utf-8"), content_type="text/css; charset=utf-8")
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
                if path == "/api/knowledge/scan":
                    state = scan(root)
                    task_root = root / ".taskmaster/tasks"
                    state["template_state"] = {"task_data_initialized": task_root.exists() and any(task_root.glob("*.json"))}
                    self.send(state)
                elif path == "/api/knowledge/query":
                    self.send(query(root, str(request.get("query") or "")))
                elif path == "/api/knowledge/impact":
                    self.send(ImpactAnalyzer(root).analyze(str(request.get("target") or ""), strict=False))
                elif path == "/api/knowledge/config":
                    self.send({"status": "saved", "config": save_config(root, request)})
                else:
                    self.send({"reason": "Not found"}, 404)
            except Exception as exc:
                self.send({"status": "failed", "reason": str(exc)}, 422)

    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args(argv)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_factory(args.repo_root.resolve()))
    server.serve_forever()


if __name__ == "__main__":
    main()
