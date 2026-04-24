import pandas as pd
import numpy as np

def regime_run_segments(df: pd.DataFrame, regime_col: str, date_col: str):
    df = df.sort_values(date_col).reset_index(drop=True)
    change_points = df[regime_col].ne(df[regime_col].shift())
    segment_id = change_points.cumsum()

    segments = (
        df.groupby(segment_id)
        .agg(
            regime=(regime_col, "first"),
            start_date=(date_col, "first"),
            end_date=(date_col, "last"),
            duration_rows=(regime_col, "size"),
        )
        .reset_index(drop=True)
    )
    return segments

def regime_persistence_summary(segments: pd.DataFrame, *, duration_col: str = "duration_rows"):
    summary = (
        segments.groupby("regime")[duration_col]
        .agg(
            mean_duration="mean",
            median_duration="median",
            min_duration="min",
            max_duration="max",
            count_segments="count",
        )
        .reset_index()
    )
    return summary

def analyze_regime_persistence(df: pd.DataFrame, regime_col: str, date_col: str):
    segments = regime_run_segments(df, regime_col, date_col)
    summary = regime_persistence_summary(segments)
    return segments, summary

def average_sector_volatility_by_regime(
    df: pd.DataFrame, 
    regime_col: str = "macro_regime", 
    vol_cols: list[str] = None, 
    *, 
    min_obs_per_cell: int | None = None
) -> pd.DataFrame:
    if vol_cols is None:
        raise ValueError("vol_cols list must be provided.")
        
    required_cols = [regime_col] + vol_cols
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in DataFrame: {missing}")

    df_clean = df.dropna(subset=[regime_col])
    summary = df_clean.groupby(regime_col, observed=True)[vol_cols].mean()

    if min_obs_per_cell is not None:
        counts = df_clean.groupby(regime_col, observed=True)[vol_cols].count()
        summary = summary.where(counts >= min_obs_per_cell)

    return summary.astype(float)
