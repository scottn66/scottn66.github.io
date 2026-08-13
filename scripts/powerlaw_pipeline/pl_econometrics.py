#!/usr/bin/env python3
"""Multi-lens econometric scrutiny of the Bitcoin power law.

Each "lens" stress-tests the claim `price = A * (days_since_genesis)^n` from a
different economic / statistical angle. Outputs runs/power_law/econ.json for the
interactive portfolio page.

Lenses:
  1. Fit + HAC inference            (OLS log-log, Newey-West SE)
  2. Spurious-regression / cointegration (ADF, KPSS, Engle-Granger, DW, Ljung-Box)
  3. Model comparison               (power / exponential / stretched-exp / logistic — AIC/BIC)
  4. Mean reversion (OU process)    (half-life, z-score oscillator)
  5. Bubbles (LPPLS / Sornette)     (log-periodic power-law singularity on a cycle)
  6. Structural stability           (rolling exponent, Chow test at halvings)
  7. Risk & deceleration            (cycle ROI decay, drawdowns)
"""
from __future__ import annotations

import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats
from statsmodels.regression.linear_model import OLS
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tools.tools import add_constant
from statsmodels.tsa.stattools import adfuller, coint, kpss

warnings.filterwarnings("ignore")

GENESIS = pd.Timestamp("2009-01-03", tz="UTC")
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/power_law"
HALVINGS = ["2012-11-28", "2016-07-09", "2020-05-11", "2024-04-20"]

EARLY_ANCHORS = [
    ("2010-07-18", 0.09), ("2010-10-01", 0.10), ("2010-12-31", 0.30),
    ("2011-06-08", 31.0), ("2011-12-31", 4.25), ("2012-12-31", 13.45),
    ("2013-04-10", 230.0), ("2013-12-04", 1150.0), ("2014-12-31", 318.0),
    ("2015-08-24", 210.0), ("2015-12-31", 430.0),
]


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def load_daily() -> pd.DataFrame:
    df = pd.read_parquet(ROOT / ".cache/candles/BTC-USD_ONE_HOUR.parquet")
    df["ts"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df["close"] = df["close"].astype(float)
    daily = df.set_index("ts").sort_index()["close"].resample("1D").last().dropna()
    out = pd.DataFrame({"date": daily.index, "price": daily.values})
    out["t"] = (out["date"] - GENESIS).dt.total_seconds() / 86400.0
    return out.reset_index(drop=True)


def full_series() -> pd.DataFrame:
    cb = load_daily()
    cb_m = cb.set_index("date")["price"].resample("1MS").last().dropna()
    anchors = pd.DataFrame(
        {"date": pd.to_datetime([d for d, _ in EARLY_ANCHORS], utc=True),
         "price": [p for _, p in EARLY_ANCHORS]}
    )
    fm = pd.DataFrame({"date": cb_m.index, "price": cb_m.values})
    full = pd.concat([anchors, fm], ignore_index=True).sort_values("date")
    full["t"] = (full["date"] - GENESIS).dt.total_seconds() / 86400.0
    return full.reset_index(drop=True)


# ---------------------------------------------------------------- lens 1: fit
def _block_bootstrap_exponent(x, y, n_boot=600, block=180, seed=0):
    """Moving-block bootstrap CI for the exponent — honest inference under the
    heavy residual autocorrelation that makes naive OLS SEs meaningless."""
    rng = np.random.default_rng(seed)
    N = len(x)
    block = max(2, min(block, N // 4))
    nb = int(np.ceil(N / block))
    slopes = []
    for _ in range(n_boot):
        starts = rng.integers(0, N - block + 1, size=nb)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:N]
        xs, ys = x[idx], y[idx]
        b = np.polyfit(xs, ys, 1)[0]
        slopes.append(b)
    lo, hi = np.quantile(slopes, [0.025, 0.975])
    return float(lo), float(hi)


def fit_powerlaw(t, price, bootstrap=False):
    x = np.log10(t)
    y = np.log10(price)
    X = add_constant(x)
    res = OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 365})
    a, n = res.params
    resid = y - res.fittedvalues
    out = {
        "a": float(a), "n": float(n), "n_se_hac": float(res.bse[1]),
        "r2": float(res.rsquared), "resid": resid, "fitted": res.fittedvalues,
        "resid_sigma": float(np.std(resid)),
    }
    if bootstrap:
        lo, hi = _block_bootstrap_exponent(x, y)
        out["n_ci_boot"] = [lo, hi]
    return out


