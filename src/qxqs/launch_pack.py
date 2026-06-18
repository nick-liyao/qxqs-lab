from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from .backtest import run_backtest
from .charts import render_signal_chart
from .data_sources.yahoo import fetch_yahoo_daily
from .explain import social_caption, zh_signal_text
from .signals import add_qxqs_signals, latest_signal_summary


DEFAULT_LAUNCH_SYMBOLS = ["QQQ", "NVDA", "TSLA", "SPY", "MSTR", "GDX", "KWEB"]
DEFAULT_DISCOVERY_UNIVERSE = [
    "NVDA",
    "AMD",
    "AVGO",
    "TSM",
    "ASML",
    "ARM",
    "MU",
    "MRVL",
    "PLTR",
    "AI",
    "SMCI",
    "SOXX",
    "SOXL",
    "QQQ",
    "SPY",
    "MSTR",
    "COIN",
    "MARA",
    "HOOD",
    "TSLA",
    "GOOGL",
    "META",
    "MSFT",
    "AMZN",
    "GDX",
    "KWEB",
]


@dataclass(frozen=True)
class LaunchAsset:
    symbol: str
    chart_path: str
    caption_path: str
    summary: dict[str, object]
    signal_title: str
    signal_tone: str


@dataclass(frozen=True)
class LaunchFailure:
    symbol: str
    error: str


@dataclass(frozen=True)
class LaunchCandidate:
    symbol: str
    score: float
    signal: str
    signal_title: str
    signal_tone: str
    last_signal_date: str | None
    close: float
    strategy_return_pct: float
    buy_hold_return_pct: float
    max_drawdown_pct: float


def discover_launch_candidates(
    universe: list[str] | None = None,
    *,
    range_: str = "2y",
    limit: int = 7,
) -> tuple[list[LaunchCandidate], list[LaunchFailure]]:
    candidates: list[LaunchCandidate] = []
    failures: list[LaunchFailure] = []
    today = date.today()
    signal_rank = {"BBB": 90, "B": 82, "HOT": 78, "SSS": 76, "SS": 68, "S": 60, "none": 0}

    for symbol in universe or DEFAULT_DISCOVERY_UNIVERSE:
        clean = symbol.strip().upper()
        if not clean:
            continue
        try:
            raw = fetch_yahoo_daily(clean, range_=range_)
            signals = add_qxqs_signals(raw)
            summary = latest_signal_summary(signals)
            backtest = run_backtest(raw, symbol=clean)
            signal = str(summary.get("signal") or "none")
            signal_zh = zh_signal_text(signal)
            last_signal_date = summary.get("last_signal_date")
            recency_score = _recency_score(str(last_signal_date), today) if last_signal_date else 0
            edge_score = max(-15, min(20, backtest.total_return_pct - backtest.buy_hold_return_pct))
            drawdown_penalty = min(15, abs(backtest.max_drawdown_pct) / 4)
            score = signal_rank.get(signal, 0) + recency_score + edge_score - drawdown_penalty
            candidates.append(
                LaunchCandidate(
                    symbol=clean,
                    score=round(score, 2),
                    signal=signal,
                    signal_title=signal_zh["title"],
                    signal_tone=signal_zh["tone"],
                    last_signal_date=str(last_signal_date) if last_signal_date else None,
                    close=float(summary["close"]),
                    strategy_return_pct=backtest.total_return_pct,
                    buy_hold_return_pct=backtest.buy_hold_return_pct,
                    max_drawdown_pct=backtest.max_drawdown_pct,
                )
            )
        except Exception as exc:  # pragma: no cover - exact vendor/network errors vary.
            failures.append(LaunchFailure(symbol=clean, error=str(exc)))

    candidates.sort(key=lambda item: item.score, reverse=True)
    return candidates[:limit], failures


