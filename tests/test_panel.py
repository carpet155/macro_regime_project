from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from macro_regime.build import build_master_df
from macro_regime.panel import build_panel_df, build_wide_panel_df, pivot_panel_wide


# ---------------------------------------------------------------------------
# Synthetic fixtures
# ---------------------------------------------------------------------------
# These helpers build a minimal processed_dir on disk so ``build_panel_df``
# can be exercised end-to-end without depending on the real data under
# ``data/processed/``. The schemas match what ``build_master_df`` expects:
#   inflation_processed.csv : date, value
#   treasury_processed.csv  : date, dgs2, dgs10, fedfunds
#   vix_processed.csv       : date, vix
#   spx_processed.csv       : date, price, return
#   sectors_processed.csv   : date, ticker, price, return, name

_DATES = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"])
_SECTORS = [
    ("XLE", "energy"),
    ("XLK", "technology"),
    ("XLF", "financials"),
]


def _write_processed_csvs(processed_dir: Path) -> None:
    """Write a synthetic set of processed feature CSVs into processed_dir/features."""
    features_dir = processed_dir / "features"
    features_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame({"date": _DATES, "value": [258.0, 258.1, 258.2]}).to_csv(
        features_dir / "inflation_processed.csv", index=False
    )

    pd.DataFrame({
        "date": _DATES,
        "dgs2":     [1.58, 1.55, 1.52],
        "dgs10":    [1.88, 1.85, 1.81],
        "fedfunds": [1.55, 1.55, 1.55],
    }).to_csv(features_dir / "treasury_processed.csv", index=False)

    pd.DataFrame({"date": _DATES, "vix": [12.47, 12.97, 13.85]}).to_csv(
        features_dir / "vix_processed.csv", index=False
    )

    pd.DataFrame({
        "date":   _DATES,
        "price":  [3257.85, 3234.85, 3246.28],
        "return": [np.nan, -0.007059, 0.003533],
    }).to_csv(features_dir / "spx_processed.csv", index=False)

    rows = []
    for ticker, name in _SECTORS:
        base = {"XLE": 60.0, "XLK": 100.0, "XLF": 30.0}[ticker]
        for i, date in enumerate(_DATES):
            rows.append({
                "date":   date,
                "ticker": ticker,
                "price":  base + i,
                "return": np.nan if i == 0 else (base + i) / (base + i - 1) - 1.0,
                "name":   name,
            })
    pd.DataFrame(rows).to_csv(
        features_dir / "sectors_processed.csv", index=False
    )


@pytest.fixture
def processed_dir(tmp_path: Path) -> Path:
    """A tmp processed_dir populated with synthetic CSVs."""
    processed_root = tmp_path / "processed"
    _write_processed_csvs(processed_root)
    return processed_root


@pytest.fixture
def panel(processed_dir: Path) -> pd.DataFrame:
    """A panel DataFrame built from the synthetic processed_dir."""
    return build_panel_df(str(processed_dir))


def test_build_master_df_missing_processed_file_raises(tmp_path):
    processed_root = tmp_path / "processed"
    features_dir = processed_root / "features"
    features_dir.mkdir(parents=True)

    with pytest.raises(FileNotFoundError, match="Missing processed file"):
        build_master_df(str(processed_root))


def test_build_master_df_missing_required_column_raises(processed_dir):
    inflation_path = processed_dir / "features" / "inflation_processed.csv"
    pd.DataFrame({"date": _DATES, "wrong_value": [258.0, 258.1, 258.2]}).to_csv(
        inflation_path,
        index=False,
    )

    with pytest.raises(ValueError, match="missing required column"):
        build_master_df(str(processed_dir))


# ---------------------------------------------------------------------------
# Tests: build_panel_df
# ---------------------------------------------------------------------------

def test_multiindex_has_two_levels_named_date_ticker(panel):
    assert panel.index.nlevels == 2
    assert list(panel.index.names) == ["date", "ticker"]


def test_no_duplicate_date_ticker_pairs(panel):
    assert panel.index.is_unique


def test_sorted_by_index(panel):
    assert panel.index.is_monotonic_increasing