# ------------------------------------------- lens 2: spurious / cointegration
def cointegration_lens(t, price):
    y = np.log10(price)
    x = np.log10(t)
    X = add_constant(x)
    ols = OLS(y, X).fit()
    resid = y - ols.fittedvalues

    adf = adfuller(resid, autolag="AIC")
    try:
        kp_stat, kp_p, *_ = kpss(resid, regression="c", nlags="auto")
    except Exception:
        kp_stat, kp_p = float("nan"), float("nan")
    # Engle-Granger (note: log-time is a deterministic trend; reported for completeness)
    try:
        eg_t, eg_p, _ = coint(y, x)
    except Exception:
        eg_t, eg_p = float("nan"), float("nan")
    dw = float(durbin_watson(resid))
    lb = acorr_ljungbox(resid, lags=[20], return_df=True)
    lb_p = float(lb["lb_pvalue"].iloc[0])

    cointegrated = (adf[1] < 0.05) and (kp_p > 0.05)
    return {
        "adf_stat": float(adf[0]), "adf_p": float(adf[1]),
        "kpss_stat": float(kp_stat), "kpss_p": float(kp_p),
        "eg_stat": float(eg_t), "eg_p": float(eg_p),
        "durbin_watson": dw, "ljungbox_p": lb_p,
        "residual_stationary": bool(adf[1] < 0.05),
        "cointegrated": bool(cointegrated),
        "verdict": (
            "Residuals are stationary → the trend relationship is statistically real "
            "(not merely spurious)." if cointegrated else
            "Residuals fail joint stationarity → the high R² is partly spurious; treat "
            "the fit as a descriptive trend, not a proven law."
        ),
    }


# ----------------------------------------------------- lens 3: model comparison
def _aic_bic(sse, n, k):
    # Gaussian likelihood AIC/BIC from SSE (same response space)
    aic = n * np.log(sse / n) + 2 * k
    bic = n * np.log(sse / n) + k * np.log(n)
    return float(aic), float(bic)


def model_comparison(t, price):
    y = np.log10(price)
    n = len(y)
    t_yr = t / 365.2425
    results = []

    # power law: y = a + b*log10(t)   (2 params)
    X = add_constant(np.log10(t))
    b = OLS(y, X).fit()
    sse = float(np.sum((y - b.fittedvalues) ** 2))
    aic, bic = _aic_bic(sse, n, 2)
    results.append({"model": "Power law  (price ∝ tⁿ)", "params": 2, "r2": float(b.rsquared),
                    "aic": aic, "bic": bic, "sse": sse, "key": "power"})

    # exponential: y = a + k*t_yr  (constant doubling time) (2 params)
    Xe = add_constant(t_yr)
    be = OLS(y, Xe).fit()
    sse = float(np.sum((y - be.fittedvalues) ** 2))
    aic, bic = _aic_bic(sse, n, 2)
    results.append({"model": "Exponential  (price ∝ eᵏᵗ)", "params": 2, "r2": float(be.rsquared),
                    "aic": aic, "bic": bic, "sse": sse, "key": "exp"})

    # stretched exponential: y = a + b * t_yr^c  (3 params)
    def stretched(tt, a, bb, c):
        return a + bb * np.power(tt, c)
    try:
        p0 = [y.min(), 1.0, 0.5]
        popt, _ = optimize.curve_fit(stretched, t_yr, y, p0=p0, maxfev=20000)
        pred = stretched(t_yr, *popt)
        sse = float(np.sum((y - pred) ** 2))
        r2 = 1 - sse / float(np.sum((y - y.mean()) ** 2))
        aic, bic = _aic_bic(sse, n, 3)
        results.append({"model": "Stretched exponential", "params": 3, "r2": r2,
                        "aic": aic, "bic": bic, "sse": sse, "key": "stretched"})
    except Exception:
        pass

    # logistic saturation in log-price: y = L/(1+exp(-r(t_yr - t0))) + c (4 params)
    def logistic(tt, L, r, t0, c):
        return c + L / (1 + np.exp(-r * (tt - t0)))
    try:
        p0 = [y.max() - y.min(), 0.3, t_yr.mean(), y.min()]
        popt, _ = optimize.curve_fit(logistic, t_yr, y, p0=p0, maxfev=40000)
        pred = logistic(t_yr, *popt)
        sse = float(np.sum((y - pred) ** 2))
        r2 = 1 - sse / float(np.sum((y - y.mean()) ** 2))
        aic, bic = _aic_bic(sse, n, 4)
        results.append({"model": "Logistic (S-curve saturation)", "params": 4, "r2": r2,
                        "aic": aic, "bic": bic, "sse": sse, "key": "logistic"})
    except Exception:
        pass

    best = min(results, key=lambda r: r["aic"])
    for r in results:
        r["delta_aic"] = r["aic"] - best["aic"]
    results.sort(key=lambda r: r["aic"])
    return {"models": results, "winner": best["model"]}


