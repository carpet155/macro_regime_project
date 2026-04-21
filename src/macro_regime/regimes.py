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