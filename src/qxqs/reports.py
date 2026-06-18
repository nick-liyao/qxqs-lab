from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
from .backtest import BacktestSummary
from .screener import RepairCandidate
from .signals import latest_signal_summary


def write_signal_report(df: pd.DataFrame, *, symbol: str, output: str | Path) -> Path:
    output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    s = latest_signal_summary(df)
    output.write_text(f"# QXQS Daily Report: {symbol}\n\n- Date: {s['date']}\n- Close: {s['close']}\n- WRV line: {s['WRV_color']}\n- DKXV line: {s['DKXV_color']}\n- XDDW: {s['FAST2']} / {s['SLOW2']}\n- Latest signal: {s['signal']}\n- Last signal date: {s['last_signal_date'] or 'none'}\n\nRead: {s['signal_reason']}\n\nThis is a research label, not a trading instruction.\n", encoding="utf-8")
    return output


def write_screener_report(candidates: list[RepairCandidate], *, output: str | Path, top: int = 10) -> Path:
    output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# QXQS Low-Repair Screener", "", "Grades: A = strong repair context, B = good watch candidate, C = early watch candidate.", ""]
    for c in candidates[:top]:
        lines.append(f"- **{c.symbol}** {c.grade} {c.score:.1f}: close {c.close}, 120d pos {c.pos_120d if c.pos_120d is not None else 'NA'}%, drawdown {c.drawdown_120d if c.drawdown_120d is not None else 'NA'}%, XDDW {c.xddw_fast}/{c.xddw_slow}; {c.reasons}")
    lines += ["", "Research and education only. Not financial advice."]
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def write_json(payload: object, output: str | Path) -> Path:
    output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return output


def backtest_markdown(summary: BacktestSummary) -> str:
    return f"# QXQS Backtest: {summary.symbol}\n\n- Strategy return: {summary.total_return_pct}%\n- Buy and hold: {summary.buy_hold_return_pct}%\n- Max drawdown: {summary.max_drawdown_pct}%\n- Trades: {summary.trades}\n- Exposure: {summary.exposure_pct}%\n\nSignals are confirmed on one bar and traded on the next bar to avoid future leakage.\n"
