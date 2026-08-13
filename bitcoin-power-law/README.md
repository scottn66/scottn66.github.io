# Does Bitcoin Follow a Power Law? — An Econometric Autopsy

An interactive, multi-lens econometric scrutiny of the Bitcoin power-law model
(`price = A · (days since genesis)ⁿ`). Built with Python (statsmodels, scipy),
Plotly, and seaborn on 10 years of real Coinbase data.

**Live:** `https://scottn66.github.io/bitcoin-power-law/`

## What it covers

Eight analytical lenses, each interactive:

1. **Fit & honest inference** — OLS in log-log space, Newey–West (HAC) SEs, and a
   moving-block bootstrap that widens the exponent CI to ≈[4.3, 6.2].
2. **Spurious regression?** — ADF / KPSS / Durbin–Watson / Ljung–Box, with the
   key nuance that cointegration is *undefined* against a deterministic clock.
3. **Model tournament** — power law vs. exponential vs. stretched-exp vs. logistic
   by AIC/BIC. Exponential is decisively rejected; logistic edges the power law
   over the recent window.
4. **Mean reversion** — the corridor as an Ornstein–Uhlenbeck process (half-life,
   z-score oscillator).
5. **Bubbles (LPPLS)** — Filimonov–Sornette log-periodic singularity on the
   2020–21 cycle, with a strict acceptance filter.
6. **Structural stability** — rolling exponent + Chow tests at the halvings.
7. **Risk & deceleration** — diminishing cycle returns as a power-law prediction.
8. **Honest scorecard** — what survives scrutiny and what doesn't.

## How it stays fresh

This folder is self-contained (HTML + `assets/`). Plotly and MathJax load from
CDNs; all data and figures are local. Two GitHub Actions keep the data current:

- **Daily** (`.github/workflows/update-btc-price.yml`, 07:23 UTC) — fetches the
  Coinbase spot price and patches only the `"current"` block in `assets/data.js`.
- **Weekly** (`.github/workflows/refresh-power-law.yml`, Mondays 10:47 UTC) —
  runs the full in-repo pipeline: refreshes the hourly candle cache, refits the
  power law, reruns every econometric lens, redraws the five figures, and
  commits `assets/data.js` + `assets/fig_*.png` if anything changed.

## Regenerate the analysis locally

From the repo root (deps: `pip install -r scripts/powerlaw_pipeline/requirements.txt`):

```bash
python scripts/powerlaw_pipeline/fetch_candles.py     # candle cache -> .cache/candles/
python scripts/powerlaw_pipeline/power_law.py         # fit + corridor -> runs/power_law/power_law.json
python scripts/powerlaw_pipeline/pl_econometrics.py   # all econometric lenses -> econ.json
python scripts/powerlaw_pipeline/pl_figures.py        # seaborn figures -> assets/fig_*.png
python scripts/powerlaw_pipeline/pl_data.py           # bundle -> assets/data.js
python scripts/powerlaw_pipeline/verify_data.py       # sanity gate
```

## Caveat

Educational analysis, not investment advice. The headline finding is deliberately
unsexy: Bitcoin *has* tracked a power law as a durable **descriptive** trend, but
it is a fragile **law** — imprecise, non-stationary in its residuals, and
statistically indistinguishable from an early-stage logistic over the recent decade.
