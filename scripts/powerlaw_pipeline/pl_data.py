#!/usr/bin/env python3
"""Assemble power_law.json + econ.json into a compact data.js for the portfolio
page (window.PL). Downsamples dense series to keep the payload light."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "runs/power_law"
OUT = ROOT / "bitcoin-power-law/assets/data.js"


def downsample(lst, n):
    if len(lst) <= n:
        return lst
    step = len(lst) / n
    return [lst[int(i * step)] for i in range(n)] + [lst[-1]]


def main():
    pl = json.loads((RUN / "power_law.json").read_text())
    ec = json.loads((RUN / "econ.json").read_text())

    ml = pl["model_line"]
    keep = list(range(0, len(ml["days"]), max(1, len(ml["days"]) // 160)))
    model_line = {
        "dates": [ml["dates"][i] for i in keep],
        "mid": [ml["mid"][i] for i in keep],
        "q05": [ml["q05"][i] for i in keep],
        "q25": [ml["q25"][i] for i in keep],
        "q75": [ml["q75"][i] for i in keep],
        "q95": [ml["q95"][i] for i in keep],
    }

    series = pl["series"]  # already weekly
    resid = ec["residuals"]
    rk = list(range(0, len(resid["dates"]), 5))  # ~weekly from daily
    residuals = {
        "dates": [resid["dates"][i] for i in rk],
        "z": [round(resid["z"][i], 3) for i in rk],
    }

    payload = {
        "genesis": pl["genesis"],
        "current": pl["current"],
        "fit_full": pl["fit_full"],
        "fit_coinbase": ec["fit_coinbase"],
        "corridor": pl["corridor_quantiles"],
        "model_line": model_line,
        "series": [{"date": s["date"], "price": s["price"]} for s in series],
        "anchors": [{"date": a["date"], "price": a["price"], "note": a.get("note", "")} for a in pl["anchors"]],
        "projections": pl["projections"],
        "residuals": residuals,
        "cointegration": ec["cointegration"],
        "model_comparison": ec["model_comparison"],
        "model_comparison_full": ec["model_comparison_full"],
        "mean_reversion": ec["mean_reversion"],
        "lppls": ec["lppls"],
        "lppls_cycles": [
            {k: c[k] for k in ("label", "tc_date", "actual_peak_date", "m", "omega", "r2", "passes_strict_filter") if k in c}
            for c in ec.get("lppls_cycles", [])
        ],
        "stability": {
            "rolling_exponent": [
                {"date": _t2date(pl["genesis"], e["t"]), "n": round(e["n"], 3)}
                for e in ec["stability"]["rolling_exponent"]
            ],
            "chow_tests": ec["stability"]["chow_tests"],
            "interpretation": ec["stability"]["interpretation"],
        },
        "risk": ec["risk"],
        "generated_at": ec["generated_at"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("window.PL = " + json.dumps(payload) + ";\n")
    print("wrote", OUT, OUT.stat().st_size, "bytes")


def _t2date(genesis, t):
    import pandas as pd
    return (pd.Timestamp(genesis, tz="UTC") + pd.to_timedelta(float(t), unit="D")).strftime("%Y-%m-%d")


if __name__ == "__main__":
    main()
