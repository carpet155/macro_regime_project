import sys
import os

# Make sure the src folder is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.macro_regime.build import build_master_df

def main():
    processed_dir = os.path.join("data", "processed")
    output_path   = os.path.join(processed_dir, "master_df.csv")

    print("Building master DataFrame...")
    master = build_master_df(processed_dir)

    print(f"Shape: {master.shape}")
    print(f"Date range: {master['date'].min().date()} → {master['date'].max().date()}")
    print(f"Unique tickers: {master['ticker'].nunique()}")
    print(f"Missing values:\n{master.isnull().sum()}")

    master.to_csv(output_path, index=False)
    print(f"\nSaved to: {output_path}")

if __name__ == "__main__":
    main()