"""
Compute average sector return by macroeconomic regime.

For each regime classification (inflation, rate, VIX, combined), this script
produces:
  - A table of mean daily returns per sector per regime value
  - A table of annualized mean returns (assuming 252 trading days per year)
  - A summary CSV with regime, sector, mean_daily_return, annualized_return,
    and observation count per cell

Output files produced:
    data/processed/avg_return_by_inflation_regime.csv
    data/processed/avg_return_by_rate_regime.csv
    data/processed/avg_return_by_vix_regime.csv
    data/processed/avg_return_by_combined_regime.csv
    data/processed/avg_return_summary.csv   (long-form, all regimes combined)

Usage:
    python scripts/compute_avg_returns_by_regime.py
    python scripts/compute_avg_returns_by_regime.py --demo

Closes issue #68.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# Standard trading days per year, used to annualize mean daily returns.
TRADING_DAYS_PER_YEAR = 252

REGIME_COLUMN_CANDIDATES = {
    "inflation": ["inflation_regime", "infl_regime", "cpi_regime"],
    "rate": ["rate_regime", "interest_rate_regime", "rates_regime"],
    "vix": ["vix_regime", "vix_stress_regime", "stress_regime"],
    "combined": ["combined_regime", "macro_regime", "regime"],
}

SECTOR_TICKERS = {
    "XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLB", "XLU", "XLRE", "XLC",
}

REPO_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = REPO_ROOT / "data" / "processed"

MERGED_FILE_CANDIDATES = [
    "merged.csv",
    "master.csv",
    "merged_master.csv",
    "all_data.csv",
]


def load_merged_frame(processed_dir: Path = PROCESSED_DIR) -> pd.DataFrame:
    """Load merged master DataFrame. Raises if no conventional file is found."""
    for name in MERGED_FILE_CANDIDATES:
        path = processed_dir / name
        if path.exists():
            return pd.read_csv(path, parse_dates=[0], index_col=0)
    raise FileNotFoundError(
        f"No merged master CSV in {processed_dir}. Tried: "
        f"{', '.join(MERGED_FILE_CANDIDATES)}. "
        "Run the pipeline (issues #58-#60) or pass --demo."
    )


def detect_regime_column(df: pd.DataFrame, regime_key: str) -> str | None:
    for candidate in REGIME_COLUMN_CANDIDATES[regime_key]:
        if candidate in df.columns:
            return candidate
    return None


def detect_sector_columns(df: pd.DataFrame) -> list[str]:
    sectors: list[str] = []
    for col in df.columns:
        upper = str(col).upper().replace("_RETURN", "").replace("_RET", "")
        if upper in SECTOR_TICKERS:
            sectors.append(col)
    return sectors


def avg_return_by_regime(
    df: pd.DataFrame,
    regime_col: str,
    sector_cols: list[str],
) -> pd.DataFrame:
    """Compute mean daily return per sector per regime value.

    Parameters
    ----------
    df : pd.DataFrame
        Merged master frame, one row per business day.
    regime_col : str
        Column in `df` containing categorical regime labels.
    sector_cols : list[str]
        Columns in `df` containing daily sector returns (decimals, not %).

    Returns
    -------
    pd.DataFrame
        Index = distinct regime values; columns = sectors; values = mean daily
        return within that regime. Rows where `regime_col` is NaN are dropped.
    """
    if regime_col not in df.columns:
        raise KeyError(f"regime column {regime_col!r} not in DataFrame")
    missing = [c for c in sector_cols if c not in df.columns]
    if missing:
        raise KeyError(f"sector columns not in DataFrame: {missing}")
    if not sector_cols:
        raise ValueError("sector_cols is empty")

    working = df[[regime_col] + sector_cols].dropna(subset=[regime_col])
    result = working.groupby(regime_col, observed=True)[sector_cols].mean()
    return result.sort_index()


def annualize_mean_return(mean_daily: pd.DataFrame) -> pd.DataFrame:
    """Convert a table of mean daily returns to annualized returns.

    Uses the standard compounding formula:
        annualized = (1 + mean_daily) ** 252 - 1

    Applies element-wise so any DataFrame shape is supported.
    """
    return (1.0 + mean_daily) ** TRADING_DAYS_PER_YEAR - 1.0


def build_long_summary(
    df: pd.DataFrame,
    regime_col: str,
    sector_cols: list[str],
) -> pd.DataFrame:
    """Build a long-form summary with one row per (regime_value, sector) pair.

    Columns: regime_type, regime_value, sector, mean_daily_return,
             annualized_return, n_observations.
    """
    working = df[[regime_col] + sector_cols].dropna(subset=[regime_col])
    grouped = working.groupby(regime_col, observed=True)

    means = grouped[sector_cols].mean()
    counts = grouped[sector_cols].count()

    rows = []
    for regime_value in means.index:
        for sector in sector_cols:
            daily = float(means.loc[regime_value, sector])
            rows.append({
                "regime_type": regime_col,
                "regime_value": regime_value,
                "sector": sector,
                "mean_daily_return": daily,
                "annualized_return": (1.0 + daily) ** TRADING_DAYS_PER_YEAR - 1.0,
                "n_observations": int(counts.loc[regime_value, sector]),
            })
    return pd.DataFrame(rows)


def _make_demo_frame(seed: int = 42, n_days: int = 1000) -> pd.DataFrame:
    """Deterministic synthetic merged frame for demo and testing."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start="2015-01-01", periods=n_days)
    df = pd.DataFrame(index=dates)
    df["XLK"] = rng.normal(loc=0.0006, scale=0.012, size=n_days)
    df["XLF"] = rng.normal(loc=0.0004, scale=0.011, size=n_days)
    df["XLE"] = rng.normal(loc=0.0002, scale=0.018, size=n_days)

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
        help="Directory to write output CSVs (default: data/processed/)",
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
        print("ERROR: no sector return columns detected.", file=sys.stderr)
        return 1
    print(f"Detected {len(sector_cols)} sector columns: {sector_cols}")

    summary_frames: list[pd.DataFrame] = []

    for regime_key in ("inflation", "rate", "vix", "combined"):
        regime_col = detect_regime_column(df, regime_key)
        if regime_col is None:
            print(f"  skipping {regime_key}: no regime column")
            continue

        mean_daily = avg_return_by_regime(df, regime_col, sector_cols)
        annualized = annualize_mean_return(mean_daily)

        out_daily = out_dir / f"avg_return_by_{regime_key}_regime.csv"
        out_annual = out_dir / f"annualized_return_by_{regime_key}_regime.csv"
        mean_daily.to_csv(out_daily)
        annualized.to_csv(out_annual)

        print(f"\n  Mean daily returns by {regime_col}:")
        print(mean_daily.round(6).to_string())
        print(f"  Annualized returns by {regime_col}:")
        print(annualized.round(4).to_string())
        print(f"  -> wrote {out_daily.name} and {out_annual.name}")

        summary_frames.append(build_long_summary(df, regime_col, sector_cols))

    if not summary_frames:
        print("ERROR: no regime columns found.", file=sys.stderr)
        return 1

    summary = pd.concat(summary_frames, ignore_index=True)
    summary_path = out_dir / "avg_return_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(f"\nLong-form summary ({len(summary)} rows) -> {summary_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
