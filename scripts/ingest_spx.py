"""Download S&P 500 index prices from Yahoo Finance and write canonical raw CSV."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf

from macro_regime.config import (
    DATE_COL,
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    PRICE_COL,
    RAW_FILES,
    SPX_TICKER,
)
from macro_regime.io import save_raw_csv


def _close_series(raw: pd.DataFrame) -> pd.Series:
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw.xs("Close", axis=1, level=0)
        return close.squeeze(axis=1)
    return raw["Close"]


def fetch_spx_data() -> pd.DataFrame:
    """Download daily closes for the S&P 500 index and return a two-column DataFrame."""
    kwargs: dict[str, str | bool] = {
        "start": DEFAULT_START_DATE,
        "progress": False,
    }
    if DEFAULT_END_DATE is not None:
        kwargs["end"] = DEFAULT_END_DATE

    raw = yf.download(SPX_TICKER, **kwargs)
    if raw.empty:
        raise ValueError(f"No data for {SPX_TICKER}")

    close = _close_series(raw)
    df = close.reset_index()
    df = df.rename(columns={df.columns[0]: DATE_COL, df.columns[1]: PRICE_COL})
    df[DATE_COL] = pd.to_datetime(df[DATE_COL])
    df = df.dropna().sort_values(DATE_COL, ascending=True).reset_index(drop=True)
    return df[[DATE_COL, PRICE_COL]]


def save_spx_data(df: pd.DataFrame) -> Path:
    """Persist S&P 500 prices to the canonical raw file and return its path."""
    return save_raw_csv(df, RAW_FILES["spx"])


def main() -> None:
    df = fetch_spx_data()
    path = save_spx_data(df)
    print(f"Saved {len(df)} rows to {path}")


if __name__ == "__main__":
    main()
