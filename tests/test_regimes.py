# Issue 81

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from macro_regime.regimes import(
    assign_inflation_regime,
    assign_rate_regime,
    classify_rate_regime,
    classify_vix_stress_regime,
    combine_macro_regime,
)

# Small Builders to keeps the test bodies readable 

def make_df(data):
    return pd.DataFrame(data) 

def make_series(values, name=None):
    return pd.Series(values, name=name)

# assign_inflation_regime (#64)

# Normal

def test_inflation_median_labels_above_and_below():
    # the median of [1,2,3,4,5] is 3.0: strictly above –> high, at or below –> low
    df = make_df({"cpi": [1.0, 2.0, 3.0, 4.0, 5.0]})
    out = assign_inflation_regime(df, method = "median")
    expected = make_series(["low", "low", "low", "high", "high"], name = "inflation_regime")
    assert_series_equal(
        out["inflation_regime"].reset_index(drop = True),
        expected,
        check_dtype = False,
        check_names = True,
    )

def test_inflation_fixed_threshold_labels():
    # above 3.5 -> high and at or below -> low
    df = make_df({"cpi": [2.0, 3.5, 4.0, 5.0]})
    out = assign_inflation_regime(df, method="fixed", fixed_threshold=3.5)
    expected = make_series(["low", "low", "high", "high"], name="inflation_regime")
    assert_series_equal(
        out["inflation_regime"].reset_index(drop=True),
        expected,
        check_dtype=False,
        check_names=True,
    )

def test_inflation_custom_column_name():
    df = make_df({"infl": [1.0, 2.0, 3.0, 4.0]})
    out = assign_inflation_regime(df, inflation_col="infl", method="fixed", fixed_threshold=2.5)
    assert "inflation_regime" in out.columns
    assert set(out["inflation_regime"].unique()) == {"high", "low"}


def test_inflation_does_not_mutate_input():
    df = make_df({"cpi": [1.0, 2.0, 3.0, 4.0]})
    assign_inflation_regime(df, method="median")
    assert "inflation_regime" not in df.columns

# Boundary

def test_inflation_value_at_median_is_low():
    # 3.0 == median -> not strictly above -> must be "low"
    df = make_df({"cpi": [1.0, 2.0, 3.0, 4.0, 5.0]})
    out = assign_inflation_regime(df, method="median")
    assert out["inflation_regime"].iloc[2] == "low"
 
def test_inflation_value_at_fixed_threshold_is_low():
    # threshold=3.0; value 3.0 is not strictly above -> "low"
    df = make_df({"cpi": [1.0, 3.0, 5.0]})
    out = assign_inflation_regime(df, method="fixed", fixed_threshold=3.0)
    assert out["inflation_regime"].iloc[1] == "low"
 
 
def test_inflation_two_row_frame_works():
    # minimum viable frame still produces both labels
    df = make_df({"cpi": [1.0, 5.0]})
    out = assign_inflation_regime(df, method="median")
    assert set(out["inflation_regime"].unique()) == {"high", "low"}

# NaN / Missing values

def test_inflation_nan_rows_get_filled():
    df = make_df({"cpi": [1.0, np.nan, np.nan, 4.0, 5.0]})
    out = assign_inflation_regime(df, method="fixed", fixed_threshold=2.5)
    assert out["inflation_regime"].isna().sum() == 0
 
 
def test_inflation_nan_row_ffills_from_low():
    # index 0 -> "low" (1.0 <= 2.5); index 1 NaN -> ffill -> "low"
    df = make_df({"cpi": [1.0, np.nan, 5.0]})
    out = assign_inflation_regime(df, method="fixed", fixed_threshold=2.5)
    assert out["inflation_regime"].iloc[1] == "low"

# Errors

def test_inflation_raises_missing_column():
    df = make_df({"not_cpi": [1.0, 2.0, 3.0]})
    with pytest.raises(ValueError, match="not found"):
        assign_inflation_regime(df, inflation_col="cpi")
 
 
