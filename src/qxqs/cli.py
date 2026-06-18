from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
import math
from datetime import date, timedelta
from .backtest import run_backtest
from .charts import render_signal_chart
from .data_sources.csv import load_csv
from .integrations.futu import export_futu_pack
from .reports import backtest_markdown, write_json, write_screener_report, write_signal_report
from .screener import screen_symbols
from .signals import add_qxqs_signals, latest_signal_summary

DEFAULT_SYMBOLS = ["QQQ", "SPY", "NVDA", "GDX", "KWEB"]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="qxqs")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("demo")
    for name in ["chart", "signals", "backtest", "report"]:
        sp = sub.add_parser(name)
        sp.add_argument("csv")
        sp.add_argument("--symbol", default="SAMPLE")
        sp.add_argument("--output", default=f"outputs/reports/{name}.md")
    screen = sub.add_parser("screen")
    screen.add_argument("--symbols", nargs="*", default=DEFAULT_SYMBOLS)
    screen.add_argument("--range", default="2y")
    screen.add_argument("--top", type=int, default=10)
    screen.add_argument("--output", default="outputs/reports/low-repair.md")
    screen.add_argument("--json", default="outputs/reports/low-repair.json")
    futu = sub.add_parser("export-futu")
    futu.add_argument("--output-dir", default="outputs/futu-pack")
    web = sub.add_parser("web")
    web.add_argument("--port", default="8501")
    return p


def _sample_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows=[]; cur=date(2024,1,2); price=100.0
    while len(rows)<260:
        if cur.weekday()<5:
            phase=len(rows)
            drift=0.22 if phase<55 else -0.42 if phase<95 else 0.34 if phase<140 else 0.08*math.sin(phase/3) if phase<180 else 0.38 if phase<220 else (-0.18 if phase%5<3 else 0.22)
            wave=math.sin(phase/5)*0.55+math.sin(phase/13)*0.35
            open_=price+math.sin(phase/7)*0.4
            close=max(5, open_+drift+wave*0.45)
            high=max(open_,close)+0.8
            low=min(open_,close)-0.8
            rows.append((cur.isoformat(),open_,high,low,close,1000000+phase*1200))
            price=close
        cur+=timedelta(days=1)
    path.write_text("date,open,high,low,close,volume\n"+"".join(f"{d},{o:.2f},{h:.2f},{l:.2f},{c:.2f},{v}\n" for d,o,h,l,c,v in rows), encoding="utf-8")


def _load_with_signals(path: str | Path):
    return add_qxqs_signals(load_csv(path))


def run_demo() -> None:
    sample = Path("examples/sample_data/sample_ohlcv.csv")
    if not sample.exists(): _sample_csv(sample)
    d = _load_with_signals(sample)
    chart_path = render_signal_chart(d, symbol="SAMPLE", output="outputs/charts/qxqs-demo.svg")
    signal_report = write_signal_report(d, symbol="SAMPLE", output="outputs/reports/latest.md")
    summary = run_backtest(load_csv(sample), symbol="SAMPLE")
    backtest_path = Path("outputs/reports/backtest.md")
    backtest_path.parent.mkdir(parents=True, exist_ok=True)
    backtest_path.write_text(backtest_markdown(summary), encoding="utf-8")
    write_json(summary.to_dict(), "outputs/reports/backtest.json")
    futu_zip = export_futu_pack()
    print(f"Chart: {chart_path}")
    print(f"Signal report: {signal_report}")
    print(f"Futu/Moomoo pack: {futu_zip}")
    print(f"Backtest: {summary.to_dict()}")


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "demo": run_demo(); return
    if args.command == "chart": print(render_signal_chart(_load_with_signals(args.csv), symbol=args.symbol, output=args.output)); return
    if args.command == "signals":
        d=_load_with_signals(args.csv)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        d.to_csv(args.output, index=False)
        print(latest_signal_summary(d)); return
    if args.command == "screen":
        c=screen_symbols(args.symbols, range_=args.range)
        print(write_screener_report(c, output=args.output, top=args.top))
        print(write_json([x.to_dict() for x in c], args.json)); return
    if args.command == "backtest":
        s=run_backtest(load_csv(args.csv), symbol=args.symbol)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(backtest_markdown(s), encoding="utf-8")
        print(s.to_dict()); return
    if args.command == "report": print(write_signal_report(_load_with_signals(args.csv), symbol=args.symbol, output=args.output)); return
    if args.command == "export-futu": print(export_futu_pack(args.output_dir)); return
    if args.command == "web":
        env = {**os.environ, "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false"}
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(Path(__file__).with_name("mobile_app.py")), "--server.port", str(args.port), "--server.headless", "true"], env=env, check=False)
        return

if __name__ == "__main__": main()
