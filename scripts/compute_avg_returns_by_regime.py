"""
Compute average sector return by macroeconomic regime.

Reads the canonical long-form master DataFrame from data/processed/base/master_df.csv,
assigns regimes, and writes mean daily/annualized returns by regime and ticker.
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

TRADING_DAYS_PER_YEAR = 252
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
ANALYSIS_DIR = PROCESSED_DIR / "analysis"
REGIME_COLUMNS = {
    "inflation": "inflation_regime",
    "rate": "rate_regime",
    "vix": "vix_regime",
    "combined": "macro_regime",
}


def avg_return_by_regime(df: pd.DataFrame, regime_col: str) -> pd.DataFrame:
    """Compute mean daily sector return by regime and ticker."""
    required = {regime_col, "ticker", "sector_return"}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise KeyError(f"Missing required column(s): {missing}")

    result = df.pivot_table(
        index=regime_col,
        columns="ticker",
        values="sector_return",
        aggfunc="mean",
    )
    result.columns.name = "ticker"
    return result.sort_index()


def annualize_mean_return(mean_daily: pd.DataFrame) -> pd.DataFrame:
    """Convert mean daily returns to annualized returns."""
    return (1.0 + mean_daily) ** TRADING_DAYS_PER_YEAR - 1.0


def build_long_summary(df: pd.DataFrame, regime_col: str) -> pd.DataFrame:
    """Build one row per regime/ticker pair with return and observation count."""
    grouped = df.groupby([regime_col, "ticker"], observed=True)["sector_return"]
    summary = grouped.agg(
        mean_daily_return="mean",
        n_observations="count",
    ).reset_index()
    summary = summary.rename(columns={regime_col: "regime_value"})
    summary.insert(0, "regime_type", regime_col)
    summary["annualized_return"] = (
        (1.0 + summary["mean_daily_return"]) ** TRADING_DAYS_PER_YEAR - 1.0
    )
    return summary[
        [
            "regime_type",
            "regime_value",
            "ticker",
            "mean_daily_return",
            "annualized_return",
            "n_observations",
        ]
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default=str(ANALYSIS_DIR),
        help="Directory to write output CSVs (default: data/processed/analysis/)",
    )
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = assign_all_regimes(load_master_df(PROCESSED_DIR))
    print(f"Loaded master_df with regimes: {df.shape[0]} rows, {df.shape[1]} columns")

    summary_frames: list[pd.DataFrame] = []

    for regime_key, regime_col in REGIME_COLUMNS.items():
        mean_daily = avg_return_by_regime(df, regime_col)
        annualized = annualize_mean_return(mean_daily)

        out_daily = out_dir / f"avg_return_by_{regime_key}_regime.csv"
        out_annual = out_dir / f"annualized_return_by_{regime_key}_regime.csv"
        mean_daily.to_csv(out_daily)
        annualized.to_csv(out_annual)

        print(f"\n  Mean daily returns by {regime_col}:")
        print(mean_daily.round(6).to_string())
        print(f"  Annualized returns by {regime_col}:")
        print(annualized.round(4).to_string())
        print(f"  wrote {out_daily} and {out_annual}")

        summary_frames.append(build_long_summary(df, regime_col))

    summary = pd.concat(summary_frames, ignore_index=True)
    summary_path = out_dir / "avg_return_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(f"\nLong-form summary ({len(summary)} rows) -> {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
