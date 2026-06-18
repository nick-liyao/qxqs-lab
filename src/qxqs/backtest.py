from __future__ import annotations

from dataclasses import asdict, dataclass
import pandas as pd
from .signals import add_qxqs_signals

ENTRY_SIGNALS = {"BBB", "B"}
EXIT_SIGNALS = {"HOT", "SSS", "SS"}

@dataclass(frozen=True)
class BacktestSummary:
    symbol: str
    total_return_pct: float
    buy_hold_return_pct: float
    max_drawdown_pct: float
    trades: int
    exposure_pct: float
    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def run_backtest(df: pd.DataFrame, *, symbol: str = "SAMPLE") -> BacktestSummary:
    d = add_qxqs_signals(df).dropna(subset=["DKXV"]).reset_index(drop=True)
    cash, shares, in_position, trades, exposure_days, equity = 1.0, 0.0, False, 0, 0, []
    for i in range(len(d) - 1):
        signal, next_row = d.iloc[i], d.iloc[i + 1]
        price, label = float(next_row["open"]), str(signal["signal"])
        if not in_position and label in ENTRY_SIGNALS:
            shares, cash, in_position, trades = cash / price, 0.0, True, trades + 1
        elif in_position and label in EXIT_SIGNALS:
            cash, shares, in_position, trades = shares * price, 0.0, False, trades + 1
        equity.append(cash + shares * float(next_row["close"]))
        if in_position:
            exposure_days += 1
    if not equity:
        return BacktestSummary(symbol, 0.0, 0.0, 0.0, 0, 0.0)
    curve = pd.Series(equity)
    drawdown = curve / curve.cummax() - 1
    first_close, last_close = float(d.iloc[0]["close"]), float(d.iloc[-1]["close"])
    return BacktestSummary(symbol, float(round((curve.iloc[-1] - 1) * 100, 2)), float(round((last_close / first_close - 1) * 100, 2)), float(round(drawdown.min() * 100, 2)), trades, float(round(exposure_days / max(len(d) - 1, 1) * 100, 1)))
