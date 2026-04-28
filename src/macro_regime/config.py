"""
Centralized Configuration Parameters.
Acts as the single source of truth for the entire pipeline, storing global variables, file paths, and identifiers.

Key Responsibilities:
- Defines directory structures for raw and processed data.
- Stores canonical ETF tickers, FRED series IDs, and Yahoo Finance identifiers.
- Sets standard column naming conventions for the output datasets.

Key Variables:
- `PROJECT_ROOT`, `RAW_DIR`, `PROCESSED_DIR`: Path objects for file I/O.
- `SECTOR_TICKERS`, `TREASURY_SERIES`: Dictionaries mapping tickers to canonical names.
- `RAW_FILES`: Dictionary mapping data types to canonical CSV filenames.

Inputs/Outputs:
- Consumes: N/A
- Returns: Standard Python data types (Path objects, dicts, strings).
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Processed data subdirectories (source-of-truth structure)
PROCESSED_BASE_DIR = PROCESSED_DIR / "base"
PROCESSED_FEATURES_DIR = PROCESSED_DIR / "features"
PROCESSED_ANALYSIS_DIR = PROCESSED_DIR / "analysis"
PROCESSED_FINAL_DIR = PROCESSED_DIR / "final"

DEFAULT_START_DATE = "2000-01-01"
DEFAULT_END_DATE = None  # use most recent available date

# Sector ETF universe
SECTOR_TICKERS = {
    "XLB": "materials",
    "XLE": "energy",
    "XLF": "financials",
    "XLI": "industrials",
    "XLK": "technology",
    "XLP": "consumer_staples",
    "XLU": "utilities",
    "XLV": "health_care",
    "XLY": "consumer_discretionary",
    "XLRE": "real_estate",
    "XLC": "communication_services",
}

# Yahoo Finance identifiers
SPX_TICKER = "^GSPC"

# FRED identifiers
VIX_SERIES = "VIXCLS"
TREASURY_SERIES = {
    "DGS2": "2y_treasury_yield",
    "DGS10": "10y_treasury_yield",
    "FEDFUNDS": "federal_funds_rate",
}
INFLATION_SERIES = "CPIAUCSL"

# Canonical raw output files
RAW_FILES = {
    "spx": "SP500.csv",
    "vix": "VIXCLS.csv",
    "inflation": "CPIAUCSL.csv",
    "treasury_2y": "DGS2.csv",
    "treasury_10y": "DGS10.csv",
    "fed_funds": "FEDFUNDS.csv",
    "sectors": "sector_prices.csv",
}

# Standardized output columns
DATE_COL = "date"
VALUE_COL = "value"
PRICE_COL = "close"
TICKER_COL = "ticker"
NAME_COL = "name"
