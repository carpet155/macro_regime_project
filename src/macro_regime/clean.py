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
import pandas as pd

def standardize_bday_index(df: pd.DataFrame, date_col: str = 'date') -> pd.DataFrame:
    """
    Standardizes a dataframe's date column to a continuous business-day frequency.
    Leaves missing values as NaN for downstream handling.

    IMPORTANT USAGE NOTE:
    This function requires datasets to be in a "wide" format (one unique date per row).
    Standard macroeconomic datasets (SP500, CPI, VIX, etc.) can be passed in directly.
    
    For "long" format datasets (like sector_prices.csv), you MUST pivot the data 
    BEFORE passing it to this function. Example:
    
    >>> wide_sector = sector_df.pivot(index='date', columns='ticker', values='close').reset_index()
    >>> clean_sector = standardize_bday_index(wide_sector)
    """
    df = df.copy()
    
    # 1. Ensure the date column is standardly named 'date'
    if date_col != 'date':
        df = df.rename(columns={date_col: 'date'})
        
    # Convert to pandas datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # 2. Sort by date ascending
    df = df.sort_values(by='date')
    
    # 3. Align to business day frequency (freq="B")
    # Temporarily set the date as the index so we can use reindex()
    df = df.set_index('date')
    
    min_date = df.index.min()
    max_date = df.index.max()
    bday_range = pd.date_range(start=min_date, end=max_date, freq="B")
    
    # 4. Preserve missing values
    # reindex() automatically inserts NaNs for any new business days that didn't exist in the original data.
    # It does NOT forward-fill or interpolate unless you explicitly tell it to.
    df = df.reindex(bday_range)
    
    # Reset index and rename the newly created index column back to 'date'
    df = df.reset_index().rename(columns={'index': 'date'})
    
    return df
