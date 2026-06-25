#!/usr/bin/env python3
"""Refresh the live BTC "current" snapshot in bitcoin-power-law/assets/data.js.

The full econometric payload in data.js is produced out-of-repo by pl_econometrics.py
and does not need regenerating day to day -- the power-law fit and the corridor are
stable on a months timescale. Only "today" moves. So this script:

  1. fetches the current BTC spot price (Coinbase, free, no key),
  2. recomputes the `current` block (today's point + the "Price / model" and
     "Corridor" chips) from the *stored* fit parameters (fit_full) and the shipped
     empirical corridor quantiles,
  3. rewrites ONLY that one block (a minimal, ~1-line diff).

It deliberately does NOT touch the historical `series`, the fit, or the Lens-4
mean_reversion block (those need a real re-fit). Run daily by GitHub Actions.

Test without network:  BTC_TEST_PRICE=101000 python3 scripts/update_btc_price.py --dry-run
"""
import datetime
import io
import json
import math
import os
import re
import sys
import urllib.request

DATA = "bitcoin-power-law/assets/data.js"
GENESIS = datetime.date(2009, 1, 3)
DRY_RUN = "--dry-run" in sys.argv


def fetch_price():
    """Current BTC-USD spot from Coinbase (matches the page's data source)."""
    test = os.environ.get("BTC_TEST_PRICE")
    if test:
        return float(test)
    req = urllib.request.Request(
        "https://api.coinbase.com/v2/prices/BTC-USD/spot",
        headers={"User-Agent": "btc-powerlaw-updater"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return float(json.load(r)["data"]["amount"])


def corridor_percentile(resid, corr):
    """Percentile of `resid` within the shipped empirical corridor quantiles.

    Piecewise-linear through q05..q95 (so it respects the corridor's real skew),
    with clamped linear extrapolation in the tails. Approximates the pipeline's
    empirical-rank percentile to within a point or two.
    """
    xs = [corr["q05"], corr["q25"], corr["q50"], corr["q75"], corr["q95"]]
    ps = [5.0, 25.0, 50.0, 75.0, 95.0]
    if resid <= xs[0]:
        slope = (ps[1] - ps[0]) / (xs[1] - xs[0]) if xs[1] != xs[0] else 0.0
        return max(0.5, ps[0] + (resid - xs[0]) * slope)
    if resid >= xs[-1]:
        slope = (ps[-1] - ps[-2]) / (xs[-1] - xs[-2]) if xs[-1] != xs[-2] else 0.0
        return min(99.5, ps[-1] + (resid - xs[-1]) * slope)
    for i in range(len(xs) - 1):
        if xs[i] <= resid <= xs[i + 1]:
            return ps[i] + (resid - xs[i]) * (ps[i + 1] - ps[i]) / (xs[i + 1] - xs[i])
    return 50.0


def main():
    raw = io.open(DATA, encoding="utf-8").read()
    m = re.search(r"window\.PL\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S)
    if not m:
        sys.exit("ERROR: could not locate the window.PL object in %s" % DATA)
    pl = json.loads(m.group(1))

    try:
        price = fetch_price()
    except Exception as e:  # transient API hiccup -> leave the file untouched
        print("price fetch failed (%s) -- no update this run" % e)
        return 0
    if not (price and price > 0):
        print("got non-positive price %r -- no update" % price)
        return 0

    today = datetime.datetime.now(datetime.timezone.utc).date()
    day = (today - GENESIS).days
    fit = pl["fit_full"]                     # current.model_price is fit_full-based
    a, n = fit["a"], fit["n"]
    log_model = a + n * math.log10(day)
    model = 10 ** log_model
    resid = math.log10(price) - log_model    # log10(price / fair value)
    ratio = price / model
    cp = max(0.5, min(99.5, corridor_percentile(resid, pl["corridor"])))

    new_cur = {
        "date": today.isoformat(),
        "day": float(day),
        "price": round(price, 2),
        "model_price": model,
        "residual": resid,
        "ratio_to_model": ratio,
        "corridor_percentile": cp,
    }
    replacement = '"current": ' + json.dumps(new_cur)
    out, n_sub = re.subn(r'"current": \{[^{}]*\}', replacement, raw, count=1)
    if n_sub != 1:
        sys.exit("ERROR: did not match exactly one `current` block (matched %d) -- "
                 "data.js structure changed; aborting without writing." % n_sub)

    print("price $%s  |  fair value $%s  |  ratio %.3f  |  corridor %.1f%%  |  day %d"
          % (round(price, 2), round(model), ratio, cp, day))
    if DRY_RUN:
        print("[dry-run] would write the above; file changed: %s" % (out != raw))
        return 0
    if out == raw:
        print("no change needed.")
        return 0
    io.open(DATA, "w", encoding="utf-8").write(out)
    print("updated data.js current block.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
