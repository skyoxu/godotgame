from __future__ import annotations

import http.client
import json
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PYTHON = ROOT / "scripts/python"
if str(PYTHON) not in sys.path:
    sys.path.insert(0, str(PYTHON))

from _project_health_http import _image, _report, handler_factory


class ProjectHealthHttpSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        report_dir = self.root / "logs/ci/project-health"
        report_dir.mkdir(parents=True)
        (report_dir / "latest.html").write_text("<html><body>dashboard</body></html>", encoding="utf-8")
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler_factory(self.root))
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self.temp.cleanup()

    def request(self, method: str, path: str, *, host: str | None = None, headers: dict[str, str] | None = None, body: bytes | None = None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        connection.putrequest(method, path, skip_host=True)
        connection.putheader("Host", host or f"127.0.0.1:{self.port}")
        for key, value in (headers or {}).items():
            connection.putheader(key, value)
        if body is not None:
            connection.putheader("Content-Length", str(len(body)))
        connection.endheaders(body)
        response = connection.getresponse()
        payload = response.read()
        result = (response.status, dict(response.getheaders()), payload)
        connection.close()
        return result

    def test_exact_host_session_and_same_origin_token_are_required(self):
        status, _, _ = self.request("GET", "/api/knowledge/session", host=f"localhost:{self.port}")
        self.assertEqual(403, status)

        status, headers, payload = self.request("GET", "/api/knowledge/session")
        self.assertEqual(200, status)
        self.assertEqual("no-store", headers.get("Cache-Control"))
        token = json.loads(payload)["token"]

        body = b"{}"
        status, _, _ = self.request(
            "POST",
            "/api/knowledge/config",
            headers={"Content-Type": "application/json"},
            body=body,
        )
        self.assertEqual(403, status)

        status, _, payload = self.request(
            "POST",
            "/api/knowledge/config",
            headers={
                "Content-Type": "application/json",
                "Origin": f"http://127.0.0.1:{self.port}",
                "X-Project-Health-Token": token,
            },
            body=body,
        )
        self.assertEqual(200, status, payload.decode("utf-8", errors="replace"))
        self.assertEqual("saved", json.loads(payload)["status"])

    def test_post_rejects_wrong_origin_and_unbounded_or_wrong_content_type(self):
        _, _, payload = self.request("GET", "/api/knowledge/session")
        token = json.loads(payload)["token"]
        auth = {
            "Origin": f"http://127.0.0.1:{self.port}",
            "X-Project-Health-Token": token,
        }
        status, _, _ = self.request(
            "POST",
            "/api/knowledge/config",
            headers={**auth, "Content-Type": "text/plain"},
            body=b"{}",
        )
        self.assertEqual(422, status)

        status, _, _ = self.request(
            "POST",
            "/api/knowledge/config",
            headers={
                "Content-Type": "application/json",
                "Origin": "http://127.0.0.1:1",
                "X-Project-Health-Token": token,
            },
            body=b"{}",
        )
        self.assertEqual(403, status)

        oversized = b"{" + b" " * 65536 + b"}"
        status, _, _ = self.request(
            "POST",
            "/api/knowledge/config",
            headers={**auth, "Content-Type": "application/json"},
            body=oversized,
        )
        self.assertEqual(422, status)

    def test_knowledge_page_csp_is_stricter_than_generated_dashboard(self):
        status, headers, _ = self.request("GET", "/knowledge/")
        self.assertEqual(200, status)
        csp = headers.get("Content-Security-Policy", "")
        self.assertIn("script-src 'self'", csp)
        self.assertNotIn("'unsafe-inline'", csp)
        self.assertEqual("DENY", headers.get("X-Frame-Options"))
        self.assertEqual("nosniff", headers.get("X-Content-Type-Options"))

        status, headers, _ = self.request("GET", "/latest.html")
        self.assertEqual(200, status)
        self.assertIn("'unsafe-inline'", headers.get("Content-Security-Policy", ""))

    def test_report_traversal_and_image_revision_mismatch_fail_closed(self):
        outside = self.root / "outside.txt"
        outside.write_text("outside", encoding="utf-8")
        with self.assertRaises(ValueError):
            _report(self.root, "/../outside.txt")
        with self.assertRaises(ValueError):
            _image(self.root, "Game.Godot/Assets/icon.png", revision="deadbeef")


if __name__ == "__main__":
    unittest.main()