def test_inflation_raises_bad_method():
    df = make_df({"cpi": [1.0, 2.0, 3.0]})
    with pytest.raises(ValueError, match="method"):
        assign_inflation_regime(df, method="zscore")
 
 
def test_inflation_raises_fixed_without_threshold():
    df = make_df({"cpi": [1.0, 2.0, 3.0]})
    with pytest.raises(ValueError, match="fixed_threshold"):
        assign_inflation_regime(df, method="fixed")


# classify_rate_regime (#65)

# normal

def test_rate_rise_then_fall():
    # diffs: NaN, +1, +1, -1, -1; NaN at idx 0 bfills to "rising"
    rates = make_series([1.0, 2.0, 3.0, 2.0, 1.0])
    out = classify_rate_regime(rates)
    expected = make_series(["rising", "rising", "rising", "falling", "falling"])
    assert_series_equal(
        out.reset_index(drop=True),
        expected,
        check_names=False,
        check_dtype=False,
    )
 
 
def test_rate_monotone_fall():
    # diffs: NaN, -1, -1, -1; idx 0 bfills from "falling"
    rates = make_series([5.0, 4.0, 3.0, 2.0])
    out = classify_rate_regime(rates)
    expected = make_series(["falling", "falling", "falling", "falling"])
    assert_series_equal(
        out.reset_index(drop=True),
        expected,
        check_names=False,
        check_dtype=False,
    )

def test_rate_output_is_series():
    assert isinstance(classify_rate_regime(make_series([1.0, 2.0, 3.0])), pd.Series)
 
 
def test_rate_index_preserved():
    idx = pd.date_range("2020-01", periods=4, freq="ME")
    rates = pd.Series([1.0, 1.5, 1.2, 2.0], index=idx)
    out = classify_rate_regime(rates)
    pd.testing.assert_index_equal(out.index, rates.index)
 
 
def test_rate_labels_only_rising_or_falling():
    out = classify_rate_regime(make_series([1.0, 2.0, 1.5, 2.5]))
    assert set(out.unique()).issubset({"rising", "falling"})

# Boundary

def test_rate_zero_diff_inherits_previous_direction():
    # diffs: NaN, +1, 0, 0, -1 -> idx 2 and 3 ffill to "rising"
    rates = make_series([1.0, 2.0, 2.0, 2.0, 1.0])
    out = classify_rate_regime(rates)
    assert out.iloc[2] == "rising"
    assert out.iloc[3] == "rising"
 
 
def test_rate_first_row_bfilled_rising():
    out = classify_rate_regime(make_series([1.0, 2.0, 3.0]))
    assert out.iloc[0] == "rising"
 
 
def test_rate_first_row_bfilled_falling():
    out = classify_rate_regime(make_series([5.0, 4.0, 3.0]))
    assert out.iloc[0] == "falling"
 
 
def test_rate_two_row_series_no_nans():
    out = classify_rate_regime(make_series([1.0, 2.0]))
    assert len(out) == 2
    assert out.isna().sum() == 0

# NaN / Missing values

def test_rate_nan_input_no_nan_output():
    # NaN in the input causes a NaN in diff; fill strategy covers it
    out = classify_rate_regime(make_series([1.0, np.nan, 3.0, 4.0]))
    assert out.isna().sum() == 0
 
 
def test_rate_nan_doesnt_corrupt_neighbours():
    out = classify_rate_regime(make_series([1.0, np.nan, 3.0, 4.0]))
    assert out.iloc[0] in ("rising", "falling")
    assert out.iloc[2] in ("rising", "falling")

# Errors

def test_rate_raises_non_numeric():
    with pytest.raises(ValueError, match="numeric"):
        classify_rate_regime(make_series(["a", "b", "c"]))
 
 
def test_rate_raises_bad_method():
    with pytest.raises(ValueError, match="method"):
        classify_rate_regime(make_series([1.0, 2.0, 3.0]), method="ols")
 
 
def test_rate_raises_window_less_than_2():
    with pytest.raises(ValueError, match="window"):
        classify_rate_regime(make_series([1.0, 2.0, 3.0]), method="rolling_slope", window=1)


