## Data Processing Pipeline (Raw → Processed)

After running the ingestion scripts, all datasets live in `data/raw/` in their canonical formats. The next step is to transform these raw files into clean, analysis-ready datasets stored in `data/processed/`.

This project separates data ingestion from data processing for clarity, reproducibility, and modularity.

## Overview

The processing layer:

- standardizes all datasets to a consistent business-day time index  
- handles missing values appropriately by data type  
- computes returns for market data  
- preserves clean, consistent schemas across all datasets  

All reusable logic lives in:


src/macro_regime/clean.py


All dataset-specific transformations live in:


scripts/process_*.py


## Processing Scripts

Each dataset has its own processing script:

- process_inflation.py  
- process_sectors.py  
- process_spx.py  
- process_treasury.py  
- process_vix.py  

Each script:

1. Loads raw data from `data/raw/`  
2. Normalizes column names (e.g., DATE → date)  
3. Applies shared cleaning functions from clean.py  
4. Validates structure (dates, duplicates, missing values)  
5. Saves a processed dataset to `data/processed/`  

## Key Transformations

### Date Standardization
- All datasets are aligned to a business-day (B) frequency  
- Missing dates are inserted  
- No filling occurs at this stage  

### Missing Data Handling

Different strategies are used depending on data type:

Macro Data (CPI, VIX, Treasury):  
- Forward filled (ffill)  
- Assumes values persist until the next observation  

Market Data (SPX, Sectors):  
- Prices are not filled  
- Returns are computed first, then:  
  - Forward filled within ticker (for sectors)  
  - Constrained so missing price implies missing return  

### Returns Calculation
- Daily returns are computed using vectorized operations  
- First observation per series is always NaN  
- For sectors, returns are computed per ticker  

## Processed Outputs

Running the processing scripts produces:


data/processed/
├── inflation_processed.csv
├── sectors_processed.csv
├── sector_returns_processed.csv
├── spx_processed.csv
├── treasury_processed.csv
└── vix_processed.csv


## Running the Full Pipeline

To run all processing steps at once:

```bash
python scripts/run_processing.py

This will:

execute all process_*.py scripts in sequence
stop if any step fails
print progress and summaries for each dataset
