"""
Statistical testing framework.
Contains functions for running hypothesis tests (e.g., T-tests, Kolmogorov-Smirnov) 
on sector performance distributions.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Collection

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
