#!/usr/bin/env python3
"""Build the static JSON data files for demographics/ (The Shape of People to Come).

Sources
-------
UN World Population Prospects 2024 (medium variant), via the official
UN-compiled wpp2024 R data package mirrored at github.com/PPgp/wpp2024
(data © 2024 United Nations, DESA, Population Division, CC BY 3.0 IGO).
Downloaded as .rda files into scripts/cache/ and read with pyreadr.

World Bank Indicators API v2 (optional; the script degrades gracefully when
the API is unreachable and leaves economic fields null — re-run later with
--only-wb from a network that can reach api.worldbank.org to backfill).

Hand-authored contextual rubric: demographics/data/context-scores.json is an
*input* (and is shipped verbatim so readers can audit it).

Outputs (all minified, stable key order)
----------------------------------------
demographics/data/countries-summary.json   map + hover + score components
demographics/data/countries/<ISO3>.json    lazy per-country detail
demographics/data/featured-series.json     series for the article's figures

Dependencies: pandas, pyreadr, requests, pycountry  (pip install)

Usage
-----
  python3 scripts/build_demographics_data.py            # full build (mirror)
  python3 scripts/build_demographics_data.py --verify   # build + sanity checks
  python3 scripts/build_demographics_data.py --only-wb  # refresh WB fields only
  python3 scripts/build_demographics_data.py --refresh  # force re-download
"""

import argparse
import json
import math
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / "scripts" / "cache"
OUT = REPO / "demographics" / "data"

MIRROR = "https://raw.githubusercontent.com/PPgp/wpp2024/master/data/"
RDA_FILES = [
    "countries.rda",       # country_code -> name (298 locations incl. aggregates)
    "popAge1dt.rda",       # single-age pop estimates 1949-2023 (popM/popF/pop, thousands)
    "popprojAge1dt.rda",   # single-age pop medium projections 2024-2100
    "tfr1dt.rda", "tfrproj1dt.rda",
    "e01dt.rda", "e0proj1dt.rda",
    "mig1dt.rda", "migproj1dt.rda",
    "mx1dt.rda",           # single-age mortality rates (for e65 life table)
]

REF_YEAR = 2025
GRID = list(range(1950, 2101, 5))            # 31 quinquennial years
BINS = list(range(0, 101, 5))                # 21 bins: 0-4 ... 95-99, 100+
BIN_LABELS = [f"{a}-{a+4}" for a in BINS[:-1]] + ["100+"]
FEATURED = ["CHN", "JPN", "KOR", "DEU", "ITA", "RUS", "USA", "MEX", "IND", "NGA"]

# WPP country_code is the ISO 3166-1 numeric code for real countries.
# Exceptions / non-ISO codes that still deserve an entry:
ISO_NUMERIC_EXCEPTIONS = {412: "XKX"}         # Kosovo (no ISO alpha-3; WB uses XKX)
DROP_CODES = {830}                            # Channel Islands aggregate

COMPONENTS = [
    {"id": "dems",  "label": "Demographic structure"},
    {"id": "demt",  "label": "Demographic trajectory"},
    {"id": "geo",   "label": "Geographic security", "authored": True},
    {"id": "agri",  "label": "Agricultural potential", "authored": True},
    {"id": "ener",  "label": "Energy & resources", "authored": True},
    {"id": "trade", "label": "Neighborhood & trade resilience", "authored": True},
    {"id": "cap",   "label": "Capital access", "authored": True},
]
PRESETS = {
    "zeihan":   {"dems": 0.25, "demt": 0.20, "geo": 0.15, "agri": 0.10,
                 "ener": 0.10, "trade": 0.10, "cap": 0.10},
    "puredemo": {"dems": 0.50, "demt": 0.50, "geo": 0.0, "agri": 0.0,
                 "ener": 0.0, "trade": 0.0, "cap": 0.0},
    "resource": {"dems": 0.10, "demt": 0.10, "geo": 0.15, "agri": 0.25,
                 "ener": 0.25, "trade": 0.05, "cap": 0.10},
}

