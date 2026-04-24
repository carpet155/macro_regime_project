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
