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

## Deploy to GitHub Pages (scottn66.github.io)

This folder is self-contained (HTML + `assets/`). Plotly and MathJax load from
CDNs; all data and figures are local.

```bash
# from your scottn66.github.io repo
cp -r /path/to/coinbase/portfolio/bitcoin-power-law ./bitcoin-power-law
git add bitcoin-power-law
git commit -m "Add Bitcoin power-law econometric analysis"
git push
```

It will be live at `https://scottn66.github.io/bitcoin-power-law/` within a minute.
(For a user/organization Pages site, no `gh-pages` branch or config is needed —
files on the default branch are served directly.)

## Regenerate the analysis

From the `coinbase` project root:

```bash
uv run python scripts/power_law.py          # fit + corridor + power_law.json
uv run python scripts/pl_econometrics.py     # all econometric lenses -> econ.json
uv run python scripts/pl_figures.py          # seaborn figures -> assets/*.png
uv run python scripts/pl_data.py             # bundle -> assets/data.js
```

## Caveat

Educational analysis, not investment advice. The headline finding is deliberately
unsexy: Bitcoin *has* tracked a power law as a durable **descriptive** trend, but
it is a fragile **law** — imprecise, non-stationary in its residuals, and
statistically indistinguishable from an early-stage logistic over the recent decade.
