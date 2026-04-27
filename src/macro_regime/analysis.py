"""
src/macro_regime/analysis.py

Cross-regime analysis utilities.
"""

from __future__ import annotations

from typing import Literal

import pandas as pd


def sector_return_correlation_by_regime(
    df: pd.DataFrame,
    regime_col: str,
    return_cols: list[str],
    *,
    min_periods: int | None = None,
    output: Literal["dict", "multiindex"] = "dict",
) -> dict[object, pd.DataFrame] | pd.DataFrame:
    """Compute pairwise correlation matrices of sector returns per regime.

    Parameters
    ----------
    df : DataFrame
        Must contain *regime_col* and every column listed in *return_cols*.
    regime_col : str
        Column whose unique values define the regimes to group by.
    return_cols : list[str]
        Sector return columns to correlate.
    min_periods : int or None
        Minimum number of overlapping non-NA observations required per pair.
        Passed directly to ``DataFrame.corr(min_periods=...)``.  When *None*
        (the default), pandas requires all values to be non-NA for a given
        pair; set a lower value to allow pairwise deletion.
    output : {"dict", "multiindex"}
        * ``"dict"`` – returns ``{regime_label: correlation_DataFrame}``
        * ``"multiindex"`` – returns a single DataFrame with a
          ``(regime, sector)`` MultiIndex produced by
          ``groupby(regime_col)[return_cols].corr()``.

    Returns
    -------
    dict[object, pd.DataFrame] or pd.DataFrame

    Missing-value policy
    --------------------
    Correlations use **pairwise** deletion: each pair of columns is computed
    using all rows where *both* values are non-NA (the default behaviour of
    ``pandas.DataFrame.corr``).  The *min_periods* parameter lets callers
    require a minimum overlap count; pairs that do not meet it produce NaN.

    Examples
    --------
    >>> corrs = sector_return_correlation_by_regime(
    ...     master, "macro_regime", ["XLK", "XLF", "XLE"])
    >>> corrs["High Inflation / Rising Rates"]  # square correlation matrix

    Raises
    ------
    ValueError
        If *regime_col* or any entry in *return_cols* is missing from *df*.
    """
    # --- input validation -------------------------------------------------
    missing = []
    if regime_col not in df.columns:
        missing.append(regime_col)
    for col in return_cols:
        if col not in df.columns:
            missing.append(col)
    if missing:
        raise ValueError(
            f"Column(s) not found in DataFrame: {missing}"
        )

    subset = df[[regime_col, *return_cols]]

    if output == "multiindex":
        return (
            subset
            .groupby(regime_col, observed=True)[return_cols]
            .corr(min_periods=min_periods)
        )

    # output == "dict"
    result: dict[object, pd.DataFrame] = {}
    for label, group in subset.groupby(regime_col, observed=True):
        result[label] = group[return_cols].corr(min_periods=min_periods)
    return result
"""
Core analysis logic for the macro regime project.
Contains functions for calculating sector returns, correlations, and performance 
metrics across different macroeconomic environments.
"""
import numpy as np
import pandas as pd


def rank_sector_returns_within_regimes(
    summary: pd.DataFrame,
    *,
    ascending_returns: bool = False,
    tie_method: str = "first",
) -> pd.DataFrame:
    rankings = summary.rank(
        axis=1,
        ascending=ascending_returns,
        method=tie_method,
        na_option="keep",
    )
    return rankings.astype("Int64")


def sector_ranking_stability(rankings: pd.DataFrame) -> pd.DataFrame:
    return rankings.T.corr(method="spearman")


def sector_ranking_stability_from_raw(
    df: pd.DataFrame,
    regime_col: str,
    sector_cols: list[str],
):
    summary = df.groupby(regime_col)[sector_cols].mean()
    rankings = rank_sector_returns_within_regimes(summary)
    stability = sector_ranking_stability(rankings)
    return rankings, stability


def regime_run_segments(df: pd.DataFrame, regime_col: str, date_col: str) -> pd.DataFrame:
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col).reset_index(drop=True)

    change_points = df[regime_col].ne(df[regime_col].shift())
    segment_id = change_points.cumsum()

    segments = (
        df.groupby(segment_id)
        .agg(
            regime=(regime_col, "first"),
            start_date=(date_col, "min"),
            end_date=(date_col, "max"),
            duration_rows=(date_col, "count"),
        )
        .reset_index(drop=True)
    )

    return segments


def regime_persistence_summary(
    segments: pd.DataFrame,
    *,
    duration_col: str = "duration_rows",
) -> pd.DataFrame:
    summary = (
        segments.groupby("regime")[duration_col]
        .agg(
            mean_duration="mean",
            median_duration="median",
            min_duration="min",
            max_duration="max",
            count_segments="count",
        )
        .reset_index()
    )
    return summary


def analyze_regime_persistence(
    df: pd.DataFrame,
    regime_col: str,
    date_col: str,
):
    segments = regime_run_segments(df, regime_col, date_col)
    summary = regime_persistence_summary(segments)
    return segments, summary


def average_sector_volatility_by_regime(
    df: pd.DataFrame,
    regime_col: str = "macro_regime",
    vol_cols: list[str] | None = None,
    *,
    min_obs_per_cell: int | None = None,
) -> pd.DataFrame:
    if vol_cols is None:
        raise ValueError("vol_cols list must be provided.")

    required_cols = [regime_col] + vol_cols
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in DataFrame: {missing}")

    df_clean = df.dropna(subset=[regime_col])
    summary = df_clean.groupby(regime_col, observed=True)[vol_cols].mean()

    if min_obs_per_cell is not None:
        counts = df_clean.groupby(regime_col, observed=True)[vol_cols].count()
        summary = summary.where(counts >= min_obs_per_cell)

    return summary.astype(float)
