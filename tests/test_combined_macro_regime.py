import pandas as pd
import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from macro_regime.regimes import combine_macro_regime


def make_df(inflation, rate):
    return pd.DataFrame({
        "inflation_regime": inflation,
        "rate_regime": rate,
    })


def test_high_inflation_rising_rates():
    df = make_df(["high"], ["rising"])
    result = combine_macro_regime(df)
    assert result["macro_regime"].iloc[0] == "High Inflation / Rising Rates"


def test_high_inflation_falling_rates():
    df = make_df(["high"], ["falling"])
    result = combine_macro_regime(df)
    assert result["macro_regime"].iloc[0] == "High Inflation / Falling Rates"


def test_low_inflation_rising_rates():
    df = make_df(["low"], ["rising"])
    result = combine_macro_regime(df)
    assert result["macro_regime"].iloc[0] == "Low Inflation / Rising Rates"


def test_low_inflation_falling_rates():
    df = make_df(["low"], ["falling"])
    result = combine_macro_regime(df)
    assert result["macro_regime"].iloc[0] == "Low Inflation / Falling Rates"


def test_nan_inflation_gives_nan():
    df = make_df([None], ["rising"])
    result = combine_macro_regime(df)
    assert pd.isna(result["macro_regime"].iloc[0])


def test_nan_rate_gives_nan():
    df = make_df(["high"], [None])
    result = combine_macro_regime(df)
    assert pd.isna(result["macro_regime"].iloc[0])


def test_unknown_label_gives_nan():
    df = make_df(["medium"], ["rising"])
    result = combine_macro_regime(df)
    assert pd.isna(result["macro_regime"].iloc[0])


def test_does_not_mutate_input():
    df = make_df(["high"], ["rising"])
    _ = combine_macro_regime(df)
    assert "macro_regime" not in df.columns


def test_index_alignment():
    df = make_df(["high", "low"], ["rising", "falling"])
    df.index = [10, 20]
    result = combine_macro_regime(df)
    assert list(result.index) == [10, 20]