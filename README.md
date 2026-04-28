# Macro Regime Project

Regime-based macroeconomic analysis of U.S. sector ETF returns. The pipeline ingests macro indicators (VIX, Treasury yields, inflation, Fed Funds rate) and sector ETF prices, classifies market regimes, and analyzes how sector returns behave across different macro environments.

## Project Structure

```
macro_regime_project/
  src/macro_regime/      # Core library (config, I/O, regime logic, analysis)
  scripts/               # Ingestion, processing, and analysis scripts
  notebooks/             # Jupyter notebooks for exploration and visualization
  data/raw/              # Downloaded source data (CSV)
  data/processed/        # Cleaned and merged outputs
  tests/                 # Test suite
  docs/                  # Documentation
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/carpet155/macro_regime_project.git
cd macro_regime_project
```

### 2. Create a Python environment

You need Python 3.9 or newer. Choose **one** of the following:

**Option A — conda:**

```bash
conda create -n macro_regime python=3.9 -y
conda activate macro_regime
```

**Option B — venv/pip:**

```bash
python3 -m venv .venv
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Then install the project itself as an editable package (this is required so the scripts can import from `src/macro_regime`):

```bash
pip install -e .
```

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

### Step 1: Ingest raw data

Each script downloads one data source into `data/raw/`. Run all five:

```bash
python scripts/ingest_spx.py
python scripts/ingest_sectors.py
python scripts/ingest_vix.py
python scripts/ingest_treasury.py
python scripts/ingest_inflation.py
```

The last three require `FRED_API_KEY` to be set. The first two pull from Yahoo Finance and need no key.

### Step 2: Process raw data

Transform all raw CSVs into cleaned files in `data/processed/`:

```bash
python scripts/run_processing.py
```

### Step 3: Build the master DataFrame

Merge all processed data into a single long-form DataFrame:

```bash
python scripts/build_master_df.py
```

### Step 4: Build derived outputs

```bash
python scripts/build_panel_df.py
python scripts/build_pivot_tables.py
python scripts/compute_avg_returns_by_regime.py
```

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
