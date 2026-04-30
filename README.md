# Macro Regime Project

## Overview

This project analyzes how different parts of the U.S. stock market (sector ETFs) perform under different macroeconomic conditions.

We classify the market into “regimes” (e.g., high volatility, rising rates, inflationary periods) using macro indicators like:
- VIX (volatility)
- Treasury yields
- Inflation
- Federal Funds rate

Then, we study how sector returns behave in each regime.

## Project Structure

```
macro_regime_project/
  src/macro_regime/      # Core library (config, I/O, regime logic, analysis)
  scripts/               # Ingestion, processing, and analysis scripts
  notebooks/             # Jupyter notebooks for exploration and visualization
  data/raw/              # Downloaded source data (CSV)
  data/processed/        # Generated outputs, organized into subfolders
    base/                # Master datasets
    features/            # Cleaned feature datasets
    analysis/            # Summary tables and analysis outputs
  tests/                 # Test suite
  docs/                  # Documentation
```

This repository does not track downloaded or generated CSV files. The `data/`
folders are included only as empty directories. Run the pipeline or individual
scripts to generate data locally.

## Installation

For the shortest setup path, see [QUICKSTART.md](QUICKSTART.md).

### 1. Clone the repository

```bash
git clone https://github.com/carpet155/macro_regime_project.git
cd macro_regime_project
```

### 2. Create a Python environment

You need Python 3.10 or newer. Choose **one** of the following:

**Option A — conda:**

```bash
conda create -n macro_regime python=3.10 -y
conda activate macro_regime
```

**Option B — venv/pip:**

```bash
python3 -m venv .venv
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install the project

```bash
pip install -e .
```

Project dependencies are defined in `pyproject.toml`, which is the source of truth for installation.

If you plan to run tests, install the dev dependencies too:

```bash
pip install -e ".[dev]"
```

### 4. Set up the FRED API key

Three of the ingestion scripts (`ingest_vix.py`, `ingest_treasury.py`, `ingest_inflation.py`) pull data from the [FRED API](https://fred.stlouisfed.org/), which requires a free API key.

1. Sign up at https://fred.stlouisfed.org/ and request an API key.
2. Before running any ingestion scripts, export the key in your terminal:

```bash
export FRED_API_KEY="your_key_here"
```

This variable only lasts for your current terminal session. To make it persistent, add that line to your shell config file (`~/.zshrc` on Mac, `~/.bashrc` on Linux).

## Downloading and Processing Data

### Option A: Run the full pipeline

After installation and `FRED_API_KEY` setup, run the entire project pipeline with one command:

```bash
python -m macro_regime.pipeline
```

This ingests raw data, processes cleaned feature files, builds the master dataset, builds the panel dataset, and writes analysis summary tables.

You can also run the same pipeline through the script wrapper:

```bash
python scripts/run_pipeline.py
```

Expected outputs include:

- `data/raw/` — downloaded raw CSV files
- `data/processed/features/` — cleaned feature datasets
- `data/processed/base/master_df.csv` — canonical long-form master dataset with regime columns
- `data/processed/base/master_panel_df.csv` — wide panel dataset
- `data/processed/analysis/` — pivot tables and average return summaries

The current pipeline does not write any required files to `data/processed/final/`.

### Option B: Run each step manually

Use these commands if you want to debug or rerun one stage at a time.

#### Step 1: Ingest raw data

Each script downloads one data source into `data/raw/`. Run all five:

```bash
python scripts/ingest_spx.py
python scripts/ingest_sectors.py
python scripts/ingest_vix.py
python scripts/ingest_treasury.py
python scripts/ingest_inflation.py
```

The FRED-based scripts require `FRED_API_KEY` to be set. The Yahoo Finance scripts need no key.

#### Step 2: Process raw data

Transform all raw CSVs into cleaned feature files in `data/processed/features/`:

```bash
python scripts/run_processing.py
```

#### Step 3: Build the master DataFrame

Merge all processed data into a single long-form DataFrame:

```bash
python scripts/build_master_df.py
```

This writes the master dataset to `data/processed/base/master_df.csv`.

#### Step 4: Build derived outputs

```bash
python scripts/build_panel_df.py
python scripts/build_pivot_tables.py
python scripts/compute_avg_returns_by_regime.py
```

These scripts write derived datasets and analysis tables to:

- `data/processed/base/`
- `data/processed/analysis/`

## Running the Analysis

Open any notebook in the `notebooks/` directory:

```bash
jupyter notebook notebooks/
```

Key notebooks:

| Notebook | Description |
|---|---|
| `60_build_main_df.ipynb` | Master DataFrame construction walkthrough |
| `72_build_panel_df.ipynb` | Panel data construction |
| `84_regime_heatmap.ipynb` | Regime heatmap visualization |
| `85_volatility_comparison.ipynb` | Volatility comparison across regimes |
| `explore.ipynb` | General exploratory analysis |

## Running Tests

```bash
pytest
```

Or with coverage:

```bash
pytest --cov=src/macro_regime
```

## Contributing

See [SETUP.md](SETUP.md) for the full contributor workflow (branching, PRs, issue tracking).