# ------------------------------------------------- lens 4: OU mean reversion
def mean_reversion(t, price, fit):
    """Fit the residual r(t)=log10(price)-trend as an Ornstein-Uhlenbeck process
        dr = lambda*(theta - r) dt + sigma dW
    via its exact AR(1) discretization r_t = c + phi*r_{t-1} + u_t, and recover
    ALL three structural parameters (speed, equilibrium, vol) — not just half-life."""
    resid = np.asarray(fit["resid"])
    r_lag = resid[:-1]
    r_now = resid[1:]
    X = add_constant(r_lag)
    ar = OLS(r_now, X).fit()
    c = float(ar.params[0])
    phi = float(ar.params[1])
    u_var = float(np.var(np.asarray(ar.resid), ddof=2))  # innovation variance
    dt = 1.0  # one day

    half_life = float(-np.log(2) / np.log(phi)) if 0 < phi < 1 else float("nan")
    lam = (-np.log(phi) / dt) if 0 < phi < 1 else float("nan")     # speed, per day
    theta = (c / (1.0 - phi)) if phi < 1 else float("nan")          # equilibrium (≈0)
    # OU instantaneous volatility: Var(u) = sigma^2 (1 - phi^2) / (2 lambda)
    sigma_ou = float(np.sqrt(2.0 * lam * u_var / (1.0 - phi**2))) if 0 < phi < 1 else float("nan")
    sigma_annual = sigma_ou * np.sqrt(365.2425)                     # dex / sqrt(year)
    sigma_eq = float(np.std(resid))                                 # stationary dispersion

    # Non-stationary volatility: rolling 90-day vol of daily residual changes (annualized).
    dr = pd.Series(np.diff(resid))
    roll_vol = (dr.rolling(90).std() * np.sqrt(365.2425)).dropna()
    vol_lo, vol_med, vol_hi = (float(roll_vol.quantile(0.05)),
                               float(roll_vol.median()),
                               float(roll_vol.quantile(0.95)))

    cur_z = float((resid[-1] - np.mean(resid)) / sigma_eq)
    cur_pct = float((resid < resid[-1]).mean() * 100)
    return {
        "ar1_phi": phi, "ar1_c": c, "half_life_days": half_life,
        "lambda_per_year": float(lam * 365.2425) if lam == lam else float("nan"),
        "theta": theta, "sigma_ou_daily": sigma_ou, "sigma_annual": sigma_annual,
        "innovation_sd_daily": float(np.sqrt(u_var)),
        "current_zscore": cur_z, "current_percentile": cur_pct,
        "resid_mean": float(np.mean(resid)), "resid_sigma": sigma_eq,
        "vol_low": vol_lo, "vol_median": vol_med, "vol_high": vol_hi,
        "vol_ratio": float(vol_hi / vol_lo) if vol_lo > 0 else float("nan"),
        "interpretation": (
            f"Deviations mean-revert with half-life ~{half_life:.0f} days "
            f"(~{half_life/30.4:.1f} months); equilibrium θ≈{theta:+.3f} dex (i.e. the trend line itself). "
            f"Bitcoin sits {abs(cur_z):.2f}σ {'below' if cur_z < 0 else 'above'} fair value "
            f"({_ordinal(int(round(cur_pct)))} percentile)."
        ),
    }


