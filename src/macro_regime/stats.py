# Issue 59 

import pandas as pd
import numpy as np

def rolling_volatility(series, window = 20, ddof = 1):
    values = np.array(series, dtype = float) # Converts our input series into a NumPy array of type float 
    n = len(values)

    if window > n:
        result = np.full(n, np.nan) # If the window is larger than the number of data points, we return an array of NaNs of the same size as the input series
        return pd.Series(result, index = series.index) # Convert the result back to a Pandas Series with the same index as the input series
    
    windows = np.array([values[i:i + window] for i in range(n - window + 1)]) # Create a 2D array where each row is a rolling window of the input values

    volatilities = np.std(windows, axis = 1, ddof = ddof) # Calculate the standard deviation (volatility) for each rolling window. The ddof parameter allows us to specify the degrees of freedom for the standard deviation calculation.

    padding = np.full(window - 1, np.nan) # Create an array of NaNs to pad the beginning of the result, since the first (window - 1) values will not have enough data points to calculate volatility
    result = np.concatenate((padding, volatilities)) # Concatenate the padding with the calculated volatilities to create the final result array

    return pd.Series(result, index = series.index) # Convert the result back to a Pandas Series with the same index as the input series 
