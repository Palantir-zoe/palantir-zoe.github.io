"""Local-only, dependency-free preview for the Markdown learning notes."""
from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
RUNTIME = ROOT / ".runtime"
STATE = RUNTIME / "server.json"
PROJECT = hashlib.sha256(str(ROOT).encode("utf-8")).hexdigest()[:20]


def request(url: str, **kwargs):
    with urllib.request.urlopen(urllib.request.Request(url, **kwargs), timeout=2) as response:
        return json.load(response)


def active_server():
    try:
        info = json.loads(STATE.read_text(encoding="utf-8"))
        if info.get("project") != PROJECT:
            return None
        health = request(info["url"] + "/__notes_health")
        if health.get("project") == PROJECT and health.get("pid") == info.get("pid"):
            return info
    except (OSError, ValueError, KeyError, urllib.error.URLError):
        pass
    return None


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def json_response(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/__notes_health":
            self.json_response(200, {"project": PROJECT, "pid": os.getpid()})
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != "/__notes_stop":
            self.json_response(404, {"error": "Not found"})
            return
        if not secrets.compare_digest(self.headers.get("X-Notes-Token", ""), self.server.stop_token):
            self.json_response(403, {"error": "Invalid token"})
            return
        self.json_response(200, {"stopping": True})
        threading.Thread(target=self.server.shutdown, daemon=True).start()


def run_server(port):
    RUNTIME.mkdir(exist_ok=True)
    handler = functools.partial(Handler, directory=str(DOCS))
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    except OSError:
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server.stop_token = secrets.token_urlsafe(32)
    info = {
        "project": PROJECT, "pid": os.getpid(),
        "url": f"http://127.0.0.1:{server.server_port}",
        "token": server.stop_token,
    }
    pending = STATE.with_suffix(".tmp")
    pending.write_text(json.dumps(info), encoding="utf-8")
    pending.replace(STATE)
    try:
        with server:
            server.serve_forever(poll_interval=0.25)
    finally:
        try:
            if json.loads(STATE.read_text(encoding="utf-8")).get("pid") == os.getpid():
                STATE.unlink()
        except (OSError, ValueError):
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", choices=["start", "stop", "run"], default="start")
    parser.add_argument("--open", action="store_true", dest="open_browser")
    parser.add_argument("--port", type=int, default=3000)
    args = parser.parse_args()
    if args.action == "run":
        run_server(args.port)
        return
    info = active_server()
    if args.action == "stop":
        if info:
            request(info["url"] + "/__notes_stop", method="POST", headers={"X-Notes-Token": info["token"]})
            for _ in range(20):
                if not active_server():
                    break
                time.sleep(0.1)
            print("Notes server stopped.")
        else:
            print("Notes server is not running.")
        return
    if info is None:
        RUNTIME.mkdir(exist_ok=True)
        flags = (subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS) if os.name == "nt" else 0
        with (RUNTIME / "server.log").open("ab") as log:
            process = subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), "run", "--port", str(args.port)],
                cwd=str(ROOT), stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                creationflags=flags, start_new_session=(os.name != "nt"),
            )
        for _ in range(50):
            info = active_server()
            if info:
                break
            if process.poll() is not None:
                break
            time.sleep(0.1)
        if info is None:
            print("Could not start notes server. See .runtime/server.log", file=sys.stderr)
            raise SystemExit(1)
    print("Learning notes: " + info["url"])
    if args.open_browser:
        webbrowser.open(info["url"])


if __name__ == "__main__":
    main()
