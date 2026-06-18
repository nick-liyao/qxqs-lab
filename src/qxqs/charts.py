from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

UP_SIGNALS = {"B", "BBB"}
DOWN_SIGNALS = {"S", "SS", "HOT", "SSS"}


def render_signal_chart(df: pd.DataFrame, *, symbol: str, output: str | Path, profile: str = "wide") -> Path:
    output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    plot_df = df.tail(180).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(8, 10) if profile == "xhs" else (12, 7))
    fig.patch.set_facecolor("#f7f7f3"); ax.set_facecolor("#f7f7f3")
    for i, row in plot_df.iterrows():
        color = "#d94f45" if row["close"] >= row["open"] else "#2f9e72"
        ax.vlines(i, row["low"], row["high"], color=color, linewidth=1)
        low, high = min(row["open"], row["close"]), max(row["open"], row["close"])
        ax.add_patch(plt.Rectangle((i - 0.32, low), 0.64, max(high - low, 0.01), color=color, alpha=0.82))
    x = list(range(len(plot_df)))
    ax.plot(x, plot_df["DKXV"], color="#111111", linewidth=2.5, alpha=0.45, label="DKXV")
    ax.plot(x, plot_df["WRV"], color="#4b6cb7", linewidth=1.2, alpha=0.8, label="WRV")
    for i, row in plot_df.iterrows():
        label = row["signal"]
        if label in UP_SIGNALS:
            ax.scatter(i, row["low"] * 0.985, marker="^", color="#1f7a4d", s=90, zorder=5); ax.text(i, row["low"] * 0.975, label, color="#1f7a4d", fontsize=8, ha="center", va="top")
        elif label in DOWN_SIGNALS:
            ax.scatter(i, row["high"] * 1.015, marker="v", color="#b7352d", s=90, zorder=5); ax.text(i, row["high"] * 1.025, label, color="#b7352d", fontsize=8, ha="center", va="bottom")
    latest = plot_df.iloc[-1]
    ax.set_title(f"{symbol} QXQS Lab | {latest['DKXV_color']} DKXV | {latest['signal'] or 'no signal'}", loc="left", fontsize=15, weight="bold")
    ax.grid(True, alpha=0.18); ax.legend(loc="upper left", frameon=False); ax.spines[["top", "right"]].set_visible(False)
    ax.text(0.01, 0.02, "Research only. Not financial advice.", transform=ax.transAxes, fontsize=9, alpha=0.65)
    fig.tight_layout(); fig.savefig(output, dpi=160); plt.close(fig)
    return output
