"""Loopback-only workbench for synthetic local demonstrations."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlsplit


def serve(demo, port):
    if not 1024 <= port <= 65535:
        raise ValueError("Choose an unprivileged local port")
    state = {"report": demo()}
    lock = Lock()
    web = Path(__file__).parent / "web"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, status, data, content_type="application/json"):
            payload = data if isinstance(data, bytes) else json.dumps(data).encode()
            self.send_response(status)
            for key, value in {
                "Content-Type": content_type,
                "Content-Length": str(len(payload)),
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; object-src 'none'; base-uri 'none'",
            }.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(payload)

        def allowed_host(self):
            return self.headers.get("Host") == f"127.0.0.1:{port}"

        def do_GET(self):
            if not self.allowed_host():
                return self.send(403, {"error": "Unexpected host"})
            path = urlsplit(self.path).path
            if path == "/api/report":
                with lock:
                    return self.send(200, state["report"])
            if path == "/health":
                return self.send(200, {"status": "ready", "data": "synthetic"})
            assets = {
                "/": ("index.html", "text/html; charset=utf-8"),
                "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                "/style.css": ("style.css", "text/css; charset=utf-8"),
            }
            if path not in assets:
                return self.send(404, {"error": "Route not found"})
            name, content_type = assets[path]
            self.send(200, (web / name).read_bytes(), content_type)

        def do_POST(self):
            if (
                not self.allowed_host()
                or self.headers.get("Origin") != f"http://127.0.0.1:{port}"
            ):
                return self.send(403, {"error": "Same-origin local requests only"})
            if self.path != "/api/run":
                return self.send(404, {"error": "Route not found"})
            try:
                length = int(self.headers.get("Content-Length", "-1"))
                if (
                    not 0 <= length <= 1024
                    or self.headers.get("Content-Type") != "application/json"
                ):
                    raise ValueError()
                if json.loads(self.rfile.read(length)) != {}:
                    raise ValueError()
            except (ValueError, json.JSONDecodeError):
                return self.send(400, {"error": "Expected an empty JSON object"})
            with lock:
                try:
                    state["report"] = demo()
                except Exception:
                    return self.send(
                        500,
                        {
                            "error": "Local demonstration failed; run the CLI tests for diagnostics"
                        },
                    )
                self.send(200, state["report"])

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Local synthetic-data workbench: http://127.0.0.1:{port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def main(demo):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["demo", "serve"])
    parser.add_argument("--port", type=int, default=8011)
    args = parser.parse_args()
    if args.command == "serve":
        serve(demo, args.port)
    else:
        print(json.dumps(demo(), indent=2))
