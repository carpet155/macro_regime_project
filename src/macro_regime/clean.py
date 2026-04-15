"""
Data cleaning functions for the macro_regime project.
"""

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

def align_inflation_to_daily(df: pd.DataFrame, date_col: str = "date", value_col: str = "value") -> pd.DataFrame:
    """
    Convert monthly CPI data to daily business-day frequency using forward fill.

    Each monthly CPI value is carried forward across all business days until
    the next monthly release — matching how macro data is interpreted in markets.

    Args:
        df: DataFrame with monthly CPI data (e.g. CPIAUCSL).
        date_col:  Name of the date column. Default is "date".
        value_col: Name of the CPI value column. Default is "value".

    Returns:
        DataFrame with one row per business day, no missing values within
        the original date range. Columns: [date_col, value_col].
    """
    df = df.copy()

    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()

    start = df.index.min()
    end = df.index.max()
    biz_day_index = pd.date_range(start=start, end=end, freq="B")

    df = df.reindex(biz_day_index)
    df[value_col] = df[value_col].ffill()

    df = df.reset_index().rename(columns={"index": date_col})

    return df[[date_col, value_col]]