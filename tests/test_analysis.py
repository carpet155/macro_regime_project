"""
tests/test_analysis.py

Unit tests for cross-sector correlation by regime (issue #74).
Run with:  pytest tests/test_analysis.py -v
"""

import pandas as pd
import numpy as np
import pytest

from src.macro_regime.analysis import sector_return_correlation_by_regime


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def toy_df():
    """Two regimes, three sectors, deterministic returns."""
    return pd.DataFrame({
        "regime": ["A", "A", "A", "A", "B", "B", "B", "B"],
        "X": [0.01, 0.02, 0.03, 0.04, 0.10, 0.08, 0.06, 0.04],
        "Y": [0.02, 0.04, 0.06, 0.08, 0.05, 0.04, 0.03, 0.02],
        "Z": [0.04, 0.03, 0.02, 0.01, 0.10, 0.08, 0.06, 0.04],
    })


@pytest.fixture
def return_cols():
    return ["X", "Y", "Z"]


# ── Correctness ──────────────────────────────────────────────────────────────

def test_known_correlations(toy_df, return_cols):
    """Regime A: X and Y perfectly correlated, X and Z perfectly neg."""
    corrs = sector_return_correlation_by_regime(toy_df, "regime", return_cols)

    mat_a = corrs["A"]
    assert mat_a.loc["X", "Y"] == pytest.approx(1.0)
    assert mat_a.loc["X", "Z"] == pytest.approx(-1.0)

    mat_b = corrs["B"]
    assert mat_b.loc["X", "Y"] == pytest.approx(1.0)
    assert mat_b.loc["X", "Z"] == pytest.approx(1.0)


def test_dict_has_one_key_per_regime(toy_df, return_cols):
    corrs = sector_return_correlation_by_regime(toy_df, "regime", return_cols)
    assert set(corrs.keys()) == {"A", "B"}


# ── Diagonal and symmetry ────────────────────────────────────────────────────

def test_diagonal_is_one(toy_df, return_cols):
    corrs = sector_return_correlation_by_regime(toy_df, "regime", return_cols)
    for mat in corrs.values():
        np.testing.assert_array_almost_equal(np.diag(mat.values), 1.0)


def test_symmetry(toy_df, return_cols):
    corrs = sector_return_correlation_by_regime(toy_df, "regime", return_cols)
    for mat in corrs.values():
        np.testing.assert_array_almost_equal(mat.values, mat.values.T)


def test_values_in_range(toy_df, return_cols):
    corrs = sector_return_correlation_by_regime(toy_df, "regime", return_cols)
    for mat in corrs.values():
        assert (mat.values >= -1.0 - 1e-10).all()
        assert (mat.values <= 1.0 + 1e-10).all()


# ── Column ordering ─────────────────────────────────────────────────────────

def test_index_matches_return_cols(toy_df, return_cols):
    corrs = sector_return_correlation_by_regime(toy_df, "regime", return_cols)
    for mat in corrs.values():
        assert list(mat.index) == return_cols
        assert list(mat.columns) == return_cols


# ── NaN / min_periods ────────────────────────────────────────────────────────

@pytest.fixture
def df_with_nans(toy_df):
    df = toy_df.copy()
    df.loc[0, "X"] = np.nan
    df.loc[1, "Y"] = np.nan
    return df


def test_nan_pairwise_default(df_with_nans, return_cols):
    """Default pairwise deletion still produces a matrix."""
    corrs = sector_return_correlation_by_regime(
        df_with_nans, "regime", return_cols,
    )
    mat_a = corrs["A"]
    # diagonal should still be 1
    np.testing.assert_array_almost_equal(np.diag(mat_a.values), 1.0)


def test_min_periods_produces_nan(df_with_nans, return_cols):
    """High min_periods should cause some cells to be NaN."""
    corrs = sector_return_correlation_by_regime(
        df_with_nans, "regime", return_cols, min_periods=4,
    )
    mat_a = corrs["A"]
    # X-Y pair has only 2 overlapping observations in regime A -> NaN
    assert np.isnan(mat_a.loc["X", "Y"])


