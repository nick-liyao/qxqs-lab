from __future__ import annotations

import numpy as np
import pandas as pd


def sma_cn(series: pd.Series, n: int, m: int = 1) -> pd.Series:
    out = pd.Series(index=series.index, dtype="float64")
    prev = np.nan
    for i, value in enumerate(series.astype("float64")):
        if np.isnan(value):
            out.iloc[i] = np.nan
            continue
        prev = value if np.isnan(prev) else (m * value + (n - m) * prev) / n
        out.iloc[i] = prev
    return out


def count_prev(signal: pd.Series, n: int) -> pd.Series:
    return signal.shift(1).fillna(False).astype(int).rolling(n, min_periods=1).sum()


def line_color_series(series: pd.Series) -> pd.Series:
    diff = series.diff()
    out = pd.Series("flat", index=series.index, dtype="object")
    out.loc[diff > 0] = "red"
    out.loc[diff < 0] = "green"
    out.loc[series.isna() | series.shift(1).isna()] = "unknown"
    return out


def add_qxqs_indicators(df: pd.DataFrame, p1: int = 5) -> pd.DataFrame:
    d = df.copy()
    close, high, low, open_ = d["close"].astype("float64"), d["high"].astype("float64"), d["low"].astype("float64"), d["open"].astype("float64")
    d["WRV"] = close.rolling(p1, min_periods=p1).mean()
    mid = (3 * close + low + open_ + high) / 6
    weights = list(range(20, 0, -1))
    d["DKXV"] = sum(w * mid.shift(i) for i, w in enumerate(weights)) / 210
    llv60 = low.rolling(60, min_periods=60).min()
    hhv60 = high.rolling(60, min_periods=60).max()
    rsv = (close - llv60) / (hhv60 - llv60).replace(0, np.nan) * 100
    k = sma_cn(rsv, 20, 1)
    d["SLOW2"] = sma_cn(k, 5, 1)
    d["FAST2"] = 3 * k - 2 * d["SLOW2"]
    d["WRV_color"] = line_color_series(d["WRV"])
    d["DKXV_color"] = line_color_series(d["DKXV"])
    d["price_to_WRV_pct"] = (close / d["WRV"] - 1) * 100
    d["price_to_DKXV_pct"] = (close / d["DKXV"] - 1) * 100
    return d
