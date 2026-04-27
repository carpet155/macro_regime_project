"""
Path and CSV I/O helpers for the macro_regime project.
"""

from pathlib import Path
import pandas as pd

from macro_regime.config import PROCESSED_DIR, RAW_DIR

MASTER_DF_FILENAME = "master_df.csv"
MASTER_DF_REQUIRED_COLUMNS = {"date", "ticker", "sector_return"}


def raw_path(filename: str) -> Path:
    """Return path to a file in data/raw."""
    return RAW_DIR / filename


def processed_path(filename: str) -> Path:
    """Return path to a file in data/processed."""
    return PROCESSED_DIR / filename


def ensure_parent_dir(path: Path) -> None:
    """Create parent directory if it does not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)


def save_csv(df: pd.DataFrame, path: Path, index: bool = False) -> None:
    """Save DataFrame to CSV."""
    ensure_parent_dir(path)
    df.to_csv(path, index=index)


def load_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Load CSV into DataFrame."""
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    return pd.read_csv(path, **kwargs)


def save_raw_csv(df: pd.DataFrame, filename: str, index: bool = False) -> Path:
    """Save to data/raw."""
    path = raw_path(filename)
    save_csv(df, path, index=index)
    return path


def save_processed_csv(df: pd.DataFrame, filename: str, index: bool = False) -> Path:
    """Save to data/processed."""
    path = processed_path(filename)
    save_csv(df, path, index=index)
    return path


def load_raw_csv(filename: str, **kwargs) -> pd.DataFrame:
    """Load from data/raw."""
    return load_csv(raw_path(filename), **kwargs)


def load_processed_csv(filename: str, **kwargs) -> pd.DataFrame:
    """Load from data/processed."""
    return load_csv(processed_path(filename), **kwargs)


def load_master_df(processed_dir: str | Path = "data/processed") -> pd.DataFrame:
    """Load and validate the canonical long-form master DataFrame."""
    path = Path(processed_dir) / MASTER_DF_FILENAME
    df = load_csv(path, parse_dates=["date"])

    missing = sorted(MASTER_DF_REQUIRED_COLUMNS.difference(df.columns))
    if missing:
        raise ValueError(
            f"{path} is missing required column(s): {missing}. "
            f"Expected at least: {sorted(MASTER_DF_REQUIRED_COLUMNS)}"
        )

    duplicate_count = df.duplicated(subset=["date", "ticker"]).sum()
    if duplicate_count:
        raise ValueError(
            f"{path} contains {duplicate_count} duplicate (date, ticker) rows."
        )

    return df