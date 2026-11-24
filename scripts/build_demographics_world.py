#!/usr/bin/env python3
"""Sum the shipped per-country pyramids into one world aggregate.

Reads  demographics/data/countries/*.json   (built by build_demographics_data.py)
Writes demographics/data/world.json         (same pyramid schema as a country file)

The forecast section of the demographics article (demographics/forecast.js)
treats "World" as one more row: every derived quantity there - economic
support ratio, demographic growth term, certainty horizon - is computed in
the browser from a pyramid, so the only thing the world needs is its pyramid.
No network, no third-party packages; re-run after rebuilding the country files.

    python3 scripts/build_demographics_world.py [--verify]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COUNTRIES = ROOT / "demographics" / "data" / "countries"
OUT = ROOT / "demographics" / "data" / "world.json"


def build():
    files = sorted(COUNTRIES.glob("*.json"))
    if not files:
        sys.exit(f"no country files under {COUNTRIES}")
    ages = years = None
    m = f = None
    used = 0
    for path in files:
        pyr = json.loads(path.read_text())["pyramid"]
        if ages is None:
            ages, years = pyr["ages"], pyr["years"]
            m = [[0.0] * len(ages) for _ in years]
            f = [[0.0] * len(ages) for _ in years]
        if pyr["ages"] != ages or pyr["years"] != years:
            sys.exit(f"{path.name}: pyramid grid differs from the first file")
        if any(row is None for row in pyr["m"]) or any(row is None for row in pyr["f"]):
            sys.exit(f"{path.name}: missing pyramid year; refusing to build a partial world")
        for j in range(len(years)):
            for b in range(len(ages)):
                m[j][b] += pyr["m"][j][b]
                f[j][b] += pyr["f"][j][b]
        used += 1
    return {
        "iso3": "WLD",
        "name": "World",
        "n_countries": used,
        "source": "sum of demographics/data/countries/*.json pyramids (UN WPP 2024, medium variant; thousands)",
        "pyramid": {
            "ages": ages,
            "years": years,
            "m": [[round(v) for v in row] for row in m],
            "f": [[round(v) for v in row] for row in f],
        },
    }


def verify(world):
    pyr = world["pyramid"]
    j = pyr["years"].index(2025)
    total = sum(pyr["m"][j]) + sum(pyr["f"][j])
    assert 8.1e6 < total < 8.4e6, f"world 2025 population {total:,.0f}k outside 8.1-8.4 bn"
    assert world["n_countries"] >= 230, f"only {world['n_countries']} country files summed"
    assert len(pyr["ages"]) == 21 and len(pyr["years"]) == 31, "unexpected pyramid grid"
    totals = [sum(pyr["m"][i]) + sum(pyr["f"][i]) for i in range(len(pyr["years"]))]
    peak = pyr["years"][totals.index(max(totals))]
    assert 2075 <= peak <= 2095, f"world population peak {peak} outside 2075-2095"
    print(f"verify ok: {world['n_countries']} countries, 2025 total {total / 1e6:.3f} bn, peak {peak}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--verify", action="store_true", help="run sanity assertions on the result")
    args = ap.parse_args()
    world = build()
    if args.verify:
        verify(world)
    OUT.write_text(json.dumps(world, separators=(",", ":"), sort_keys=True))
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.1f} KB)")
