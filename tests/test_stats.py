import pytest
import pandas as pd
import numpy as np
from src.macro_regime.stats import compare_sector_volatility_distributions_ks

def test_compare_volatility_returns_nans_when_min_n_not_met():
    # Create a tiny dataframe with only 5 rows
    df = pd.DataFrame({
        'regime': ['A', 'A', 'A', 'B', 'B'],
        'vol_1': [0.1, 0.1, 0.1, 0.2, 0.2],
        'vol_2': [0.1, 0.1, 0.1, 0.2, 0.2]
    })
    
    # min_n is 200, but we have < 5, so it should return NaNs
    ks_summary, _ = compare_sector_volatility_distributions_ks(
        df, 'regime', ['vol_1', 'vol_2'], regime_a='A', regime_b='B', min_n=200
    )
    
    # Assert that the result is NaN (Not a Number) as expected
    assert np.isnan(ks_summary['ks_statistic'].iloc[0])
