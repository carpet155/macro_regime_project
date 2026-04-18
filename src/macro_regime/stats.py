import pandas as pd
import numpy as np

def calculate_daily_returns(series, method='simple'):

    prices = np.array(series, dtype = float) # This converts the input series to a Numpy array of floats.
    ratios = prices[1:] / prices[:-1] # This comuptes the ratio of each price to the previous price. 

    if method == "log":
        returns = np.log(ratios) # This computes the log returns by taking the natural logarithm of the ratios.
    else: 
        returns = ratios - 1 # A simpler computation for simple returns

    result = np.insert(returns, 0, np.nan) # This inserts an NaN at the beginning of the returns array to account for the first price which has no previous price to compare to.

    return pd.Series(result, index = series.index) # This converts the result back to a Pandas Series, using the same index as the input series.