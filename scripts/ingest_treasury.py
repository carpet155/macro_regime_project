"""Download treasury and fed funds series from FRED and write canonical raw CSVs."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from fredapi import Fred

from macro_regime.config import (
    DATE_COL,
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    RAW_FILES,
    TREASURY_SERIES,
    VALUE_COL,
)
from macro_regime.io import save_raw_csv

RAW_FILES_KEY_BY_SERIES: dict[str, str] = {
    "DGS2": "treasury_2y",
    "DGS10": "treasury_10y",
    "FEDFUNDS": "fed_funds",
}


def get_fred_client() -> Fred:
    """Return a FRED client using ``FRED_API_KEY`` from the environment."""
    api_key = os.getenv("FRED_API_KEY")
    if api_key is None:
        raise ValueError(
            "FRED_API_KEY not set. Set it via environment variable. "
            "See README for setup instructions."
        )
    return Fred(api_key=api_key)


def fetch_fred_series(fred: Fred, series_id: str) -> pd.DataFrame:
    """Fetch one FRED series and return a cleaned long-format DataFrame."""
    kwargs: dict[str, str] = {"observation_start": DEFAULT_START_DATE}
    if DEFAULT_END_DATE is not None:
        kwargs["observation_end"] = DEFAULT_END_DATE

    series = fred.get_series(series_id, **kwargs)
    df = pd.DataFrame({DATE_COL: pd.to_datetime(series.index), VALUE_COL: series.values})
    df = df.dropna().sort_values(DATE_COL, ascending=True).reset_index(drop=True)
    return df


def save_treasury_series(df: pd.DataFrame, filename: str) -> Path:
    """Write one treasury-related series to raw data and return its path."""
    return save_raw_csv(df, filename)


def fetch_all_treasury_data(fred: Fred) -> dict[str, pd.DataFrame]:
    """Fetch all series listed in ``TREASURY_SERIES``."""
    return {series_id: fetch_fred_series(fred, series_id) for series_id in TREASURY_SERIES}


def save_all_treasury_data(data: dict[str, pd.DataFrame]) -> dict[str, Path]:
    """Save each DataFrame to its canonical raw file; keys are FRED series IDs."""
    paths: dict[str, Path] = {}
    for series_id, df in data.items():
        raw_key = RAW_FILES_KEY_BY_SERIES[series_id]
        paths[series_id] = save_treasury_series(df, RAW_FILES[raw_key])
    return paths


def main() -> None:
    fred = get_fred_client()
    data = fetch_all_treasury_data(fred)
    paths = save_all_treasury_data(data)
    for series_id in TREASURY_SERIES:
        df = data[series_id]
        path = paths[series_id]
        print(f"Saved {len(df)} rows for {series_id} to {path}")


if __name__ == "__main__":
    main()
