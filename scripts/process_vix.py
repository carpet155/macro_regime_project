"""Load raw VIX, standardize business days and forward-fill via macro_regime.clean, save processed CSV."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from macro_regime.clean import (
    coerce_numeric,
    fill_macro_series,
    standardize_dates,
    summarize_frame,
    validate_monotonic_dates,
    validate_no_duplicate_keys,
    validate_required_columns,
)

ROOT = Path(__file__).resolve().parent.parent
RAW_VIX_PATH = ROOT / "data" / "raw" / "VIXCLS.csv"
PROCESSED_VIX_PATH = ROOT / "data" / "processed" / "features" / "vix_processed.csv"


def _rename_to_canonical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map FRED-style or ``date``/``value`` headers to ``date`` and ``vix``."""
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    rename: dict[str, str] = {}
    for c in out.columns:
        u = c.upper().replace(" ", "_")
        if u == "DATE":
            rename[c] = "date"
        elif u in ("VALUE", "VIXCLS", "VIX"):
            rename[c] = "vix"
    return out.rename(columns=rename)


def load_raw_vix() -> pd.DataFrame:
    return _rename_to_canonical_columns(pd.read_csv(RAW_VIX_PATH))


def process_vix(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce, business-day calendar, validate keys, forward-fill ``vix``, validate again."""
    df = coerce_numeric(df, ["vix"])
    df = standardize_dates(df, date_col="date", freq="B")
    validate_monotonic_dates(df)
    validate_no_duplicate_keys(df, ["date"])
    df = fill_macro_series(df, ["vix"])
    validate_monotonic_dates(df)
    validate_no_duplicate_keys(df, ["date"])
    return df


def save_processed_vix(df: pd.DataFrame) -> Path:
    PROCESSED_VIX_PATH.parent.mkdir(parents=True, exist_ok=True)
    cols = ["date", "vix"]
    validate_required_columns(df, cols)
    df[cols].to_csv(PROCESSED_VIX_PATH, index=False)
    return PROCESSED_VIX_PATH


def main() -> None:
    raw = load_raw_vix()
    validate_required_columns(raw, ["date", "vix"])
    print(summarize_frame(raw, "raw vix"))

    processed = process_vix(raw)
    print(summarize_frame(processed, "processed vix"))

    path = save_processed_vix(processed)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
