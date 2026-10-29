#!/usr/bin/env python3
"""Check solar source URLs that lychee excludes.

Lychee skips nrel.gov, eia.gov, emp.lbl.gov, and openei.org because those
hosts time out, 403, 429, or 503 from GitHub-hosted runners. This script
requests every such URL cited under solar/ and fails only on HTTP 404 or 410.
Timeouts, connection errors, 403, 429, and other non-404 statuses are warnings.

apps.openei.org is not excluded by lychee, so it is not checked here.
"""

from __future__ import annotations

import re
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
FAIL_STATUSES = {404, 410}
TRAILING = ".,);]}>\"'"


def is_solar_source(hostname: str) -> bool:
    host = hostname.lower().rstrip(".")
    if host == "openei.org" or host == "emp.lbl.gov":
        return True
    return (
        host == "nrel.gov"
        or host.endswith(".nrel.gov")
        or host == "eia.gov"
        or host.endswith(".eia.gov")
        or host.endswith(".emp.lbl.gov")
    )


def clean_url(raw: str) -> str:
    url = raw.replace("&amp;", "&").rstrip(TRAILING)
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))


def extract_urls(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for match in URL_RE.finditer(text):
        url = clean_url(match.group(0))
        host = urlparse(url).hostname
        if not host or not is_solar_source(host):
            continue
        if url in seen:
            continue
        seen.add(url)
        found.append(url)
    return found


def cited_urls(root: Path) -> list[str]:
    output = subprocess.check_output(["git", "ls-files", "-z", "solar"], cwd=root)
    found: list[str] = []
    seen: set[str] = set()
    for raw in output.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode()
        if Path(rel).suffix.lower() not in {".html", ".htm", ".md", ".markdown"}:
            continue
        text = (root / rel).read_text(errors="replace")
        for url in extract_urls(text):
            if url not in seen:
                seen.add(url)
                found.append(url)
    return sorted(found)


def fetch(url: str, timeout: float) -> tuple[int | None, str | None]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, None
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError, OSError) as exc:
        return None, str(exc.reason if isinstance(exc, urllib.error.URLError) and exc.reason else exc)


def outcome(status: int | None) -> str:
    if status in FAIL_STATUSES:
        return "fail"
    if status is None or status in {403, 429} or status >= 400:
        return "warn"
    return "ok"


def check_urls(
    urls: list[str], timeout: float
) -> list[tuple[str, int | None, str | None, str]]:
    rows: list[tuple[str, int | None, str | None, str]] = []
    for url in urls:
        status, error = fetch(url, timeout)
        rows.append((outcome(status), status, error, url))
    return rows


def format_row(kind: str, status: int | None, error: str | None, url: str) -> str:
    if kind == "fail":
        return f"FAIL {status} {url}"
    if kind == "warn":
        detail = error or f"HTTP {status}"
        return f"warn {detail} {url} (not a failure)"
    return f"ok {status} {url}"


def hosts_of(urls: list[str]) -> set[str]:
    hosts: set[str] = set()
    for url in urls:
        host = (urlparse(url).hostname or "").lower()
        if host == "openei.org":
            hosts.add("openei.org")
        elif host == "emp.lbl.gov" or host.endswith(".emp.lbl.gov"):
            hosts.add("emp.lbl.gov")
        elif host == "nrel.gov" or host.endswith(".nrel.gov"):
            hosts.add("nrel.gov")
        elif host == "eia.gov" or host.endswith(".eia.gov"):
            hosts.add("eia.gov")
    return hosts


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/slow":
            time.sleep(3)
            self.send_response(200)
            self.end_headers()
            return
        if path == "/to-missing":
            self.send_response(302)
            self.send_header("Location", "/missing")
            self.end_headers()
            return
        codes = {"/ok": 200, "/missing": 404, "/gone": 410, "/forbidden": 403, "/rate": 429}
        code = codes.get(path, 500)
        body = b"x"
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        return


def self_test() -> None:
    sample = """
    <a href="https://pvwatts.nrel.gov/">pv</a>
    <a href="https://developer.nrel.gov/">dev</a>
    <a href="https://www.eia.gov/electricity/monthly/epm_table_5_6_a.html">eia</a>
    <a href="https://emp.lbl.gov/tracking-the-sun">tts</a>
    <a href="https://openei.org/wiki/Utility_Rate_Database">wiki</a>
    <a href="https://apps.openei.org/IURDB/rate/view/abc">apps</a>
    <a href="https://example.com/nope">other</a>
    """
    urls = extract_urls(sample)
    if hosts_of(urls) != {"nrel.gov", "eia.gov", "emp.lbl.gov", "openei.org"}:
        raise SystemExit(f"self-test extraction mismatch: {urls}")
    if any("apps.openei.org" in url for url in urls):
        raise SystemExit("self-test extracted apps.openei.org, which lychee still checks")
    if outcome(404) != "fail" or outcome(410) != "fail":
        raise SystemExit("self-test: 404 and 410 must fail")
    for status in (None, 200, 301, 403, 429, 503):
        if outcome(status) == "fail":
            raise SystemExit(f"self-test: status {status} must not fail")

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}"
    try:
        rows = check_urls(
            [
                f"{base}/ok",
                f"{base}/missing",
                f"{base}/gone",
                f"{base}/to-missing",
                f"{base}/forbidden",
                f"{base}/rate",
                f"{base}/slow",
            ],
            timeout=1,
        )
        by_url = {url: kind for kind, _status, _error, url in rows}
        expected = {
            f"{base}/ok": "ok",
            f"{base}/missing": "fail",
            f"{base}/gone": "fail",
            f"{base}/to-missing": "fail",
            f"{base}/forbidden": "warn",
            f"{base}/rate": "warn",
            f"{base}/slow": "warn",
        }
        if by_url != expected:
            print("\n".join(format_row(*row) for row in rows))
            raise SystemExit(f"self-test status mismatch:\n{by_url}")
        refused = check_urls(["http://127.0.0.1:1/nope"], timeout=1)
        if any(kind == "fail" for kind, _status, _error, _url in refused):
            print("\n".join(format_row(*row) for row in refused))
            raise SystemExit("self-test: connection refusal must not fail")
        failed = {f"{status} {url}" for kind, status, _error, url in rows if kind == "fail"}
        if failed != {
            f"404 {base}/missing",
            f"410 {base}/gone",
            f"404 {base}/to-missing",
        }:
            raise SystemExit(f"self-test failure list mismatch:\n{failed}")
    finally:
        server.shutdown()
    print("solar-source self-test: 404 and 410 failed, including after a redirect")
    print("solar-source self-test: 403, 429, timeout, and connection refusal did not fail")
    print("solar-source self-test: apps.openei.org was left to lychee")
    print("solar-source self-test: ok")


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        self_test()
        return 0
    if argv[1:]:
        raise SystemExit(f"usage: {argv[0]} [--self-test]")
    urls = cited_urls(ROOT)
    print(f"solar source URLs: {len(urls)}")
    for url in urls:
        print(f"cite {url}")
    missing_hosts = {"nrel.gov", "eia.gov", "emp.lbl.gov", "openei.org"} - hosts_of(urls)
    if missing_hosts:
        print(
            "FAIL solar pages no longer cite: " + ", ".join(sorted(missing_hosts)),
            file=sys.stderr,
        )
        return 1
    rows = check_urls(urls, timeout=20)
    for row in rows:
        print(format_row(*row))
    failures = [row for row in rows if row[0] == "fail"]
    if failures:
        print(f"FAIL {len(failures)} solar source URL(s) returned 404 or 410", file=sys.stderr)
        return 1
    print("solar sources: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
