"""
Statistical helper functions for the macro_regime project.
"""


def calculate_returns(series):
    """Placeholder function for calculating returns."""
    return series


from collections.abc import Collection

import numpy as np
import pandas as pd
from scipy.stats import ttest_ind


def _normalize_group_labels(labels: str | Collection[str]) -> list[str]:
    """Convert a single label or collection of labels into a list of strings."""
    if isinstance(labels, str):
        return [labels]
    return list(labels)


def ttest_sector_returns_between_regimes(
    df: pd.DataFrame,
    regime_col: str,
    return_cols: list[str],
    *,
    regime_a: str | Collection[str],
    regime_b: str | Collection[str],
    equal_var: bool = False,
    min_n: int = 30,
) -> pd.DataFrame:
  
    if regime_col not in df.columns:
        raise ValueError(f"{regime_col!r} is not a column in df.")

    missing_cols = [col for col in return_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing return columns: {missing_cols}")

    group_a_labels = _normalize_group_labels(regime_a)
    group_b_labels = _normalize_group_labels(regime_b)

    regime_series = df[regime_col]
    mask_a = regime_series.isin(group_a_labels)
    mask_b = regime_series.isin(group_b_labels)

    if mask_a.sum() == 0:
        raise ValueError("No rows found for regime_a labels.")
    if mask_b.sum() == 0:
        raise ValueError("No rows found for regime_b labels.")

    results = []

    for col in return_cols:
        sample_a = df.loc[mask_a, col].dropna()
        sample_b = df.loc[mask_b, col].dropna()

        n_a = int(sample_a.shape[0])
        n_b = int(sample_b.shape[0])

        mean_a = float(sample_a.mean()) if n_a > 0 else np.nan
        mean_b = float(sample_b.mean()) if n_b > 0 else np.nan

        if n_a < min_n or n_b < min_n:
            t_stat = np.nan
            p_val = np.nan
        else:
            t_stat, p_val = ttest_ind(
                sample_a,
                sample_b,
                equal_var=equal_var,
                nan_policy="omit",
            )

        results.append(
            {
                "sector": col,
                "t_statistic": t_stat,
                "p_value": p_val,
                "n_regime_a": n_a,
                "n_regime_b": n_b,
                "mean_a": mean_a,
                "mean_b": mean_b,
            }
        )

    return pd.DataFrame(results).set_index("sector")