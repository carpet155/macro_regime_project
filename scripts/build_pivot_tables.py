"""
Build pivot tables of sector performance by macroeconomic regime.

Reads the canonical long-form master DataFrame from data/processed/base/master_df.csv,
assigns regimes, and writes regime x ticker mean-return pivots.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from macro_regime.io import load_master_df
from macro_regime.regimes import assign_all_regimes

PROCESSED_DIR = REPO_ROOT / "data" / "processed"
ANALYSIS_DIR = PROCESSED_DIR / "analysis"
REGIME_COLUMNS = {
    "inflation": "inflation_regime",
    "rate": "rate_regime",
    "vix": "vix_regime",
    "combined": "macro_regime",
}


def build_regime_pivot(
    df: pd.DataFrame,
    regime_col: str,
    aggfunc: str = "mean",
) -> pd.DataFrame:
    """Build a long-form master pivot: regime rows x ticker columns."""
    required = {regime_col, "ticker", "sector_return"}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise KeyError(f"Missing required column(s): {missing}")

    pivot = df.pivot_table(
        index=regime_col,
        columns="ticker",
        values="sector_return",
        aggfunc=aggfunc,
    )
    pivot.columns.name = "ticker"
    return pivot.sort_index()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default=str(ANALYSIS_DIR),
        help="Directory to write pivot CSVs to (default: data/processed/analysis/)",
    )
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = assign_all_regimes(load_master_df(PROCESSED_DIR))
    print(f"Loaded master_df with regimes: {df.shape[0]} rows, {df.shape[1]} columns")

    for regime_key, regime_col in REGIME_COLUMNS.items():
        pivot = build_regime_pivot(df, regime_col, aggfunc="mean")
        out_path = out_dir / f"pivot_sector_by_{regime_key}_regime.csv"
        pivot.to_csv(out_path)
        print(f"  wrote {out_path}")
        print(pivot.round(6).to_string())
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
