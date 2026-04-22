import pandas as pd
import numpy as np
import pytest
from macro_regime.analysis import average_sector_volatility_by_regime

def test_volatility_aggregation_logic():
    """Test that the mean is calculated correctly across regimes with floating point tolerance."""
    df = pd.DataFrame({
        'macro_regime': ['High', 'High', 'Low', 'Low'],
        'vol_XLB': [0.10, 0.20, 0.05, 0.05],  # High mean: 0.15, Low mean: 0.05
        'vol_XLE': [0.40, 0.60, 0.10, 0.20]   # High mean: 0.50, Low mean: 0.15
    })
    
    vol_cols = ['vol_XLB', 'vol_XLE']
    result = average_sector_volatility_by_regime(df, 'macro_regime', vol_cols)
    
    # Using pytest.approx to handle 0.15000000000000002 issue
    assert result.loc['High', 'vol_XLB'] == pytest.approx(0.15)
    assert result.loc['Low', 'vol_XLE'] == pytest.approx(0.15)
    assert result.shape == (2, 2)

def test_missing_column_error():
    """Test that the function fails fast if columns are missing."""
    df = pd.DataFrame({'wrong_col': [1, 2, 3]})
    with pytest.raises(ValueError, match="Missing columns"):
        average_sector_volatility_by_regime(df, 'macro_regime', ['vol_XLB'])

def test_nan_regime_handling():
    """Test that rows with NaN regimes are dropped from the analysis."""
    df = pd.DataFrame({
        'macro_regime': ['High', None, 'Low'],
        'vol_XLB': [0.10, 0.50, 0.05]
    })
    result = average_sector_volatility_by_regime(df, 'macro_regime', ['vol_XLB'])
    
    # The 0.50 value should be ignored because its regime is NaN
    assert len(result) == 2
    assert 'High' in result.index
    assert 'Low' in result.index
    assert result.loc['High', 'vol_XLB'] == 0.10