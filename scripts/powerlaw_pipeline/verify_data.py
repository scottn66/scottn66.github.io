#!/usr/bin/env python3
"""Sanity gate for a freshly regenerated bitcoin-power-law/assets/data.js.

Hard failures (exit 1) guard the page and the daily price patcher:
structure, key set, the exact `"current": {...}` shape update_btc_price.py
regex-patches, freshness, and the five figure PNGs.

Soft tripwires print GitHub `::warning::` annotations when regenerated data
flips a claim that index.html still hardcodes in prose, so drift is visible
in the workflow run without blocking the refresh.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "bitcoin-power-law/assets/data.js"
FIGURES = ["fig_residual_dist.png", "fig_qq.png", "fig_lag.png", "fig_cycles.png", "fig_aic.png"]
EXPECTED_KEYS = {
    "genesis", "current", "fit_full", "fit_coinbase", "corridor", "model_line",
    "series", "anchors", "projections", "residuals", "cointegration",
    "model_comparison", "model_comparison_full", "mean_reversion", "lppls",
    "lppls_cycles", "stability", "risk", "generated_at",
}

errors: list[str] = []
warnings: list[str] = []

raw = DATA.read_text()
match = re.search(r"window\.PL\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S)
if not match:
    sys.exit("FAIL: data.js does not match `window.PL = {...};`")
try:
    pl = json.loads(match.group(1))
except json.JSONDecodeError as exc:
    sys.exit(f"FAIL: data.js payload is not valid JSON: {exc}")

if set(pl) != EXPECTED_KEYS:
    errors.append(f"top-level keys changed: missing={EXPECTED_KEYS - set(pl)} extra={set(pl) - EXPECTED_KEYS}")

# The daily price patcher (scripts/update_btc_price.py) regex-substitutes the
# single flat `"current": {...}` block; both properties must survive a regen.
if raw.count('"current"') != 1:
    errors.append(f'`"current"` appears {raw.count(chr(34) + "current" + chr(34))} times, expected exactly 1')
if not re.search(r'"current": \{[^{}]*\}', raw):
    errors.append('`"current": {...}` block not found in the shape update_btc_price.py patches')

series = pl.get("series", [])
if len(series) <= 400:
    errors.append(f"series has {len(series)} points, expected > 400")
if series:
    last = dt.date.fromisoformat(series[-1]["date"])
    age = (dt.date.today() - last).days
    if age > 14:
        errors.append(f"series ends {last} ({age} days ago), expected within 14 days")
cur = pl.get("current", {})
if not cur.get("price", 0) > 0:
    errors.append(f"current.price is {cur.get('price')!r}")

for name in FIGURES:
    fig = ROOT / "bitcoin-power-law/assets" / name
    if not fig.exists() or fig.stat().st_size < 10_000:
        errors.append(f"figure {name} missing or under 10 KB")

# --- drift tripwires: claims index.html hardcodes in prose -------------------
if cur.get("residual", -1) >= 0:
    warnings.append("current.residual >= 0: page prose still says price sits below fair value")
passing = [c["label"] for c in pl.get("lppls_cycles", []) if c.get("passes_strict_filter")]
if len(passing) != 1:
    warnings.append(f"LPPLS cycles passing the strict filter: {passing or 'none'} "
                    "(page prose says exactly one, the 2024-25 cycle)")
ci = pl.get("fit_coinbase", {}).get("n_ci_boot", [None, None])
if ci[0] is None or not (4.0 <= ci[0] and ci[1] <= 6.5):
    warnings.append(f"bootstrap CI {ci} left [4.0, 6.5]: page prose quotes 'roughly [4.3, 6.2]'")

for w in warnings:
    print(f"::warning::{w}")
if errors:
    for e in errors:
        print(f"FAIL: {e}")
    sys.exit(1)
print(f"OK: data.js valid ({len(raw)} bytes), series through {series[-1]['date']}, "
      f"price ${cur['price']:,.2f}, generated {pl['generated_at']}, {len(warnings)} warning(s)")
