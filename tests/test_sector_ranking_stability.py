import pandas as pd

from macro_regime.analysis import (
    rank_sector_returns_within_regimes,
    sector_ranking_stability_from_raw,
)

def test_rank_sector_returns_within_regimes_basic():
    summary = pd.DataFrame(
        {
            "Tech": [0.10, 0.03],
            "Energy": [0.05, 0.07],
            "Health": [0.02, 0.01],
        },
        index=["Regime_A", "Regime_B"],
    )

    rankings = rank_sector_returns_within_regimes(summary)

    expected = pd.DataFrame(
        {
            "Tech": pd.array([1, 2], dtype="Int64"),
            "Energy": pd.array([2, 1], dtype="Int64"),
            "Health": pd.array([3, 3], dtype="Int64"),
        },
        index=["Regime_A", "Regime_B"],
    )

    pd.testing.assert_frame_equal(rankings, expected)


def test_rank_sector_returns_within_regimes_tie_first():
    summary = pd.DataFrame(
        {
            "Tech": [0.10],
            "Energy": [0.10],
            "Health": [0.05],
        },
        index=["Regime_A"],
    )

    rankings = rank_sector_returns_within_regimes(summary)

    expected = pd.DataFrame(
        {
            "Tech": pd.array([1], dtype="Int64"),
            "Energy": pd.array([2], dtype="Int64"),
            "Health": pd.array([3], dtype="Int64"),
        },
        index=["Regime_A"],
    )

    pd.testing.assert_frame_equal(rankings, expected)


def test_sector_ranking_stability_from_raw():
    df = pd.DataFrame(
        {
            "regime": ["A", "A", "B", "B"],
            "Tech": [0.10, 0.20, 0.02, 0.04],
            "Energy": [0.03, 0.05, 0.10, 0.08],
            "Health": [0.01, 0.02, 0.00, 0.01],
        }
    )

    rankings, stability = sector_ranking_stability_from_raw(
        df,
        regime_col="regime",
        sector_cols=["Tech", "Energy", "Health"],
    )

    expected_rankings = pd.DataFrame(
        {
            "Tech": pd.array([1, 2], dtype="Int64"),
            "Energy": pd.array([2, 1], dtype="Int64"),
            "Health": pd.array([3, 3], dtype="Int64"),
        },
        index=["A", "B"],
    )

    pd.testing.assert_frame_equal(rankings, expected_rankings)
    assert stability.loc["A", "A"] == 1.0
    assert stability.loc["B", "B"] == 1.0