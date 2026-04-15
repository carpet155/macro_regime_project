"""
Configuration values for the macro_regime project.

This file is the single source of truth for:
- market tickers
- FRED series identifiers
- canonical raw file names
- default ingestion date range
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

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