import pandas as pd
import numpy as np

def average_sector_volatility_by_regime(
    df: pd.DataFrame, 
    regime_col: str = "macro_regime", 
    vol_cols: list[str] = None, 
    *, 
    min_obs_per_cell: int | None = None
) -> pd.DataFrame:
    """
    Summarizes average sector rolling volatility conditional on a regime column.
    
    Args:
        df: The merged master DataFrame.
        regime_col: The column name for macro regimes (e.g., 'inflation_regime').
        vol_cols: List of precomputed rolling volatility columns (e.g., ['vol_XLB']).
        min_obs_per_cell: Minimum observations required in a regime to compute a mean.
        
    Returns:
        pd.DataFrame: A tidy summary with regimes as rows and sectors as columns.
    """
    # 1. Validation: Fail fast if columns are missing
    if vol_cols is None:
        raise ValueError("vol_cols list must be provided.")
        
    required_cols = [regime_col] + vol_cols
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in DataFrame: {missing}")

    # 2. NA Handling: Drop rows where regime is NaN (as per requirements)
    # We use skipna=True (default in .mean()) for volatility columns
    df_clean = df.dropna(subset=[regime_col])

    # 3. Vectorized Aggregation: No Python loops over dates or sectors
    # observed=True handles categorical data correctly
    summary = df_clean.groupby(regime_col, observed=True)[vol_cols].mean()

    if min_obs_per_cell is not None:
        counts = df_clean.groupby(regime_col, observed=True)[vol_cols].count()
        summary = summary.where(counts >= min_obs_per_cell)

    return summary.astype(float)