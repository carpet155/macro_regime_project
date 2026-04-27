"""Load raw CPI, align to business days via macro_regime.clean, save processed CSV."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from macro_regime.clean import (
    align_inflation_to_daily,
    coerce_numeric,
    summarize_frame,
    validate_monotonic_dates,
    validate_no_duplicate_keys,
    validate_required_columns,
)

ROOT = Path(__file__).resolve().parent.parent
RAW_INFLATION_PATH = ROOT / "data" / "raw" / "CPIAUCSL.csv"
PROCESSED_INFLATION_PATH = (
    ROOT / "data" / "processed" / "features" / "inflation_processed.csv"
)


def _rename_to_canonical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map FRED-style (DATE, CPIAUCSL) or equivalent headers to ``date`` and ``value``."""
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    rename: dict[str, str] = {}
    for c in out.columns:
        u = c.upper()
        if u == "DATE":
            rename[c] = "date"
        elif u in ("CPIAUCSL", "VALUE"):
            rename[c] = "value"
    return out.rename(columns=rename)


def load_raw_inflation() -> pd.DataFrame:
    """Read ``CPIAUCSL.csv`` and return a frame with ``date`` and ``value`` columns."""
    return _rename_to_canonical_columns(pd.read_csv(RAW_INFLATION_PATH))


def process_inflation(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce values, align to business-day frequency and forward-fill (via ``clean``)."""
    df = coerce_numeric(df, ["value"])
    df = align_inflation_to_daily(df, date_col="date", value_col="value")
    validate_monotonic_dates(df)
    validate_no_duplicate_keys(df, ["date"])
    return df


def save_processed_inflation(df: pd.DataFrame) -> Path:
    """Write processed inflation to ``data/processed/features/inflation_processed.csv``."""
    PROCESSED_INFLATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_INFLATION_PATH, index=False)
    return PROCESSED_INFLATION_PATH


def main() -> None:
    raw = load_raw_inflation()
    validate_required_columns(raw, ["date", "value"])
    print(summarize_frame(raw, "raw inflation"))

    processed = process_inflation(raw)
    print(summarize_frame(processed, "processed inflation"))

    path = save_processed_inflation(processed)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