# assign_rate_regime  (wrapper, #65)

def test_assign_rate_attaches_column():
    df = make_df({"fedfunds": [1.0, 2.0, 3.0, 2.0]})
    assert "rate_regime" in assign_rate_regime(df).columns
 
 
def test_assign_rate_custom_column():
    df = make_df({"dgs2": [1.0, 1.5, 1.2, 1.8]})
    assert "rate_regime" in assign_rate_regime(df, rate_col="dgs2").columns
 
 
def test_assign_rate_does_not_mutate_input():
    df = make_df({"fedfunds": [1.0, 2.0, 3.0]})
    assign_rate_regime(df)
    assert "rate_regime" not in df.columns
 
 
def test_assign_rate_raises_missing_column():
    df = make_df({"not_fedfunds": [1.0, 2.0]})
    with pytest.raises(ValueError, match="not found"):
        assign_rate_regime(df, rate_col="fedfunds")


# classify_vix_stress_regime  (#67)

# normal

def test_vix_output_name():
    out = classify_vix_stress_regime(make_series([10.0, 20.0, 30.0]))
    assert out.name == "vix_regime"
 
 
def test_vix_labels_only_stress_or_calm():
    out = classify_vix_stress_regime(make_series([10.0, 15.0, 20.0, 25.0, 30.0]))
    assert set(out.dropna().unique()).issubset({"stress", "calm"})
 
 
def test_vix_index_preserved():
    idx = pd.date_range("2020-01", periods=5, freq="ME")
    vix = pd.Series([10.0, 15.0, 20.0, 25.0, 30.0], index=idx)
    pd.testing.assert_index_equal(classify_vix_stress_regime(vix).index, vix.index)
 
 
def test_vix_spike_is_stress():
    # [10,10,10,10,40]: expanding q=0.75 at idx 4 = 32.5 -> 40 >= 32.5 -> stress
    vix = make_series([10.0, 10.0, 10.0, 10.0, 40.0])
    assert classify_vix_stress_regime(vix, q=0.75).iloc[4] == "stress"

def test_vix_dip_is_calm():
    # [20,20,20,20,1]: expanding q=0.75 at idx 4 = 20 -> 1 < 20 -> calm
    vix = make_series([20.0, 20.0, 20.0, 20.0, 1.0])
    assert classify_vix_stress_regime(vix, q=0.75).iloc[4] == "calm"
 
 
def test_vix_rolling_window_produces_valid_labels():
    vix = make_series([10.0, 20.0, 10.0, 30.0, 10.0])
    out = classify_vix_stress_regime(vix, q=0.75, window=3)
    assert set(out.dropna().unique()).issubset({"stress", "calm"})

# Boundary

def test_vix_tie_at_threshold_is_stress():
    # all identical -> expanding quantile = that value -> >= -> stress
    vix = make_series([15.0, 15.0, 15.0, 15.0])
    out = classify_vix_stress_regime(vix, q=0.75)
    assert (out == "stress").all()
 
 
def test_vix_first_row_classified_with_min_periods_1():
    # single-obs expanding window: 20 >= quantile([20]) = 20 -> stress
    out = classify_vix_stress_regime(make_series([20.0, 10.0, 30.0]), min_periods=1)
    assert out.iloc[0] == "stress"
 
 
def test_vix_rows_below_min_periods_are_nan():
    # min_periods=3: rows 0 and 1 can't compute -> NaN; row 2 can
    out = classify_vix_stress_regime(make_series([10.0, 20.0, 30.0, 40.0]), min_periods=3)
    assert pd.isna(out.iloc[0])
    assert pd.isna(out.iloc[1])
    assert not pd.isna(out.iloc[2])

# NaN / Missing

def test_vix_nan_input_gives_nan_output():
    out = classify_vix_stress_regime(make_series([10.0, np.nan, 30.0]))
    assert pd.isna(out.iloc[1])
 
 
def test_vix_nan_doesnt_corrupt_neighbours():
    out = classify_vix_stress_regime(make_series([10.0, np.nan, 30.0]))
    assert out.iloc[0] in ("stress", "calm")
    assert out.iloc[2] in ("stress", "calm")
 
 
