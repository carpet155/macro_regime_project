"""
Data cleaning functions for the macro_regime project.
"""

import pandas as pd


def clean_dataframe(df, date_col="date", value_col="value", full_index=None):
    """
    
    Parameters
    df : pandas.DataFrame
        Input dataframe containing a date column and value column.
    date_col : str
        Name of the date column.
    value_col : str
        Name of the value column.
    full_index : pandas.DatetimeIndex or None
        Optional full date index to align to. If None, one is created
        from the min and max dates in the dataframe.

    """
    df = df.copy()

    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    df = df[[date_col, value_col]].drop_duplicates(subset=date_col)
    df = df.set_index(date_col)

    if full_index is None:
        full_index = pd.date_range(df.index.min(), df.index.max(), freq="D")

    df = df.reindex(full_index)
    df[value_col] = df[value_col].ffill()

    df.index.name = date_col
    return df.reset_index()