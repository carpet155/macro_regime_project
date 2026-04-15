"""Load raw sector panel, standardize dates and returns via macro_regime.clean, save processed CSVs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from macro_regime.clean import (
    add_grouped_returns,
    coerce_numeric,
    fill_sector_return_gaps,
    standardize_panel_dates,
    summarize_frame,
    validate_monotonic_dates,
    validate_no_duplicate_keys,
    validate_required_columns,
)

ROOT = Path(__file__).resolve().parent.parent
RAW_SECTORS_PATH = ROOT / "data" / "raw" / "sector_prices.csv"
PROCESSED_SECTORS_PATH = ROOT / "data" / "processed" / "sectors_processed.csv"
PROCESSED_RETURNS_PATH = ROOT / "data" / "processed" / "sector_returns_processed.csv"


def _rename_to_canonical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize headers to ``date``, ``ticker``, optional ``name``, and ``price``."""
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    rename: dict[str, str] = {}
    for c in out.columns:
        u = c.upper().replace(" ", "_")
        if u == "DATE":
            rename[c] = "date"
        elif u in ("TICKER", "SYMBOL"):
            rename[c] = "ticker"
        elif u == "NAME":
            rename[c] = "name"
        elif u in ("PRICE", "CLOSE", "ADJ_CLOSE"):
            rename[c] = "price"
    return out.rename(columns=rename)


def load_raw_sectors() -> pd.DataFrame:
    """Read ``sector_prices.csv`` with canonical column names."""
    return _rename_to_canonical_columns(pd.read_csv(RAW_SECTORS_PATH))


def _validate_monotonic_dates_by_ticker(df: pd.DataFrame, ticker_col: str = "ticker") -> None:
    """Ensure ``date`` is non-decreasing within each ``ticker_col`` group."""
    for _, g in df.groupby(ticker_col, sort=False):
        validate_monotonic_dates(g.reset_index(drop=True), date_col="date")


def process_sectors(df: pd.DataFrame) -> pd.DataFrame:
    """Business-day panel by ticker, simple returns, then within-ticker return gap fill."""
    df = coerce_numeric(df, ["price"])
    df = standardize_panel_dates(df, group_col="ticker", date_col="date", freq="B")
    validate_no_duplicate_keys(df, ["ticker", "date"])
    _validate_monotonic_dates_by_ticker(df)
    df = add_grouped_returns(
        df,
        value_col="price",
        group_col="ticker",
        date_col="date",
        return_col="return",
        method="simple",
    )
    df = fill_sector_return_gaps(df, ticker_col="ticker", return_col="return", date_col="date")
    
    df.loc[df["price"].isna(), "return"] = pd.NA

    return df


def save_processed_sectors(df: pd.DataFrame) -> tuple[Path, Path]:
    """Write ``sectors_processed.csv`` and a slim ``sector_returns_processed.csv``."""
    PROCESSED_SECTORS_PATH.parent.mkdir(parents=True, exist_ok=True)

    base_cols = ["date", "ticker", "price", "return"]
    extra = ["name"] if "name" in df.columns else []
    ordered = [c for c in base_cols + extra if c in df.columns]
    df_out = df[ordered].sort_values(["ticker", "date"], kind="mergesort").reset_index(drop=True)
    df_out.to_csv(PROCESSED_SECTORS_PATH, index=False)

    ret_cols = ["date", "ticker", "return"] + (["name"] if "name" in df.columns else [])
    df_ret = df[ret_cols].sort_values(["ticker", "date"], kind="mergesort").reset_index(drop=True)
    df_ret.to_csv(PROCESSED_RETURNS_PATH, index=False)

    return PROCESSED_SECTORS_PATH, PROCESSED_RETURNS_PATH


def main() -> None:
    raw = load_raw_sectors()
    validate_required_columns(raw, ["date", "ticker", "price"])
    print(summarize_frame(raw, "raw sectors"))
    print(f"Tickers: {raw['ticker'].nunique()}")

    processed = process_sectors(raw)
    print(summarize_frame(processed, "processed sectors"))
    print(
        f"Tickers: {processed['ticker'].nunique()}, "
        f"date span {processed['date'].min()} .. {processed['date'].max()}"
    )

    path_main, path_ret = save_processed_sectors(processed)
    print(f"Wrote {path_main}")
    print(f"Wrote {path_ret}")


if __name__ == "__main__":
    main()
