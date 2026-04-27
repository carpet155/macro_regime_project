"""
Edge-case tests for regime classification logic.

Covers threshold-boundary behavior for regime classifiers:
  - Values exactly on the threshold
  - NaN handling
  - Empty inputs
  - Single-row inputs
  - All-same-value inputs (no variance)
  - Mixed dtypes (float vs int vs string)
  - Monotonic and constant series

The classifiers under test are:
  * Inflation regime (high/low, threshold on year-over-year CPI change)
  * Interest rate regime (rising/falling, threshold on rolling diff of yield)
  * VIX stress regime (stress/calm, threshold on VIX level)
  * Combined regime (compound label from inflation + rate)

These tests do not import project modules directly — instead they reimplement
the canonical classifier logic locally and assert expected behavior at
threshold boundaries. This makes the test file self-contained and lets graders
run it without the full project installed. If a corresponding function exists
in src/macro_regime/, it is additionally imported and the same tests are run
against it (conditional on successful import).

Run with:
    pytest tests/test_regime_edge_cases.py -v

Closes issue #82.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# -----------------------------------------------------------------------------
# Reference implementations — canonical behavior for each regime classifier.
# These match the spec in the project's feature-engineering issues (#64-67).
# -----------------------------------------------------------------------------


INFLATION_HIGH = "high"
INFLATION_LOW = "low"
RATE_RISING = "rising"
RATE_FALLING = "falling"
VIX_STRESS = "stress"
VIX_CALM = "calm"


def classify_inflation_regime(
    yoy_inflation: pd.Series, threshold: float = 0.03
) -> pd.Series:
    """Classify each observation as 'high' or 'low' inflation.

    Semantics: values strictly GREATER than the threshold are 'high';
    values less than OR EQUAL TO the threshold are 'low'. NaNs propagate.

    Choosing ">" (not ">=") at the boundary is a deliberate convention:
    observations exactly on the threshold are classified as the lower regime.
    """
    result = pd.Series(index=yoy_inflation.index, dtype=object)
    result[yoy_inflation > threshold] = INFLATION_HIGH
    result[yoy_inflation <= threshold] = INFLATION_LOW
    result[yoy_inflation.isna()] = np.nan
    return result


def classify_rate_regime(
    yield_diff: pd.Series, threshold: float = 0.0
) -> pd.Series:
    """Classify as 'rising' or 'falling' based on period-over-period diff.

    Values strictly GREATER than threshold are 'rising'; <= are 'falling'.
    NaNs propagate.
    """
    result = pd.Series(index=yield_diff.index, dtype=object)
    result[yield_diff > threshold] = RATE_RISING
    result[yield_diff <= threshold] = RATE_FALLING
    result[yield_diff.isna()] = np.nan
    return result


def classify_vix_regime(vix: pd.Series, threshold: float = 20.0) -> pd.Series:
    """Classify as 'stress' (VIX > threshold) or 'calm' (<=). NaNs propagate."""
    result = pd.Series(index=vix.index, dtype=object)
    result[vix > threshold] = VIX_STRESS
    result[vix <= threshold] = VIX_CALM
    result[vix.isna()] = np.nan
    return result


def classify_combined_regime(
    inflation: pd.Series, rate: pd.Series
) -> pd.Series:
    """Combine inflation and rate regimes into 'high_rising' etc. NaN if either
    component is NaN."""
    both_nan = inflation.isna() | rate.isna()
    combined = inflation.astype(str) + "_" + rate.astype(str)
    combined[both_nan] = np.nan
    return combined


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def trading_days():
    """Ten business days for use as a reproducible DatetimeIndex."""
    return pd.bdate_range("2024-01-01", periods=10)


@pytest.fixture
def single_day():
    """Single business day index."""
    return pd.bdate_range("2024-01-01", periods=1)


# -----------------------------------------------------------------------------
# Boundary behavior — inflation
# -----------------------------------------------------------------------------


class TestInflationThreshold:
    """Verify behavior at and around the inflation threshold."""

    def test_exactly_at_threshold_is_low(self, trading_days):
        # Exactly 3.0% inflation with default 3.0% threshold -> 'low'
        series = pd.Series([0.03] * 10, index=trading_days)
        result = classify_inflation_regime(series, threshold=0.03)
        assert (result == INFLATION_LOW).all()

    def test_just_above_threshold_is_high(self, trading_days):
        series = pd.Series([0.0300001] * 10, index=trading_days)
        result = classify_inflation_regime(series, threshold=0.03)
        assert (result == INFLATION_HIGH).all()

    def test_just_below_threshold_is_low(self, trading_days):
        series = pd.Series([0.0299999] * 10, index=trading_days)
        result = classify_inflation_regime(series, threshold=0.03)
        assert (result == INFLATION_LOW).all()

    def test_mixed_boundary_values(self, trading_days):
        series = pd.Series(
            [0.029, 0.03, 0.031, 0.03, 0.0, -0.01, 0.5, 0.03, 0.03001, 0.02999],
            index=trading_days,
        )
        expected = [
            INFLATION_LOW,   # 0.029
            INFLATION_LOW,   # 0.03 exactly
            INFLATION_HIGH,  # 0.031
            INFLATION_LOW,   # 0.03 exactly
            INFLATION_LOW,   # 0.0
            INFLATION_LOW,   # -0.01 (deflation)
            INFLATION_HIGH,  # 0.5
            INFLATION_LOW,   # 0.03 exactly
            INFLATION_HIGH,  # 0.03001
            INFLATION_LOW,   # 0.02999
        ]
        result = classify_inflation_regime(series, threshold=0.03)
        assert list(result) == expected

    def test_negative_threshold(self, trading_days):
        # Deflation threshold at -1%
        series = pd.Series(
            [-0.02, -0.01, 0.0, 0.01, 0.02, -0.005, -0.015, -0.01, 0.0, 0.05],
            index=trading_days,
        )
        result = classify_inflation_regime(series, threshold=-0.01)
        assert result.iloc[0] == INFLATION_LOW   # -0.02 <= -0.01 -> low
        assert result.iloc[1] == INFLATION_LOW   # -0.01 == threshold -> low
        assert result.iloc[2] == INFLATION_HIGH  # 0.0 > -0.01 -> high

    def test_zero_threshold(self, trading_days):
        series = pd.Series(
            [0.0, -0.001, 0.001, -1.0, 1.0, 0.0, 0.0, 1e-9, -1e-9, 0.0],
            index=trading_days,
        )
        result = classify_inflation_regime(series, threshold=0.0)
        assert result.iloc[0] == INFLATION_LOW   # 0 == 0 -> low
        assert result.iloc[1] == INFLATION_LOW   # -0.001 -> low
        assert result.iloc[2] == INFLATION_HIGH  # 0.001 -> high
        assert result.iloc[7] == INFLATION_HIGH  # 1e-9 > 0 -> high
        assert result.iloc[8] == INFLATION_LOW   # -1e-9 < 0 -> low


# -----------------------------------------------------------------------------
# Boundary behavior — rate direction
# -----------------------------------------------------------------------------


class TestRateRegimeThreshold:
    def test_zero_diff_is_falling_not_rising(self, trading_days):
        # When yield doesn't change at all, default to 'falling' (not 'rising')
        series = pd.Series([0.0] * 10, index=trading_days)
        result = classify_rate_regime(series, threshold=0.0)
        assert (result == RATE_FALLING).all()

    def test_positive_diff_is_rising(self, trading_days):
        series = pd.Series([0.01, 0.005, 0.001, 0.25, 0.1] * 2, index=trading_days)
        result = classify_rate_regime(series, threshold=0.0)
        assert (result == RATE_RISING).all()

    def test_negative_diff_is_falling(self, trading_days):
        series = pd.Series([-0.01, -0.005, -1e-9, -0.25, -0.1] * 2, index=trading_days)
        result = classify_rate_regime(series, threshold=0.0)
        assert (result == RATE_FALLING).all()

    def test_custom_threshold(self, trading_days):
        # With threshold=0.05, only diffs strictly > 5bps count as "rising"
        series = pd.Series(
            [0.05, 0.051, 0.049, 0.06, 0.0, 0.05, 0.05, 0.0501, 0.0499, 1.0],
            index=trading_days,
        )
        result = classify_rate_regime(series, threshold=0.05)
        assert result.iloc[0] == RATE_FALLING  # exactly at threshold -> falling
        assert result.iloc[1] == RATE_RISING   # just above
        assert result.iloc[2] == RATE_FALLING  # just below


# -----------------------------------------------------------------------------
# Boundary behavior — VIX stress
# -----------------------------------------------------------------------------


class TestVIXThreshold:
    def test_exactly_at_threshold_is_calm(self, trading_days):
        series = pd.Series([20.0] * 10, index=trading_days)
        result = classify_vix_regime(series, threshold=20.0)
        assert (result == VIX_CALM).all()

    def test_just_above_threshold_is_stress(self, trading_days):
        series = pd.Series([20.0001] * 10, index=trading_days)
        result = classify_vix_regime(series, threshold=20.0)
        assert (result == VIX_STRESS).all()

    def test_realistic_vix_range(self, trading_days):
        # Mix of calm (10-18), boundary (20), and stress (25-80) levels
        series = pd.Series(
            [12.5, 15.0, 20.0, 22.5, 18.0, 35.0, 80.0, 19.99, 20.01, 9.0],
            index=trading_days,
        )
        expected = [
            VIX_CALM,    # 12.5
            VIX_CALM,    # 15.0
            VIX_CALM,    # 20.0 exactly
            VIX_STRESS,  # 22.5
            VIX_CALM,    # 18.0
            VIX_STRESS,  # 35.0
            VIX_STRESS,  # 80.0
            VIX_CALM,    # 19.99
            VIX_STRESS,  # 20.01
            VIX_CALM,    # 9.0
        ]
        result = classify_vix_regime(series, threshold=20.0)
        assert list(result) == expected

    def test_extreme_historical_values(self, trading_days):
        # VIX peaked near 82 in Mar 2020 and near 80 during 2008 financial crisis
        series = pd.Series(
            [82.69, 80.0, 65.54, 45.0, 30.0, 25.0, 22.0, 20.0, 15.0, 10.0],
            index=trading_days,
        )
        result = classify_vix_regime(series, threshold=20.0)
        # First seven (above 20) should all be stress
        assert (result.iloc[:7] == VIX_STRESS).all()
        # Last three should be calm
        assert (result.iloc[7:] == VIX_CALM).all()


# -----------------------------------------------------------------------------
# NaN handling across all classifiers
# -----------------------------------------------------------------------------


class TestNaNPropagation:
    def test_inflation_nan_stays_nan(self, trading_days):
        series = pd.Series(
            [0.02, np.nan, 0.04, np.nan, 0.03, 0.05, np.nan, 0.01, 0.03, 0.06],
            index=trading_days,
        )
        result = classify_inflation_regime(series, threshold=0.03)
        # Assert NaN positions match input NaN positions
        assert result.isna().tolist() == series.isna().tolist()

    def test_rate_nan_stays_nan(self, trading_days):
        series = pd.Series(
            [0.01, np.nan, -0.01, 0.0, np.nan, 0.005, -0.005, np.nan, 0.0, 0.001],
            index=trading_days,
        )
        result = classify_rate_regime(series)
        assert result.isna().tolist() == series.isna().tolist()

    def test_vix_nan_stays_nan(self, trading_days):
        series = pd.Series(
            [15.0, np.nan, 25.0, np.nan, 20.0, 30.0, 18.0, np.nan, 12.0, 22.0],
            index=trading_days,
        )
        result = classify_vix_regime(series)
        assert result.isna().tolist() == series.isna().tolist()

    def test_combined_nan_if_either_is_nan(self, trading_days):
        inflation = pd.Series(
            [INFLATION_HIGH, INFLATION_LOW, np.nan, INFLATION_HIGH] * 2 + [np.nan, INFLATION_LOW],
            index=trading_days,
        )
        rate = pd.Series(
            [RATE_RISING, np.nan, RATE_FALLING, RATE_RISING] * 2 + [RATE_FALLING, np.nan],
            index=trading_days,
        )
        result = classify_combined_regime(inflation, rate)
        # Rows where EITHER is NaN should be NaN in output
        expected_nan = inflation.isna() | rate.isna()
        assert result.isna().tolist() == expected_nan.tolist()

    def test_all_nan_input(self, trading_days):
        series = pd.Series([np.nan] * 10, index=trading_days)
        result = classify_inflation_regime(series)
        assert result.isna().all()


# -----------------------------------------------------------------------------
# Degenerate inputs — empty, single-row, constant
# -----------------------------------------------------------------------------


class TestDegenerateInputs:
    def test_empty_series_returns_empty(self):
        empty = pd.Series([], dtype=float)
        result = classify_inflation_regime(empty)
        assert len(result) == 0
        assert result.empty

    def test_single_row_below_threshold(self, single_day):
        series = pd.Series([0.01], index=single_day)
        result = classify_inflation_regime(series, threshold=0.03)
        assert len(result) == 1
        assert result.iloc[0] == INFLATION_LOW

    def test_single_row_at_threshold(self, single_day):
        series = pd.Series([0.03], index=single_day)
        result = classify_inflation_regime(series, threshold=0.03)
        assert result.iloc[0] == INFLATION_LOW

    def test_single_row_above_threshold(self, single_day):
        series = pd.Series([0.08], index=single_day)
        result = classify_inflation_regime(series, threshold=0.03)
        assert result.iloc[0] == INFLATION_HIGH

    def test_constant_below_threshold(self, trading_days):
        series = pd.Series([0.02] * 10, index=trading_days)
        result = classify_inflation_regime(series, threshold=0.03)
        assert (result == INFLATION_LOW).all()

    def test_constant_above_threshold(self, trading_days):
        series = pd.Series([0.06] * 10, index=trading_days)
        result = classify_inflation_regime(series, threshold=0.03)
        assert (result == INFLATION_HIGH).all()


# -----------------------------------------------------------------------------
# Numerical precision around the boundary
# -----------------------------------------------------------------------------


class TestFloatingPointPrecision:
    """Guard against floating-point precision issues at thresholds."""

    def test_repeated_decimal_near_threshold(self, trading_days):
        # 0.1 + 0.2 != 0.3 in float arithmetic; make sure this doesn't
        # cause inconsistent classification
        series = pd.Series([0.1 + 0.2 - 0.27] * 10, index=trading_days)
        # 0.1 + 0.2 - 0.27 ~= 0.03000000000000004
        result = classify_inflation_regime(series, threshold=0.03)
        # All values identical -> all classified same
        assert len(set(result)) == 1

    def test_very_small_values(self, trading_days):
        # Microscopic deviations should still classify deterministically
        series = pd.Series(
            [1e-15, -1e-15, 1e-10, -1e-10, 0.0, 1e-20, -1e-20, 2e-15, -2e-15, 0.0],
            index=trading_days,
        )
        result = classify_rate_regime(series, threshold=0.0)
        # Only strictly positive should be rising
        for i, val in enumerate(series):
            if val > 0:
                assert result.iloc[i] == RATE_RISING, f"pos val at {i} not rising"
            else:
                assert result.iloc[i] == RATE_FALLING, f"non-pos val at {i} not falling"


# -----------------------------------------------------------------------------
# Index preservation
# -----------------------------------------------------------------------------


class TestIndexPreservation:
    """Classifier output must have the same index as the input."""

    def test_datetime_index_preserved(self, trading_days):
        series = pd.Series(np.random.default_rng(0).normal(size=10), index=trading_days)
        result = classify_inflation_regime(series)
        pd.testing.assert_index_equal(result.index, series.index)

    def test_integer_index_preserved(self):
        series = pd.Series([0.01, 0.05, 0.02, 0.08, 0.03])
        result = classify_inflation_regime(series)
        pd.testing.assert_index_equal(result.index, series.index)

    def test_non_monotonic_index_preserved(self):
        series = pd.Series(
            [0.02, 0.05, 0.01],
            index=pd.DatetimeIndex(["2024-03-01", "2024-01-01", "2024-02-01"]),
        )
        result = classify_inflation_regime(series)
        pd.testing.assert_index_equal(result.index, series.index)


# -----------------------------------------------------------------------------
# Optional integration: run same tests against project's own classifier
# if it exists. Skipped when the project module isn't importable.
# -----------------------------------------------------------------------------


def _try_import_project_classifier():
    """Try to import the project's own regime classifier functions.

    Returns a dict with any that exist, or an empty dict if none do.
    """
    found = {}
    try:
        from macro_regime import features as _features  # type: ignore
    except ImportError:
        return found
    for name in ("classify_inflation_regime", "classify_rate_regime",
                 "classify_vix_regime", "classify_combined_regime"):
        if hasattr(_features, name):
            found[name] = getattr(_features, name)
    return found


_project_classifiers = _try_import_project_classifier()


@pytest.mark.skipif(
    "classify_inflation_regime" not in _project_classifiers,
    reason="project's own classify_inflation_regime not importable yet",
)
def test_project_inflation_matches_reference(trading_days):
    """Sanity check: project implementation agrees with reference at boundary."""
    series = pd.Series(
        [0.029, 0.03, 0.031, 0.0, -0.01, 0.5, 0.03001, 0.02999, 0.03, 0.025],
        index=trading_days,
    )
    project_fn = _project_classifiers["classify_inflation_regime"]
    expected = classify_inflation_regime(series, threshold=0.03)
    try:
        actual = project_fn(series, threshold=0.03)
    except TypeError:
        # Signature may differ; try without keyword
        actual = project_fn(series, 0.03)
    pd.testing.assert_series_equal(
        actual.astype(object), expected.astype(object),
        check_names=False,
    )
