"""
Statistical Testing Framework.
Fits into the analysis phase to rigorously evaluate sector performance and volatility distributions across regimes.

Key Responsibilities:
- Computes rolling historical volatility using expanding windows.
- Calculates standardized daily returns (simple or log).
- Performs Kolmogorov-Smirnov (KS) tests to compare distributions across regimes.

Key Functions:
- `rolling_volatility`: Calculates standard deviation over a rolling window.
- `calculate_daily_returns`: Generates day-over-day price returns.
- `compare_sector_volatility_distributions_ks`: Runs 2-sample KS tests on regimes.

Inputs/Outputs:
- Consumes: pd.DataFrame or pd.Series (price data, volatility metrics).
- Returns: pd.Series or Tuple[pd.DataFrame, pd.DataFrame] containing test statistics.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Collection

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
def rolling_volatility(series, window=20, ddof=1):
    values = np.array(series, dtype=float)
    n = len(values)

    if window > n:
        result = np.full(n, np.nan)
        return pd.Series(result, index=series.index)

    windows = np.array([values[i:i + window] for i in range(n - window + 1)])
    volatilities = np.std(windows, axis=1, ddof=ddof)

    padding = np.full(window - 1, np.nan)
    result = np.concatenate((padding, volatilities))

    return pd.Series(result, index=series.index)


def calculate_daily_returns(series, method='simple'):
    prices = np.array(series, dtype=float)
    ratios = prices[1:] / prices[:-1]

    if method == "log":
        returns = np.log(ratios)
    else:
        returns = ratios - 1

    result = np.insert(returns, 0, np.nan)

    return pd.Series(result, index=series.index)

def compare_sector_volatility_distributions_ks(
    df: pd.DataFrame, 
    regime_col: str, 
    vol_cols: list[str], 
    *, 
    regime_a: str | Collection[str], 
    regime_b: str | Collection[str], 
    min_n: int = 200
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compares volatility distributions between two regimes using the KS test.
    Pools all values from vol_cols within each regime to form one 1D sample.
    """
    # 1. Normalize inputs to lists if they are strings
    regime_a_list = [regime_a] if isinstance(regime_a, str) else list(regime_a)
    regime_b_list = [regime_b] if isinstance(regime_b, str) else list(regime_b)

    # 2. Helper to extract and pool data
    def get_pooled_sample(regime_list):
        mask = df[regime_col].isin(regime_list)
        # Stack aligns all sectors into one long column, dropna removes gaps
        return df.loc[mask, vol_cols].stack().dropna()

    s_a = get_pooled_sample(regime_a_list)
    s_b = get_pooled_sample(regime_b_list)

    # 3. Handle Minimum Observations (min_n)
    if len(s_a) < min_n or len(s_b) < min_n:
        # Return NaNs if we don't have enough data
        ks_summary = pd.DataFrame({
            'ks_statistic': [np.nan], 'p_value': [np.nan], 
            'n_regime_a': [len(s_a)], 'n_regime_b': [len(s_b)]
        })
        return ks_summary, pd.DataFrame()

    # 4. Perform KS Test
    ks_stat, p_val = stats.ks_2samp(s_a, s_b, alternative='two-sided')
    ks_summary = pd.DataFrame({
        'ks_statistic': [ks_stat], 
        'p_value': [p_val],
        'n_regime_a': [len(s_a)], 
        'n_regime_b': [len(s_b)]
    })

    # 5. Descriptive Stats
    percentiles = [0.25, 0.50, 0.75, 0.95]
    desc_a = s_a.describe(percentiles=percentiles)
    desc_b = s_b.describe(percentiles=percentiles)
    
    # Organize into a readable summary table
    describe_by_regime = pd.concat([desc_a, desc_b], axis=1, keys=['Regime_A', 'Regime_B']).T

    return ks_summary, describe_by_regime
