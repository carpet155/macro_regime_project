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
