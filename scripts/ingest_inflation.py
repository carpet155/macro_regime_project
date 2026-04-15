"""Download CPI (CPIAUCSL) from FRED and write the canonical raw CSV."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from fredapi import Fred

from macro_regime.config import (
    DATE_COL,
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    INFLATION_SERIES,
    RAW_FILES,
    VALUE_COL,
)
from macro_regime.io import save_raw_csv


def get_fred_client() -> Fred:
    """Return a FRED client using ``FRED_API_KEY`` from the environment."""
    api_key = os.getenv("FRED_API_KEY")
    if api_key is None:
        raise ValueError(
    "FRED_API_KEY not set. Set it via environment variable. "
    "See README for setup instructions."
)
    return Fred(api_key=api_key)


def fetch_inflation_series(fred: Fred) -> pd.DataFrame:
    """Fetch CPIAUCSL from FRED and return a cleaned long-format DataFrame."""
    kwargs: dict[str, str] = {"observation_start": DEFAULT_START_DATE}
    if DEFAULT_END_DATE is not None:
        kwargs["observation_end"] = DEFAULT_END_DATE

    series = fred.get_series(INFLATION_SERIES, **kwargs)
    df = pd.DataFrame({DATE_COL: pd.to_datetime(series.index), VALUE_COL: series.values})
    df = df.dropna().sort_values(DATE_COL, ascending=True).reset_index(drop=True)
    return df


def save_inflation_data(df: pd.DataFrame) -> Path:
    """Persist inflation data to the canonical raw file and return its path."""
    return save_raw_csv(df, RAW_FILES["inflation"])


def main() -> None:
    fred = get_fred_client()
    df = fetch_inflation_series(fred)
    path = save_inflation_data(df)
    print(f"Saved {len(df)} rows to {path}")


if __name__ == "__main__":
    main()