def test_macro_columns_broadcast_correctly(panel):
    """Macro values should be identical across every ticker on a given date."""
    macro_cols = ["cpi", "dgs2", "dgs10", "fedfunds", "vix", "spx_price", "spx_return"]
    for date in panel.index.get_level_values("date").unique():
        cross_section = panel.loc[date, macro_cols]
        for col in macro_cols:
            assert cross_section[col].nunique(dropna=False) == 1, (
                f"macro column '{col}' varies across tickers on {date}"
            )


def test_name_column_dropped_by_default(panel):
    assert "name" not in panel.columns


def test_name_column_kept_when_drop_name_false(processed_dir):
    panel = build_panel_df(str(processed_dir), drop_name=False)
    assert "name" in panel.columns


def test_expected_columns_present(panel):
    expected = {
        "sector_price", "sector_return",
        "cpi", "dgs2", "dgs10", "fedfunds",
        "vix", "spx_price", "spx_return",
    }
    assert expected.issubset(set(panel.columns))


def test_shape_matches_dates_times_tickers(panel):
    """A fully populated synthetic panel has len(dates) * len(tickers) rows."""
    assert panel.shape[0] == len(_DATES) * len(_SECTORS)


# ---------------------------------------------------------------------------
# Tests: pivot_panel_wide
# ---------------------------------------------------------------------------

def test_pivot_panel_wide_shape(panel):
    wide = pivot_panel_wide(panel, value="sector_return")
    assert wide.shape == (len(_DATES), len(_SECTORS))
    assert list(wide.columns) == sorted(t for t, _ in _SECTORS)


def test_pivot_panel_wide_default_value_is_sector_return(panel):
    wide_default = pivot_panel_wide(panel)
    wide_explicit = pivot_panel_wide(panel, value="sector_return")
    pd.testing.assert_frame_equal(wide_default, wide_explicit)


def test_pivot_panel_wide_raises_on_missing_column(panel):
    with pytest.raises(ValueError):
        pivot_panel_wide(panel, value="does_not_exist")


# ---------------------------------------------------------------------------
# Tests: CSV round-trip preserves MultiIndex
# ---------------------------------------------------------------------------

def test_roundtrip_csv_preserves_multiindex(panel, tmp_path):
    out_path = tmp_path / "panel.csv"
    panel.to_csv(out_path, index=True)

    reloaded = pd.read_csv(out_path, index_col=[0, 1], parse_dates=["date"])

    assert list(reloaded.index.names) == ["date", "ticker"]
    assert reloaded.index.is_unique
    assert reloaded.index.is_monotonic_increasing
    assert reloaded.shape == panel.shape
    pd.testing.assert_frame_equal(
        reloaded.sort_index(),
        panel.sort_index(),
        check_dtype=False,
    )


# ---------------------------------------------------------------------------
# Tests: build_wide_panel_df
# ---------------------------------------------------------------------------

def test_wide_panel_row_index_is_date(processed_dir):
    wide = build_wide_panel_df(str(processed_dir))
    assert wide.index.name == "date"
    assert wide.index.is_monotonic_increasing


def test_wide_panel_column_multiindex_names(processed_dir):
    wide = build_wide_panel_df(str(processed_dir))
    assert wide.columns.nlevels == 2
    assert list(wide.columns.names) == ["feature", "ticker"]


def test_wide_panel_shape(processed_dir, panel):
    wide = build_wide_panel_df(str(processed_dir))
    n_features = len(panel.columns)
    assert wide.shape == (len(_DATES), n_features * len(_SECTORS))


def test_wide_panel_roundtrip_csv(processed_dir, tmp_path):
    wide = build_wide_panel_df(str(processed_dir))
    out_path = tmp_path / "wide_panel.csv"
    wide.to_csv(out_path, index=True)

    reloaded = pd.read_csv(
        out_path, header=[0, 1], index_col=0, parse_dates=[0]
    )
    reloaded.columns = reloaded.columns.set_names(["feature", "ticker"])

    assert list(reloaded.columns.names) == ["feature", "ticker"]
    assert reloaded.shape == wide.shape
    pd.testing.assert_frame_equal(
        reloaded.sort_index(),
        wide.sort_index(),
        check_dtype=False,
    )
