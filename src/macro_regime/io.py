"""
Input/output helper functions for the macro_regime project.
"""

from pathlib import Path


def raw_path(filename: str) -> Path:
    """Return the path to a file in the raw data folder."""
    return Path("data/raw") / filename


def processed_path(filename: str) -> Path:
    """Return the path to a file in the processed data folder."""
    return Path("data/processed") / filename
