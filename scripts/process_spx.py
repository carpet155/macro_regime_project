"""Load raw S&P 500 prices, standardize to business days via macro_regime.clean, save processed CSV."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from macro_regime.clean import (
    coerce_numeric,
    compute_returns,
    standardize_dates,
    summarize_frame,
    validate_monotonic_dates,
    validate_no_duplicate_keys,
    validate_required_columns,
)

ROOT = Path(__file__).resolve().parent.parent
RAW_SPX_PATH = ROOT / "data" / "raw" / "SP500.csv"
PROCESSED_SPX_PATH = ROOT / "data" / "processed" / "features" / "spx_processed.csv"


def _rename_to_canonical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize headers to ``date`` and ``price`` (e.g. ``close`` → ``price``)."""
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    rename: dict[str, str] = {}
    for c in out.columns:
        u = c.upper().replace(" ", "_")
        if u == "DATE":
            rename[c] = "date"
        elif u in ("PRICE", "CLOSE", "ADJ_CLOSE", "SP500", "GSPC"):
            rename[c] = "price"
    return out.rename(columns=rename)


def load_raw_spx() -> pd.DataFrame:
    """Read ``SP500.csv`` with canonical ``date`` / ``price`` columns."""
    return _rename_to_canonical_columns(pd.read_csv(RAW_SPX_PATH))


def process_spx(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce prices, business-day calendar, simple returns; NaN price forces NaN return."""
    df = coerce_numeric(df, ["price"])
    df = standardize_dates(df, date_col="date", freq="B")
    validate_monotonic_dates(df)
    validate_no_duplicate_keys(df, ["date"])
    df = df.copy()
    df["return"] = compute_returns(df["price"], method="simple")
    df.loc[df["price"].isna(), "return"] = np.nan
    return df


def save_processed_spx(df: pd.DataFrame) -> Path:
    """Write ``data/processed/features/spx_processed.csv`` with ``date``, ``price``, ``return``."""
    PROCESSED_SPX_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = df[["date", "price", "return"]].copy()
    out.to_csv(PROCESSED_SPX_PATH, index=False)
    return PROCESSED_SPX_PATH


def main() -> None:
    raw = load_raw_spx()
    validate_required_columns(raw, ["date", "price"])
    print(summarize_frame(raw, "raw spx"))

    processed = process_spx(raw)
    print(summarize_frame(processed, "processed spx"))

    path = save_processed_spx(processed)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
