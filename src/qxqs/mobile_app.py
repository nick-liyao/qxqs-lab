from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st

from .backtest import run_backtest
from .charts import render_signal_chart
from .data_sources.csv import load_csv
from .data_sources.yahoo import fetch_yahoo_daily
from .signals import add_qxqs_signals, latest_signal_summary


def _load_data(symbol: str, uploaded_file, range_: str):
    if uploaded_file is not None:
        with NamedTemporaryFile("wb", suffix=".csv", delete=False) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = Path(tmp.name)
        return load_csv(tmp_path), symbol or "UPLOAD"
    clean_symbol = (symbol or "QQQ").strip().upper()
    return fetch_yahoo_daily(clean_symbol, range_=range_), clean_symbol


def main() -> None:
    st.set_page_config(page_title="QXQS Lab", page_icon="Q", layout="centered")
    st.markdown("""
        <style>
        .block-container { max-width: 520px; padding-top: 1rem; }
        div[data-testid="stMetric"] { background: #f7f7f3; border: 1px solid #e7e3d8; padding: 12px; border-radius: 8px; }
        </style>
        """, unsafe_allow_html=True)
    st.title("QXQS Lab")
    st.caption("Mobile-friendly low-frequency signal chart. Research only, not financial advice.")
    symbol = st.text_input("Symbol", value="QQQ")
    range_ = st.selectbox("Yahoo range", ["6mo", "1y", "2y", "5y"], index=2)
    uploaded = st.file_uploader("Or upload OHLCV CSV", type=["csv"])
    profile = st.segmented_control("Chart format", ["xhs", "wide"], default="xhs")
    if st.button("Generate chart", type="primary", use_container_width=True):
        try:
            raw, resolved_symbol = _load_data(symbol, uploaded, range_)
            signals = add_qxqs_signals(raw)
            summary = latest_signal_summary(signals)
            backtest = run_backtest(raw, symbol=resolved_symbol)
            out = Path("outputs/mobile") / f"{resolved_symbol.lower()}-{profile}.png"
            render_signal_chart(signals, symbol=resolved_symbol, output=out, profile=profile)
            st.image(str(out), use_container_width=True)
            c1, c2 = st.columns(2)
            c1.metric("Latest signal", str(summary["signal"]))
            c2.metric("DKXV", str(summary["DKXV_color"]))
            c1.metric("Close", str(summary["close"]))
            c2.metric("XDDW", f"{summary['FAST2']} / {summary['SLOW2']}")
            st.markdown(f"**Read:** {summary['signal_reason']}")
            st.markdown(f"**Backtest:** {backtest.total_return_pct}% strategy vs {backtest.buy_hold_return_pct}% buy-hold, max drawdown {backtest.max_drawdown_pct}%.")
            st.download_button("Download screenshot", data=out.read_bytes(), file_name=out.name, mime="image/png", use_container_width=True)
            st.link_button("Open source on GitHub", "https://github.com/nick-liyao/qxqs-lab", use_container_width=True)
        except Exception as exc:
            st.error(f"Could not generate chart: {exc}")


if __name__ == "__main__":
    main()