# ----------------------------------------- lens 7 helper: predict next cycle
def predict_next_cycle(risk):
    """From the observed peak-to-peak multiples, estimate the next cycle's
    multiple two ways — and be honest that 3 points can't pin a 4th precisely."""
    mults = [p["multiple"] for p in risk.get("peak_to_peak", []) if p.get("multiple")]
    out = {"observed_multiples": [round(m, 2) for m in mults]}
    if len(mults) < 3:
        return out
    arr = np.asarray(mults, dtype=float)
    # (a) geometric decay of the EXCESS multiple (mult - 1), which must shrink toward 0
    excess = arr - 1.0
    ratios = excess[1:] / excess[:-1]                  # how fast the excess shrinks
    next_excess = excess[-1] * float(np.mean(ratios))
    pred_excess = float(1.0 + max(next_excess, 0.0))
    # (b) log-linear extrapolation of the multiples themselves (steeper)
    k = np.arange(1, len(arr) + 1)
    slope, intercept = np.polyfit(k, np.log(arr), 1)
    pred_loglin = float(np.exp(intercept + slope * (len(arr) + 1)))
    lo, hi = sorted([pred_loglin, pred_excess])
    if hi < 1.0:
        verdict = f"both extrapolations land below 1× ({lo:.1f}×–{hi:.1f}×) — i.e. they imply the cycle may <b>not</b> make a new all-time high at all"
    elif lo < 1.0 <= hi:
        verdict = f"the two extrapolations disagree — the gentler one implies a marginal new high (~{hi:.1f}×), the steeper one little to none (~{lo:.1f}×)"
    else:
        verdict = f"the current cycle's peak-to-peak gain lands near {lo:.1f}×–{hi:.1f}× — a new high, but a modest one"
    return {
        "observed_multiples": [round(m, 2) for m in mults],
        "pred_excess_geometric": round(pred_excess, 2),
        "pred_loglinear": round(pred_loglin, 2),
        "range_low": round(lo, 2), "range_high": round(hi, 2),
        "interpretation": (
            f"Extrapolating the {len(mults)} observed multiples, {verdict}. "
            f"Either way the era of 10×+ cycles is over. Three points cannot pin a fourth precisely — "
            f"this is a trend reading, not a forecast."
        ),
    }


