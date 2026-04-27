import sys
import os

# Make sure the src folder is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.macro_regime.build import build_master_df

def main():
    processed_dir = os.path.join("data", "processed")
    output_path   = os.path.join(processed_dir, "master_df.csv")

    if not os.path.isdir(processed_dir):
        raise FileNotFoundError(
            f"Processed data directory does not exist: {processed_dir}. "
            "Run the upstream processing scripts first (e.g. scripts/run_processing.py)."
        )

    print("Building master DataFrame...")
    try:
        master = build_master_df(processed_dir)
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to build master DataFrame: {e}") from e

    print(f"Shape: {master.shape}")
    print(f"Date range: {master['date'].min().date()} → {master['date'].max().date()}")
    print(f"Unique tickers: {master['ticker'].nunique()}")
    print(f"Missing values:\n{master.isnull().sum()}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        master.to_csv(output_path, index=False)
    except Exception as e:
        raise RuntimeError(f"Failed to write {output_path}: {e}") from e
    print(f"\nSaved to: {output_path}")

if __name__ == "__main__":
    main()
