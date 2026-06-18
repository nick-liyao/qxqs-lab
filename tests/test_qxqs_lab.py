from pathlib import Path

from qxqs.backtest import run_backtest
from qxqs.data_sources.csv import load_csv
from qxqs.screener import score_dataframe
from qxqs.signals import add_qxqs_signals, latest_signal_summary


SAMPLE = Path(__file__).resolve().parents[1] / "examples" / "sample_data" / "sample_ohlcv.csv"


def test_signals_include_core_columns():
    df = add_qxqs_signals(load_csv(SAMPLE))
    for column in ["WRV", "DKXV", "FAST2", "SLOW2", "B", "BBB", "HOT", "SSS", "signal"]:
        assert column in df.columns
    summary = latest_signal_summary(df)
    assert summary["signal"] in {"B", "BBB", "HOT", "SSS", "SS", "S", "none"}


def test_backtest_returns_summary():
    summary = run_backtest(load_csv(SAMPLE), symbol="SAMPLE")
    assert summary.symbol == "SAMPLE"
    assert isinstance(summary.total_return_pct, float)
    assert summary.trades >= 0


def test_low_repair_score_shape():
    candidate = score_dataframe("SAMPLE", load_csv(SAMPLE))
    assert candidate is not None
    assert candidate.grade in {"A", "B", "C", "watch"}
    assert 0 <= candidate.score <= 100