# ------------------------------------------------------ lens 5: LPPLS bubble
def lppls_fit(daily: pd.DataFrame, start: str, end: str):
    sub = daily[(daily["date"] >= start) & (daily["date"] <= end)].reset_index(drop=True)
    tt = (sub["date"] - sub["date"].iloc[0]).dt.total_seconds().to_numpy() / 86400.0
    ly = np.log(sub["price"].to_numpy())
    N = len(tt)

    def linear_solve(tc, m, w):
        dt = np.maximum(tc - tt, 1e-6)
        f = dt ** m
        g = (dt ** m) * np.cos(w * np.log(dt))
        h = (dt ** m) * np.sin(w * np.log(dt))
        D = np.column_stack([np.ones(N), f, g, h])
        coef, *_ = np.linalg.lstsq(D, ly, rcond=None)
        resid = ly - D @ coef
        return coef, float(np.sum(resid ** 2))

    def cost(params):
        tc, m, w = params
        try:
            _, sse = linear_solve(tc, m, w)
            return sse
        except Exception:
            return 1e18

    tmax = tt[-1]
    best = None
    # grid over tc, m, omega; refine each with local minimization (bounded)
    for tc0 in np.linspace(tmax * 1.01, tmax * 1.25, 7):
        for m0 in [0.3, 0.5, 0.7]:
            for w0 in [6.0, 9.0, 12.0]:
                res = optimize.minimize(
                    cost, [tc0, m0, w0], method="L-BFGS-B",
                    bounds=[(tmax * 1.001, tmax * 1.4), (0.1, 0.9), (4.0, 15.0)],
                )
                if best is None or res.fun < best.fun:
                    best = res
    tc, m, w = best.x
    coef, sse = linear_solve(tc, m, w)
    pred = coef[0] + coef[1] * (tc - tt) ** m + (tc - tt) ** m * (
        coef[2] * np.cos(w * np.log(tc - tt)) + coef[3] * np.sin(w * np.log(tc - tt)))
    r2 = 1 - sse / float(np.sum((ly - ly.mean()) ** 2))
    tc_date = sub["date"].iloc[0] + pd.to_timedelta(tc, unit="D")
    peak_idx = int(sub["price"].idxmax())
    m_ok = bool(0.1 <= m <= 0.9)
    w_ok = bool(6 <= w <= 13)
    if m_ok and w_ok:
        verdict = (
            f"m={m:.2f}, ω={w:.1f} fall in the literature's bubble-regime bounds — log-periodic "
            f"acceleration is detectable, but tc is weakly identified and this is a diagnostic, not a forecast."
        )
    else:
        m_part = f"m={m:.2f} is in-bounds" if m_ok else f"m={m:.2f} falls outside the [0.1,0.9] band"
        if w <= 4.05:
            w_part = f"omega={w:.1f} sits at the search floor, below the [6,13] bubble band"
        elif w < 6:
            w_part = f"omega={w:.1f} sits below the [6,13] bubble band"
        elif w > 13:
            w_part = f"omega={w:.1f} sits above the [6,13] bubble band"
        else:
            w_part = f"omega={w:.1f} is in-bounds"
        joiner = " and " if not (m_ok or w_ok) else ", but "
        verdict = (
            f"{m_part}{joiner}{w_part}, so the log-periodic wobble is not robustly present; "
            f"this fit fails the strict filter and is a weak diagnostic, not a forecast."
        )
    return {
        "window": [start, end],
        "tc_days": float(tc), "tc_date": tc_date.strftime("%Y-%m-%d"),
        "m": float(m), "omega": float(w), "r2": float(r2),
        "actual_peak_date": sub["date"].iloc[peak_idx].strftime("%Y-%m-%d"),
        "actual_peak_price": float(sub["price"].iloc[peak_idx]),
        "dates": [d.strftime("%Y-%m-%d") for d in sub["date"]],
        "log_price": [float(v) for v in ly],
        "lppls_fit": [float(v) for v in pred],
        "valid_m": m_ok,
        "valid_omega": bool(4 < w <= 15),
        "passes_strict_filter": bool(m_ok and w_ok),
        "interpretation": (
            f"LPPLS fits a finite-time singularity (critical time tc) at {tc_date.strftime('%Y-%m-%d')}, "
            f"vs the actual cycle peak on {sub['date'].iloc[peak_idx].strftime('%Y-%m-%d')}. "
            + verdict
        ),
    }


