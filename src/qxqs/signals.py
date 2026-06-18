from __future__ import annotations

import numpy as np
import pandas as pd
from .indicators import add_qxqs_indicators, count_prev

SIGNAL_ORDER = ["BBB", "B", "HOT", "SSS", "SS", "S"]
SIGNAL_DEFINITIONS = {
    "BBB": "Panic low: new-low context with deep DKX deviation.",
    "B": "Pullback build: trend repair near WRV/DKXV with improving XDDW.",
    "HOT": "Overheat: high relative position and stretched above WRV.",
    "SSS": "Strong break risk: turn-down with DKX break or both lines weakening.",
    "SS": "Medium risk: turn-down or failed rebound with structural weakness.",
    "S": "Light risk: failed rebound under weakening trend.",
}


def add_qxqs_signals(df: pd.DataFrame) -> pd.DataFrame:
    d = add_qxqs_indicators(df)
    close, high, low, open_ = d["close"], d["high"], d["low"], d["open"]
    wrv, dkxv, fast2, slow2 = d["WRV"], d["DKXV"], d["FAST2"], d["SLOW2"]
    updev = (high / wrv - 1) * 100
    dndev = (low / dkxv - 1) * 100
    qspower = 10 * (close - close.shift(14)).abs() / (high - low).rolling(14, min_periods=14).mean()
    newlow = low <= low.rolling(20, min_periods=20).min()
    buy_low = newlow & (dndev < -4.5) & (low < low.rolling(20, min_periods=20).min().shift(1) * 0.98) & (low <= low.rolling(5, min_periods=5).min())
    touchline = (low < wrv * 1.01) | (low < dkxv * 1.01)
    trendok = (wrv > wrv.shift(1)) | (dkxv > dkxv.shift(1))
    dkxok = (dkxv >= dkxv.shift(1)) | (dkxv - dkxv.shift(1) >= dkxv.shift(1) - dkxv.shift(2))
    buy_pullback = trendok & touchline & (fast2 < 65) & (fast2 > fast2.shift(1)) & dkxok & (close > open_)
    buy_pullback = buy_pullback & (count_prev(buy_pullback, 5) == 0)
    highzone = (fast2 > 75) | (slow2 > 75)
    xddw_hot = (fast2 > 75) & (slow2 > 75)
    tophigh = (updev > 3) & highzone & (qspower > 35)
    sell_hot = tophigh & (count_prev(tophigh, 12) == 0)
    wrturn = (wrv < wrv.shift(1)) & (wrv.shift(1) >= wrv.shift(2))
    sell_turn = highzone & wrturn & (updev > 1.5) & (count_prev(highzone & wrturn & (updev > 1.5), 12) == 0)
    rebound = (high > wrv * 0.99) | (high > dkxv * 0.99)
    sell_fail = rebound & ((wrv < wrv.shift(1)) | (dkxv < dkxv.shift(1))) & (close < open_) & (close < wrv)
    sell_fail = sell_fail & (count_prev(sell_fail, 12) == 0)
    break_dkx = close < dkxv
    both_weak = (wrv < wrv.shift(1)) & (dkxv < dkxv.shift(1))
    d["BBB"] = buy_low.fillna(False)
    d["B"] = buy_pullback.fillna(False)
    d["HOT"] = (sell_hot | (sell_turn & xddw_hot & (~break_dkx) & (~both_weak))).fillna(False)
    d["SSS"] = (sell_turn & (break_dkx | both_weak)).fillna(False)
    d["SS"] = ((sell_turn | (sell_fail & (break_dkx | both_weak))) & (~d["HOT"]) & (~d["SSS"])).fillna(False)
    d["S"] = (sell_fail & (~d["SS"]) & (~d["HOT"]) & (~d["SSS"])).fillna(False)
    d["signal"] = ""
    d["signal_reason"] = ""
    for label in SIGNAL_ORDER:
        mask = d["signal"].eq("") & d[label].astype(bool)
        d.loc[mask, "signal"] = label
        d.loc[mask, "signal_reason"] = SIGNAL_DEFINITIONS[label]
    d["risk_side"] = np.select([d["BBB"] | d["B"], d["HOT"] | d["SSS"] | d["SS"] | d["S"]], ["opportunity", "risk"], default="neutral")
    return d


def latest_signal_summary(df: pd.DataFrame) -> dict[str, object]:
    d = df.dropna(subset=["DKXV"]).reset_index(drop=True)
    row = d.iloc[-1]
    signal_dates = d.loc[d["signal"].ne(""), "date"].tolist()
    return {"date": row["date"].date().isoformat() if hasattr(row["date"], "date") else str(row["date"])[:10], "close": round(float(row["close"]), 2), "WRV_color": row["WRV_color"], "DKXV_color": row["DKXV_color"], "FAST2": round(float(row["FAST2"]), 2), "SLOW2": round(float(row["SLOW2"]), 2), "signal": row["signal"] or "none", "signal_reason": row["signal_reason"] or "No fresh tiered signal.", "last_signal_date": str(signal_dates[-1])[:10] if signal_dates else None}
