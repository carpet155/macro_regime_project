# Quickstart

Use this guide when you want to install the project and start exploring quickly. You do **not** need to run the full pipeline for this quickstart.

## Project Setup

```bash
git clone https://github.com/carpet155/macro_regime_project.git
cd macro_regime_project
python -m venv .venv
```

Activate the environment:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the project in editable mode:

```bash
pip install -e .
```

This makes the package importable as `macro_regime`.

## Set API Key

Some ingestion scripts use the FRED API for VIX, Treasury, Federal Funds, and inflation data. If you plan to download fresh data, set `FRED_API_KEY` first. Request an API key at this link: https://fredaccount.stlouisfed.org/apikeys

Mac/Linux:

```bash
export FRED_API_KEY="your_key_here"
```

Windows PowerShell:

```powershell
$env:FRED_API_KEY="your_key_here"
```

You do not need the API key just to import the package or load existing processed files.

## Quick Example: Load and Explore Data

Start Python from the project root:

```bash
python
```

Then run:

```python
from macro_regime.io import load_master_df
from macro_regime.regimes import assign_all_regimes

df = load_master_df()
df = assign_all_regimes(df)

print(df.head())
print(df[["ticker", "macro_regime", "vix_regime"]].head())
```

At this point, you have a `pandas` DataFrame in memory and can explore the project data interactively.

## Optional: Run a Simple Script

If processed feature files already exist, you can rebuild the master dataset without running the full pipeline:

```bash
python scripts/build_master_df.py
```

This writes:

```text
data/processed/base/master_df.csv
```

You can then load it with:

```python
from macro_regime.io import load_master_df

df = load_master_df()
df.head()
```

## Optional: Run a Small Ingestion Script

These scripts download raw data and write CSV files to `data/raw/`.

Yahoo Finance scripts do not require `FRED_API_KEY`:

```bash
python scripts/ingest_spx.py
python scripts/ingest_sectors.py
```

FRED-based scripts require `FRED_API_KEY`:

```bash
python scripts/ingest_vix.py
python scripts/ingest_treasury.py
python scripts/ingest_inflation.py
```

## What to Try Next

- Read `README.md` for the full project workflow.
- Read `SETUP.md` for team workflow and GitHub contribution instructions.
- Explore notebooks in `notebooks/`.
- Run tests with `python -m pytest -q` after installing dev dependencies with `pip install -e ".[dev]"`.
- When you are ready to reproduce everything end-to-end, run the full pipeline documented in `README.md`.
