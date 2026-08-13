#!/usr/bin/env python3
"""Demonstrate (or refute) the Bitcoin power law: price ~ A * (days_since_genesis)^n.

Methodology (grounded in the research briefing):
  - t = days since the Bitcoin genesis block (2009-01-03).
  - Fit log10(price) = a + n*log10(t) by OLS in log-log space.
  - Report n with Newey-West (HAC) standard error, R^2, residual sigma.
  - Build the "power-law corridor" from EMPIRICAL residual quantiles (not Gaussian).
  - Validation: expanding-window exponent stability + residual AR(1) half-life.

Data:
  - 2016-2026: real Coinbase BTC-USD daily closes (resampled from cached hourly).
  - 2010-2015: well-documented year-end / first-trade reference prices (external,
    clearly labelled) so the demonstration spans Bitcoin's full ~6-orders-of-magnitude
    history, which is where the power law is most striking.

Outputs:
  - runs/power_law/power_law.json   (everything the dashboard needs)
  - runs/power_law/power_law.png    (static matplotlib verification figure)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

GENESIS = datetime(2009, 1, 3, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "runs/power_law"

# ---------------------------------------------------------------------------
# Early reference prices (2010-2015), pre-Coinbase. Year-end + first-trade points
# are very well documented across Wikipedia's BTC price timeline, historical
# exchange charts (Mt. Gox / Bitstamp), and CoinMetrics community data. These are
# used ONLY to extend the visual demonstration into Bitcoin's earliest era; the
# rigorous Coinbase-era fit is reported separately so provenance is transparent.
# ---------------------------------------------------------------------------
EARLY_ANCHORS = [
    ("2010-07-18", 0.09, "First Mt. Gox market trades (~$0.05-0.09)"),
    ("2010-10-01", 0.10, "Oct 2010"),
    ("2010-12-31", 0.30, "Year-end 2010"),
    ("2011-06-08", 31.0, "June 2011 bubble peak"),
    ("2011-12-31", 4.25, "Year-end 2011 (post-crash)"),
    ("2012-12-31", 13.45, "Year-end 2012"),
    ("2013-04-10", 230.0, "April 2013 peak"),
    ("2013-12-04", 1150.0, "Nov/Dec 2013 peak"),
    ("2014-12-31", 318.0, "Year-end 2014 (bear)"),
    ("2015-08-24", 210.0, "Aug 2015 low"),
    ("2015-12-31", 430.0, "Year-end 2015"),
]


def load_coinbase_daily() -> pd.DataFrame:
    df = pd.read_parquet(ROOT / ".cache/candles/BTC-USD_ONE_HOUR.parquet")
    df["ts"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df["close"] = df["close"].astype(float)
    df = df.set_index("ts").sort_index()
    daily = df["close"].resample("1D").last().dropna()
    out = pd.DataFrame({"date": daily.index, "price": daily.values})
    out["source"] = "coinbase"
    return out


def build_anchor_frame() -> pd.DataFrame:
    rows = [
        {"date": pd.Timestamp(d, tz="UTC"), "price": p, "source": "reference", "note": note}
        for d, p, note in EARLY_ANCHORS
    ]
    return pd.DataFrame(rows)


def days_since_genesis(dates: pd.DatetimeIndex | pd.Series) -> np.ndarray:
    delta = pd.to_datetime(dates, utc=True) - pd.Timestamp(GENESIS)
    return delta.dt.total_seconds().to_numpy() / 86400.0


def ols_loglog(days: np.ndarray, price: np.ndarray):
    """Fit log10(price) = a + n*log10(days). Returns (a, n, yhat_log, resid, r2)."""
    x = np.log10(days)
    y = np.log10(price)
    X = np.vstack([np.ones_like(x), x]).T
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    a, n = float(beta[0]), float(beta[1])
    yhat = X @ beta
    resid = y - yhat
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot
    return a, n, yhat, resid, r2, X


def newey_west_se(X: np.ndarray, resid: np.ndarray, lags: int) -> np.ndarray:
    """HAC (Newey-West) standard errors for OLS coefficients. Returns SE vector."""
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    u = resid.reshape(-1, 1)
    # S = sum of weighted autocovariances of the score X_t * u_t
    Xu = X * u  # n x k
    S = Xu.T @ Xu  # lag 0
    for L in range(1, lags + 1):
        w = 1.0 - L / (lags + 1.0)  # Bartlett kernel
        G = Xu[L:].T @ Xu[:-L]
        S += w * (G + G.T)
    cov = XtX_inv @ S @ XtX_inv
    return np.sqrt(np.diag(cov))


def expanding_exponent(days: np.ndarray, price: np.ndarray, step: int = 90):
    """Re-fit n on expanding windows to check stability over time."""
    order = np.argsort(days)
    d = days[order]
    p = price[order]
    out = []
    start_min = 200  # need enough points
    for end in range(start_min, len(d), step):
        a, n, *_ = ols_loglog(d[:end], p[:end])
        out.append({"as_of_day": float(d[end - 1]), "n": n})
    return out


def ar1_half_life(resid_series: np.ndarray) -> float:
    """Half-life of mean reversion implied by an AR(1) fit on residuals (in samples)."""
    r = resid_series
    r0, r1 = r[:-1], r[1:]
    # rho = cov / var
    rho = float(np.corrcoef(r0, r1)[0, 1])
    if rho <= 0 or rho >= 1:
        return float("nan")
    return float(-np.log(2) / np.log(rho))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cb = load_coinbase_daily()
    anchors = build_anchor_frame()

    # ---- Primary rigorous fit: Coinbase daily only (real, dense, self-consistent) ----
    cb_days = days_since_genesis(cb["date"])
    cb_price = cb["price"].to_numpy()
    a_cb, n_cb, yhat_cb, resid_cb, r2_cb, X_cb = ols_loglog(cb_days, cb_price)
    # HAC lags ~ 4*(n/100)^(2/9) rule, but residuals here are highly persistent;
    # use a generous lag of ~ floor(len^(1/4))*... -> use 365 (one year) for daily.
    nw_lags = min(365, len(resid_cb) // 4)
    se_cb = newey_west_se(X_cb, resid_cb, nw_lags)

    # ---- Full-history fit: anchors + monthly-resampled Coinbase ----
    # Monthly resample of Coinbase so the dense recent era doesn't swamp the early
    # points; gives each era more comparable leverage (closer to literature method).
    cb_m = cb.set_index("date")["price"].resample("1MS").last().dropna()
    cb_m_df = pd.DataFrame({"date": cb_m.index, "price": cb_m.values, "source": "coinbase"})
    full = pd.concat([anchors[["date", "price", "source"]], cb_m_df], ignore_index=True)
    full = full.sort_values("date").reset_index(drop=True)
    full_days = days_since_genesis(full["date"])
    full_price = full["price"].to_numpy()
    a_full, n_full, yhat_full, resid_full, r2_full, X_full = ols_loglog(full_days, full_price)
    se_full = newey_west_se(X_full, resid_full, min(24, len(resid_full) // 4))

    # ---- Corridor from residual quantiles (use full-history residuals) ----
    quantiles = {
        "q05": float(np.quantile(resid_full, 0.05)),
        "q25": float(np.quantile(resid_full, 0.25)),
        "q50": float(np.quantile(resid_full, 0.50)),
        "q75": float(np.quantile(resid_full, 0.75)),
        "q95": float(np.quantile(resid_full, 0.95)),
    }

    # ---- Validation: expanding exponent + residual AR(1) half-life ----
    exp_stab = expanding_exponent(cb_days, cb_price, step=120)
    half_life_days = ar1_half_life(resid_cb)
    resid_autocorr1 = float(np.corrcoef(resid_cb[:-1], resid_cb[1:])[0, 1])

    # ---- Current standing ----
    cur_day = float(cb_days[-1])
    cur_price = float(cb_price[-1])
    cur_model_full = 10 ** (a_full + n_full * np.log10(cur_day))
    cur_resid = float(np.log10(cur_price) - (a_full + n_full * np.log10(cur_day)))
    cur_percentile = float((resid_full < cur_resid).mean() * 100.0)

    # ---- Model line for plotting (smooth, over full span incl. projection) ----
    line_days = np.logspace(np.log10(cb_days.min() if len(EARLY_ANCHORS) == 0 else 500),
                            np.log10(cur_day * 3.0), 400)
    line_days = np.unique(np.concatenate([
        np.logspace(np.log10(500), np.log10(cur_day), 300),
        np.logspace(np.log10(cur_day), np.log10(cur_day * 3.2), 100),
    ]))
    line_model = 10 ** (a_full + n_full * np.log10(line_days))

    def line_for_offset(offset: float) -> list[float]:
        return [float(v) for v in 10 ** (a_full + n_full * np.log10(line_days) + offset)]

    # ---- Projections at notable future dates (extrapolation; labelled as such) ----
    proj = []
    for year in [2026, 2028, 2030, 2032, 2035, 2040]:
        d = (datetime(year, 1, 1, tzinfo=timezone.utc) - GENESIS).days
        if d <= cur_day:
            continue
        price_mid = 10 ** (a_full + n_full * np.log10(d))
        proj.append({
            "year": year,
            "days": d,
            "model_price": float(price_mid),
            "low_q05": float(price_mid * 10 ** quantiles["q05"]),
            "high_q95": float(price_mid * 10 ** quantiles["q95"]),
        })

    # ---- Downsample series for the dashboard (weekly) ----
    cb_weekly = cb.set_index("date")["price"].resample("1W").last().dropna()
    series = [
        {"date": d.strftime("%Y-%m-%d"), "days": float((d - pd.Timestamp(GENESIS)).total_seconds() / 86400.0),
         "price": float(p), "source": "coinbase"}
        for d, p in cb_weekly.items()
    ]
    anchor_series = [
        {"date": r["date"].strftime("%Y-%m-%d"),
         "days": float((r["date"] - pd.Timestamp(GENESIS)).total_seconds() / 86400.0),
         "price": float(r["price"]), "source": "reference", "note": r["note"]}
        for _, r in anchors.iterrows()
    ]

    # residual oscillator series (full history, for the "where in the corridor" panel)
    osc = []
    for d, pr in zip(full_days, full_price):
        rr = float(np.log10(pr) - (a_full + n_full * np.log10(d)))
        dt = GENESIS + pd.to_timedelta(d, unit="D")
        osc.append({"date": dt.strftime("%Y-%m-%d"), "residual": rr})

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "genesis": GENESIS.strftime("%Y-%m-%d"),
        "fit_coinbase": {
            "label": "Coinbase daily 2016-2026 (real exchange data)",
            "n": n_cb, "n_se": float(se_cb[1]), "a": a_cb, "r2": r2_cb,
            "resid_sigma": float(np.std(resid_cb)),
            "n_points": int(len(cb_days)),
            "newey_west_lags": int(nw_lags),
        },
        "fit_full": {
            "label": "Full history 2010-2026 (early reference points + Coinbase, monthly)",
            "n": n_full, "n_se": float(se_full[1]), "a": a_full, "r2": r2_full,
            "resid_sigma": float(np.std(resid_full)),
            "n_points": int(len(full_days)),
            "A": float(10 ** a_full),
        },
        "corridor_quantiles": quantiles,
        "current": {
            "date": cb["date"].iloc[-1].strftime("%Y-%m-%d"),
            "day": cur_day,
            "price": cur_price,
            "model_price": float(cur_model_full),
            "residual": cur_resid,
            "ratio_to_model": float(cur_price / cur_model_full),
            "corridor_percentile": cur_percentile,
        },
        "validation": {
            "expanding_exponent": exp_stab,
            "resid_autocorr_lag1": resid_autocorr1,
            "ar1_half_life_days": half_life_days,
        },
        "model_line": {
            "days": [float(d) for d in line_days],
            "dates": [(GENESIS + pd.to_timedelta(float(d), unit="D")).strftime("%Y-%m-%d") for d in line_days],
            "mid": [float(v) for v in line_model],
            "q05": line_for_offset(quantiles["q05"]),
            "q25": line_for_offset(quantiles["q25"]),
            "q75": line_for_offset(quantiles["q75"]),
            "q95": line_for_offset(quantiles["q95"]),
        },
        "projections": proj,
        "series": series,
        "anchors": anchor_series,
        "oscillator": osc,
    }

    (OUT_DIR / "power_law.json").write_text(json.dumps(payload, indent=2))

    # ---- Static verification figure ----
    _static_figure(payload)

    # ---- Console summary ----
    print("=" * 70)
    print("BITCOIN POWER LAW — fit summary")
    print("=" * 70)
    print(f"Genesis t0: {GENESIS.date()}")
    print(f"\n[Coinbase daily 2016-2026]  ({len(cb_days)} days)")
    print(f"  price = 10^{a_cb:.3f} * t^{n_cb:.3f}")
    print(f"  exponent n = {n_cb:.3f}  (Newey-West SE {se_cb[1]:.3f}, {nw_lags} lags)")
    print(f"  R^2 (log-log) = {r2_cb:.4f}   residual sigma = {np.std(resid_cb):.3f} dex")
    print(f"\n[Full history 2010-2026]  ({len(full_days)} pts; early refs + monthly Coinbase)")
    print(f"  price = 10^{a_full:.3f} * t^{n_full:.3f}")
    print(f"  exponent n = {n_full:.3f}  (SE {se_full[1]:.3f})")
    print(f"  R^2 (log-log) = {r2_full:.4f}   residual sigma = {np.std(resid_full):.3f} dex")
    print(f"\n[Current standing]  {payload['current']['date']}")
    print(f"  price ${cur_price:,.0f}  vs model ${cur_model_full:,.0f}  "
          f"({payload['current']['ratio_to_model']:.2f}x)")
    print(f"  corridor percentile: {cur_percentile:.0f}%  "
          f"(0=floor, 100=ceiling)")
    print(f"\n[Validation]")
    ns = [e['n'] for e in exp_stab]
    print(f"  expanding exponent range: {min(ns):.2f} - {max(ns):.2f} "
          f"(last {ns[-1]:.2f})")
    print(f"  residual lag-1 autocorr: {resid_autocorr1:.3f}  "
          f"AR(1) half-life: {half_life_days:.0f} days")
    print(f"\nArtifacts: {OUT_DIR}/power_law.json , {OUT_DIR}/power_law.png")


def _static_figure(p: dict) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    ml = p["model_line"]
    ax.fill_between(ml["days"], ml["q05"], ml["q95"], color="#f7931a", alpha=0.10, label="5-95% corridor")
    ax.fill_between(ml["days"], ml["q25"], ml["q75"], color="#f7931a", alpha=0.18, label="25-75% corridor")
    ax.plot(ml["days"], ml["mid"], color="#f7931a", lw=2, label=f"power-law fit (n={p['fit_full']['n']:.2f})")
    s_days = [x["days"] for x in p["series"]]
    s_price = [x["price"] for x in p["series"]]
    ax.plot(s_days, s_price, color="#1f6feb", lw=0.9, alpha=0.85, label="BTC (Coinbase)")
    a_days = [x["days"] for x in p["anchors"]]
    a_price = [x["price"] for x in p["anchors"]]
    ax.scatter(a_days, a_price, color="#2ea043", s=28, zorder=5, label="early reference (2010-15)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("days since genesis block (2009-01-03)")
    ax.set_ylabel("BTC price (USD)")
    ax.set_title(f"Bitcoin Power Law  —  R²={p['fit_full']['r2']:.3f}, n={p['fit_full']['n']:.2f}")
    ax.grid(True, which="both", alpha=0.15)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "power_law.png", dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