WB_INDICATORS = {
    "gdppc": "NY.GDP.PCAP.CD",
    "ca":    "BN.CAB.XOKA.GD.ZS",
    "gcf":   "NE.GDI.TOTL.ZS",
    "sav":   "NY.GNS.ICTR.ZS",
    "urb":   "SP.URB.TOTL.IN.ZS",
    "trade": "NE.TRD.GNFS.ZS",
    "arable": "AG.LND.ARBL.HA.PC",
    "fuelx": "TX.VAL.FUEL.ZS.UN",
    "eimp":  "EG.IMP.CONS.ZS",
}
WB_SERIES_KEYS = ["gdppc", "ca", "gcf", "sav", "urb", "trade"]  # shipped as series


# ---------------------------------------------------------------- utilities

def siground(x, sig=4):
    """Round to `sig` significant digits; return None for NaN."""
    if x is None:
        return None
    x = float(x)
    if math.isnan(x):
        return None
    if x == 0:
        return 0
    r = round(x, sig - 1 - int(math.floor(math.log10(abs(x)))))
    return int(r) if float(r).is_integer() and abs(r) >= 1 else r


def dump_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    txt = json.dumps(obj, separators=(",", ":"), sort_keys=True, allow_nan=False)
    path.write_text(txt)
    return len(txt)


