#!/usr/bin/env python3
"""
build_manifest.py — emit published-corpus.json, the machine-readable face
of the P (Publish) plane for the three-plane reconciliation rig.

Scans the site for published content pages and writes one entry per unit:
  { "unit", "url", "title", "last_modified", "kind" }

unit  = <meta name="unit" content="..."> if the page declares one,
        else the path slug (filename stem for top-level pages, dir name
        for project directories). Pages self-describe; the path is the
        fallback. This lets a path like /solar/ carry the vault unit
        "solar-viability" without renaming the directory.

Spec: ~/AInt/_vault/_reconciliation.md
Stdlib only — runs unmodified in GitHub Actions (ubuntu, python3).
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repo root (scripts/ is one level down)

# Infrastructure / chrome — published but not "project units".
EXCLUDE_FILES = {"index.html", "dashboard.html", "resume.html", "404.html"}
EXCLUDE_DIRS = {"pages", "scripts", "assets", "node_modules", ".git", ".github"}

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
META_UNIT_RE = re.compile(
    r"""<meta\s+name=["']unit["']\s+content=["']([^"']+)["']""", re.I
)


def git_last_modified(rel: str):
    """ISO-8601 commit date of the last change to rel, or None."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", rel],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        return out or None
    except Exception:
        return None


def extract(html_path: Path):
    txt = html_path.read_text(encoding="utf-8", errors="ignore")
    tm = TITLE_RE.search(txt)
    title = re.sub(r"\s+", " ", tm.group(1)).strip() if tm else None
    um = META_UNIT_RE.search(txt)
    return title, (um.group(1) if um else None)


def slug(name: str) -> str:
    return name.lower().removesuffix(".html").strip("/")


def main():
    entries = []

    # Top-level *.html content pages.
    for f in sorted(ROOT.glob("*.html")):
        if f.name in EXCLUDE_FILES:
            continue
        title, meta_unit = extract(f)
        entries.append({
            "unit": meta_unit or slug(f.name),
            "url": "/" + f.name,
            "title": title,
            "last_modified": git_last_modified(f.name),
            "kind": "page",
        })

    # Single-level project directories holding an index.html.
    for idx in sorted(ROOT.glob("*/index.html")):
        d = idx.parent
        if d.name in EXCLUDE_DIRS:
            continue
        title, meta_unit = extract(idx)
        entries.append({
            "unit": meta_unit or slug(d.name),
            "url": "/" + d.name + "/",
            "title": title,
            "last_modified": git_last_modified(f"{d.name}/index.html"),
            "kind": "project",
        })

    entries.sort(key=lambda e: e["unit"])
    out = ROOT / "published-corpus.json"
    out.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {out.name} — {len(entries)} units:")
    for e in entries:
        print(f"  {e['unit']:26} {e['url']:28} {e['kind']}")


if __name__ == "__main__":
    main()
