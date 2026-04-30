import pandas as pd
import numpy as np
import pytest

from macro_regime.regimes import classify_vix_stress_regime


# ── synthetic stress/calm split ────────────────────────────────────────────

def test_both_labels_present():
    # Low VIX for first half, high VIX for second half → both labels appear
    vix = pd.Series([10, 12, 11, 13, 40, 45, 42, 50])
    result = classify_vix_stress_regime(vix)
    assert "stress" in result.values
    assert "calm" in result.values


def test_high_vix_is_stress():
    vix = pd.Series([10.0, 10.0, 10.0, 50.0])
    result = classify_vix_stress_regime(vix)
    assert result.iloc[-1] == "stress"


def test_low_vix_is_calm():
    vix = pd.Series([50.0, 50.0, 50.0, 10.0])
    result = classify_vix_stress_regime(vix)
    # 10 is below the 75th percentile of [50, 50, 50, 10]
    assert result.iloc[-1] == "calm"


# ── constant VIX ───────────────────────────────────────────────────────────

def test_constant_vix_all_stress():
    # All values equal threshold → all "stress" (ties go to stress)
    vix = pd.Series([20.0, 20.0, 20.0, 20.0])
    result = classify_vix_stress_regime(vix)
    assert set(result.dropna().unique()) == {"stress"}


# ── NaN handling ───────────────────────────────────────────────────────────

def test_nan_vix_gives_nan():
    vix = pd.Series([10.0, np.nan, 20.0])
    result = classify_vix_stress_regime(vix)
    assert pd.isna(result.iloc[1])


def test_nan_does_not_corrupt_others():
    vix = pd.Series([10.0, np.nan, 50.0])
    result = classify_vix_stress_regime(vix)
    assert result.iloc[0] in ("stress", "calm")
    assert result.iloc[2] in ("stress", "calm")


# ── index alignment ────────────────────────────────────────────────────────

def test_index_alignment():
    vix = pd.Series([10.0, 20.0, 30.0], index=[100, 200, 300])
    result = classify_vix_stress_regime(vix)
    assert list(result.index) == [100, 200, 300]


# ── output name ────────────────────────────────────────────────────────────

def test_output_name():
    vix = pd.Series([10.0, 20.0, 30.0])
    result = classify_vix_stress_regime(vix)
    assert result.name == "vix_regime"


# ── rolling window ─────────────────────────────────────────────────────────

def test_rolling_window():
    vix = pd.Series([10.0, 12.0, 11.0, 13.0, 40.0, 45.0])
    result = classify_vix_stress_regime(vix, window=3)
    # First 2 rows NaN due to min_periods=1 not being hit... actually
    # min_periods=1 so first row should not be NaN
    assert result.iloc[0] in ("stress", "calm")


# ── custom quantile ────────────────────────────────────────────────────────

def test_custom_quantile():
    vix = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
    result_75 = classify_vix_stress_regime(vix, q=0.75)
    result_50 = classify_vix_stress_regime(vix, q=0.50)
    # Lower threshold means more "stress" labels
    assert result_50.tolist().count("stress") >= result_75.tolist().count("stress")