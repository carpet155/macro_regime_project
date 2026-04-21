"""
src/macro_regime/panel.py

Restructure the master DataFrame into a panel indexed by (date, ticker)
for panel-style analysis (issue #72).

Functions
---------
build_panel_df    : wrap build_master_df and set a (date, ticker) MultiIndex
pivot_panel_wide  : pivot a panel column to wide format (index=date, cols=ticker)

All functions are fully vectorized and do not mutate their inputs.
"""

from __future__ import annotations

import pandas as pd

from macro_regime.build import build_master_df


def build_panel_df(
    processed_dir: str = "data/processed",
    drop_name: bool = True,
) -> pd.DataFrame:
    """
    Build a (date, ticker) MultiIndex panel DataFrame for panel analysis.

    Wraps ``build_master_df`` and restructures the flat output into a
    panel indexed by (date, ticker). Macro columns (cpi, dgs2, dgs10,
    fedfunds, vix, spx_price, spx_return) are broadcast across every
    ticker on each date.

    Parameters
    ----------
    processed_dir : str
        Path to the folder containing processed CSVs. Forwarded to
        ``build_master_df``.
    drop_name : bool, default True
        If True, drop the ``name`` column (redundant with ticker via a
        1-to-1 mapping). Set False to keep ``name`` as a data column,
        e.g. when labeling plots with the human-readable sector name.

    Returns
    -------
    pd.DataFrame
        Panel DataFrame with MultiIndex names ``["date", "ticker"]``,
        sorted by (date, ticker), with no duplicate index pairs.

    Notes
    -----
    Reload from CSV with::

        pd.read_csv(path, index_col=[0, 1], parse_dates=["date"])
    """
    master = build_master_df(processed_dir)

    if drop_name and "name" in master.columns:
        master = master.drop(columns=["name"])

    if master.duplicated(subset=["date", "ticker"]).any():
        raise RuntimeError(
            "duplicate (date, ticker) pairs found in master_df; "
            "cannot build a well-defined panel index."
        )

    panel = master.set_index(["date", "ticker"]).sort_index()
    return panel


def pivot_panel_wide(
    panel: pd.DataFrame,
    value: str = "sector_return",
) -> pd.DataFrame:
    """
    Pivot a (date, ticker) panel to wide format: index=date, columns=ticker.

    Parameters
    ----------
    panel : pd.DataFrame
        MultiIndex (date, ticker) panel from ``build_panel_df``.
    value : str, default "sector_return"
        Column to pivot.

    Returns
    -------
    pd.DataFrame
        Wide DataFrame indexed by date, with one column per ticker.
    """
    if value not in panel.columns:
        raise ValueError(
            f"Column '{value}' not found. Available: {list(panel.columns)}"
        )
    return panel[value].unstack("ticker")
