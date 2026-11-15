#!/usr/bin/env python3
"""Compute the productivity-weighted age-structure score and the NTA
economic support ratio for every country in the portfolio site's
shipped WPP 2024 pyramids, using a measured NTA cross-country average
labor-income profile as the weight.

Inputs (read-only):
  - scottn66.github.io demographics country JSON (WPP 2024 medium,
    5-year age groups, 1950-2100), already built by
    scripts/build_demographics_data.py
  - NTA "Yl and C CSV" from Mason, Lee, Abrigo & Lee, UN DESA
    Population Division Technical Paper 2017/1, downloaded from
    https://ntaccounts.org/doc/repository/Yl%20and%20C%20CSV.csv

Outputs written under data/:
  profiles.json, scores.json, display.json, report.txt, data.js

Run from the repository root:
  python3 demographics/finance-draft/scripts/compute_scores.py
Needs Python 3 with numpy and pandas. Set DEMOGRAPHICS_DIR to point at a
different copy of the essay's demographics/ folder if needed.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import os
import sys

# Layout on the review branch: demographics/finance-draft/scripts/compute_scores.py
ROOT = Path(__file__).resolve().parent.parent          # demographics/finance-draft
REPO = Path(os.environ.get("DEMOGRAPHICS_DIR", ROOT.parent))  # demographics/
NTA_CSV = ROOT / "data/source/nta-yl-c-2017.csv"
OUT = ROOT / "data"

AGE_LABELS = [
    "0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39",
    "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79",
    "80-84", "85-89", "90-94", "95-99", "100+",
]
# Midpoints used only for plotting the binned weight; 100+ plotted at 102.
MIDPOINTS = [2, 7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72, 77, 82, 87, 92, 97, 102]

DISPLAY_ISO = [
    "NER", "NGA", "ETH", "KEN", "PAK", "EGY", "PHL", "BGD", "ZAF",
    "IND", "MEX", "IDN", "COL", "BRA", "TUR", "IRN", "VNM", "SAU",
    "THA", "CHN", "USA", "AUS", "CAN", "GBR", "SWE", "FRA", "POL",
    "RUS", "DEU", "KOR", "ESP", "ITA", "GRC", "JPN",
]

SHORT_NAME = {
    "USA": "United States",
    "GBR": "United Kingdom",
    "KOR": "South Korea",
    "RUS": "Russia",
    "TUR": "Turkey",
    "VNM": "Vietnam",
    "IRN": "Iran",
    "TWN": "Taiwan",
    "CIV": "Côte d'Ivoire",
    "BOL": "Bolivia",
    "VEN": "Venezuela",
    "TZA": "Tanzania",
    "COD": "DR Congo",
    "CZE": "Czechia",
    "SVK": "Slovakia",
    "SYR": "Syria",
    "LAO": "Laos",
    "MDA": "Moldova",
    "MKD": "North Macedonia",
    "BIH": "Bosnia and Herzegovina",
    "KHM": "Cambodia",
    "MMR": "Myanmar",
    "PRK": "North Korea",
    "ARE": "UAE",
    "SGP": "Singapore",
    "HKG": "Hong Kong",
    "MAC": "Macao",
    "PSE": "Palestine",
    "COD": "DR Congo",
    "CAF": "Central African Republic",
    "GNB": "Guinea-Bissau",
    "GNQ": "Equatorial Guinea",
    "STP": "São Tomé and Príncipe",
    "TLS": "Timor-Leste",
}

# Featured country colors, matching the live demographics page, plus extras.
COLORS = {
    "USA": "#1F4E9E", "CHN": "#B83A2E", "DEU": "#A8861D", "NGA": "#2F7A4A",
    "JPN": "#6A4FA3", "KOR": "#0782AF", "IND": "#C2632F",
    "ITA": "#8B3A62", "BRA": "#3D7A5A", "MEX": "#C2632F",
    "FRA": "#1F4E9E", "GBR": "#555555", "ETH": "#2F7A4A",
}


def stylized_profiles_single():
    """The live page's stylized pair, ages 0..100, in % of peak labor income.
    Kept in sync with demographics/app.js and build_demographics_data.py.
    """
    yl, cons = [], []
    for a in range(101):
        aa = min(a, 90)
        ramp = 100.0 / (1.0 + math.exp(-(aa - 30) / 5.5))
        fade = 1.0 / (1.0 + math.exp((aa - 61) / 4.5))
        yl.append(max(0.0, ramp * fade * 1.19 - (100.0 if aa < 15 else 0.0)))
        c = 34.0 + 24.0 / (1.0 + math.exp(-(aa - 10) / 4.0))
        c += 12.0 / (1.0 + math.exp(-(aa - 22) / 3.0))
        c += 10.0 / (1.0 + math.exp(-(aa - 74) / 6.0))
        cons.append(c)
    return np.array(yl, dtype=float), np.array(cons, dtype=float)


def normalize_3049(arr):
    """NTA convention: divide by the mean of ages 30 through 49 inclusive."""
    scale = arr[30:50].mean()
    if scale <= 0:
        raise ValueError("30-49 mean is non-positive")
    return arr / scale, float(scale)


def bin_weights(single, n_ages=101):
    """Average a single-age 0..n_ages-1 profile into the 21 WPP 5-year bins.
    Ages past the last measured point reuse the last value (documented).
    """
    ext = np.empty(101, dtype=float)
    m = len(single)
    ext[:m] = single
    if m < 101:
        ext[m:] = single[-1]
    bins = []
    for start in range(0, 100, 5):
        bins.append(float(ext[start:start + 5].mean()))
    bins.append(float(ext[100]))  # 100+
    assert len(bins) == 21
    return bins


def load_nta_country_estimates():
    df = pd.read_csv(NTA_CSV)
    ce = df[df["Age profile estimate"] == "Country estimate"].copy()
    age_cols = [f"Age{i}" for i in range(91)]
    profiles = {}
    meta = []
    for _, row in ce.iterrows():
        iso = row["ISO 3166-alpha 3"]
        var = row["Variable Name"]
        vals = row[age_cols].to_numpy(dtype=float)
        profiles.setdefault(iso, {})[var] = vals
        if var == "Labor income":
            meta.append({
                "iso3": iso,
                "name": row["Name"],
                "year": int(row["Year"]),
                "region": row["Region"],
                "subregion": row["Sub-region"],
                "income_group": row["Income group"],
                "peak_age": int(np.nanargmax(vals)),
                "peak_value": float(np.nanmax(vals)),
                "yl65": float(vals[65]),
                "yl80": float(vals[80]),
            })
    # Unweighted cross-country average of the 56 country-team profiles.
    # Each is already normalized so its own 30-49 mean equals 1.
    yl_stack = np.stack([profiles[i]["Labor income"] for i in profiles])
    c_stack = np.stack([profiles[i]["Consumption"] for i in profiles])
    yl_avg = yl_stack.mean(axis=0)
    c_avg = c_stack.mean(axis=0)
    # Each country is already at a 30-49 mean of 1, up to rounding.
    # Renormalize the average so the convention holds exactly.
    yl_avg = yl_avg / yl_avg[30:50].mean()
    c_avg = c_avg / c_avg[30:50].mean()
    assert abs(yl_avg[30:50].mean() - 1) < 1e-12
    assert abs(c_avg[30:50].mean() - 1) < 1e-12
    return profiles, meta, yl_avg, c_avg


def short(iso, full):
    if iso in SHORT_NAME:
        return SHORT_NAME[iso]
    # Trim common long forms
    for suffix in (
        " of America",
        " (Islamic Republic of)",
        " (Bolivarian Republic of)",
        " (Plurinational State of)",
    ):
        if full.endswith(suffix):
            full = full[: -len(suffix)]
    if full.startswith("United Kingdom"):
        return "United Kingdom"
    return full


def main():
    nta_profiles, nta_meta, yl_nta, c_nta = load_nta_country_estimates()
    yl_sty, c_sty = stylized_profiles_single()
    yl_sty_n, yl_sty_scale = normalize_3049(yl_sty)
    c_sty_n, c_sty_scale = normalize_3049(c_sty)

    w_nta = bin_weights(yl_nta)       # primary productivity weights
    c_nta_b = bin_weights(c_nta)
    w_sty = bin_weights(yl_sty_n)
    c_sty_b = bin_weights(c_sty_n)

    summary = json.loads((REPO / "data/countries-summary.json").read_text())
    countries_sum = summary["countries"]

    # Single-age stylized peak, for the lifecycle figure annotation.
    peak_nta = int(yl_nta.argmax())
    peak_sty = int(yl_sty.argmax())

    scores = {}
    for iso, summ in countries_sum.items():
        path = REPO / "data/countries" / f"{iso}.json"
        detail = json.loads(path.read_text())
        pyr = detail["pyramid"]
        years = pyr["years"]
        # years is a list of ints
        def pop_vec(year):
            i = years.index(year)
            m, f = pyr["m"][i], pyr["f"][i]
            if m is None or f is None:
                return None
            return np.array(m, dtype=float) + np.array(f, dtype=float)

        def weighted_sum(vec, w):
            tot = vec.sum()
            if tot <= 0:
                return None
            return float(np.dot(w, vec) / tot)

        def esr(vec, yl, c):
            den = float(np.dot(c, vec))
            if den <= 0:
                return None
            return float(np.dot(yl, vec) / den)

        # Shipped ESR is computed from single-year ages with the stylized pair.
        esr_series = detail["series"]["esr"]
        esr_years = detail["series"]["years"]

        rec = {
            "iso3": iso,
            "name": summ["n"],
            "short": short(iso, summ["n"]),
            "pop_2025_thousands": summ["pop"],
            "median_age_2025": summ["ma"],
            "median_age_2050": summ["ma50"],
            "tfr_2025": summ["tfr"],
            "headcount_sr_2025": summ["sr"],
            "esr_shipped_2025": summ["esr"],
            "nta_country_profile": iso in nta_profiles,
        }
        for year in (2025, 2050):
            vec = pop_vec(year)
            if vec is None:
                continue
            shares = (vec / vec.sum()).tolist()
            rec[f"pop_{year}_thousands_from_pyramid"] = float(vec.sum())
            rec[f"S_nta_{year}"] = weighted_sum(vec, w_nta)
            rec[f"S_sty_{year}"] = weighted_sum(vec, w_sty)
            rec[f"esr_nta_{year}"] = esr(vec, w_nta, c_nta_b)
            rec[f"esr_sty_{year}"] = esr(vec, w_sty, c_sty_b)
            rec[f"share_45_64_{year}"] = float(vec[9:13].sum() / vec.sum())  # 45-49 .. 60-64
            rec[f"share_0_14_{year}"] = float(vec[0:3].sum() / vec.sum())
            rec[f"share_65plus_{year}"] = float(vec[13:].sum() / vec.sum())
            yi = esr_years.index(year)
            rec[f"esr_shipped_{year}"] = esr_series[yi]
            rec[f"shares_{year}"] = [round(s, 6) for s in shares]
        # First-dividend growth, annualized, 2025-2050 (identity: d/dt ln SR).
        if rec.get("esr_nta_2025") and rec.get("esr_nta_2050"):
            rec["fdg_nta_2025_2050"] = math.log(rec["esr_nta_2050"] / rec["esr_nta_2025"]) / 25.0
        if rec.get("S_nta_2025") and rec.get("S_nta_2050"):
            rec["dS_nta"] = rec["S_nta_2050"] - rec["S_nta_2025"]
        scores[iso] = rec

    # Rank (descending) among all 236 with a 2025 score.
    def add_ranks(key):
        items = [(iso, rec[key]) for iso, rec in scores.items() if rec.get(key) is not None]
        items.sort(key=lambda x: x[1], reverse=True)
        n = len(items)
        for r, (iso, _) in enumerate(items, start=1):
            scores[iso][f"rank_{key}"] = r
            scores[iso][f"n_{key}"] = n

    for key in (
        "S_nta_2025", "S_nta_2050", "esr_nta_2025", "esr_nta_2050",
        "S_sty_2025", "esr_sty_2025", "esr_shipped_2025",
        "share_45_64_2025",
    ):
        add_ranks(key)

    # Correlations, to judge whether the hypothesis is informative.
    def corr(a, b, isos=None):
        xs, ys = [], []
        src = isos if isos is not None else scores.keys()
        for iso in src:
            rec = scores[iso]
            if rec.get(a) is not None and rec.get(b) is not None:
                xs.append(rec[a])
                ys.append(rec[b])
        if len(xs) < 5:
            return None
        return float(np.corrcoef(xs, ys)[0, 1])

    diagnostics = {
        "n_countries": len(scores),
        "n_nta_country_profiles": len(nta_meta),
        "corr_S_nta_vs_S_sty_2025": corr("S_nta_2025", "S_sty_2025"),
        "corr_S_nta_vs_esr_nta_2025": corr("S_nta_2025", "esr_nta_2025"),
        "corr_S_nta_vs_share_45_64_2025": corr("S_nta_2025", "share_45_64_2025"),
        "corr_S_nta_vs_median_age_2025": corr("S_nta_2025", "median_age_2025"),
        "corr_esr_nta_vs_esr_shipped_2025": corr("esr_nta_2025", "esr_shipped_2025"),
        "corr_esr_sty_vs_esr_shipped_2025": corr("esr_sty_2025", "esr_shipped_2025"),
        "corr_S_nta_2025_vs_2050": corr("S_nta_2025", "S_nta_2050"),
        "mean_abs_esr_sty_vs_shipped": None,
    }
    diffs = []
    for rec in scores.values():
        if rec.get("esr_sty_2025") is not None and rec.get("esr_shipped_2025") is not None:
            diffs.append(abs(rec["esr_sty_2025"] - rec["esr_shipped_2025"]))
    diagnostics["mean_abs_esr_sty_vs_shipped"] = float(np.mean(diffs))
    diagnostics["max_abs_esr_sty_vs_shipped"] = float(np.max(diffs))

    def top_bottom(key, k=10):
        items = [(rec["short"], rec["iso3"], rec[key]) for rec in scores.values() if rec.get(key) is not None]
        items.sort(key=lambda x: x[2], reverse=True)
        return {"top": items[:k], "bottom": items[-k:]}

    diagnostics["leaderboard_S_nta_2025"] = top_bottom("S_nta_2025", 15)
    diagnostics["leaderboard_S_nta_2050"] = top_bottom("S_nta_2050", 15)
    diagnostics["leaderboard_esr_nta_2025"] = top_bottom("esr_nta_2025", 15)
    diagnostics["leaderboard_esr_nta_2050"] = top_bottom("esr_nta_2050", 15)

    # Display subset, with shares for the small-multiples figure.
    display = []
    for iso in DISPLAY_ISO:
        rec = dict(scores[iso])
        rec["color"] = COLORS.get(iso)
        display.append(rec)

    # Small-multiples countries (types along the transition).
    small = ["NGA", "IND", "MEX", "USA", "CHN", "JPN"]

    # Profiles file: single-age measured average, a few country examples,
    # and the stylized pair (renormalized) for comparison with Fig 3.
    example_isos = ["USA", "DEU", "JPN", "CHN", "IND", "NGA", "MEX"]
    examples = {}
    for iso in example_isos:
        if iso in nta_profiles:
            examples[iso] = {
                "iso3": iso,
                "name": short(iso, countries_sum[iso]["n"] if iso in countries_sum else iso),
                "year": next(m["year"] for m in nta_meta if m["iso3"] == iso),
                "yl": [round(float(x), 5) for x in nta_profiles[iso]["Labor income"]],
                "c": [round(float(x), 5) for x in nta_profiles[iso]["Consumption"]],
            }

    profiles_out = {
        "meta": {
            "nta_source": (
                "Mason, Lee, Abrigo & Lee, 2017, 'Support Ratio and Demographic "
                "Dividends: Estimates for the World', UN DESA Population Division "
                "Technical Paper 2017/1. Labor-income and consumption profiles "
                "downloaded from https://ntaccounts.org/doc/repository/Yl%20and%20C%20CSV.csv "
                "(file timestamp on the NTA server is the 2017 release). "
                "Unit: each country's profile is normalized so the mean of ages "
                "30-49 equals 1. The global weight is the unweighted average of "
                "the 56 country-team ('Country estimate') profiles."
            ),
            "nta_source_url": "https://ntaccounts.org/doc/repository/Yl%20and%20C%20CSV.csv",
            "nta_project_page": "https://ntaccounts.org/web/nta/show/Documents/UNPD%20Project%202016",
            "wpp_source": (
                "United Nations, Department of Economic and Social Affairs, "
                "Population Division, World Population Prospects 2024, medium "
                "variant, as already shipped by this site "
                "(demographics/data/countries/*.json), built from the "
                "PPgp/wpp2024 data package. CC BY 3.0 IGO."
            ),
            "wpp_url": "https://population.un.org/wpp/",
            "wpp_package": "https://github.com/PPgp/wpp2024",
            "n_country_estimates": len(nta_meta),
            "normalization": "mean labor income (or consumption) of ages 30-49 equals 1",
            "ages_beyond_90": (
                "NTA profiles end at age 90; ages 91-100+ reuse the age-90 value. "
                "The 100+ population bin uses that same value."
            ),
            "binning": (
                "Single-age weights are averaged inside each WPP 5-year group "
                "(equal weight on the five ages). This is an approximation: the "
                "site's shipped economic support ratio uses single-year population."
            ),
            "stylized_note": (
                "The stylized pair is the same formula as Fig 3 on the live "
                "demographics page, renormalized here to a 30-49 mean of 1 so "
                "levels can be compared with the NTA average. The live page "
                "plots it as % of peak labor income."
            ),
            "peak_age_nta_average": peak_nta,
            "peak_value_nta_average": float(yl_nta[peak_nta]),
            "peak_age_stylized": peak_sty,
            "yl_stylized_3049_scale_in_peak_percent": yl_sty_scale,
        },
        "ages": list(range(91)),
        "yl_nta_average": [round(float(x), 6) for x in yl_nta],
        "c_nta_average": [round(float(x), 6) for x in c_nta],
        "yl_stylized_normalized": [round(float(x), 6) for x in yl_sty_n[:91]],
        "c_stylized_normalized": [round(float(x), 6) for x in c_sty_n[:91]],
        "yl_stylized_peak_percent": [round(float(x), 6) for x in yl_sty[:91]],
        "c_stylized_peak_percent": [round(float(x), 6) for x in c_sty[:91]],
        "weights_5yr_nta": [round(x, 6) for x in w_nta],
        "consumption_5yr_nta": [round(x, 6) for x in c_nta_b],
        "weights_5yr_stylized": [round(x, 6) for x in w_sty],
        "age_labels_5yr": AGE_LABELS,
        "midpoints_5yr": MIDPOINTS,
        "country_examples": examples,
        "country_estimate_meta": nta_meta,
    }

    # Slim scores for the page (no full share vectors for all 236 in the
    # main scores file... actually we want shares only for display countries).
    scores_slim = {}
    for iso, rec in scores.items():
        slim = {k: v for k, v in rec.items() if not k.startswith("shares_")}
        scores_slim[iso] = slim

    display_out = []
    for rec in display:
        display_out.append(rec)

    meta_out = {
        "generated_for": "portfolio-demographics finance-section draft (not published)",
        "ref_years": [2025, 2050],
        "wpp": "2024 medium variant",
        "primary_weight": (
            "Unweighted average of 56 NTA country-team labor-income profiles, "
            "normalized to a 30-49 mean of 1."
        ),
        "metrics": {
            "S": "sum_a w(a) * P(a) / sum P(a), with w = NTA average labor income. "
                 "Units: effective prime-age labor-income equivalents per person.",
            "esr": "sum_a yl(a) P(a) / sum_a c(a) P(a), same NTA average profiles. "
                   "Levels are profile-relative (yl and c are each normalized to "
                   "their own 30-49 mean); ranks and changes are not.",
        },
        "diagnostics": diagnostics,
        "display_iso": DISPLAY_ISO,
        "small_multiples_iso": small,
        "n_display": len(DISPLAY_ISO),
        "n_all": len(scores_slim),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "profiles.json").write_text(json.dumps(profiles_out, indent=2))
    (OUT / "scores.json").write_text(json.dumps({
        "meta": meta_out,
        "countries": scores_slim,
    }, indent=2))
    (OUT / "display.json").write_text(json.dumps({
        "meta": {k: meta_out[k] for k in (
            "generated_for", "ref_years", "wpp", "primary_weight", "metrics",
            "display_iso", "small_multiples_iso", "n_display", "n_all",
        )},
        "diagnostics": diagnostics,
        "countries": display_out,
    }, indent=2))

    # Human-readable report for the parent agent.
    def fmt_board(board, keylabel):
        lines = [f"  Top 15 by {keylabel}:"]
        for name, iso, v in board["top"]:
            lines.append(f"    {iso:3}  {name:<22} {v:.3f}")
        lines.append(f"  Bottom 15 by {keylabel}:")
        for name, iso, v in board["bottom"]:
            lines.append(f"    {iso:3}  {name:<22} {v:.3f}")
        return "\n".join(lines)

    report = []
    report.append("=== DIAGNOSTICS ===")
    for k, v in diagnostics.items():
        if k.startswith("leaderboard"):
            continue
        report.append(f"  {k}: {v}")
    report.append("")
    report.append(fmt_board(diagnostics["leaderboard_S_nta_2025"], "S_nta 2025"))
    report.append("")
    report.append(fmt_board(diagnostics["leaderboard_S_nta_2050"], "S_nta 2050"))
    report.append("")
    report.append(fmt_board(diagnostics["leaderboard_esr_nta_2025"], "ESR_nta 2025"))
    report.append("")
    report.append("=== DISPLAY SET (S_nta 2025 and 2050, ESR, ranks among 236) ===")
    report.append(f"{'iso':3} {'name':22} {'S25':>6} {'rS25':>5} {'S50':>6} {'rS50':>5} {'dS':>6} {'ESR25':>6} {'rE25':>5} {'ESR50':>6} {'ma':>5} {'ma50':>5}")
    # sort display by S 2025 desc
    rows = sorted(display_out, key=lambda r: r["S_nta_2025"], reverse=True)
    for r in rows:
        report.append(
            f"{r['iso3']:3} {r['short']:<22} {r['S_nta_2025']:.3f} {r['rank_S_nta_2025']:5d} "
            f"{r['S_nta_2050']:.3f} {r['rank_S_nta_2050']:5d} {r['dS_nta']:+.3f} "
            f"{r['esr_nta_2025']:.3f} {r['rank_esr_nta_2025']:5d} {r['esr_nta_2050']:.3f} "
            f"{r['median_age_2025']:5.1f} {r['median_age_2050']:5.1f}"
        )
    pop_w = emit_data_js(
        profiles_out,
        json.loads((OUT / "display.json").read_text()),
        json.loads((OUT / "scores.json").read_text()),
    )
    report.append("")
    report.append("=== WORLD (population-weighted S) ===")
    for year in (2025, 2050):
        report.append(f"  {year}: S={pop_w[year][0]:.4f}  population={pop_w[year][1]:.2f} billion")
    text = "\n".join(report)
    (OUT / "report.txt").write_text(text)
    print(text)
    print("\nWrote", OUT)


def emit_data_js(profiles, display, scores):
    """Write data/data.js, the payload the page loads with a script tag."""
    pop_w = {}
    for year in (2025, 2050):
        num = den = 0.0
        for r in scores["countries"].values():
            pop = r.get(f"pop_{year}_thousands_from_pyramid")
            s = r.get(f"S_nta_{year}")
            if pop and s is not None:
                num += s * pop
                den += pop
        pop_w[year] = (num / den, den / 1e6)
    allc = []
    for iso, r in scores["countries"].items():
        allc.append({
            "iso3": iso, "short": r["short"], "pop": r["pop_2025_thousands"],
            "ma": r["median_age_2025"], "ma50": r["median_age_2050"],
            "S25": round(r["S_nta_2025"], 4), "S50": round(r["S_nta_2050"], 4),
            "dS": round(r["dS_nta"], 4), "esr25": round(r["esr_nta_2025"], 4),
            "esr50": round(r["esr_nta_2050"], 4), "rS25": r["rank_S_nta_2025"],
            "rS50": r["rank_S_nta_2050"], "rE25": r["rank_esr_nta_2025"],
            "tfr": r["tfr_2025"], "sr": r["headcount_sr_2025"],
            "display": iso in display["meta"]["display_iso"],
        })
    disp = []
    for r in display["countries"]:
        disp.append({
            "iso3": r["iso3"], "short": r["short"], "pop": r["pop_2025_thousands"],
            "ma": r["median_age_2025"], "ma50": r["median_age_2050"],
            "S25": round(r["S_nta_2025"], 4), "S50": round(r["S_nta_2050"], 4),
            "dS": round(r["dS_nta"], 4), "esr25": round(r["esr_nta_2025"], 4),
            "esr50": round(r["esr_nta_2050"], 4),
            "esr_ship_25": r["esr_shipped_2025"], "esr_ship_50": r.get("esr_shipped_2050"),
            "rS25": r["rank_S_nta_2025"], "rS50": r["rank_S_nta_2050"],
            "rE25": r["rank_esr_nta_2025"], "rE50": r["rank_esr_nta_2050"],
            "tfr": r["tfr_2025"], "sr": r["headcount_sr_2025"],
            "share_0_14_25": round(r["share_0_14_2025"], 4),
            "share_45_64_25": round(r["share_45_64_2025"], 4),
            "share_65plus_25": round(r["share_65plus_2025"], 4),
            "share_0_14_50": round(r["share_0_14_2050"], 4),
            "share_45_64_50": round(r["share_45_64_2050"], 4),
            "share_65plus_50": round(r["share_65plus_2050"], 4),
            "shares25": r["shares_2025"], "shares50": r["shares_2050"],
            "color": r.get("color"), "nta_own": r["nta_country_profile"],
        })
    dg = display["diagnostics"]
    payload = {
        "meta": {
            "wpp": "UN World Population Prospects 2024, medium variant",
            "nta": profiles["meta"]["nta_source"],
            "nta_url": profiles["meta"]["nta_source_url"],
            "n_nta": profiles["meta"]["n_country_estimates"],
            "n_all": len(scores["countries"]),
            "world_S_2025": round(pop_w[2025][0], 4),
            "world_S_2050": round(pop_w[2050][0], 4),
            "world_pop_2025_bn": round(pop_w[2025][1], 2),
            "world_pop_2050_bn": round(pop_w[2050][1], 2),
            "peak_age": profiles["meta"]["peak_age_nta_average"],
            "peak_value": round(profiles["meta"]["peak_value_nta_average"], 4),
            "normalization": profiles["meta"]["normalization"],
            "small_multiples": ["NGA", "IND", "MEX", "USA", "KOR", "JPN"],
            "diagnostics": {
                "corr_S_vs_sty": round(dg["corr_S_nta_vs_S_sty_2025"], 3),
                "corr_S_vs_esr": round(dg["corr_S_nta_vs_esr_nta_2025"], 3),
                "corr_S_vs_share4564": round(dg["corr_S_nta_vs_share_45_64_2025"], 3),
                "corr_S_vs_median": round(dg["corr_S_nta_vs_median_age_2025"], 3),
                "corr_S_2025_2050": round(dg["corr_S_nta_2025_vs_2050"], 3),
                "corr_esr_nta_vs_shipped": round(dg["corr_esr_nta_vs_esr_shipped_2025"], 3),
            },
        },
        "ages": profiles["ages"], "yl_avg": profiles["yl_nta_average"],
        "c_avg": profiles["c_nta_average"], "yl_sty": profiles["yl_stylized_normalized"],
        "c_sty": profiles["c_stylized_normalized"], "weights_5yr": profiles["weights_5yr_nta"],
        "age_labels": profiles["age_labels_5yr"], "midpoints": profiles["midpoints_5yr"],
        "examples": profiles["country_examples"], "display": disp, "all": allc,
    }
    js = "/* generated by scripts/compute_scores.py; do not edit by hand */\n"
    js += "window.FINANCE_DATA = " + json.dumps(payload, separators=(",", ":")) + ";\n"
    (OUT / "data.js").write_text(js)
    return pop_w


if __name__ == "__main__":
    main()
