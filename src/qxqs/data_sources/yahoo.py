from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
import pandas as pd


def fetch_yahoo_daily(symbol: str, *, range_: str = "2y") -> pd.DataFrame:
    query = urllib.parse.urlencode({"range": range_, "interval": "1d", "includePrePost": "false", "events": "div,splits"})
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    result = (payload.get("chart", {}).get("result") or [None])[0]
    if not result:
        raise RuntimeError(f"Yahoo returned no chart result for {symbol}")
    timestamps = result.get("timestamp") or []
    quote = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    rows = []
    for idx, ts in enumerate(timestamps):
        try:
            open_, high, low, close = quote["open"][idx], quote["high"][idx], quote["low"][idx], quote["close"][idx]
            volume = quote.get("volume", [None] * len(timestamps))[idx]
        except (KeyError, IndexError):
            continue
        if None in (open_, high, low, close):
            continue
        rows.append({"date": datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat(), "open": float(open_), "high": float(high), "low": float(low), "close": float(close), "volume": float(volume or 0)})
    if len(rows) < 80:
        raise RuntimeError(f"Not enough daily bars for {symbol}: {len(rows)}")
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)
