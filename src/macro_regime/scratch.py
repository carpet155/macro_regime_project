"""
Exploratory Workspace Module.
Acts as a sandbox for temporary code, experimental functions, and debugging outside the main pipeline.

Key Responsibilities:
- Provides a safe space to test function behavior (e.g., regime persistence).
- Exists outside the production execution path.

Key Functions:
- N/A (Contains experimental/imperative script execution).

Inputs/Outputs:
- Consumes: Ad-hoc local data or mock DataFrames.
- Returns: Terminal standard output.
"""

from macro_regime.analysis import analyze_regime_persistence
import pandas as pd

df = pd.DataFrame({
    "date": pd.date_range("2020-01-01", periods=6),
    "regime": ["A","A","B","B","A","A"],
})

segments, summary = analyze_regime_persistence(df, "regime", "date")

print("Segments:")
print(segments)

print("\nSummary:")
print(summary)
