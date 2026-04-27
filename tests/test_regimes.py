"""
tests/test_regimes.py

Unit tests for regime classification logic (issues #64 and #65).
Run with:  pytest tests/test_regimes.py -v
"""

import pandas as pd
import numpy as np
import pytest

from src.macro_regime.regimes import (
    assign_all_regimes,
    assign_inflation_regime,
    classify_rate_regime,
    assign_rate_regime,
)


# ── Shared fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "date":     pd.date_range("2000-01-01", periods=10, freq="ME"),
        "ticker":   ["XLK"] * 10,
        "cpi":      [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        "fedfunds": [5.0, 5.0, 5.25, 5.25, 5.5, 5.25, 5.0, 4.75, 4.75, 4.5],
    })

@pytest.fixture
def rising_rates():
    return pd.Series([1.0, 2.0, 3.0, 4.0, 5.0], name="fedfunds")

@pytest.fixture
def falling_rates():
    return pd.Series([5.0, 4.0, 3.0, 2.0, 1.0], name="fedfunds")

@pytest.fixture
def flat_rates():
    return pd.Series([3.0, 3.0, 3.0, 3.0, 3.0], name="fedfunds")

@pytest.fixture
def df_with_nan_cpi(sample_df):
    df = sample_df.copy()
    df.loc[2, "cpi"] = np.nan
    df.loc[5, "cpi"] = np.nan
    return df


# ══════════════════════════════════════════════════════════════════════════════
# Inflation regime tests (issue #64)
# ══════════════════════════════════════════════════════════════════════════════

def test_inflation_returns_dataframe(sample_df):
    assert isinstance(assign_inflation_regime(sample_df), pd.DataFrame)

def test_inflation_regime_column_exists(sample_df):
    result = assign_inflation_regime(sample_df)
    assert "inflation_regime" in result.columns

def test_both_inflation_labels_present(sample_df):
    result = assign_inflation_regime(sample_df)
    vals = set(result["inflation_regime"].unique())
    assert {"high", "low"}.issubset(vals)

def test_inflation_median_split_balanced(sample_df):
    result = assign_inflation_regime(sample_df)
    high_pct = (result["inflation_regime"] == "high").mean()
    assert 0.3 <= high_pct <= 0.7

def test_inflation_fixed_threshold_high(sample_df):
    # strictly above 5.0 -> high
    result = assign_inflation_regime(sample_df, method="fixed", fixed_threshold=5.0)
    assert (result[result["cpi"] > 5.0]["inflation_regime"] == "high").all()

def test_inflation_fixed_threshold_low(sample_df):
    # at or below 5.0 -> low
    result = assign_inflation_regime(sample_df, method="fixed", fixed_threshold=5.0)
    assert (result[result["cpi"] <= 5.0]["inflation_regime"] == "low").all()

def test_inflation_boundary_is_low(sample_df):
    # exactly at threshold is low (strictly above = high)
    median = sample_df["cpi"].median()
    result = assign_inflation_regime(sample_df, method="fixed", fixed_threshold=median)
    assert (result[result["cpi"] == median]["inflation_regime"] == "low").all()

def test_inflation_no_nans(sample_df):
    assert assign_inflation_regime(sample_df)["inflation_regime"].isna().sum() == 0

def test_inflation_no_nans_with_missing_cpi(df_with_nan_cpi):
    assert assign_inflation_regime(df_with_nan_cpi)["inflation_regime"].isna().sum() == 0

def test_inflation_does_not_modify_input(sample_df):
    original_cols = list(sample_df.columns)
    assign_inflation_regime(sample_df)
    assert list(sample_df.columns) == original_cols

def test_inflation_missing_column_raises(sample_df):
    with pytest.raises(ValueError, match="not found"):
        assign_inflation_regime(sample_df, inflation_col="nonexistent")

def test_inflation_unknown_method_raises(sample_df):
    with pytest.raises(ValueError, match="method must be"):
        assign_inflation_regime(sample_df, method="rolling")

def test_inflation_fixed_without_threshold_raises(sample_df):
    with pytest.raises(ValueError, match="fixed_threshold must be provided"):
        assign_inflation_regime(sample_df, method="fixed")


# ══════════════════════════════════════════════════════════════════════════════
# Rate regime tests (issue #65)
# ══════════════════════════════════════════════════════════════════════════════

def test_rate_rising_series_all_rising(rising_rates):
    result = classify_rate_regime(rising_rates)
    assert (result[1:] == "rising").all()

def test_rate_falling_series_all_falling(falling_rates):
    result = classify_rate_regime(falling_rates)
    assert (result[1:] == "falling").all()

def test_rate_flat_no_nans(flat_rates):
    result = classify_rate_regime(flat_rates)
    assert result.isna().sum() == 0

def test_rate_flat_only_valid_labels(flat_rates):
    result = classify_rate_regime(flat_rates)
    assert set(result.unique()).issubset({"rising", "falling"})

def test_rate_index_alignment(rising_rates):
    result = classify_rate_regime(rising_rates)
    assert list(result.index) == list(rising_rates.index)

def test_rate_no_nans_output(rising_rates):
    assert classify_rate_regime(rising_rates).isna().sum() == 0

def test_rate_rolling_slope_method(rising_rates):
    result = classify_rate_regime(rising_rates, method="rolling_slope", window=2)
    assert result.isna().sum() == 0
    assert set(result.unique()).issubset({"rising", "falling"})

def test_rate_unknown_method_raises(rising_rates):
    with pytest.raises(ValueError, match="method must be"):
        classify_rate_regime(rising_rates, method="ema")

def test_rate_invalid_window_raises(rising_rates):
    with pytest.raises(ValueError, match="window must be"):
        classify_rate_regime(rising_rates, window=1)

def test_rate_non_numeric_raises():
    with pytest.raises(ValueError, match="must be numeric"):
        classify_rate_regime(pd.Series(["a", "b", "c"]))

def test_assign_rate_regime_attaches_column(sample_df):
    result = assign_rate_regime(sample_df)
    assert "rate_regime" in result.columns

def test_assign_rate_regime_no_nans(sample_df):
    result = assign_rate_regime(sample_df)
    assert result["rate_regime"].isna().sum() == 0

def test_assign_rate_regime_missing_column_raises(sample_df):
    with pytest.raises(ValueError, match="not found"):
        assign_rate_regime(sample_df, rate_col="nonexistent")

def test_assign_rate_regime_does_not_modify_input(sample_df):
    original_cols = list(sample_df.columns)
    assign_rate_regime(sample_df)
    assert list(sample_df.columns) == original_cols


def test_assign_all_regimes_adds_expected_columns():
    df = pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=6),
            "ticker": ["XLK"] * 6,
            "sector_return": [0.01, 0.02, -0.01, 0.03, 0.00, 0.01],
            "cpi": [1, 2, 3, 4, 5, 6],
            "fedfunds": [1.0, 1.1, 1.2, 1.1, 1.0, 1.1],
            "vix": [10, 11, 12, None, 14, 15],
        }
    )

    result = assign_all_regimes(df)
    regime_cols = [
        "inflation_regime",
        "rate_regime",
        "macro_regime",
        "vix_regime",
    ]

    assert set(regime_cols).issubset(result.columns)
    assert result[regime_cols].isna().sum().sum() == 0
