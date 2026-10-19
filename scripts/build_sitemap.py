#!/usr/bin/env python3
"""
build_sitemap.py — write sitemap.xml from published-corpus.json.

The corpus is the list of project units. The manifest deliberately leaves
out site chrome (index, resume, dashboard, 404). This sitemap adds the
three published chrome pages and leaves 404.html out.

    python3 scripts/build_sitemap.py          # write sitemap.xml
    python3 scripts/build_sitemap.py --check  # fail if the file drifted,
                                              # or if robots.txt misses a
                                              # markdown path

Stdlib only — runs unmodified in GitHub Actions (ubuntu, python3).
"""
import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "published-corpus.json"
SITEMAP = ROOT / "sitemap.xml"
ROBOTS = ROOT / "robots.txt"
ORIGIN = "https://scottn66.github.io"

# Published HTML that build_manifest.py excludes as chrome. 404 is omitted
# on purpose: it is not a page to index.
CHROME_PATHS = ("/", "/resume.html", "/dashboard.html")


def load_corpus():
    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("published-corpus.json must be a list")
    return data


def lastmod(value):
    if not value or not isinstance(value, str) or len(value) < 10:
        return None
    date = value[:10]
    if len(date) == 10 and date[4] == "-" and date[7] == "-":
        return date
    return None


def entries():
    """(loc, lastmod or None) in stable sitemap order."""
    by_path = {}
    for item in load_corpus():
        url = item.get("url")
        if not url or not str(url).startswith("/"):
            raise SystemExit(f"corpus entry has no site path: {item!r}")
        by_path[url] = lastmod(item.get("last_modified"))
    for path in CHROME_PATHS:
        by_path.setdefault(path, None)
    rows = []
    for path in sorted(by_path, key=lambda p: (p != "/", p)):
        rows.append((ORIGIN + path, by_path[path]))
    return rows


def render(rows):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, modified in rows:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(loc)}</loc>")
        if modified:
            lines.append(f"    <lastmod>{modified}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    lines.append("")
    return "\n".join(lines)


def markdown_paths():
    paths = []
    for path in ROOT.rglob("*.md"):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(".git/"):
            continue
        paths.append("/" + rel)
    return sorted(paths)


def disallow_rules(text):
    rules = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line.lower().startswith("disallow:"):
            continue
        rule = line.split(":", 1)[1].strip()
        if rule:
            rules.append(rule)
    return rules


def prefix_covers(rule, path):
    """A robots prefix rule, ignoring wildcard rules so the explicit list is load-bearing."""
    if any(ch in rule for ch in "*$"):
        return False
    return path.startswith(rule)


def robots_problems():
    if not ROBOTS.is_file():
        return ["robots.txt is missing"]
    text = ROBOTS.read_text(encoding="utf-8")
    problems = []
    sitemap_line = f"Sitemap: {ORIGIN}/sitemap.xml"
    if sitemap_line not in text:
        problems.append(f"robots.txt is missing {sitemap_line!r}")
    rules = disallow_rules(text)
    for path in markdown_paths():
        if any(prefix_covers(rule, path) for rule in rules):
            continue
        problems.append(
            f"{path} is not kept out of indexing. Add a Disallow prefix in robots.txt."
        )
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if sitemap.xml or the robots.txt markdown rules are stale",
    )
    args = parser.parse_args()
    body = render(entries())
    problems = []
    if args.check:
        current = SITEMAP.read_text(encoding="utf-8") if SITEMAP.is_file() else ""
        if current != body:
            problems.append("sitemap.xml does not match published-corpus.json. Run: python3 scripts/build_sitemap.py")
        problems.extend(robots_problems())
        if problems:
            for line in problems:
                print(line, file=sys.stderr)
            return 1
        print(f"sitemap.xml and robots.txt match ({body.count('<loc>')} URLs).")
        return 0

    SITEMAP.write_text(body, encoding="utf-8")
    print(f"Wrote {SITEMAP.name} — {body.count('<loc>')} URLs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
