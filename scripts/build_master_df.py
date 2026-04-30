import sys
from pathlib import Path

# Make sure the src folder is on the path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from macro_regime.build import build_master_df

def main():
    processed_dir = REPO_ROOT / "data" / "processed"
    output_path = processed_dir / "base" / "master_df.csv"
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print("Building master DataFrame...")
        master = build_master_df(str(processed_dir))

        print(f"Shape: {master.shape}")
        print(f"Date range: {master['date'].min().date()} -> {master['date'].max().date()}")
        print(f"Unique tickers: {master['ticker'].nunique()}")
        print(f"Missing values:\n{master.isnull().sum()}")

        master.to_csv(output_path, index=False)
        print(f"\nSaved to: {output_path.as_posix()}")
    except Exception as exc:
        print(f"ERROR: Failed to build master DataFrame: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

if __name__ == "__main__":
    main()