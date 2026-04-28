"""Load raw Treasury and Fed Funds series, standardize and merge via macro_regime.clean."""

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
RAW_DGS2_PATH = ROOT / "data" / "raw" / "DGS2.csv"
RAW_DGS10_PATH = ROOT / "data" / "raw" / "DGS10.csv"
RAW_FEDFUNDS_PATH = ROOT / "data" / "raw" / "FEDFUNDS.csv"
PROCESSED_TREASURY_PATH = (
    ROOT / "data" / "processed" / "features" / "treasury_processed.csv"
)


def _rename_to_canonical_columns(df: pd.DataFrame, value_name: str) -> pd.DataFrame:
    """Map raw headers to ``date`` and a single series column ``value_name`` (e.g. ``dgs2``)."""
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    rename: dict[str, str] = {}
    value_cols: list[str] = []
    for c in out.columns:
        u = c.upper().replace(" ", "_")
        if u == "DATE":
            rename[c] = "date"
        else:
            value_cols.append(c)
    if len(value_cols) != 1:
        raise ValueError(
            f"Expected one value column plus date; got value columns {value_cols!r} for {value_name!r}"
        )
    rename[value_cols[0]] = value_name
    return out.rename(columns=rename)


def load_raw_dgs2() -> pd.DataFrame:
    return _rename_to_canonical_columns(pd.read_csv(RAW_DGS2_PATH), "dgs2")


def load_raw_dgs10() -> pd.DataFrame:
    return _rename_to_canonical_columns(pd.read_csv(RAW_DGS10_PATH), "dgs10")


def load_raw_fedfunds() -> pd.DataFrame:
    return _rename_to_canonical_columns(pd.read_csv(RAW_FEDFUNDS_PATH), "fedfunds")


def process_one_series(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Coerce numeric, business-day ``standardize_dates``, then monotonic / key checks."""
    validate_required_columns(df, ["date", value_col])
    df = coerce_numeric(df, [value_col])
    df = standardize_dates(df, date_col="date", freq="B")
    validate_monotonic_dates(df)
    validate_no_duplicate_keys(df, ["date"])
    return df


def merge_treasury_series(
    dgs2: pd.DataFrame,
    dgs10: pd.DataFrame,
    fedfunds: pd.DataFrame,
) -> pd.DataFrame:
    """Outer-merge standardized series on ``date`` and sort."""
    out = dgs2.merge(dgs10, on="date", how="outer").merge(fedfunds, on="date", how="outer")
    return out.sort_values("date", kind="mergesort").reset_index(drop=True)


def save_processed_treasury(df: pd.DataFrame) -> Path:
    """Persist merged treasury frame as ``treasury_processed.csv``."""
    PROCESSED_TREASURY_PATH.parent.mkdir(parents=True, exist_ok=True)
    cols = ["date", "dgs2", "dgs10", "fedfunds"]
    validate_required_columns(df, cols)
    df[cols].to_csv(PROCESSED_TREASURY_PATH, index=False)
    return PROCESSED_TREASURY_PATH


def main() -> None:
    raw_dgs2 = load_raw_dgs2()
    raw_dgs10 = load_raw_dgs10()
    raw_ff = load_raw_fedfunds()

    validate_required_columns(raw_dgs2, ["date", "dgs2"])
    validate_required_columns(raw_dgs10, ["date", "dgs10"])
    validate_required_columns(raw_ff, ["date", "fedfunds"])

    print(summarize_frame(raw_dgs2, "raw DGS2"))
    print(summarize_frame(raw_dgs10, "raw DGS10"))
    print(summarize_frame(raw_ff, "raw FEDFUNDS"))

    s2 = process_one_series(raw_dgs2, "dgs2")
    s10 = process_one_series(raw_dgs10, "dgs10")
    sff = process_one_series(raw_ff, "fedfunds")

    merged = merge_treasury_series(s2, s10, sff)
    merged = fill_macro_series(merged, ["dgs2", "dgs10", "fedfunds"])

    validate_monotonic_dates(merged)
    validate_no_duplicate_keys(merged, ["date"])
    print(summarize_frame(merged, "processed treasury"))

    path = save_processed_treasury(merged)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
