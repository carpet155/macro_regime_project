import numpy as np
import pandas as pd

from macro_regime.stats import rolling_volatility


def test_rolling_volatility_basic_window_behavior():
    """Rolling volatility should compute the sample standard deviation over the window."""
    returns = pd.Series([0.02, 0.04, 0.06, 0.08, 0.10])

    # For a fixed spacing of 0.02, the sample standard deviation over any 3-value
    # window is 0.02: values [0.02,0.04,0.06], [0.04,0.06,0.08], [0.06,0.08,0.10].
    expected = np.array([np.nan, np.nan, 0.02, 0.02, 0.02])

    result = rolling_volatility(returns, window=3).to_numpy()

    assert len(result) == len(returns), "Output length must match input length."
    assert np.isnan(result[0]) and np.isnan(result[1]), "Initial periods before the window is filled should be NaN."
    np.testing.assert_allclose(result[2:], expected[2:], rtol=1e-12, atol=1e-12)


def test_rolling_volatility_uses_sample_standard_deviation():
    """The function must use ddof=1 for sample standard deviation."""
    returns = pd.Series([0.01, -0.01, 0.03])

    # For window=2, sample std of [0.01, -0.01] is sqrt((0.0001 + 0.0001) / 1) = 0.0141421.
    # For window=2, sample std of [-0.01, 0.03] is sqrt((0.0004 + 0.0004) / 1) = 0.0282843.
    expected = np.array([np.nan, 0.01414213562373095, 0.0282842712474619])

    result = rolling_volatility(returns, window=2).to_numpy()

    assert np.isnan(result[0]), "The first output should be NaN for window=2."
    np.testing.assert_allclose(result[1:], expected[1:], rtol=1e-12, atol=1e-12)


def test_rolling_volatility_requires_full_window_when_missing_values_present():
    """Missing values inside the window should prevent a result until the full window is available."""
    returns = pd.Series([0.01, np.nan, 0.02, 0.03, 0.04])

    # Window=3 requires 3 non-missing values to compute a volatility. Because the
    # second value is NaN, the first valid rolling computation occurs after index 4.
    expected = np.array([np.nan, np.nan, np.nan, np.nan, 0.01])

    result = rolling_volatility(returns, window=3).to_numpy()

    assert len(result) == len(returns), "Output length must remain aligned with input."
    np.testing.assert_allclose(result, expected, rtol=1e-12, atol=1e-12)
