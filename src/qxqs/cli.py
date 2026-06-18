from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

from .backtest import run_backtest
from .charts import render_signal_chart
from .data_sources.csv import load_csv
from .integrations.futu import export_futu_pack
from .launch_pack import DEFAULT_LAUNCH_SYMBOLS, build_launch_pack, discover_launch_candidates, write_discovery_report
from .reports import backtest_markdown, write_json, write_screener_report, write_signal_report
from .screener import screen_symbols
from .signals import add_qxqs_signals, latest_signal_summary


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SAMPLE = ROOT / "examples" / "sample_data" / "sample_ohlcv.csv"
DEFAULT_SYMBOLS = ["QQQ", "SPY", "NVDA", "GDX", "KWEB"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qxqs")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("demo", help="Run the built-in sample workflow.")

    chart = sub.add_parser("chart", help="Render a QXQS signal chart from CSV.")
    chart.add_argument("csv")
    chart.add_argument("--symbol", default="SAMPLE")
    chart.add_argument("--profile", choices=["wide", "xhs"], default="wide")
    chart.add_argument("--output", default="outputs/charts/qxqs-demo.png")

    signals = sub.add_parser("signals", help="Print the latest tiered signal summary from CSV.")
    signals.add_argument("csv")
    signals.add_argument("--symbol", default="SAMPLE")
    signals.add_argument("--output", default="outputs/reports/signals.csv")

    screen = sub.add_parser("screen", help="Screen low-repair candidates from Yahoo daily bars.")
    screen.add_argument("--symbols", nargs="*", default=DEFAULT_SYMBOLS)
    screen.add_argument("--range", default="2y")
    screen.add_argument("--top", type=int, default=10)
    screen.add_argument("--output", default="outputs/reports/low-repair.md")
    screen.add_argument("--json", default="outputs/reports/low-repair.json")

    backtest = sub.add_parser("backtest", help="Run a simple next-bar research backtest from CSV.")
    backtest.add_argument("csv")
    backtest.add_argument("--symbol", default="SAMPLE")
    backtest.add_argument("--output", default="outputs/reports/backtest.md")
    backtest.add_argument("--json", default="outputs/reports/backtest.json")

    report = sub.add_parser("report", help="Generate a Markdown signal report from CSV.")
    report.add_argument("csv")
    report.add_argument("--symbol", default="SAMPLE")
    report.add_argument("--output", default="outputs/reports/latest.md")
    report.add_argument("--json", default="outputs/reports/latest.json")

    futu = sub.add_parser("export-futu", help="Export Futu/Moomoo copy-paste indicator formulas.")
    futu.add_argument("--output-dir", default="outputs/futu-pack")

    web = sub.add_parser("web", help="Launch the mobile-friendly Streamlit chart app.")
    web.add_argument("--port", default="8501")

    launch = sub.add_parser("launch-pack", help="Generate social launch charts and captions.")
    launch.add_argument("--symbols", nargs="*", default=DEFAULT_LAUNCH_SYMBOLS)
    launch.add_argument("--discover", action="store_true", help="Discover the strongest candidates from a hot AI/ETF universe.")
    launch.add_argument("--limit", type=int, default=7)
    launch.add_argument("--range", default="2y")
    launch.add_argument("--output-dir", default="outputs/launch")
    return parser


def _load_with_signals(path: str | Path) -> pd.DataFrame:
    return add_qxqs_signals(load_csv(path))


def run_demo() -> None:
    d = _load_with_signals(DEFAULT_SAMPLE)
    chart_path = render_signal_chart(d, symbol="SAMPLE", output="outputs/charts/qxqs-demo.png")
    xhs_path = render_signal_chart(d, symbol="SAMPLE", output="outputs/charts/qxqs-demo-xhs.png", profile="xhs")
    signal_report = write_signal_report(d, symbol="SAMPLE", output="outputs/reports/latest.md")
    signals_csv = Path("outputs/reports/signals.csv")
    signals_csv.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(signals_csv, index=False)
    backtest_summary = run_backtest(load_csv(DEFAULT_SAMPLE), symbol="SAMPLE")
    backtest_path = Path("outputs/reports/backtest.md")
    backtest_path.write_text(backtest_markdown(backtest_summary), encoding="utf-8")
    write_json(backtest_summary.to_dict(), "outputs/reports/backtest.json")
    futu_zip = export_futu_pack()
    print(f"Chart: {chart_path}")
    print(f"XHS chart: {xhs_path}")
    print(f"Signal report: {signal_report}")
    print(f"Signals CSV: {signals_csv}")
    print(f"Futu/Moomoo pack: {futu_zip}")
    print(f"Backtest: {backtest_summary.to_dict()}")


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "demo":
        run_demo()
        return

    if args.command == "chart":
        d = _load_with_signals(args.csv)
        print(render_signal_chart(d, symbol=args.symbol, output=args.output, profile=args.profile))
        return

    if args.command == "signals":
        d = _load_with_signals(args.csv)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        d.to_csv(output, index=False)
        print(latest_signal_summary(d))
        print(output)
        return

    if args.command == "screen":
        candidates = screen_symbols(args.symbols, range_=args.range)
        md_path = write_screener_report(candidates, output=args.output, top=args.top)
        json_path = write_json([c.to_dict() for c in candidates], args.json)
        print(md_path)
        print(json_path)
        return

    if args.command == "backtest":
        summary = run_backtest(load_csv(args.csv), symbol=args.symbol)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(backtest_markdown(summary), encoding="utf-8")
        print(output)
        print(write_json(summary.to_dict(), args.json))
        print(summary.to_dict())
        return

    if args.command == "report":
        d = _load_with_signals(args.csv)
        md_path = write_signal_report(d, symbol=args.symbol, output=args.output)
        json_path = write_json(latest_signal_summary(d), args.json)
        print(md_path)
        print(json_path)
        return

    if args.command == "export-futu":
        print(export_futu_pack(args.output_dir))
        return

    if args.command == "web":
        env = {**os.environ, "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false"}
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(Path(__file__).with_name("mobile_app.py")),
                "--server.port",
                str(args.port),
                "--server.headless",
                "true",
            ],
            env=env,
            check=False,
        )
        return

    if args.command == "launch-pack":
        symbols = args.symbols
        if args.discover:
            candidates, failures = discover_launch_candidates(range_=args.range, limit=args.limit)
            write_discovery_report(candidates, failures, output_dir=args.output_dir)
            symbols = [candidate.symbol for candidate in candidates]
            print(f"Discovery selected: {' '.join(symbols)}")
        assets = build_launch_pack(symbols, output_dir=args.output_dir, range_=args.range)
        for asset in assets:
            print(f"{asset.symbol}: {asset.chart_path} | {asset.caption_path} | {asset.signal_title}")


if __name__ == "__main__":
    main()
