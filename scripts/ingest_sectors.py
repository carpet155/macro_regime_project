"""Download sector ETF prices from Yahoo Finance and write canonical raw CSV."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf

from macro_regime.config import (
    DATE_COL,
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    NAME_COL,
    PRICE_COL,
    RAW_FILES,
    SECTOR_TICKERS,
    TICKER_COL,
)
from macro_regime.io import save_raw_csv


def _close_series(raw: pd.DataFrame) -> pd.Series:
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw.xs("Close", axis=1, level=0)
        return close.squeeze(axis=1)
    return raw["Close"]


def fetch_sector_prices(ticker: str, name: str) -> pd.DataFrame:
    """Download daily closes for one sector ETF and return a long-format DataFrame."""
    kwargs: dict[str, str | bool] = {
        "start": DEFAULT_START_DATE,
        "progress": False,
    }
    if DEFAULT_END_DATE is not None:
        kwargs["end"] = DEFAULT_END_DATE

    raw = yf.download(ticker, **kwargs)
    if raw.empty:
        raise ValueError(f"No data for {ticker}")

    close = _close_series(raw)
    df = close.reset_index()
    df = df.rename(columns={df.columns[0]: DATE_COL, df.columns[1]: PRICE_COL})
    df[DATE_COL] = pd.to_datetime(df[DATE_COL])
    df[TICKER_COL] = ticker
    df[NAME_COL] = name
    df = df.dropna()
    return df[[DATE_COL, TICKER_COL, NAME_COL, PRICE_COL]]


def fetch_all_sector_prices() -> pd.DataFrame:
    """Fetch all sector ETFs and stack into one sorted DataFrame."""
    frames = [fetch_sector_prices(ticker, name) for ticker, name in SECTOR_TICKERS.items()]
    out = pd.concat(frames, ignore_index=True)
    out = out.sort_values([DATE_COL, TICKER_COL]).reset_index(drop=True)
    return out[[DATE_COL, TICKER_COL, NAME_COL, PRICE_COL]]


def save_sector_data(df: pd.DataFrame) -> Path:
    """Persist sector panel to the canonical raw file and return its path."""
    return save_raw_csv(df, RAW_FILES["sectors"])


def main() -> None:
    df = fetch_all_sector_prices()
    path = save_sector_data(df)
    print(f"Saved {len(df)} rows to {path}")


if __name__ == "__main__":
    main()
