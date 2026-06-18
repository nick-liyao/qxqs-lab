from __future__ import annotations

from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {"date", "open", "high", "low", "close"}


def load_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    if "time_key" in df.columns and "date" not in df.columns:
        df["date"] = df["time_key"]
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    df["date"] = pd.to_datetime(df["date"])
    if "volume" not in df.columns:
        df["volume"] = 0
    return df.sort_values("date").reset_index(drop=True)
