#!/usr/bin/env python3
"""Prove lychee.toml still fails closed on real breakage.

A local server returns 200, 301, 403, 404, 410, 429, 503, and a hang.
lychee, using this repo's lychee.toml, must:
  exit 0 when the only problems are 403, 429, 503, and a timeout
  exit non-zero on 404, on 410, and on a missing local file
  exit non-zero when a timeout and a 404 are in the same file
"""

from __future__ import annotations

import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "lychee.toml"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/slow":
            time.sleep(5)
            body = b"slow"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/go":
            self.send_response(301)
            self.send_header("Location", "/ok")
            self.end_headers()
            return
        codes = {
            "/ok": 200,
            "/missing": 404,
            "/gone": 410,
            "/forbidden": 403,
            "/rate": 429,
            "/unavailable": 503,
        }
        code = codes.get(path, 500)
        body = b"x"
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        return


def start_server() -> tuple[ThreadingHTTPServer, int]:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, port


def run_lychee(lychee: str, root: Path, page: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            lychee,
            "--config",
            str(CONFIG),
            "--root-dir",
            str(root),
            "--no-progress",
            "--timeout",
            "2",
            "--max-retries",
            "0",
            str(page),
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def expect(result: subprocess.CompletedProcess[str], name: str, ok: bool, needles: list[str]) -> None:
    output = result.stdout or ""
    failed = (result.returncode == 0) if not ok else (result.returncode != 0)
    missing = [needle for needle in needles if needle not in output]
    if failed or missing:
        print(output)
        detail = f"exit {result.returncode}"
        if missing:
            detail += f", missing {missing}"
        raise SystemExit(f"link policy self-test failed ({name}): {detail}")
    print(f"link policy: {name} ({'exit 0' if ok else 'exit ' + str(result.returncode)})")


def main() -> int:
    lychee = shutil.which("lychee")
    if lychee is None:
        raise SystemExit("lychee is not on PATH")
    if not CONFIG.is_file():
        raise SystemExit(f"missing {CONFIG}")
    server, port = start_server()
    try:
        with tempfile.TemporaryDirectory(prefix="link-policy-") as tmp:
            root = Path(tmp)
            (root / "ok.html").write_text("ok\n")
            (root / "ok.png").write_bytes(b"png")
            base = f"http://127.0.0.1:{port}"
            (root / "pass.html").write_text(
                "\n".join(
                    [
                        '<a href="ok.html">local</a>',
                        '<img src="ok.png" alt="">',
                        f'<a href="{base}/ok">200</a>',
                        f'<a href="{base}/go">301</a>',
                        f'<a href="{base}/forbidden">403</a>',
                        f'<a href="{base}/rate">429</a>',
                        f'<a href="{base}/unavailable">503</a>',
                        f'<a href="{base}/slow">slow</a>',
                    ]
                )
            )
            (root / "notfound.html").write_text(
                f'<a href="ok.html">ok</a><a href="{base}/missing">404</a>\n'
            )
            (root / "gone.html").write_text(f'<a href="{base}/gone">410</a>\n')
            (root / "missing-local.html").write_text(
                '<a href="nope.html">missing</a><img src="nope.png" alt="">\n'
            )
            (root / "both.html").write_text(
                f'<a href="{base}/slow">slow</a><a href="{base}/missing">404</a>\n'
            )
            passed = run_lychee(lychee, root, root / "pass.html")
            expect(
                passed,
                "403, 429, 503, and timeout did not fail",
                ok=True,
                needles=["Request timed out"],
            )
            if "Rejected status code" in (passed.stdout or ""):
                print(passed.stdout)
                raise SystemExit("link policy self-test failed: 403 or 429 was rejected")
            expect(
                run_lychee(lychee, root, root / "notfound.html"),
                "404 failed",
                ok=False,
                needles=["Rejected status code: 404"],
            )
            expect(
                run_lychee(lychee, root, root / "gone.html"),
                "410 failed",
                ok=False,
                needles=["Rejected status code: 410"],
            )
            expect(
                run_lychee(lychee, root, root / "missing-local.html"),
                "missing local file failed",
                ok=False,
                needles=["File not found"],
            )
            expect(
                run_lychee(lychee, root, root / "both.html"),
                "timeout did not hide a 404",
                ok=False,
                needles=["Rejected status code: 404", "Request timed out"],
            )
    finally:
        server.shutdown()
    print("link policy: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
