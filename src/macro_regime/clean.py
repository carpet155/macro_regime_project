import pandas as pd
import numpy as np

def clean_sector_returns(df):
    """
    Handles missing values in sector return data using forward fill.
    Ensures no cross-contamination between different tickers.
    """
    # Sort by ticker and date to ensure chronological forward fill
    df = df.sort_values(['ticker', 'date'])

    # Requirement 3: Apply by sector (groupby ticker)
    # Requirement 2: Option A - Forward fill (ffill)
    df['return'] = df.groupby('ticker')['return'].ffill()

    return df