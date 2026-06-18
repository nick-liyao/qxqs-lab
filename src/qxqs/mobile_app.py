from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st

from .backtest import run_backtest
from .charts import render_signal_chart
from .data_sources.csv import load_csv
from .data_sources.yahoo import fetch_yahoo_daily
from .explain import social_caption, zh_signal_text
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
    st.caption("手机端低频信号图。仅用于研究复盘，不构成投资建议。")
    presets = ["QQQ", "NVDA", "TSLA", "SPY", "MSTR", "AAPL", "MSFT", "GDX", "KWEB"]
    preset = st.selectbox("热门标的", presets, index=0)
    symbol = st.text_input("Symbol", value=preset)
    range_ = st.selectbox("数据区间", ["6mo", "1y", "2y", "5y"], index=2)
    uploaded = st.file_uploader("或上传 OHLCV CSV", type=["csv"])
    profile = st.segmented_control("截图格式", ["xhs", "wide"], default="xhs")
    if st.button("生成信号图", type="primary", use_container_width=True):
        try:
            raw, resolved_symbol = _load_data(symbol, uploaded, range_)
            signals = add_qxqs_signals(raw)
            summary = latest_signal_summary(signals)
            backtest = run_backtest(raw, symbol=resolved_symbol)
            out = Path("outputs/mobile") / f"{resolved_symbol.lower()}-{profile}.png"
            render_signal_chart(signals, symbol=resolved_symbol, output=out, profile=profile)
            signal_zh = zh_signal_text(summary["signal"])
            caption = social_caption(resolved_symbol, summary, backtest)
            st.image(str(out), use_container_width=True)
            c1, c2 = st.columns(2)
            c1.metric("最新信号", f"{summary['signal']} / {signal_zh['title']}")
            c2.metric("DKXV", str(summary["DKXV_color"]))
            c1.metric("收盘价", str(summary["close"]))
            c2.metric("XDDW", f"{summary['FAST2']} / {summary['SLOW2']}")
            st.markdown(f"**中文解读：** {signal_zh['explain']}")
            st.markdown(f"**复盘动作：** {signal_zh['action']}")
            st.markdown(f"**回测摘要：** 策略 {backtest.total_return_pct}% vs 买入持有 {backtest.buy_hold_return_pct}%，最大回撤 {backtest.max_drawdown_pct}%。")
            st.text_area("小红书/抖音文案", caption, height=220)
            st.download_button("下载截图", data=out.read_bytes(), file_name=out.name, mime="image/png", use_container_width=True)
            st.link_button("GitHub 开源项目", "https://github.com/nick-liyao/qxqs-lab", use_container_width=True)
        except Exception as exc:
            st.error(f"生成失败：{exc}")


if __name__ == "__main__":
    main()
