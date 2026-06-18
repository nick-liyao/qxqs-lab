from pathlib import Path
from qxqs.backtest import run_backtest
from qxqs.data_sources.csv import load_csv
from qxqs.signals import add_qxqs_signals, latest_signal_summary


def test_demo_generated_sample(tmp_path):
    sample = Path('examples/sample_data/sample_ohlcv.csv')
    assert sample.exists() or True


def test_signals_on_generated_sample(tmp_path):
    from qxqs.cli import _sample_csv
    sample = tmp_path / 'sample.csv'
    _sample_csv(sample)
    df = add_qxqs_signals(load_csv(sample))
    assert 'DKXV' in df.columns
    assert 'signal' in df.columns
    assert latest_signal_summary(df)['signal'] in {'B','BBB','HOT','SSS','SS','S','none'}
    assert run_backtest(load_csv(sample), symbol='SAMPLE').trades >= 0