def test_vix_all_nan_returns_all_nan():
    out = classify_vix_stress_regime(make_series([np.nan, np.nan, np.nan]))
    assert out.isna().all()


# combine_macro_regime  (#66)

# Normal

@pytest.mark.parametrize("infl, rate, label", [
    ("high", "rising",  "High Inflation / Rising Rates"),
    ("high", "falling", "High Inflation / Falling Rates"),
    ("low",  "rising",  "Low Inflation / Rising Rates"),
    ("low",  "falling", "Low Inflation / Falling Rates"),
])

def test_combine_all_four_quadrants(infl, rate, label):
    # each valid pair must map to the exact label string
    df = make_df({"inflation_regime": [infl], "rate_regime": [rate]})
    assert combine_macro_regime(df)["macro_regime"].iloc[0] == label
 
 
def test_combine_full_cartesian_frame():
    df = make_df({
        "inflation_regime": ["high", "high", "low",     "low"],
        "rate_regime":      ["rising", "falling", "rising", "falling"],
    })
    out = combine_macro_regime(df)
    expected = make_series(
        [
            "High Inflation / Rising Rates",
            "High Inflation / Falling Rates",
            "Low Inflation / Rising Rates",
            "Low Inflation / Falling Rates",
        ],
        name="macro_regime",
    )
    assert_series_equal(
        out["macro_regime"].reset_index(drop=True),
        expected,
        check_dtype=False,
        check_names=True,
    )

def test_combine_default_output_column():
    df = make_df({"inflation_regime": ["high"], "rate_regime": ["rising"]})
    assert "macro_regime" in combine_macro_regime(df).columns
 
 
def test_combine_custom_out_col():
    df = make_df({"inflation_regime": ["low"], "rate_regime": ["falling"]})
    assert "combined" in combine_macro_regime(df, out_col="combined").columns
 
 
def test_combine_does_not_mutate_input():
    df = make_df({"inflation_regime": ["high"], "rate_regime": ["rising"]})
    combine_macro_regime(df)
    assert "macro_regime" not in df.columns

# NaN / Missing

def test_combine_nan_inflation_gives_nan():
    df = make_df({"inflation_regime": [np.nan], "rate_regime": ["rising"]})
    assert pd.isna(combine_macro_regime(df)["macro_regime"].iloc[0])
 
 
def test_combine_nan_rate_gives_nan():
    df = make_df({"inflation_regime": ["high"], "rate_regime": [np.nan]})
    assert pd.isna(combine_macro_regime(df)["macro_regime"].iloc[0])
 
 
def test_combine_both_nan_gives_nan():
    df = make_df({"inflation_regime": [np.nan], "rate_regime": [np.nan]})
    assert pd.isna(combine_macro_regime(df)["macro_regime"].iloc[0])
 
 
def test_combine_invalid_label_gives_nan():
    # unrecognised label must not silently map to a wrong quadrant
    df = make_df({"inflation_regime": ["medium"], "rate_regime": ["rising"]})
    assert pd.isna(combine_macro_regime(df)["macro_regime"].iloc[0])

def test_combine_nan_row_doesnt_corrupt_neighbours():
    df = make_df({
        "inflation_regime": ["high",   np.nan,  "low"],
        "rate_regime":      ["rising", "rising", "falling"],
    })
    out = combine_macro_regime(df)
    assert out["macro_regime"].iloc[0] == "High Inflation / Rising Rates"
    assert pd.isna(out["macro_regime"].iloc[1])
    assert out["macro_regime"].iloc[2] == "Low Inflation / Falling Rates"

# Errors

def test_combine_raises_missing_inflation_col():
    df = make_df({"rate_regime": ["rising"]})
    with pytest.raises(ValueError, match="inflation_regime"):
        combine_macro_regime(df)
 
 
def test_combine_raises_missing_rate_col():
    df = make_df({"inflation_regime": ["high"]})
    with pytest.raises(ValueError, match="rate_regime"):
        combine_macro_regime(df)