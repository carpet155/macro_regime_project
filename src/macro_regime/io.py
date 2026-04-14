"""
Path and CSV I/O helpers for the macro_regime project.
"""

from pathlib import Path
import pandas as pd

from macro_regime.config import PROCESSED_DIR, RAW_DIR


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