# ── Input validation ─────────────────────────────────────────────────────────

def test_missing_regime_col_raises(toy_df, return_cols):
    with pytest.raises(ValueError, match="not found"):
        sector_return_correlation_by_regime(toy_df, "nonexistent", return_cols)


def test_missing_return_col_raises(toy_df):
    with pytest.raises(ValueError, match="not found"):
        sector_return_correlation_by_regime(toy_df, "regime", ["X", "missing"])


def test_missing_both_raises(toy_df):
    with pytest.raises(ValueError, match="not found"):
        sector_return_correlation_by_regime(toy_df, "bad", ["X", "missing"])


# ── MultiIndex output mode ──────────────────────────────────────────────────

def test_multiindex_output_shape(toy_df, return_cols):
    result = sector_return_correlation_by_regime(
        toy_df, "regime", return_cols, output="multiindex",
    )
    assert isinstance(result, pd.DataFrame)
    n_regimes = toy_df["regime"].nunique()
    n_cols = len(return_cols)
    assert len(result) == n_regimes * n_cols


def test_multiindex_matches_dict(toy_df, return_cols):
    """Both output modes should produce identical correlation values."""
    d = sector_return_correlation_by_regime(
        toy_df, "regime", return_cols, output="dict",
    )
    mi = sector_return_correlation_by_regime(
        toy_df, "regime", return_cols, output="multiindex",
    )
    for label, mat in d.items():
        mi_slice = mi.loc[label]
        pd.testing.assert_frame_equal(mat, mi_slice)


# ── Does not pull extra columns ──────────────────────────────────────────────

def test_extra_numeric_cols_excluded(toy_df, return_cols):
    """An extra numeric column in df must NOT appear in correlations."""
    df = toy_df.copy()
    df["noise"] = np.random.default_rng(0).normal(size=len(df))
    corrs = sector_return_correlation_by_regime(df, "regime", return_cols)
    for mat in corrs.values():
        assert "noise" not in mat.columns
        assert "noise" not in mat.index
import pandas as pd
import numpy as np
import pytest
from macro_regime.analysis import (
    regime_run_segments,
    regime_persistence_summary,
    average_sector_volatility_by_regime,
)

def test_constant_regime():
    df = pd.DataFrame({
        "date": pd.date_range("2020-01-01", periods=5),
        "regime": ["A"] * 5,
    })

    segments = regime_run_segments(df, "regime", "date")

    assert len(segments) == 1
    assert segments.loc[0, "duration_rows"] == 5

def test_volatility_aggregation_logic():
    df = pd.DataFrame({
        'macro_regime': ['High', 'High', 'Low', 'Low'],
        'vol_XLB': [0.10, 0.20, 0.05, 0.05],
        'vol_XLE': [0.40, 0.60, 0.10, 0.20]
    })
    
    vol_cols = ['vol_XLB', 'vol_XLE']
    result = average_sector_volatility_by_regime(df, 'macro_regime', vol_cols)
    
    assert result.loc['High', 'vol_XLB'] == pytest.approx(0.15)
    assert result.loc['Low', 'vol_XLE'] == pytest.approx(0.15)
    assert result.shape == (2, 2)

def test_missing_column_error():
    df = pd.DataFrame({'wrong_col': [1, 2, 3]})
    with pytest.raises(ValueError, match="Missing columns"):
        average_sector_volatility_by_regime(df, 'macro_regime', ['vol_XLB'])

def test_nan_regime_handling():
    df = pd.DataFrame({
        'macro_regime': ['High', None, 'Low'],
        'vol_XLB': [0.10, 0.50, 0.05]
    })
    result = average_sector_volatility_by_regime(df, 'macro_regime', ['vol_XLB'])
    
    assert len(result) == 2
    assert 'High' in result.index
    assert 'Low' in result.index
    assert result.loc['High', 'vol_XLB'] == 0.10
