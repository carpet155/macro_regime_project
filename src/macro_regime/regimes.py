"""
src/macro_regime/regimes.py

Regime classification functions for macro analysis.

Functions
---------
assign_inflation_regime : high / low inflation label per row  (issue #64)
classify_rate_regime    : rising / falling rate label per row (issue #65)
assign_rate_regime      : convenience wrapper that attaches rate_regime to df

Both functions are fully vectorized (no Python loops over rows) and are
designed to compose cleanly for the combined regime in issue #66.
"""

import pandas as pd
import numpy as np


# ── Inflation Regime (issue #64) ──────────────────────────────────────────────

def assign_inflation_regime(
    df: pd.DataFrame,
    inflation_col: str = "cpi",
    method: str = "median",
    fixed_threshold: float = None,
) -> pd.DataFrame:
    """
    Assign a high/low inflation regime to each row in the master DataFrame.

    Threshold methods
    -----------------
    "median" (default)
        Rows where CPI is strictly above the full-sample median are "high";
        at or below are "low".
    "fixed"
        Uses fixed_threshold. Rows strictly above -> "high", else -> "low".

    Parameters
    ----------
    df : pd.DataFrame
    inflation_col : str, default "cpi"
    method : str, default "median"
    fixed_threshold : float, optional — required when method="fixed"

    Returns
    -------
    pd.DataFrame with new "inflation_regime" column ("high" or "low").
    """
    if inflation_col not in df.columns:
        raise ValueError(
            f"Column '{inflation_col}' not found in DataFrame. "
            f"Available columns: {list(df.columns)}"
        )
    if method not in ("median", "fixed"):
        raise ValueError(f"method must be 'median' or 'fixed', got '{method}'")
    if method == "fixed" and fixed_threshold is None:
        raise ValueError("fixed_threshold must be provided when method='fixed'")

    out = df.copy()
    threshold = out[inflation_col].median() if method == "median" else fixed_threshold

    # Vectorized classification — strictly above threshold = "high"
    out["inflation_regime"] = out[inflation_col].apply(
        lambda v: "high" if (v == v and v > threshold) else ("low" if v == v else None)
    )

    # Forward/back fill NaNs introduced by missing CPI values
    out["inflation_regime"] = out["inflation_regime"].ffill().bfill()

    # Validate
    unique_vals = set(out["inflation_regime"].dropna().unique())
    if not {"high", "low"}.issubset(unique_vals):
        raise RuntimeError(
            f"inflation_regime only contains {unique_vals}. "
            "Check that the inflation column has sufficient variance."
        )
    remaining_nans = out["inflation_regime"].isna().sum()
    if remaining_nans > 0:
        raise RuntimeError(
            f"inflation_regime still has {remaining_nans} NaNs after fill."
        )

    high_pct = (out["inflation_regime"] == "high").mean() * 100
    low_pct  = (out["inflation_regime"] == "low").mean()  * 100
    print(
        f"[inflation_regime] threshold={threshold:.4f} ({method}) | "
        f"high={high_pct:.1f}%  low={low_pct:.1f}%"
    )

    return out


# ── Rate Regime (issue #65) ───────────────────────────────────────────────────

def classify_rate_regime(
    rates: pd.Series,
    *,
    method: str = "diff",
    window: int = 21,
    primary_series: str = "fedfunds",
) -> pd.Series:
    """
    Return a Series of "rising" | "falling" labels aligned to rates index.

    Primary series
    --------------
    The canonical input is the Federal Funds Rate ("fedfunds") because it is
    the direct policy rate and drives the broadest macro regime interpretation.
    dgs2 or dgs10 can be substituted by passing a different Series.

    Rising / falling rule
    ---------------------
    method="diff" (default)
        sign( rates.diff() ) determines direction.
        - diff > 0  -> "rising"
        - diff < 0  -> "falling"
        - diff == 0 -> forward-filled from the previous label.
        - First row has no prior value; back-filled from next valid label.

    method="rolling_slope"
        sign( rolling mean of diff over window periods ).
        Smooths out day-to-day noise. window defaults to 21 trading days.

    No Python loops are used; all ops are pandas/numpy vectorized.

    Parameters
    ----------
    rates : pd.Series — numeric interest rate time-series
    method : str — "diff" or "rolling_slope"
    window : int — rolling window (only used for rolling_slope), default 21
    primary_series : str — label used in logs/errors, default "fedfunds"

    Returns
    -------
    pd.Series of "rising"/"falling" with same index as rates. No NaNs.
    """
    if not pd.api.types.is_numeric_dtype(rates):
        raise ValueError(
            f"rates Series must be numeric (primary_series='{primary_series}')."
        )
    if method not in ("diff", "rolling_slope"):
        raise ValueError(
            f"method must be 'diff' or 'rolling_slope', got '{method}'"
        )
    if window < 2:
        raise ValueError(f"window must be >= 2, got {window}")

    if method == "diff":
        delta = rates.diff()
    else:
        delta = rates.diff().rolling(window=window, min_periods=1).mean()

    # Vectorized label assignment — use None instead of np.nan to avoid
    # dtype promotion error between str and float in newer numpy versions
    regime = pd.Series(index=rates.index, dtype="object")
    regime[delta > 0] = "rising"
    regime[delta < 0] = "falling"
    # ties (delta == 0) and NaNs left as None, filled below

    # Fill ties and warm-up rows
    regime = regime.ffill().bfill().fillna("falling")

    remaining_nans = regime.isna().sum()
    if remaining_nans > 0:
        raise RuntimeError(
            f"rate_regime has {remaining_nans} NaNs after fill."
        )

    rising_pct  = (regime == "rising").mean()  * 100
    falling_pct = (regime == "falling").mean() * 100
    print(
        f"[rate_regime] method={method} | primary={primary_series} | "
        f"rising={rising_pct:.1f}%  falling={falling_pct:.1f}%"
    )

    return regime


def assign_rate_regime(
    df: pd.DataFrame,
    rate_col: str = "fedfunds",
    method: str = "diff",
    window: int = 21,
) -> pd.DataFrame:
    """
    Convenience wrapper: attach rate_regime column to the master DataFrame.

    Parameters
    ----------
    df : pd.DataFrame — master DataFrame with a rate column
    rate_col : str — default "fedfunds"
    method : str — passed to classify_rate_regime, default "diff"
    window : int — passed to classify_rate_regime, default 21

    Returns
    -------
    pd.DataFrame copy with new "rate_regime" column ("rising" or "falling").
    """
    if rate_col not in df.columns:
        raise ValueError(
            f"Column '{rate_col}' not found. Available: {list(df.columns)}"
        )
    out = df.copy()
    out["rate_regime"] = classify_rate_regime(
        out[rate_col],
        method=method,
        window=window,
        primary_series=rate_col,
    )
    return out