def build_launch_pack(
    symbols: list[str] | None = None,
    *,
    output_dir: str | Path = "outputs/launch",
    range_: str = "2y",
) -> list[LaunchAsset]:
    out = Path(output_dir)
    charts_dir = out / "charts"
    captions_dir = out / "captions"
    charts_dir.mkdir(parents=True, exist_ok=True)
    captions_dir.mkdir(parents=True, exist_ok=True)

    assets: list[LaunchAsset] = []
    failures: list[LaunchFailure] = []
    for symbol in symbols or DEFAULT_LAUNCH_SYMBOLS:
        clean = symbol.strip().upper()
        if not clean:
            continue
        try:
            raw = fetch_yahoo_daily(clean, range_=range_)
            signals = add_qxqs_signals(raw)
            summary = latest_signal_summary(signals)
            backtest = run_backtest(raw, symbol=clean)
            signal_zh = zh_signal_text(summary["signal"])

            chart_path = charts_dir / f"{clean.lower()}-xhs.png"
            render_signal_chart(signals, symbol=clean, output=chart_path, profile="xhs")

            caption = social_caption(clean, summary, backtest)
            caption_path = captions_dir / f"{clean.lower()}.md"
            caption_path.write_text(caption, encoding="utf-8")

            assets.append(
                LaunchAsset(
                    symbol=clean,
                    chart_path=str(chart_path),
                    caption_path=str(caption_path),
                    summary={
                        **summary,
                        "backtest": backtest.to_dict(),
                    },
                    signal_title=signal_zh["title"],
                    signal_tone=signal_zh["tone"],
                )
            )
        except Exception as exc:  # pragma: no cover - exact vendor/network errors vary.
            failures.append(LaunchFailure(symbol=clean, error=str(exc)))

    manifest = {
        "symbols": [asset.symbol for asset in assets],
        "assets": [asdict(asset) for asset in assets],
        "failures": [asdict(failure) for failure in failures],
        "cta": "GitHub 搜 qxqs-lab，觉得有用可以点 Star。",
        "disclaimer": "不是荐股，不是买卖建议，只展示一个开源低频复盘工具。",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "README.md").write_text(_build_launch_readme(assets, failures), encoding="utf-8")
    return assets


def write_discovery_report(
    candidates: list[LaunchCandidate],
    failures: list[LaunchFailure],
    *,
    output_dir: str | Path = "outputs/launch",
) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    lines = [
        "# QXQS Lab Discovery Report",
        "",
        "| Rank | Symbol | Score | Signal | Last signal | Strategy | Buy-hold | Max DD |",
        "|---:|---|---:|---|---|---:|---:|---:|",
    ]
    for index, candidate in enumerate(candidates, start=1):
        lines.append(
            f"| {index} | {candidate.symbol} | {candidate.score} | "
            f"{candidate.signal_title} / {candidate.signal_tone} | "
            f"{candidate.last_signal_date or '-'} | {candidate.strategy_return_pct}% | "
            f"{candidate.buy_hold_return_pct}% | {candidate.max_drawdown_pct}% |"
        )
    if failures:
        lines.extend(["", "## Failed Symbols", ""])
        for failure in failures:
            lines.append(f"- `{failure.symbol}`: {failure.error}")
    path = out / "discovery.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    (out / "discovery.json").write_text(
        json.dumps(
            {
                "candidates": [asdict(candidate) for candidate in candidates],
                "failures": [asdict(failure) for failure in failures],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def _build_launch_readme(assets: list[LaunchAsset], failures: list[LaunchFailure] | None = None) -> str:
    lines = [
        "# QXQS Lab Launch Pack",
        "",
        "Generated mobile-first chart and caption assets for the first content push.",
        "",
        "| Symbol | Signal | Tone | Chart | Caption |",
        "|---|---|---|---|---|",
    ]
    for asset in assets:
        lines.append(
            f"| {asset.symbol} | {asset.signal_title} | {asset.signal_tone} | "
            f"`{asset.chart_path}` | `{asset.caption_path}` |"
        )
    if failures:
        lines.extend(["", "## Failed Symbols", ""])
        for failure in failures:
            lines.append(f"- `{failure.symbol}`: {failure.error}")
    lines.extend(
        [
            "",
            "CTA:",
            "",
            "```text",
            "GitHub 搜 qxqs-lab，觉得有用可以点 Star。",
            "```",
            "",
            "Boundary: research only, not financial advice.",
        ]
    )
    return "\n".join(lines)


def _recency_score(value: str, today: date) -> float:
    try:
        days = max(0, (today - date.fromisoformat(value[:10])).days)
    except ValueError:
        return 0
    return max(0, 30 - days)
