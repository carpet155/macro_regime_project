import pandas as pd
import numpy as np


# Expected component label sets (from issues #64 and #65)
_INFLATION_LABELS = {"high", "low"}
_RATE_LABELS      = {"rising", "falling"}

# Explicit 2x2 lookup — strings must match character-for-character
_REGIME_MAP = {
    ("high", "rising") : "High Inflation / Rising Rates",
    ("high", "falling"): "High Inflation / Falling Rates",
    ("low",  "rising") : "Low Inflation / Rising Rates",
    ("low",  "falling"): "Low Inflation / Falling Rates",
}


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
    df = df.copy()

    # Normalize: lowercase + strip whitespace so "High " == "high"
    inflation = df[inflation_col].str.strip().str.lower()
    rate      = df[rate_col].str.strip().str.lower()

    # Build a combined key Series of tuples, vectorized via zip
    keys = pd.Series(
        list(zip(inflation, rate)),
        index=df.index
    )

    # Map keys to labels; unmapped keys (incl. NaN tuples) become NaN
    df[out_col] = keys.map(_REGIME_MAP)

    return df



### for issue 67
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
        - vix >= threshold → "stress"; vix < threshold → "calm".
        - Ties at the threshold are classified as "stress".

    NaN policy:
        - NaN VIX values are excluded from threshold computation.
        - Rows where VIX is NaN receive NaN in the output (not "stress"
          or "calm").
        - Rows where the expanding/rolling window has not yet accumulated
          enough data (fewer than min_periods observations) also receive
          NaN.

    Parameters
    ----------
    vix : pd.Series
        Time-indexed VIX level series (e.g. master_df["vix"]).
    q : float
        Quantile level for the stress threshold (default: 0.75).
    window : int or None
        Rolling window size. None means expanding (default: None).
    min_periods : int or None
        Minimum observations required to compute a threshold.
        Default is 1 (expanding computes from the first valid value).

    Returns
    -------
    pd.Series
        String Series with values "stress", "calm", or NaN,
        same index as vix. Output name is "vix_regime".

    Notes
    -----
    Fully vectorized — no Python loops over rows.
    Compatible with combine_macro_regime() in this module.
    """
    if window is None:
        threshold = vix.expanding(min_periods=min_periods).quantile(q)
    else:
        threshold = vix.rolling(window=window, min_periods=min_periods).quantile(q)

    regime = pd.Series(index=vix.index, dtype=object, name="vix_regime")
    mask_nan = vix.isna() | threshold.isna()
    mask_stress = vix >= threshold

    regime = pd.Series("calm", index=vix.index, dtype=object, name="vix_regime")
    regime[mask_stress] = "stress"
    regime[mask_nan] = np.nan

    return regime

