import sys
import os

# Make sure the src folder is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.macro_regime.panel import build_panel_df

def main():
    processed_dir = os.path.join("data", "processed")
    output_path   = os.path.join(processed_dir, "master_panel_df.csv")

    print("Building panel DataFrame...")
    panel = build_panel_df(processed_dir)

    dates   = panel.index.get_level_values("date")
    tickers = panel.index.get_level_values("ticker")

    print(f"Shape: {panel.shape}")
    print(f"Index levels: {list(panel.index.names)}")
    print(f"Date range: {dates.min().date()} → {dates.max().date()}")
    print(f"Unique tickers: {tickers.nunique()}")
    print(f"Missing values:\n{panel.isnull().sum()}")

    panel.to_csv(output_path, index=True)
    print(f"\nSaved to: {output_path}")
    print("Reload: pd.read_csv(path, index_col=[0, 1], parse_dates=['date'])")

if __name__ == "__main__":
    main()
