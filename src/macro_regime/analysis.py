import pandas as pd

from src.macro_regime.analysis import (
    rank_sector_returns_within_regimes,
    sector_ranking_stability_from_raw,
)


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