import numpy as np
import pandas as pd


def rank_sector_returns_within_regimes(
    summary: pd.DataFrame,
    *,
    ascending_returns: bool = False,
    tie_method: str = "first",
) -> pd.DataFrame:
    rankings = summary.rank(
        axis=1,
        ascending=ascending_returns,
        method=tie_method,
        na_option="keep",
    )
    return rankings.astype("Int64")


def sector_ranking_stability(rankings: pd.DataFrame) -> pd.DataFrame:
    return rankings.T.corr(method="spearman")


def sector_ranking_stability_from_raw(
    df: pd.DataFrame,
    regime_col: str,
    sector_cols: list[str],
):
    summary = df.groupby(regime_col)[sector_cols].mean()
    rankings = rank_sector_returns_within_regimes(summary)
    stability = sector_ranking_stability(rankings)
    return rankings, stability


def regime_run_segments(df: pd.DataFrame, regime_col: str, date_col: str) -> pd.DataFrame:
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col).reset_index(drop=True)

    change_points = df[regime_col].ne(df[regime_col].shift())
    segment_id = change_points.cumsum()

    segments = (
        df.groupby(segment_id)
        .agg(
            regime=(regime_col, "first"),
            start_date=(date_col, "min"),
            end_date=(date_col, "max"),
            duration_rows=(date_col, "count"),
        )
        .reset_index(drop=True)
    )

    return segments


def regime_persistence_summary(
    segments: pd.DataFrame,
    *,
    duration_col: str = "duration_rows",
) -> pd.DataFrame:
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


def analyze_regime_persistence(
    df: pd.DataFrame,
    regime_col: str,
    date_col: str,
):
    segments = regime_run_segments(df, regime_col, date_col)
    summary = regime_persistence_summary(segments)
    return segments, summary


def average_sector_volatility_by_regime(
    df: pd.DataFrame,
    regime_col: str = "macro_regime",
    vol_cols: list[str] | None = None,
    *,
    min_obs_per_cell: int | None = None,
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