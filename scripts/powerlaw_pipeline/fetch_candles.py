#!/usr/bin/env python3
"""Incrementally fetch BTC-USD hourly candles from Coinbase's public market-data
API into .cache/candles/BTC-USD_ONE_HOUR.parquet, the input the power-law
pipeline reads.

Mirrors the paging/caching behavior of the original out-of-repo fetcher:
350 candles per request, pages fully present in the cache are skipped, new
candles are merged and the parquet rewritten with the identical schema
(product str, timestamp int64, open/high/low/close/volume as strings).

No auth required. Cold cache = ~256 requests (2016-05-29 -> today); a warm
cache fetches only the pages since the last run.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache/candles/BTC-USD_ONE_HOUR.parquet"
PRODUCT = "BTC-USD"
GRANULARITY = "ONE_HOUR"
STEP = 3600
# First hour of Coinbase BTC-USD hourly history (2016-05-29 22:00 UTC). Fixed
# and hour-aligned so page boundaries line up across runs and the page-skip
# logic keeps working.
START_EPOCH = 1464559200
MAX_CANDLES_PER_REQUEST = 350
URL = (
    "https://api.coinbase.com/api/v3/brokerage/market/products/"
    f"{PRODUCT}/candles?start={{start}}&end={{end}}&granularity={GRANULARITY}"
)
UA = "btc-powerlaw-updater (github.com/scottn66/scottn66.github.io)"


def fetch_page(start: int, end: int) -> list[dict]:
    req = urllib.request.Request(URL.format(start=start, end=end), headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))["candles"]
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            code = getattr(exc, "code", None)
            if attempt == 3 or (code is not None and code not in (429, 500, 502, 503, 504)):
                raise SystemExit(f"ERROR: candle fetch failed for [{start}, {end}]: {exc}")
            time.sleep(2 ** (attempt + 1))
    raise SystemExit("unreachable")


def main() -> None:
    cached: dict[int, dict] = {}
    if CACHE.exists():
        df = pd.read_parquet(CACHE)
        cached = {int(row.timestamp): row._asdict() for row in df.itertuples(index=False)}
    print(f"cache: {len(cached)} candles")

    end_epoch = int(time.time()) // STEP * STEP  # exclude the in-progress hour
    page_seconds = STEP * MAX_CANDLES_PER_REQUEST
    cursor = START_EPOCH
    pages_fetched = pages_skipped = 0
    while cursor < end_epoch:
        page_end = min(cursor + page_seconds, end_epoch)
        if all(ts in cached for ts in range(cursor, page_end, STEP)):
            pages_skipped += 1
            cursor = page_end
            continue
        for c in fetch_page(cursor, page_end):
            cached[int(c["start"])] = {
                "product": PRODUCT,
                "timestamp": int(c["start"]),
                "open": str(c["open"]),
                "high": str(c["high"]),
                "low": str(c["low"]),
                "close": str(c["close"]),
                "volume": str(c["volume"]),
            }
        pages_fetched += 1
        cursor = page_end
        time.sleep(0.13)  # stay under Coinbase's 10 req/s public cap

    if not cached:
        raise SystemExit("ERROR: no candles fetched")
    out = pd.DataFrame(sorted(cached.values(), key=lambda r: r["timestamp"]),
                       columns=["product", "timestamp", "open", "high", "low", "close", "volume"])
    out["timestamp"] = out["timestamp"].astype("int64")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(CACHE, index=False)
    first, last = out["timestamp"].iloc[0], out["timestamp"].iloc[-1]
    print(f"wrote {len(out)} candles ({pages_fetched} pages fetched, {pages_skipped} skipped): "
          f"{pd.Timestamp(first, unit='s', tz='UTC')} -> {pd.Timestamp(last, unit='s', tz='UTC')}")
    if last < end_epoch - 3 * 86400:
        raise SystemExit(f"ERROR: newest candle is stale ({pd.Timestamp(last, unit='s', tz='UTC')})")


if __name__ == "__main__":
    main()
