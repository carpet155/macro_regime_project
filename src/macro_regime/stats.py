import pandas as pd
import numpy as np


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
