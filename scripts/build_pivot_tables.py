"""
Build pivot tables of sector performance by macroeconomic regime.

Reads the merged master DataFrame from data/processed/, groups sector returns
by each regime column, and writes pivot tables to data/processed/.

Output files produced:
    data/processed/pivot_sector_by_inflation_regime.csv
    data/processed/pivot_sector_by_rate_regime.csv
    data/processed/pivot_sector_by_vix_regime.csv
    data/processed/pivot_sector_by_combined_regime.csv

Each pivot has regimes as rows, sectors as columns, and mean daily return
(in decimal, e.g. 0.0012 = 0.12% per day) as the cell value.

Usage:
    python scripts/build_pivot_tables.py
    python scripts/build_pivot_tables.py --demo    # synthetic data demo

Closes issue #70.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# Column-name candidates. The merge step (#60) may use any of these conventions;
# we try them in order and fall back gracefully.
REGIME_COLUMN_CANDIDATES = {
    "inflation": ["inflation_regime", "infl_regime", "cpi_regime"],
    "rate": ["rate_regime", "interest_rate_regime", "rates_regime"],
    "vix": ["vix_regime", "vix_stress_regime", "stress_regime"],
    "combined": ["combined_regime", "macro_regime", "regime"],
}

# Standard SPDR sector ETF tickers (matches scripts/ingest_sectors.py conventions).
# Any column in the merged frame matching one of these is treated as a sector.
SECTOR_TICKERS = {
    "XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLB", "XLU", "XLRE", "XLC",
}

REPO_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = REPO_ROOT / "data" / "processed"

# Candidate filenames for the merged master frame produced by issue #60.
MERGED_FILE_CANDIDATES = [
    "merged.csv",
    "master.csv",
    "merged_master.csv",
    "all_data.csv",
]


def load_merged_frame(processed_dir: Path = PROCESSED_DIR) -> pd.DataFrame:
    """Load the merged master DataFrame from data/processed/.

    Tries several conventional filenames. Raises FileNotFoundError with a
    helpful message if none are present.
    """
    for name in MERGED_FILE_CANDIDATES:
        path = processed_dir / name
        if path.exists():
            df = pd.read_csv(path, parse_dates=[0], index_col=0)
            return df
    raise FileNotFoundError(
        f"No merged master CSV found in {processed_dir}. Looked for: "
        f"{', '.join(MERGED_FILE_CANDIDATES)}. "
        "Run the pipeline scripts first (issues #58-#60) or pass --demo."
    )


def detect_regime_column(df: pd.DataFrame, regime_key: str) -> str | None:
    """Return the first regime column name present in `df` matching the key.

    `regime_key` is one of 'inflation', 'rate', 'vix', 'combined'. Returns None
    if no candidate column exists — the caller can skip that pivot.
    """
    for candidate in REGIME_COLUMN_CANDIDATES[regime_key]:
        if candidate in df.columns:
            return candidate
    return None


def detect_sector_columns(df: pd.DataFrame) -> list[str]:
    """Return columns in `df` that look like sector return columns.

    A column is treated as a sector if its name is a known SPDR sector ticker
    or ends with '_return' after stripping a ticker prefix.
    """
    sectors: list[str] = []
    for col in df.columns:
        upper = str(col).upper().replace("_RETURN", "").replace("_RET", "")
        if upper in SECTOR_TICKERS:
            sectors.append(col)
    return sectors


def build_regime_pivot(
    df: pd.DataFrame,
    regime_col: str,
    sector_cols: list[str],
    aggfunc: str = "mean",
) -> pd.DataFrame:
    """Build a pivot table: regime values (rows) x sectors (cols).

    Parameters
    ----------
    df : pd.DataFrame
        Merged master frame with one row per business day. Must contain
        `regime_col` and every entry of `sector_cols`.
    regime_col : str
        Name of the categorical regime column to group by.
    sector_cols : list[str]
        Names of the sector return columns to aggregate.
    aggfunc : str, default 'mean'
        Aggregation function to apply. Any name accepted by
        pandas.pivot_table is valid ('mean', 'median', 'std', 'count', ...).

    Returns
    -------
    pd.DataFrame
        Index = unique values of `regime_col` (sorted); columns = `sector_cols`;
        values = aggregated sector returns. Rows with a NaN regime are dropped.
    """
    if regime_col not in df.columns:
        raise KeyError(f"regime column {regime_col!r} not found in DataFrame")
    missing = [c for c in sector_cols if c not in df.columns]
    if missing:
        raise KeyError(f"sector columns not found in DataFrame: {missing}")
    if not sector_cols:
        raise ValueError("sector_cols is empty — nothing to pivot")

    working = df[[regime_col] + sector_cols].dropna(subset=[regime_col])
    pivot = working.pivot_table(
        index=regime_col,
        values=sector_cols,
        aggfunc=aggfunc,
    )
    # pivot_table can return a Series when there's one value column; normalize.
    if isinstance(pivot, pd.Series):
        pivot = pivot.to_frame()
    pivot = pivot.sort_index()
    pivot.columns.name = "sector"
    return pivot


def _make_demo_frame(seed: int = 42, n_days: int = 1000) -> pd.DataFrame:
    """Build a deterministic synthetic merged frame for demo/test purposes.

    Returns a DataFrame with a business-day index, 3 sector return columns,
    and 4 regime columns. Structure matches what the real merge step produces.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start="2015-01-01", periods=n_days)
    df = pd.DataFrame(index=dates)
    df["XLK"] = rng.normal(loc=0.0006, scale=0.012, size=n_days)
    df["XLF"] = rng.normal(loc=0.0004, scale=0.011, size=n_days)
    df["XLE"] = rng.normal(loc=0.0002, scale=0.018, size=n_days)

    # Deterministic regime assignments based on row index modulo.
    idx = np.arange(n_days)
    df["inflation_regime"] = np.where(idx % 2 == 0, "high", "low")
    df["rate_regime"] = np.where(idx % 3 == 0, "rising", "falling")
    df["vix_regime"] = np.where(idx % 4 == 0, "stress", "calm")
    df["combined_regime"] = (
        df["inflation_regime"].astype(str) + "_" + df["rate_regime"].astype(str)
    )
    return df


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run on synthetic data instead of reading data/processed/",
    )
    parser.add_argument(
        "--out-dir",
        default=str(PROCESSED_DIR),
        help="Directory to write pivot CSVs to (default: data/processed/)",
    )
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.demo:
        print("Running in --demo mode with synthetic data.")
        df = _make_demo_frame()
    else:
        df = load_merged_frame()
    print(f"Loaded frame: {df.shape[0]} rows, {df.shape[1]} columns")

    sector_cols = detect_sector_columns(df)
    if not sector_cols:
        print(
            "ERROR: no sector return columns detected. Expected columns named "
            "after SPDR sector ETFs (XLK, XLF, XLE, ...)",
            file=sys.stderr,
        )
        return 1
    print(f"Detected {len(sector_cols)} sector columns: {sector_cols}")

    any_written = False
    for regime_key in ("inflation", "rate", "vix", "combined"):
        regime_col = detect_regime_column(df, regime_key)
        if regime_col is None:
            print(f"  skipping {regime_key}: no matching regime column found")
            continue
        pivot = build_regime_pivot(df, regime_col, sector_cols, aggfunc="mean")
        out_path = out_dir / f"pivot_sector_by_{regime_key}_regime.csv"
        pivot.to_csv(out_path)
        any_written = True
        print(f"  wrote {out_path.relative_to(REPO_ROOT) if out_path.is_relative_to(REPO_ROOT) else out_path}")
        print(pivot.round(6).to_string())
        print()

    if not any_written:
        print("ERROR: no regime columns found in merged frame.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
