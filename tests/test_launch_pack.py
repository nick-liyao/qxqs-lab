from pathlib import Path

from qxqs.data_sources.csv import load_csv
from qxqs.launch_pack import build_launch_pack, discover_launch_candidates


SAMPLE = Path(__file__).resolve().parents[1] / "examples" / "sample_data" / "sample_ohlcv.csv"


def test_build_launch_pack_uses_local_fixture(monkeypatch, tmp_path):
    def fake_fetch_yahoo_daily(symbol, range_="2y"):
        return load_csv(SAMPLE)

    monkeypatch.setattr("qxqs.launch_pack.fetch_yahoo_daily", fake_fetch_yahoo_daily)

    assets = build_launch_pack(["sample"], output_dir=tmp_path / "launch")

    assert len(assets) == 1
    assert assets[0].symbol == "SAMPLE"
    assert Path(assets[0].chart_path).exists()
    assert Path(assets[0].caption_path).exists()
    caption = Path(assets[0].caption_path).read_text(encoding="utf-8")
    assert "\\n" not in caption
    assert caption.count("\n") >= 4
    assert (tmp_path / "launch" / "manifest.json").exists()
    assert (tmp_path / "launch" / "README.md").exists()


def test_discover_launch_candidates_uses_local_fixture(monkeypatch):
    def fake_fetch_yahoo_daily(symbol, range_="2y"):
        return load_csv(SAMPLE)

    monkeypatch.setattr("qxqs.launch_pack.fetch_yahoo_daily", fake_fetch_yahoo_daily)

    candidates, failures = discover_launch_candidates(["aaa", "bbb"], limit=1)

    assert len(candidates) == 1
    assert candidates[0].symbol in {"AAA", "BBB"}
    assert failures == []
