import sys
import os

# Make sure the src folder is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from macro_regime.panel import build_wide_panel_df

def main():
    processed_dir = os.path.join("data", "processed")
    output_path   = os.path.join(processed_dir, "master_panel_df.csv")

    if not os.path.isdir(processed_dir):
        raise FileNotFoundError(
            f"Processed data directory does not exist: {processed_dir}. "
            "Run the upstream processing scripts first (e.g. scripts/run_processing.py)."
        )

    print("Building wide panel DataFrame...")
    try:
        wide = build_wide_panel_df(processed_dir)
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to build wide panel DataFrame: {e}") from e

    features = wide.columns.get_level_values("feature").unique()
    tickers  = wide.columns.get_level_values("ticker").unique()

    print(f"Shape: {wide.shape}")
    print(f"Row index: {wide.index.name}")
    print(f"Column levels: {list(wide.columns.names)}")
    print(f"Date range: {wide.index.min().date()} → {wide.index.max().date()}")
    print(f"Features: {list(features)}")
    print(f"Unique tickers: {tickers.nunique()}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        wide.to_csv(output_path, index=True)
    except Exception as e:
        raise RuntimeError(f"Failed to write {output_path}: {e}") from e
    print(f"\nSaved to: {output_path}")
    print("Reload: pd.read_csv(path, header=[0, 1], index_col=0, parse_dates=[0])")

if __name__ == "__main__":
    main()
