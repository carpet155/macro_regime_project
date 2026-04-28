import sys
import os
from pathlib import Path

# Make sure the src folder is on the path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from macro_regime.build import build_master_df

def main():
    processed_dir = Path("data") / "processed"
    output_path = processed_dir / "base" / "master_df.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not os.path.isdir(processed_dir):
        raise FileNotFoundError(
            f"Processed data directory does not exist: {processed_dir}. "
            "Run the upstream processing scripts first (e.g. scripts/run_processing.py)."
        )

    print("Building master DataFrame...")
    try:
        master = build_master_df(str(processed_dir))
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to build master DataFrame: {e}") from e

    print(f"Shape: {master.shape}")
    print(f"Date range: {master['date'].min().date()} -> {master['date'].max().date()}")
    print(f"Unique tickers: {master['ticker'].nunique()}")
    print(f"Missing values:\n{master.isnull().sum()}")

    try:
        master.to_csv(output_path, index=False)
    except Exception as e:
        raise RuntimeError(f"Failed to write {output_path}: {e}") from e
    print(f"\nSaved to: {output_path.as_posix()}")

if __name__ == "__main__":
    main()
