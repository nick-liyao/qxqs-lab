# QXQS Lab

Local-first low-frequency quant toolkit for red/green QXQS trend lines, tiered B/BBB/S/SS/HOT/SSS signals, low-repair screening, backtests, and Markdown reports.

No broker keys required. No live trading by default. Research software only.

## Quick Start

```bash
git clone https://github.com/nick-liyao/qxqs-lab.git
cd qxqs-lab
python -m venv .venv
source .venv/bin/activate
pip install -e .
qxqs demo
```

## Commands

```bash
qxqs demo
qxqs chart examples/sample_data/sample_ohlcv.csv --symbol SAMPLE
qxqs signals examples/sample_data/sample_ohlcv.csv --symbol SAMPLE
qxqs backtest examples/sample_data/sample_ohlcv.csv --symbol SAMPLE
qxqs report examples/sample_data/sample_ohlcv.csv --symbol SAMPLE
qxqs screen --symbols QQQ SPY NVDA GDX KWEB
qxqs export-futu
```

## Futu/Moomoo Indicator Pack

```bash
qxqs export-futu
```

This creates:

- `outputs/futu-pack/QXQS_Lab_Main_Trend.txt`
- `outputs/futu-pack/QXQS_Lab_XDDW_Subchart.txt`
- `outputs/futu-pack.zip`

This is not an official Futu/Moomoo plugin or a one-click installer. It is a copy-paste indicator package for manual custom-indicator setup.

See [Futu/Moomoo Indicator Import](docs/futu_moomoo_import.md).

## Signal Labels

| Label | Meaning | Default interpretation |
|---|---|---|
| BBB | Panic low | Strong low-position opportunity context |
| B | Pullback build | Trend-repair watch context |
| HOT | Overheat | Stretched high-position risk |
| SSS | Strong break risk | Structural risk context |
| SS | Medium risk | Risk-reduction context |
| S | Light risk | Early warning context |

Signals are labels for research and review. They are not buy/sell instructions.

## Why QXQS Lab

Most chart indicators are hard to reproduce, and many trading scripts mix private broker credentials with research logic. QXQS Lab keeps the public version clean:

- CSV and Yahoo daily bars first;
- deterministic indicator and signal logic;
- next-bar backtest to avoid future leakage;
- Markdown and JSON reports;
- Futu/Moomoo-style copy-paste indicator pack;
- no private account data;
- no live trading.

## Roadmap

- Futu/Moomoo copy-paste indicator pack.
- Mobile-friendly 4:5 chart screenshots.
- Better chart themes for Xiaohongshu, Douyin, YouTube Shorts, and X.
- Watchlist presets.
- Streamlit UI.
- Optional webhook reports.
- AI brief generator and MCP server.

## Disclaimer

This project is for research and education only. It is not financial advice, investment advice, a trading recommendation, or an automated trading system. Backtests are historical simulations and do not predict future performance.
