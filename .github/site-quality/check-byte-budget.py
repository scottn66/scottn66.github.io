#!/usr/bin/env python3
"""Fail tracked files over 1 MiB unless they are on the allowlist.

Newly added files, and files that were small and then grew, are not on the
allowlist, so they fail. Files already over the budget on main are listed in
byte-budget-allowlist.txt with a cap, so main stays green. Growing a listed
file past its cap fails. Removing one does not.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BUDGET = 1_048_576  # 1 MiB, about 1 MB
ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = Path(__file__).resolve().parent / "byte-budget-allowlist.txt"


def parse_allowlist(text: str) -> dict[str, int]:
    allowlist: dict[str, int] = {}
    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            raise SystemExit(f"{ALLOWLIST_PATH}:{line_no}: expected 'path max_bytes'")
        path, cap_text = parts
        if path.startswith("/") or ".." in Path(path).parts:
            raise SystemExit(f"{ALLOWLIST_PATH}:{line_no}: path must stay inside the repo")
        try:
            cap = int(cap_text)
        except ValueError:
            raise SystemExit(f"{ALLOWLIST_PATH}:{line_no}: max_bytes is not an integer") from None
        if cap <= BUDGET:
            raise SystemExit(
                f"{ALLOWLIST_PATH}:{line_no}: max_bytes must be over the {BUDGET} byte budget"
            )
        if path in allowlist:
            raise SystemExit(f"{ALLOWLIST_PATH}:{line_no}: duplicate path {path}")
        allowlist[path] = cap
    return allowlist


def evaluate(
    sizes: dict[str, int], allowlist: dict[str, int], budget: int = BUDGET
) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    for path in sorted(sizes):
        size = sizes[path]
        if size <= budget:
            if path in allowlist:
                warnings.append(
                    f"{path} is {size} bytes, at or under the budget; "
                    "the allowlist entry can be removed"
                )
            continue
        cap = allowlist.get(path)
        if cap is None:
            failures.append(
                f"{path} is {size} bytes, over the {budget} byte budget"
            )
        elif size > cap:
            failures.append(
                f"{path} is {size} bytes, over its allowlist cap of {cap} bytes"
            )
    for path in sorted(allowlist):
        if path not in sizes:
            warnings.append(f"allowlist entry has no tracked file: {path}")
    return failures, warnings


def tracked_sizes(root: Path) -> dict[str, int]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    sizes: dict[str, int] = {}
    for raw in output.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode()
        path = root / rel
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"tracked path is not a regular file: {rel}")
        sizes[rel] = path.stat().st_size
    return sizes


def self_test() -> None:
    budget = 100
    allowlist = {"kept.bin": 150, "gone.bin": 180, "small-listed.bin": 200}
    sizes = {
        "ok.txt": 100,
        "new-big.bin": 101,
        "kept.bin": 150,
        "grown.bin": 140,
        "small-listed.bin": 50,
    }
    # grown.bin is over the budget and not allowlisted.
    failures, warnings = evaluate(sizes, allowlist, budget)
    expected_failures = {
        "new-big.bin is 101 bytes, over the 100 byte budget",
        "grown.bin is 140 bytes, over the 100 byte budget",
    }
    if set(failures) != expected_failures:
        raise SystemExit(f"self-test failures mismatch:\n{failures}")
    warning_text = "\n".join(warnings)
    if "gone.bin" not in warning_text or "small-listed.bin" not in warning_text:
        raise SystemExit(f"self-test warnings mismatch:\n{warnings}")
    over_cap, _ = evaluate({"kept.bin": 151}, allowlist, budget)
    if over_cap != ["kept.bin is 151 bytes, over its allowlist cap of 150 bytes"]:
        raise SystemExit(f"self-test cap mismatch:\n{over_cap}")
    under, under_warnings = evaluate({"kept.bin": 80, "ok.txt": 10}, {"kept.bin": 150}, budget)
    if under or not any("kept.bin" in warning for warning in under_warnings):
        raise SystemExit(f"self-test shrink mismatch:\n{under}\n{under_warnings}")
    print("byte-budget self-test: new or grown file over the budget failed as expected")
    print("byte-budget self-test: allowlisted file under its cap passed")
    print("byte-budget self-test: allowlisted file over its cap failed as expected")
    print("byte-budget self-test: missing allowlist entry warned and did not fail")
    print("byte-budget self-test: ok")


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        self_test()
        return 0
    if argv[1:]:
        raise SystemExit(f"usage: {argv[0]} [--self-test]")
    allowlist = parse_allowlist(ALLOWLIST_PATH.read_text())
    sizes = tracked_sizes(ROOT)
    failures, warnings = evaluate(sizes, allowlist)
    over = [path for path, size in sizes.items() if size > BUDGET]
    print(f"byte budget: {BUDGET} bytes (1 MiB)")
    print(f"tracked files: {len(sizes)}")
    print(f"over budget: {len(over)}")
    print(f"allowlisted: {len(allowlist)}")
    for warning in warnings:
        print(f"warning: {warning}")
    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1
    print("byte budget: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