# --------------------------------------------- lens 6: structural stability
def structural_stability(t, price):
    y = np.log10(price)
    x = np.log10(t)
    n = len(y)
    # rolling exponent (2-year window = ~730 obs)
    win = 730
    roll = []
    for end in range(win, n, 30):
        sl = slice(end - win, end)
        bb = OLS(y[sl], add_constant(x[sl])).fit()
        roll.append({"t": float(t[end - 1]), "n": float(bb.params[1])})

    # Chow test at each halving
    def chow(split_t):
        mask = t < split_t
        if mask.sum() < 30 or (~mask).sum() < 30:
            return None
        Xf = add_constant(x)
        rss_pool = float(np.sum(OLS(y, Xf).fit().resid ** 2))
        r1 = float(np.sum(OLS(y[mask], add_constant(x[mask])).fit().resid ** 2))
        r2 = float(np.sum(OLS(y[~mask], add_constant(x[~mask])).fit().resid ** 2))
        k = 2
        num = (rss_pool - (r1 + r2)) / k
        den = (r1 + r2) / (n - 2 * k)
        F = num / den
        p = 1 - stats.f.cdf(F, k, n - 2 * k)
        return {"F": float(F), "p": float(p)}

    chows = []
    for h in HALVINGS:
        ht = (pd.Timestamp(h, tz="UTC") - GENESIS).total_seconds() / 86400.0
        c = chow(ht)
        if c:
            chows.append({"halving": h, **c, "break": bool(c["p"] < 0.05)})
    n_breaks = sum(1 for c in chows if c["break"])
    return {
        "rolling_exponent": roll,
        "chow_tests": chows,
        "interpretation": (
            f"The exponent drifts within a band rather than holding a single constant; "
            f"Chow tests flag structural shifts at {n_breaks}/{len(chows)} halvings — the power law "
            f"is a strong descriptive frame but not a perfectly stationary parameter."
        ),
    }


# ------------------------------------------------- lens 7: risk & deceleration
def risk_deceleration(daily: pd.DataFrame):
    s = daily.set_index("date")["price"]
    # Identify the four cycles by halving epochs
    epochs = [("2011", "2012-11-28"), ("2012-11-28", "2016-07-09"),
              ("2016-07-09", "2020-05-11"), ("2020-05-11", "2024-04-20"),
              ("2024-04-20", "2027")]
    cycles = []
    for i, (a, b) in enumerate(epochs):
        seg = s[(s.index >= pd.Timestamp(a, tz="UTC")) & (s.index < pd.Timestamp(b, tz="UTC"))]
        if len(seg) < 10:
            continue
        peak = float(seg.max()); trough = float(seg.min())
        peak_date = seg.idxmax(); trough_date = seg.idxmin()
        cycles.append({
            "cycle": i, "start": a, "peak": peak, "trough": trough,
            "peak_date": peak_date.strftime("%Y-%m-%d"),
            "peak_multiple_vs_trough": float(peak / trough) if trough > 0 else None,
        })
    # peak-to-peak multiples (diminishing returns)
    p2p = []
    for i in range(1, len(cycles)):
        if cycles[i]["peak"] and cycles[i - 1]["peak"]:
            p2p.append({"from": cycles[i - 1]["peak_date"], "to": cycles[i]["peak_date"],
                        "multiple": float(cycles[i]["peak"] / cycles[i - 1]["peak"])})
    # max drawdown overall
    roll_max = s.cummax()
    dd = (s / roll_max - 1.0)
    return {
        "cycles": cycles,
        "peak_to_peak": p2p,
        "max_drawdown_pct": float(dd.min() * 100),
        "interpretation": (
            "Each halving cycle delivers a smaller peak-to-peak multiple than the last — "
            "diminishing returns that are exactly what a decelerating power law predicts: "
            "constant log-log slope means arithmetic ROI must shrink over calendar time."
        ),
    }


