"""
Data Assembly Module.
Sits in the middle of the pipeline (after cleaning, before analysis) to merge independent sector and macroeconomic datasets into a unified structure.

Key Responsibilities:
- Loads individual processed CSV files from the data/processed directory.
- Merges macroeconomic indicators (CPI, Treasury, VIX, SPX).
- Joins sector ETF data onto the macro dataset aligned by date.

Key Functions:
- `build_master_df`: Merges all cleaned data into a single master dataset.

Inputs/Outputs:
- Consumes: Local CSV file paths (strings).
- Returns: pd.DataFrame (the unified master dataset).
"""

import pandas as pd
from pathlib import Path


def build_master_df(processed_dir: str = "data/processed") -> pd.DataFrame:
    """
    Load all cleaned CSVs and merge them into a single master DataFrame.

    Parameters
    ----------
    processed_dir : str
        Path to the folder containing processed CSVs.

    Returns
    -------
    pd.DataFrame
        Master DataFrame with one row per (date, ticker) containing
        both sector-level and macroeconomic columns.
    """
    processed_dir = Path(processed_dir)
    features_dir = processed_dir if processed_dir.name == "features" else (processed_dir / "features")

    def load(filename: str) -> pd.DataFrame:
        path = features_dir / filename
        return pd.read_csv(path, parse_dates=["date"])

    # Load all datasets
    inflation = load("inflation_processed.csv").rename(columns={"value": "cpi"})
    treasury  = load("treasury_processed.csv")
    vix       = load("vix_processed.csv")
    spx       = load("spx_processed.csv").rename(columns={"price": "spx_price", "return": "spx_return"})
    sectors   = load("sectors_processed.csv").rename(columns={"price": "sector_price", "return": "sector_return"})

    # Merge macro datasets
    macro = inflation.merge(treasury, on="date", how="outer")
    macro = macro.merge(vix,         on="date", how="outer")
    macro = macro.merge(spx,         on="date", how="outer")
    macro = macro.sort_values("date").reset_index(drop=True)

    # Join sectors onto macro
    master = sectors.merge(macro, on="date", how="left")
    master = master.sort_values(["date", "ticker"]).reset_index(drop=True)

    return master
