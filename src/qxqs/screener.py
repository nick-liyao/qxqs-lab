from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable
import pandas as pd
from .data_sources.yahoo import fetch_yahoo_daily
from .signals import add_qxqs_signals

@dataclass(frozen=True)
class RepairCandidate:
    symbol: str
    date: str
    close: float
    score: float
    grade: str
    pos_120d: float | None
    drawdown_120d: float | None
    xddw_fast: float | None
    xddw_slow: float | None
    reasons: str
    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def pct_change(cur: float, prev: float | None) -> float | None:
    return None if prev is None or prev == 0 else (cur / prev - 1.0) * 100.0


def _safe_float(value: object) -> float | None:
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def score_dataframe(symbol: str, df: pd.DataFrame) -> RepairCandidate | None:
    d = add_qxqs_signals(df).sort_values("date").reset_index(drop=True)
    if len(d) < 140:
        return None
    idx, row = len(d) - 1, d.iloc[-1]
    close = float(row["close"])
    high, low, close_s = d["high"].astype(float), d["low"].astype(float), d["close"].astype(float)
    reasons = []
    hhv120 = _safe_float(high.rolling(120, min_periods=120).max().iloc[idx])
    llv120 = _safe_float(low.rolling(120, min_periods=120).min().iloc[idx])
    pos_120 = None if hhv120 is None or llv120 is None or hhv120 == llv120 else (close - llv120) / (hhv120 - llv120) * 100
    drawdown_120 = pct_change(close, hhv120)
    score = 0.0
    if pos_120 is not None and pos_120 <= 35:
        score += 20; reasons.append(f"120d lower zone ({pos_120:.1f}%)")
    if drawdown_120 is not None and drawdown_120 <= -8:
        score += min(abs(drawdown_120), 25); reasons.append(f"{abs(drawdown_120):.1f}% below 120d high")
    low_5, prev_low_20 = float(low.iloc[idx-4:idx+1].min()), float(low.iloc[idx-24:idx-4].min())
    if low_5 >= prev_low_20 * 0.99:
        score += 10; reasons.append("no obvious 5d lower low")
    ma5 = close_s.rolling(5, min_periods=5).mean()
    ma20 = close_s.rolling(20, min_periods=20).mean()
    if pct_change(float(ma5.iloc[idx]), _safe_float(ma5.iloc[idx-3])) and pct_change(float(ma5.iloc[idx]), _safe_float(ma5.iloc[idx-3])) > 0:
        score += 10; reasons.append("MA5 improving")
    if pct_change(float(ma20.iloc[idx]), _safe_float(ma20.iloc[idx-5])) and pct_change(float(ma20.iloc[idx]), _safe_float(ma20.iloc[idx-5])) > -0.5:
        score += 10; reasons.append("MA20 stabilizing")
    if row["WRV_color"] == "red":
        score += 8; reasons.append("WRV red")
    if row["DKXV_color"] == "red":
        score += 8; reasons.append("DKXV red")
    fast_now, slow_now = _safe_float(row["FAST2"]), _safe_float(row["SLOW2"])
    if fast_now is not None and slow_now is not None and (fast_now < 50 or slow_now < 50):
        score += 12; reasons.append(f"XDDW low/recovering ({fast_now:.1f}/{slow_now:.1f})")
    score = round(min(score, 100), 1)
    low_context = score >= 50 and (pos_120 is None or pos_120 <= 70)
    grade = "A" if low_context and score >= 80 else "B" if low_context and score >= 65 else "C" if low_context else "watch"
    return RepairCandidate(symbol, row["date"].date().isoformat() if hasattr(row["date"], "date") else str(row["date"])[:10], round(close, 2), score, grade, round(pos_120, 2) if pos_120 is not None else None, round(drawdown_120, 2) if drawdown_120 is not None else None, round(fast_now, 2) if fast_now is not None else None, round(slow_now, 2) if slow_now is not None else None, "; ".join(reasons[:8]))


def screen_symbols(symbols: Iterable[str], *, range_: str = "2y") -> list[RepairCandidate]:
    out = []
    for symbol in symbols:
        c = score_dataframe(symbol.upper(), fetch_yahoo_daily(symbol, range_=range_))
        if c:
            out.append(c)
    return sorted(out, key=lambda c: c.score, reverse=True)