def _lppls_all_cycles(daily: pd.DataFrame):
    """Apply LPPLS consistently to every major run-up in the data — not just the
    one cycle that happens to fit best. Windows end at each cycle's actual peak."""
    # Each window is a run-UP ending at (near) that cycle's actual peak — never
    # past it, or the model has nothing to accelerate toward.
    recent_peak = daily[daily["date"] >= "2024-01-01"].set_index("date")["price"].idxmax()
    windows = [
        ("2017 cycle", "2016-06-01", "2017-12-17"),
        ("2021 cycle", "2019-12-01", "2021-11-10"),
        ("2024–25 cycle", "2023-01-01", recent_peak.strftime("%Y-%m-%d")),
    ]
    out = []
    for label, a, b in windows:
        try:
            r = lppls_fit(daily, a, b)
            r["label"] = label
            out.append(r)
        except Exception as exc:  # noqa
            out.append({"label": label, "window": [a, b], "error": str(exc)})
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    daily = load_daily()
    full = full_series()
    t, price = daily["t"].to_numpy(), daily["price"].to_numpy()

    fit = fit_powerlaw(t, price, bootstrap=True)
    full_fit = fit_powerlaw(full["t"].to_numpy(), full["price"].to_numpy(), bootstrap=True)

    out = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "genesis": GENESIS.strftime("%Y-%m-%d"),
        "data_note": f"Formal tests on continuous Coinbase daily 2016–2026 ({len(t)} obs). "
                     f"Full-history fit (n={full_fit['n']:.2f}) adds 2010–2015 reference points for the visual.",
        "fit_coinbase": {k: v for k, v in fit.items() if k not in ("resid", "fitted")},
        "fit_full": {k: v for k, v in full_fit.items() if k not in ("resid", "fitted")},
        "cointegration": cointegration_lens(t, price),
        "model_comparison": model_comparison(t, price),
        "model_comparison_full": model_comparison(full["t"].to_numpy(), full["price"].to_numpy()),
        "mean_reversion": mean_reversion(t, price, fit),
        "lppls": lppls_fit(daily, "2020-01-01", "2021-11-10"),
        "lppls_cycles": _lppls_all_cycles(daily),
        "stability": structural_stability(t, price),
        "risk": risk_deceleration(daily),
    }
    out["risk"]["prediction"] = predict_next_cycle(out["risk"])
    # residual series for plotting
    resid = np.asarray(fit["resid"])
    out["residuals"] = {
        "dates": [d.strftime("%Y-%m-%d") for d in daily["date"]],
        "z": [float(v) for v in (resid - resid.mean()) / np.std(resid)],
        "values": [float(v) for v in resid],
    }
    (OUT / "econ.json").write_text(json.dumps(out, indent=2))

    print("=" * 64)
    print("ECONOMETRIC LENSES — summary")
    print("=" * 64)
    c = out["cointegration"]
    print(f"\n[Cointegration] ADF p={c['adf_p']:.3f}  KPSS p={c['kpss_p']:.3f}  "
          f"DW={c['durbin_watson']:.2f}  → {'stationary/real' if c['cointegrated'] else 'partly spurious'}")
    print(f"\n[Model comparison]  winner = {out['model_comparison']['winner']}")
    for m in out["model_comparison"]["models"]:
        print(f"   {m['model']:<32} R²={m['r2']:.3f}  ΔAIC={m['delta_aic']:+.0f}")
    mr = out["mean_reversion"]
    print(f"\n[Mean reversion] half-life={mr['half_life_days']:.0f}d  "
          f"current z={mr['current_zscore']:+.2f}  ({mr['current_percentile']:.0f}th pctile)")
    lp = out["lppls"]
    print(f"\n[LPPLS] tc={lp['tc_date']} vs actual peak {lp['actual_peak_date']}  "
          f"m={lp['m']:.2f} ω={lp['omega']:.1f}  R²={lp['r2']:.3f}")
    st = out["stability"]
    nb = sum(1 for x in st['chow_tests'] if x['break'])
    print(f"\n[Stability] Chow breaks at {nb}/{len(st['chow_tests'])} halvings")
    rk = out["risk"]
    p2p = ", ".join(f"{p['multiple']:.1f}x" for p in rk["peak_to_peak"])
    print(f"\n[Risk] peak-to-peak multiples: {p2p}")
    print(f"        max drawdown: {rk['max_drawdown_pct']:.0f}%")
    print(f"\n[Model comparison — full history]  winner = {out['model_comparison_full']['winner']}")
    for m in out["model_comparison_full"]["models"]:
        print(f"   {m['model']:<32} R²={m['r2']:.3f}  ΔAIC={m['delta_aic']:+.0f}")
    print(f"\nArtifact: {OUT/'econ.json'}")


if __name__ == "__main__":
    main()
