import sys
import os
from pathlib import Path

# Make sure the src folder is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from macro_regime.panel import build_wide_panel_df

def main():
    processed_dir = Path("data") / "processed"
    output_path = processed_dir / "base" / "master_panel_df.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Building wide panel DataFrame...")
    wide = build_wide_panel_df(str(processed_dir))

    features = wide.columns.get_level_values("feature").unique()
    tickers  = wide.columns.get_level_values("ticker").unique()

    print(f"Shape: {wide.shape}")
    print(f"Row index: {wide.index.name}")
    print(f"Column levels: {list(wide.columns.names)}")
    print(f"Date range: {wide.index.min().date()} -> {wide.index.max().date()}")
    print(f"Features: {list(features)}")
    print(f"Unique tickers: {tickers.nunique()}")

    wide.to_csv(output_path, index=True)
    print(f"\nSaved to: {output_path.as_posix()}")
    print("Reload: pd.read_csv(path, header=[0, 1], index_col=0, parse_dates=[0])")

if __name__ == "__main__":
    main()
