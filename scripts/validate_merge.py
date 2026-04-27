"""
scripts/validate_merge.py

Issue #63 — Check for NaNs after merge
Validates the master merged DataFrame for NaN issues after all
ingest + merge steps have run. Logs a full report and raises on
any critical failures.
"""

import logging
import sys
from pathlib import Path

import pandas as pd

# ── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Config ───────────────────────────────────────────────────────────────────

MASTER_PATH = Path("data/processed/base/master_df.csv")

# Columns that must NEVER have NaNs after merge — hard fail if they do
CRITICAL_COLUMNS = ["cpi", "fedfunds", "vix", "spx_price"]

# Columns allowed up to this % NaN before raising (e.g. newly listed ETFs)
NAN_THRESHOLD_PCT = 5.0

# Expected date range for the full dataset
EXPECTED_START = "2000-01-01"
EXPECTED_END   = "2024-12-31"

# Expected minimum number of columns
MIN_COLUMNS = 10


# ── Validation helpers ────────────────────────────────────────────────────────

def check_file_exists(path: Path) -> pd.DataFrame:
    """Load master CSV or exit with a clear message."""
    if not path.exists():
        log.error(f"Master file not found: {path}")
        log.error("Run build_master_df.py (issue #60) before this script.")
        sys.exit(1)
    df = pd.read_csv(path, parse_dates=["date"])
    log.info(f"Loaded {path}  ->  shape {df.shape}")
    return df


def check_shape(df: pd.DataFrame) -> None:
    """Validate the DataFrame has a reasonable number of rows and columns."""
    log.info("-- Shape check ----------------------------------------------")
    rows, cols = df.shape
    log.info(f"  Rows   : {rows:,}")
    log.info(f"  Columns: {cols}")

    if cols < MIN_COLUMNS:
        raise ValueError(
            f"Only {cols} columns found — expected at least {MIN_COLUMNS}. "
            "Merge may be incomplete."
        )
    log.info("  PASS Shape OK")


def check_date_range(df: pd.DataFrame) -> None:
    """Confirm the date column spans the expected date range."""
    log.info("-- Date-range check -----------------------------------------")
    actual_start = df["date"].min()
    actual_end   = df["date"].max()
    log.info(f"  Date start : {actual_start.date()}")
    log.info(f"  Date end   : {actual_end.date()}")

    if actual_start > pd.Timestamp(EXPECTED_START):
        log.warning(
            f"  WARNING Data starts {actual_start.date()}, expected <= {EXPECTED_START}"
        )
    if actual_end < pd.Timestamp(EXPECTED_END):
        log.warning(
            f"  WARNING Data ends {actual_end.date()}, expected >= {EXPECTED_END}"
        )

    dupes = df.duplicated(subset=["date", "ticker"]).sum()
    if dupes:
        raise ValueError(f"  FAIL {dupes} duplicate (date, ticker) rows found.")
    log.info("  PASS Date range OK")


def check_dtypes(df: pd.DataFrame) -> None:
    """All columns except date/ticker/name should be numeric after cleaning."""
    log.info("-- dtype check ----------------------------------------------")
    skip = {"date", "ticker", "name"}
    non_numeric = [
        c for c in df.columns
        if c not in skip and not pd.api.types.is_numeric_dtype(df[c])
    ]
    if non_numeric:
        raise ValueError(
            f"Non-numeric columns found after merge: {non_numeric}\n"
            "These should have been converted during ingestion/cleaning."
        )
    log.info("  PASS All numeric columns are numeric")


def check_nans(df: pd.DataFrame) -> None:
    """
    Full NaN report.
    - Logs every column with NaN counts and %.
    - Hard-fails on CRITICAL_COLUMNS having any NaN.
    - Hard-fails on any column exceeding NAN_THRESHOLD_PCT.
    """
    log.info("-- NaN check ------------------------------------------------")
    nan_counts = df.isnull().sum()
    nan_pct    = df.isnull().mean() * 100
    total_nans = nan_counts.sum()

    if total_nans == 0:
        log.info("  PASS Zero NaNs in entire DataFrame — perfect.")
        return

    log.warning(f"  Total NaNs across all columns: {total_nans:,}")

    cols_with_nans = nan_counts[nan_counts > 0]
    for col in cols_with_nans.index:
        pct = nan_pct[col]
        if col in CRITICAL_COLUMNS:
            flag = "CRITICAL"
        elif pct > NAN_THRESHOLD_PCT:
            flag = "EXCEEDS THRESHOLD"
        else:
            flag = "WARNING"
        log.warning(f"  {flag}  {col}: {nan_counts[col]:,} NaNs ({pct:.2f}%)")

    critical_with_nans = [
        c for c in CRITICAL_COLUMNS
        if c in df.columns and nan_counts.get(c, 0) > 0
    ]
    if critical_with_nans:
        raise ValueError(
            f"Critical columns have NaNs after merge — "
            f"check alignment/cleaning steps: {critical_with_nans}"
        )

    over_threshold = [
        c for c in df.columns
        if nan_pct.get(c, 0) > NAN_THRESHOLD_PCT
    ]
    if over_threshold:
        raise ValueError(
            f"Columns exceed {NAN_THRESHOLD_PCT}% NaN threshold: {over_threshold}\n"
            "Review interpolation / forward-fill steps in cleaning."
        )

    log.info(
        f"  PASS NaN check passed (all NaNs within {NAN_THRESHOLD_PCT}% threshold "
        "and no critical columns affected)"
    )


def check_consecutive_nans(df: pd.DataFrame, max_run: int = 5) -> None:
    """
    Flag columns with long consecutive NaN runs.
    A run > max_run rows usually means a data gap, not just a missing point.
    """
    log.info("-- Consecutive-NaN check ------------------------------------")
    numeric_cols = [
        c for c in df.columns
        if c not in {"date", "ticker", "name"}
        and pd.api.types.is_numeric_dtype(df[c])
    ]
    flagged = []
    for col in numeric_cols:
        s = df[col].isnull()
        run = (s * (s.groupby((s != s.shift()).cumsum()).cumcount() + 1)).max()
        if run > max_run:
            flagged.append((col, int(run)))
            log.warning(f"  WARNING {col}: longest consecutive NaN run = {run} rows")

    if flagged:
        log.warning(
            f"  {len(flagged)} column(s) have runs > {max_run} rows. "
            "Consider a stronger interpolation strategy."
        )
    else:
        log.info(f"  PASS No column has a consecutive NaN run > {max_run} rows")


# ── Main ─────────────────────────────────────────────────────────────────────

def validate(path: Path = MASTER_PATH) -> pd.DataFrame:
    log.info("=" * 60)
    log.info("Starting post-merge NaN validation  (issue #63)")
    log.info("=" * 60)

    df = check_file_exists(path)

    failures = []
    checks = [
        ("shape",            lambda: check_shape(df)),
        ("date range",       lambda: check_date_range(df)),
        ("dtypes",           lambda: check_dtypes(df)),
        ("NaNs",             lambda: check_nans(df)),
        ("consecutive NaNs", lambda: check_consecutive_nans(df)),
    ]

    for name, fn in checks:
        try:
            fn()
        except ValueError as exc:
            log.error(f"  FAIL {name} check FAILED: {exc}")
            failures.append(name)

    log.info("=" * 60)
    if failures:
        log.error(f"Validation FAILED on: {failures}")
        sys.exit(1)
    else:
        log.info("PASS All validation checks passed.")
        log.info("=" * 60)

    return df


if __name__ == "__main__":
    validate()