def download_rda(refresh=False):
    CACHE.mkdir(parents=True, exist_ok=True)
    for name in RDA_FILES:
        dest = CACHE / name
        if dest.exists() and not refresh:
            continue
        url = MIRROR + name
        print(f"  downloading {name} ...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
            f.write(r.read())


def read_rda(name):
    import pyreadr
    res = pyreadr.read_r(str(CACHE / name))
    df = list(res.values())[0]
    return df


def iso3_map(codes):
    """Map WPP numeric country_code -> ISO alpha-3. Aggregates return None."""
    import pycountry
    out = {}
    for code in codes:
        code = int(code)
        if code in DROP_CODES or code >= 900:
            continue
        if code in ISO_NUMERIC_EXCEPTIONS:
            out[code] = ISO_NUMERIC_EXCEPTIONS[code]
            continue
        c = pycountry.countries.get(numeric=f"{code:03d}")
        if c is not None:
            out[code] = c.alpha_3
    return out


# ------------------------------------------------------- demographic maths

def median_age(single_age_pop):
    """Exact median from a single-age population vector (index = age 0..100)."""
    total = single_age_pop.sum()
    if total <= 0:
        return None
    half, cum = total / 2.0, 0.0
    for age, n in enumerate(single_age_pop):
        if cum + n >= half:
            return age + (half - cum) / n if n > 0 else float(age)
        cum += n
    return 100.0


def e_at_age(mx, start_age=65):
    """Remaining life expectancy at start_age from single-age mortality rates
    (index age 0..100; closed with the open-ended 100+ rate)."""
    lx = 1.0
    l_list = []  # survivors at each age from start_age
    # survive to start_age
    for a in range(0, start_age):
        lx *= math.exp(-mx[a])
    l_start = lx
    if l_start <= 0:
        return 0.0
    person_years = 0.0
    for a in range(start_age, 100):
        l_next = lx * math.exp(-mx[a])
        person_years += (lx + l_next) / 2.0
        lx = l_next
    if mx[100] > 0:
        person_years += lx / mx[100]  # open interval closure
    return person_years / l_start


def pyramid_matrix(df_years):
    """df_years: single-age frame for one country with columns year, age, popM, popF.
    Returns (m, f): lists [year][bin] binned 5-yearly, sig-rounded (thousands)."""
    m_rows, f_rows = [], []
    for y in GRID:
        sub = df_years[df_years.year == y]
        if sub.empty:
            m_rows.append(None)
            f_rows.append(None)
            continue
        mvals = sub.sort_values("age").popM.to_numpy()
        fvals = sub.sort_values("age").popF.to_numpy()
        mbin = [siground(mvals[a:min(a + 5, 101)].sum()) for a in BINS[:-1]] + [siground(mvals[100:].sum())]
        fbin = [siground(fvals[a:min(a + 5, 101)].sum()) for a in BINS[:-1]] + [siground(fvals[100:].sum())]
        m_rows.append(mbin)
        f_rows.append(fbin)
    return m_rows, f_rows


def age_slice_sum(vec, lo, hi):
    """Sum of single-age vector for lo <= age <= hi (inclusive)."""
    return float(vec[lo:hi + 1].sum())


# -------------------------------------------------------------- World Bank

def fetch_worldbank():
    """Return {iso3: {key: {year:int -> value}}} or None if unreachable."""
    import requests
    data = {}
    try:
        for key, code in WB_INDICATORS.items():
            url = (f"https://api.worldbank.org/v2/country/all/indicator/{code}"
                   f"?format=json&per_page=20000&date=1990:{REF_YEAR}")
            page = 1
            while True:
                r = requests.get(f"{url}&page={page}", timeout=60)
                r.raise_for_status()
                meta, rows = r.json()
                for row in rows or []:
                    iso3 = row.get("countryiso3code") or ""
                    if len(iso3) != 3 or row["value"] is None:
                        continue
                    data.setdefault(iso3, {}).setdefault(key, {})[int(row["date"])] = row["value"]
                if page >= int(meta.get("pages", 1)):
                    break
                page += 1
            print(f"  WB {code}: ok")
    except Exception as exc:  # graceful skip — sandbox blocks this host
        print(f"  !! World Bank API unreachable ({exc}); economic fields will be null.")
        return None
    return data


def wb_latest(wb_c, key, since=2015):
    """Latest value since `since` for one country dict, else None."""
    if not wb_c or key not in wb_c:
        return None
    years = [y for y in wb_c[key] if y >= since]
    return wb_c[key][max(years)] if years else None


# ------------------------------------------------------------------- build

def build(args):
    print("== downloading/caching WPP mirror files")
    download_rda(refresh=args.refresh)

    print("== loading tables")
    countries = read_rda("countries.rda")
    code2name = dict(zip(countries.country_code.astype(int), countries.name))
    code2iso = iso3_map(code2name.keys())
    iso2code = {v: k for k, v in code2iso.items()}
    print(f"  {len(code2iso)} countries mapped to ISO3 "
          f"(dropped {len(code2name) - len(code2iso)} aggregates/unmapped)")

    est = read_rda("popAge1dt.rda")
    proj = read_rda("popprojAge1dt.rda")
    est = est[est.country_code.isin(code2iso)][["country_code", "year", "age", "popM", "popF"]]
    proj = proj[proj.country_code.isin(code2iso)][["country_code", "year", "age", "popM", "popF"]]
    est = est[est.year >= 1950]
    pop = pd.concat([est, proj], ignore_index=True)
    # pyreadr returns differing dtypes across files; normalize the keys
    for col in ("country_code", "year", "age"):
        pop[col] = pop[col].astype(int)

    def load_series(est_name, proj_name, col):
        a = read_rda(est_name)[["country_code", "year", col]]
        b = read_rda(proj_name)[["country_code", "year", col]]
        df = pd.concat([a, b], ignore_index=True)
        df = df[df.country_code.isin(code2iso)]
        return {(int(r.country_code), int(r.year)): float(getattr(r, col))
                for r in df.itertuples()}

    tfr = load_series("tfr1dt.rda", "tfrproj1dt.rda", "tfr")
    e0 = load_series("e01dt.rda", "e0proj1dt.rda", "e0B")
    mig = load_series("mig1dt.rda", "migproj1dt.rda", "mig")

    print("== life table e65 from mx (latest estimate year)")
    mx = read_rda("mx1dt.rda")
    mx = mx[mx.country_code.isin(code2iso)]
    mx["year"] = mx.year.astype(int)
    # mx1dt spans 1950-2100 (estimates + medium projection); use the reference year
    mx_year = REF_YEAR if (mx.year == REF_YEAR).any() else int(mx.year.max())
    mx = mx[mx.year == mx_year][["country_code", "age", "mxB"]]
    e65 = {}
    for code, sub in mx.groupby("country_code"):
        vec = sub.sort_values("age").mxB.to_numpy()
        if len(vec) == 101:
            e65[int(code)] = e_at_age(vec, 65)
    print(f"  e65 computed for {len(e65)} countries (mx year {mx_year})")

    # hand-authored rubric
    ctx_path = OUT / "context-scores.json"
    ctx = json.loads(ctx_path.read_text()) if ctx_path.exists() else {"DEFAULTS": {}}
    defaults = ctx.get("DEFAULTS", {})

    print("== optional World Bank fetch")
    wb = None if args.skip_wb else fetch_worldbank()

    print("== computing per-country metrics")
    summary = {}
    detail = {}
    raw_metrics = {}   # iso3 -> dict of raw metric values (for z-scoring)

    for code, iso3 in sorted(code2iso.items(), key=lambda kv: kv[1]):
        sub = pop[pop.country_code == code]
        if sub.empty:
            continue
        name = code2name[code]

        def yearvec(y):
            s = sub[sub.year == y].sort_values("age")
            return s.popM.to_numpy() + s.popF.to_numpy() if len(s) == 101 else None

        v25, v40, v50 = yearvec(REF_YEAR), yearvec(2040), yearvec(2050)
        if v25 is None:
            continue

        pop25 = v25.sum()
        sr = age_slice_sum(v25, 20, 64) / max(age_slice_sum(v25, 65, 100), 1e-9)
        ma25 = median_age(v25)
        ma50 = median_age(v50) if v50 is not None else None
        wrr = age_slice_sum(v25, 20, 24) / max(age_slice_sum(v25, 60, 64), 1e-9)
        mom = (v50.sum() / pop25) if v50 is not None else None
        cs25 = age_slice_sum(v25, 35, 64) / max(age_slice_sum(v25, 65, 100), 1e-9)
        cs40 = (age_slice_sum(v40, 35, 64) / max(age_slice_sum(v40, 65, 100), 1e-9)
                if v40 is not None else None)
        cshift = (cs40 - cs25) if cs40 is not None else None

        # prospective OADR: threshold T where remaining LE ~ 15y
        poadr = None
        if code in e65:
            T = 65 + max(0.0, e65[code] - 15.0)
            T = min(T, 99.0)
            fl = int(math.floor(T))
            frac = 1.0 - (T - fl)                     # fraction of age-fl bucket above T
            old = frac * v25[fl] + age_slice_sum(v25, fl + 1, 100)
            workers = age_slice_sum(v25, 20, fl) - frac * v25[fl]
            poadr = old / max(workers, 1e-9)

        tfr25 = tfr.get((code, REF_YEAR))
        tfr10 = tfr.get((code, 2010))
        tfr_slope = ((tfr25 - tfr10) / 15.0) if (tfr25 is not None and tfr10 is not None) else None

        raw_metrics[iso3] = {"sr": sr, "ma": ma25, "poadr": poadr, "wrr": wrr,
                             "mom": mom, "tfr": tfr25, "cshift": cshift}

        wb_c = wb.get(iso3) if wb else None
        summary[iso3] = {
            "n": name,
            "pop": siground(pop25),
            "ma": siground(ma25, 3), "ma50": siground(ma50, 3),
            "tfr": siground(tfr25, 3), "sr": siground(sr, 3),
            "poadr": siground(poadr, 3), "wrr": siground(wrr, 3),
            "mom": siground(mom, 3), "cshift": siground(cshift, 3),
            "tfrsl": siground(tfr_slope, 2),
            "gdppc": siground(wb_latest(wb_c, "gdppc"), 3),
            "ca": siground(wb_latest(wb_c, "ca"), 3),
            "urb": siground(wb_latest(wb_c, "urb"), 3),
        }

        # ---- detail file
        m_rows, f_rows = pyramid_matrix(sub)
        series = {"years": GRID}
        for key, lookup in (("tfr", tfr), ("le", e0), ("nmig", mig)):
            series[key] = [siground(lookup.get((code, y)), 3) for y in GRID]
        sr_series, ma_series, pop_series = [], [], []
        for y in GRID:
            v = yearvec(y)
            if v is None:
                sr_series.append(None); ma_series.append(None); pop_series.append(None)
            else:
                sr_series.append(siground(age_slice_sum(v, 20, 64) /
                                          max(age_slice_sum(v, 65, 100), 1e-9), 3))
                ma_series.append(siground(median_age(v), 3))
                pop_series.append(siground(v.sum()))
        series.update({"sr": sr_series, "ma": ma_series, "pop": pop_series})

        wb_detail = None
        if wb_c:
            wb_years = list(range(1990, REF_YEAR + 1))
            wb_detail = {"years": wb_years}
            for k in WB_SERIES_KEYS:
                wb_detail[k] = [siground(wb_c.get(k, {}).get(y), 3) for y in wb_years]

        notes = (ctx.get(iso3) or {}).get("notes")
        detail[iso3] = {
            "iso3": iso3, "name": name, "locid": code,
            "pyramid": {"ages": BIN_LABELS, "years": GRID, "m": m_rows, "f": f_rows},
            "series": series,
            **({"wb": wb_detail} if wb_detail else {}),
            **({"context_notes": notes} if notes else {}),
        }

    print(f"  computed {len(summary)} countries")

    # ---------------- z-scores
    print("== z-scoring")

    def zscores(key, sign):
        vals = {k: v[key] for k, v in raw_metrics.items() if v[key] is not None}
        s = pd.Series(vals)
        lo, hi = s.quantile(0.05), s.quantile(0.95)
        w = s.clip(lo, hi)
        mu, sd = w.mean(), w.std()
        if sd == 0 or math.isnan(sd):
            return {}
        return {k: max(-3.0, min(3.0, sign * (val - mu) / sd)) for k, val in w.items()}

    z_parts = {
        "sr": zscores("sr", +1), "ma": zscores("ma", -1), "poadr": zscores("poadr", -1),
        "wrr": zscores("wrr", +1), "mom": zscores("mom", +1),
        "tfr": zscores("tfr", +1), "cshift": zscores("cshift", +1),
    }

    def mean_available(iso3, keys):
        vals = [z_parts[k][iso3] for k in keys if iso3 in z_parts[k]]
        return sum(vals) / len(vals) if vals else None

    # WB-derived contextual defaults (percentile -> score units), if WB available
    def wb_percentile_z(metric_by_iso):
        if not metric_by_iso:
            return {}
        s = pd.Series(metric_by_iso).rank(pct=True)
        return {k: (p - 0.5) * 5.0 for k, p in s.items()}   # -2.5 .. +2.5

    agri_derived, ener_derived, cap_derived = {}, {}, {}
    if wb:
        agri_derived = wb_percentile_z({k: wb_latest(v, "arable") for k, v in wb.items()
                                        if wb_latest(v, "arable") is not None})
        # energy security: fuel exports good, energy import dependence bad
        fx = {k: wb_latest(v, "fuelx") for k, v in wb.items() if wb_latest(v, "fuelx") is not None}
        ei = {k: wb_latest(v, "eimp") for k, v in wb.items() if wb_latest(v, "eimp") is not None}
        fxz, eiz = wb_percentile_z(fx), wb_percentile_z(ei)
        for k in set(fxz) | set(eiz):
            parts = [fxz.get(k, 0.0), -eiz.get(k, 0.0)]
            ener_derived[k] = sum(parts) / 2.0
        cap_derived = wb_percentile_z({k: wb_latest(v, "gdppc") for k, v in wb.items()
                                       if wb_latest(v, "gdppc") is not None})

    def ctx_z(iso3, comp, derived_map):
        entry = ctx.get(iso3) or {}
        score = entry.get(comp, defaults.get(comp))
        if score is not None:
            return (float(score) - 5.0) / 2.0          # rubric 0-10 -> -2.5..+2.5
        if iso3 in derived_map:
            return derived_map[iso3]
        return None

    for iso3 in summary:
        z = {
            "dems": mean_available(iso3, ["sr", "ma", "poadr"]),
            "demt": mean_available(iso3, ["wrr", "mom", "tfr", "cshift"]),
            "geo": ctx_z(iso3, "geo", {}),
            "agri": ctx_z(iso3, "agri", agri_derived),
            "ener": ctx_z(iso3, "ener", ener_derived),
            "trade": ctx_z(iso3, "trade", {}),
            "cap": ctx_z(iso3, "cap", cap_derived),
        }
        summary[iso3]["z"] = {k: siground(v, 3) for k, v in z.items()}
        authored = ctx.get(iso3) or {}
        summary[iso3]["ctxa"] = sorted(k for k in ("geo", "agri", "ener", "trade", "cap")
                                       if authored.get(k) is not None)

    # ---------------- write outputs
    print("== writing outputs")
    meta = {
        "generated": args.stamp,
        "wpp": "2024 (medium variant; PPgp/wpp2024 mirror; CC BY 3.0 IGO)",
        "wb": "World Bank Indicators API v2" if wb else None,
        "refYear": REF_YEAR, "mxYear": mx_year,
        "components": COMPONENTS, "presets": PRESETS,
        "featured": FEATURED,
    }
    n = dump_json(OUT / "countries-summary.json", {"meta": meta, "countries": summary})
    print(f"  countries-summary.json  {n/1024:.0f} KB  ({len(summary)} countries)")

    total = 0
    for iso3, d in detail.items():
        total += dump_json(OUT / "countries" / f"{iso3}.json", d)
    print(f"  countries/*.json        {total/1024/1024:.1f} MB  ({len(detail)} files)")

    feat = {"years": GRID, "countries": {}}
    for iso3 in FEATURED:
        if iso3 in detail:
            s = detail[iso3]["series"]
            feat["countries"][iso3] = {"n": summary[iso3]["n"], "tfr": s["tfr"],
                                       "sr": s["sr"], "urb": None}
            if "wb" in detail[iso3]:
                feat["countries"][iso3]["urb"] = detail[iso3]["wb"].get("urb")
    n = dump_json(OUT / "featured-series.json", feat)
    print(f"  featured-series.json    {n/1024:.1f} KB")

    return summary, detail


def verify(summary, detail):
    print("== verify")
    errs = []
    world_pop = sum(c["pop"] for c in summary.values() if c["pop"])
    if not 7.8e6 < world_pop < 8.7e6:
        errs.append(f"sum of country pops {world_pop:.0f} k not ~8.2e6 k")
    jp = summary.get("JPN", {})
    if not (jp.get("ma") and 48 <= jp["ma"] <= 51):
        errs.append(f"Japan median age {jp.get('ma')} outside [48,51]")
    ng = summary.get("NGA", {})
    if not (ng.get("ma") and ng["ma"] < 22):
        errs.append(f"Nigeria median age {ng.get('ma')} not < 22")
    for iso3 in FEATURED:
        if iso3 not in summary:
            errs.append(f"featured {iso3} missing from summary")
    for iso3, d in detail.items():
        size = (OUT / "countries" / f"{iso3}.json").stat().st_size
        if size > 25 * 1024:
            errs.append(f"{iso3}.json is {size/1024:.0f} KB (> 25 KB)")
    for iso3, c in summary.items():
        for k, v in c["z"].items():
            if v is not None and not -3.001 <= v <= 3.001:
                errs.append(f"{iso3} z.{k} = {v} out of range")
    if errs:
        print("  FAILED:\n   - " + "\n   - ".join(errs))
        sys.exit(1)
    print(f"  OK — {len(summary)} countries, world pop {world_pop/1e6:.2f} bn, "
          f"JPN ma {jp['ma']}, NGA ma {ng['ma']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="force re-download of cache")
    ap.add_argument("--skip-wb", action="store_true", help="skip the World Bank fetch")
    ap.add_argument("--only-wb", action="store_true",
                    help="(re)fetch WB and rebuild outputs (uses cached WPP files)")
    ap.add_argument("--verify", action="store_true", help="run sanity assertions")
    ap.add_argument("--stamp", default=None,
                    help="generation date stamp (YYYY-MM-DD); defaults to today")
    args = ap.parse_args()
    if args.stamp is None:
        from datetime import date
        args.stamp = date.today().isoformat()
    summary, detail = build(args)
    if args.verify:
        verify(summary, detail)


if __name__ == "__main__":
    main()
