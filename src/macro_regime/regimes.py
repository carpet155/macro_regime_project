"""
src/macro_regime/regimes.py

Regime classification functions for macro analysis.

Functions
---------
assign_inflation_regime : high / low inflation label per row  (issue #64)
classify_rate_regime    : rising / falling rate label per row (issue #65)
assign_rate_regime      : convenience wrapper that attaches rate_regime to df
combine_macro_regime    : combine inflation + rate regimes into 4 macro labels (issue #66)
classify_vix_stress_regime : classify VIX as stress/calm using a quantile threshold (issue #67)

All functions are fully vectorized and designed to compose cleanly.
"""

import numpy as np
import pandas as pd

# Expected component label sets (from issues #64 and #65)
_INFLATION_LABELS = {"high", "low"}
_RATE_LABELS = {"rising", "falling"}

# Explicit 2x2 lookup — strings must match character-for-character
_REGIME_MAP = {
    ("high", "rising"): "High Inflation / Rising Rates",
    ("high", "falling"): "High Inflation / Falling Rates",
    ("low", "rising"): "Low Inflation / Rising Rates",
    ("low", "falling"): "Low Inflation / Falling Rates",
}


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

    col = out[inflation_col]
    out["inflation_regime"] = pd.Series(np.nan, index=out.index, dtype=object)
    out.loc[col > threshold, "inflation_regime"] = "high"
    out.loc[col.notna() & (col <= threshold), "inflation_regime"] = "low"

    out["inflation_regime"] = out["inflation_regime"].ffill().bfill()

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
    low_pct = (out["inflation_regime"] == "low").mean() * 100
    print(
        f"[inflation_regime] threshold={threshold:.4f} ({method}) | "
        f"high={high_pct:.1f}%  low={low_pct:.1f}%"
    )

    return out


def classify_rate_regime(
    rates: pd.Series,
    *,
    method: str = "diff",
    window: int = 21,
    primary_series: str = "fedfunds",
) -> pd.Series:
    """
    Return a Series of "rising" | "falling" labels aligned to rates index.
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

    regime = pd.Series(index=rates.index, dtype=object)
    regime[delta > 0] = "rising"
    regime[delta < 0] = "falling"
   # delta == 0 (unchanged rate): carry last known direction; leading all-flat
    # series has no diff signal — default remaining NaNs to "rising".
    regime = regime.ffill().bfill()
    regime = regime.fillna("rising")

    remaining_nans = regime.isna().sum()
    if remaining_nans > 0:
        raise RuntimeError(f"rate_regime has {remaining_nans} NaNs after fill.")

    rising_pct = (regime == "rising").mean() * 100
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

def combine_macro_regime(
    df: pd.DataFrame,
    *,
    inflation_col: str = "inflation_regime",
    rate_col: str = "rate_regime",
    out_col: str = "macro_regime",
) -> pd.DataFrame:
    """
    Add a composite macro regime column to a copy of df.

    Combines inflation_regime and rate_regime into one of four labels:
        "High Inflation / Rising Rates"
        "High Inflation / Falling Rates"
        "Low Inflation / Rising Rates"
        "Low Inflation / Falling Rates"

    Component label sets (case-insensitive, whitespace-stripped):
        inflation_regime : "high" | "low"    (from issue #64)
        rate_regime      : "rising" | "falling" (from issue #65)

    NaN policy:
        If either component is NaN or not in the allowed label set,
        the output is NaN. No quadrant label is silently assigned.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns named by inflation_col and rate_col.
    inflation_col : str
        Column name for inflation regime (default: "inflation_regime").
    rate_col : str
        Column name for rate regime (default: "rate_regime").
    out_col : str
        Name of the new output column (default: "macro_regime").

    Returns
    -------
    pd.DataFrame
        Copy of df with out_col added. Does not modify the input.
    
    Notes
    -----
    Implementation is fully vectorized — no Python loops over rows.
    Does not depend on VIX / stress regime (issue #67).
    """
    if inflation_col not in df.columns:
        raise ValueError(
            f"Column '{inflation_col}' not found. Available: {list(df.columns)}"
        )
    if rate_col not in df.columns:
        raise ValueError(
            f"Column '{rate_col}' not found. Available: {list(df.columns)}"
        )

    out = df.copy()

    inflation = out[inflation_col].astype("string").str.strip().str.lower()
    rate = out[rate_col].astype("string").str.strip().str.lower()

    valid_inflation = inflation.isin(_INFLATION_LABELS)
    valid_rate = rate.isin(_RATE_LABELS)

    keys = pd.Series(list(zip(inflation, rate)), index=out.index)
    out[out_col] = keys.map(_REGIME_MAP)

    invalid_mask = ~(valid_inflation & valid_rate)
    out.loc[invalid_mask, out_col] = np.nan

    return out


def classify_vix_stress_regime(
    vix: pd.Series,
    *,
    q: float = 0.75,
    window: int | None = None,
    min_periods: int | None = 1,
) -> pd.Series:
    """
    Classify each row as "stress" or "calm" based on VIX level vs a
    data-driven percentile threshold.

    Threshold rule:
        - If window is None (default): expanding quantile at level q.
        - If window is an int: rolling quantile over that many periods.
        - vix >= threshold -> "stress"; vix < threshold -> "calm".
        - Ties at the threshold are classified as "stress".

    NaN policy:
        - NaN VIX values are excluded from threshold computation.
        - Rows where VIX is NaN receive NaN in the output.
        - Rows where the expanding/rolling window has not yet accumulated
          enough data also receive NaN.

    Parameters
    ----------
    vix : pd.Series
        Time-indexed VIX level series.
    q : float
        Quantile level for the stress threshold.
    window : int or None
        Rolling window size. None means expanding.
    min_periods : int or None
        Minimum observations required to compute a threshold.

    Returns
    -------
    pd.Series
        String Series with values "stress", "calm", or NaN,
        same index as vix. Output name is "vix_regime".
    """
    if window is None:
        threshold = vix.expanding(min_periods=min_periods).quantile(q)
    else:
        threshold = vix.rolling(window=window, min_periods=min_periods).quantile(q)

    mask_nan = vix.isna() | threshold.isna()
    mask_stress = vix >= threshold

    regime = pd.Series("calm", index=vix.index, dtype="object", name="vix_regime")
    regime[mask_stress] = "stress"
    regime[mask_nan] = np.nan

    return regime