import numpy as np
import pandas as pd

from macro_regime.stats import calculate_daily_returns


def test_calculate_daily_returns_simple_known_values():
    """Simple returns should match manually computed values for a small series."""
    prices = pd.Series([100.0, 105.0, 102.0, 104.0])

    expected = np.array([
        np.nan,
        0.05,
        -0.02857142857142857,
        0.0196078431372549,
    ])

    result = calculate_daily_returns(prices, method="simple").to_numpy()

    assert np.isnan(result[0]), "The first return should always be NaN."
    np.testing.assert_allclose(result[1:], expected[1:], rtol=1e-12, atol=1e-12)


def test_calculate_daily_returns_log_known_values():
    """Log returns should equal log(current / previous) for each step."""
    prices = pd.Series([100.0, 105.0, 102.0, 104.0])

    expected = np.array([
        np.nan,
        np.log(105.0 / 100.0),
        np.log(102.0 / 105.0),
        np.log(104.0 / 102.0),
    ])

    result = calculate_daily_returns(prices, method="log").to_numpy()

    assert np.isnan(result[0]), "The first log return should be NaN."
    np.testing.assert_allclose(result[1:], expected[1:], rtol=1e-12, atol=1e-12)


def test_calculate_daily_returns_handles_missing_values():
    """Missing prices should produce NaN returns and still allow later valid steps."""
    prices = pd.Series([100.0, np.nan, 102.0, 104.0])

    expected_simple = np.array([
        np.nan,
        np.nan,
        np.nan,
        (104.0 / 102.0) - 1.0,
    ])

    expected_log = np.array([
        np.nan,
        np.nan,
        np.nan,
        np.log(104.0 / 102.0),
    ])

    result_simple = calculate_daily_returns(prices, method="simple").to_numpy()
    result_log = calculate_daily_returns(prices, method="log").to_numpy()

    assert np.isnan(result_simple[0]) and np.isnan(result_simple[1])
    assert np.isnan(result_log[0]) and np.isnan(result_log[1])
    np.testing.assert_allclose(result_simple[3], expected_simple[3], rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(result_log[3], expected_log[3], rtol=1e-12, atol=1e-12)
