"""Pure in-memory cleaning utilities for macro and panel time series (pandas/numpy only)."""

from __future__ import annotations

from functools import partial
from typing import Any, Literal

import numpy as np
import pandas as pd


def validate_required_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    """Raise ``ValueError`` if ``df`` is missing any of ``required_columns``."""
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def coerce_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Return a copy with ``columns`` coerced via ``pd.to_numeric(..., errors='coerce')``."""
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def summarize_frame(df: pd.DataFrame, name: str, date_col: str = "date") -> dict[str, Any]:
    """Lightweight summary for logging: shape, optional date span, and per-column NA counts."""
    summary: dict[str, Any] = {
        "name": name,
        "n_rows": int(len(df)),
        "n_columns": int(df.shape[1]),
    }
    if date_col in df.columns:
        dates = pd.to_datetime(df[date_col], errors="coerce")
        if dates.notna().any():
            summary["min_date"] = dates.min()
            summary["max_date"] = dates.max()
    summary["missing_counts"] = df.isna().sum().astype(int).to_dict()
    return summary


def _validate_non_empty(df: pd.DataFrame, *, what: str) -> None:
    if df.empty:
        raise ValueError(f"Cannot {what}: DataFrame is empty.")


def _rename_date_col_to_date(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Rename ``date_col`` to ``date`` when it is not already ``date``."""
    if date_col != "date":
        validate_required_columns(df, [date_col])
        return df.rename(columns={date_col: "date"})
    validate_required_columns(df, ["date"])
    return df


def _reindex_dataframe_to_freq_range(
    df: pd.DataFrame,
    *,
    freq: str,
) -> pd.DataFrame:
    """Reindex a frame whose index is datetime to a full ``freq`` range from min to max index."""
    if df.index.size == 0:
        raise ValueError("Cannot reindex: no rows with valid dates remain.")
    dr = pd.date_range(df.index.min(), df.index.max(), freq=freq)
    out = df.reindex(dr)
    out.index.name = "date"
    return out


def standardize_dates(
    df: pd.DataFrame,
    date_col: str = "date",
    freq: str = "B",
    keep: Literal["first", "last", False] = "last",
) -> pd.DataFrame:
    """Sort by date, drop duplicate timestamps, reindex to a dense ``freq`` range, output column ``date``.

    Missing values are preserved (no filling). The output always uses the column name ``date``.
    """
    _validate_non_empty(df, what="standardize dates")
    validate_required_columns(df, [date_col])
    out = df.copy()
    out = _rename_date_col_to_date(out, date_col)
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    if not out["date"].notna().any():
        raise ValueError("Cannot standardize dates: date column is all null or non-parsable.")
    out = out.sort_values("date", kind="mergesort")
    out = out.drop_duplicates(subset=["date"], keep=keep)
    _validate_non_empty(out, what="standardize dates after dropping duplicate dates")
    out = out.set_index("date")
    out = _reindex_dataframe_to_freq_range(out, freq=freq)
    return out.reset_index()


def standardize_panel_dates(
    df: pd.DataFrame,
    group_col: str,
    date_col: str = "date",
    freq: str = "B",
    keep: Literal["first", "last", False] = "last",
) -> pd.DataFrame:
    """Apply :func:`standardize_dates` independently within each ``group_col`` group (long / panel data)."""
    _validate_non_empty(df, what="standardize panel dates")
    validate_required_columns(df, [group_col, date_col])

    def _one_group(sub: pd.DataFrame) -> pd.DataFrame:
        label = sub[group_col].iloc[0]
        body = sub.drop(columns=[group_col])
        std = standardize_dates(body, date_col=date_col, freq=freq, keep=keep)
        std[group_col] = label
        cols = [group_col, "date"] + [c for c in std.columns if c not in (group_col, "date")]
        return std[cols]

    pieces = (_one_group(g) for _, g in df.groupby(group_col, sort=False))
    out = pd.concat(pieces, ignore_index=True)
    return out.sort_values([group_col, "date"], kind="mergesort").reset_index(drop=True)


def compute_returns(series: pd.Series, method: str = "simple") -> pd.Series:
    """Vectorized simple or log returns; first observation is NaN, index aligned to input."""
    s = series.astype(float)
    if method == "simple":
        return s.pct_change()
    if method == "log":
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.log(s / s.shift(1))
    raise ValueError(f"Unsupported return method {method!r}; use 'simple' or 'log'.")


def add_grouped_returns(
    df: pd.DataFrame,
    value_col: str,
    group_col: str,
    date_col: str = "date",
    return_col: str = "return",
    method: str = "simple",
) -> pd.DataFrame:
    """Sort by ``group_col`` then ``date_col``, compute returns per group, add ``return_col``."""
    validate_required_columns(df, [value_col, group_col, date_col])
    out = df.copy()
    out = out.sort_values([group_col, date_col], kind="mergesort")
    out[return_col] = out.groupby(group_col, sort=False)[value_col].transform(
        partial(compute_returns, method=method)
    )
    return out


def fill_macro_series(df: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    """Forward-fill only ``value_cols`` (no backward fill)."""
    if value_cols:
        validate_required_columns(df, value_cols)
    out = df.copy()
    for col in value_cols:
        out[col] = out[col].ffill()
    return out


def fill_sector_return_gaps(
    df: pd.DataFrame,
    ticker_col: str = "ticker",
    return_col: str = "return",
    date_col: str = "date",
) -> pd.DataFrame:
    """Forward-fill ``return_col`` within each ``ticker_col`` group; force the first row per ticker to NaN."""
    validate_required_columns(df, [ticker_col, return_col, date_col])
    out = df.copy().sort_values([ticker_col, date_col], kind="mergesort")
    out[return_col] = out.groupby(ticker_col, sort=False)[return_col].ffill()
    first_mask = ~out.duplicated(subset=[ticker_col], keep="first")
    out.loc[first_mask, return_col] = np.nan
    return out


def align_inflation_to_daily(
    df: pd.DataFrame,
    date_col: str = "date",
    value_col: str = "value",
    freq: str = "B",
) -> pd.DataFrame:
    """Business-day inflation series: standardize dates, then forward-fill until the next release."""
    validate_required_columns(df, [date_col, value_col])
    work = df[[date_col, value_col]].copy()
    out = standardize_dates(work, date_col=date_col, freq=freq, keep="last")
    out[value_col] = out[value_col].ffill()
    return out[["date", value_col]]


def validate_monotonic_dates(df: pd.DataFrame, date_col: str = "date") -> None:
    """Raise ``ValueError`` if non-null ``date_col`` values are not monotonic increasing in row order."""
    validate_required_columns(df, [date_col])
    series = pd.to_datetime(df[date_col], errors="coerce")
    valid = series[series.notna()]
    if valid.empty:
        raise ValueError("Cannot validate monotonic dates: all date values are null.")
    if not valid.is_monotonic_increasing:
        raise ValueError(f"Dates in column {date_col!r} are not monotonic increasing (non-null rows).")


def validate_no_duplicate_keys(df: pd.DataFrame, subset: list[str]) -> None:
    """Raise ``ValueError`` if duplicate rows exist for the given key ``subset``."""
    validate_required_columns(df, subset)
    dup = df.duplicated(subset=subset, keep=False)
    if dup.any():
        raise ValueError(f"Duplicate keys for subset {subset}: {int(dup.sum())} conflicting rows.")
