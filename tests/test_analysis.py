import pandas as pd
import numpy as np
import pytest
from macro_regime.analysis import (
    regime_run_segments,
    regime_persistence_summary,
    average_sector_volatility_by_regime,
)

def test_constant_regime():
    df = pd.DataFrame({
        "date": pd.date_range("2020-01-01", periods=5),
        "regime": ["A"] * 5,
    })

    segments = regime_run_segments(df, "regime", "date")

    assert len(segments) == 1
    assert segments.loc[0, "duration_rows"] == 5

def test_volatility_aggregation_logic():
    df = pd.DataFrame({
        'macro_regime': ['High', 'High', 'Low', 'Low'],
        'vol_XLB': [0.10, 0.20, 0.05, 0.05],
        'vol_XLE': [0.40, 0.60, 0.10, 0.20]
    })
    
    vol_cols = ['vol_XLB', 'vol_XLE']
    result = average_sector_volatility_by_regime(df, 'macro_regime', vol_cols)
    
    assert result.loc['High', 'vol_XLB'] == pytest.approx(0.15)
    assert result.loc['Low', 'vol_XLE'] == pytest.approx(0.15)
    assert result.shape == (2, 2)

def test_missing_column_error():
    df = pd.DataFrame({'wrong_col': [1, 2, 3]})
    with pytest.raises(ValueError, match="Missing columns"):
        average_sector_volatility_by_regime(df, 'macro_regime', ['vol_XLB'])

def test_nan_regime_handling():
    df = pd.DataFrame({
        'macro_regime': ['High', None, 'Low'],
        'vol_XLB': [0.10, 0.50, 0.05]
    })
    result = average_sector_volatility_by_regime(df, 'macro_regime', ['vol_XLB'])
    
    assert len(result) == 2
    assert 'High' in result.index
    assert 'Low' in result.index
    assert result.loc['High', 'vol_XLB'] == 0.10
