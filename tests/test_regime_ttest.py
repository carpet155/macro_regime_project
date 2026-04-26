import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from macro_regime.stats import ttest_sector_returns_between_regimes


def test_ttest_sector_returns_between_regimes_detects_difference():
    df = pd.DataFrame(
        {
            "inflation_regime": ["high"] * 5 + ["low"] * 5,
            "Tech": [10, 11, 9, 10, 12, 1, 2, 0, 1, 3],
            "Energy": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
        }
    )

    result = ttest_sector_returns_between_regimes(
        df,
        regime_col="inflation_regime",
        return_cols=["Tech", "Energy"],
        regime_a="high",
        regime_b="low",
        min_n=2,
    )

    assert result.loc["Tech", "n_regime_a"] == 5
    assert result.loc["Tech", "n_regime_b"] == 5
    assert result.loc["Tech", "t_statistic"] > 0
    assert result.loc["Tech", "p_value"] < 0.05


def test_ttest_sector_returns_between_regimes_equal_means():
    df = pd.DataFrame(
        {
            "inflation_regime": ["high"] * 4 + ["low"] * 4,
            "Tech": [1, 2, 3, 4, 1, 2, 3, 4],
        }
    )

    result = ttest_sector_returns_between_regimes(
        df,
        regime_col="inflation_regime",
        return_cols=["Tech"],
        regime_a="high",
        regime_b="low",
        min_n=2,
    )

    assert np.isclose(result.loc["Tech", "t_statistic"], 0.0)
    assert result.loc["Tech", "p_value"] > 0.9


def test_ttest_sector_returns_between_regimes_insufficient_sample():
    df = pd.DataFrame(
        {
            "inflation_regime": ["high", "high", "low"],
            "Tech": [1.0, 2.0, 3.0],
        }
    )

    result = ttest_sector_returns_between_regimes(
        df,
        regime_col="inflation_regime",
        return_cols=["Tech"],
        regime_a="high",
        regime_b="low",
        min_n=2,
    )

    assert result.loc["Tech", "n_regime_a"] == 2
    assert result.loc["Tech", "n_regime_b"] == 1
    assert pd.isna(result.loc["Tech", "t_statistic"])
    assert pd.isna(result.loc["Tech", "p_value"])


def test_ttest_sector_returns_between_regimes_omits_nans():
    df = pd.DataFrame(
        {
            "inflation_regime": ["high", "high", "high", "low", "low", "low"],
            "Tech": [1.0, np.nan, 3.0, 1.0, 2.0, np.nan],
        }
    )

    result = ttest_sector_returns_between_regimes(
        df,
        regime_col="inflation_regime",
        return_cols=["Tech"],
        regime_a="high",
        regime_b="low",
        min_n=2,
    )

    assert result.loc["Tech", "n_regime_a"] == 2
    assert result.loc["Tech", "n_regime_b"] == 2


def test_ttest_sector_returns_between_regimes_unknown_label_raises():
    df = pd.DataFrame(
        {
            "inflation_regime": ["high", "high", "low", "low"],
            "Tech": [1.0, 2.0, 3.0, 4.0],
        }
    )

    try:
        ttest_sector_returns_between_regimes(
            df,
            regime_col="inflation_regime",
            return_cols=["Tech"],
            regime_a="missing",
            regime_b="low",
            min_n=2,
        )
        assert False, "Expected ValueError for unknown regime_a label."
    except ValueError as exc:
        assert "regime_a" in str(exc)