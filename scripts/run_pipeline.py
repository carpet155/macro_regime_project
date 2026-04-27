"""Unified pipeline: ingest all raw data, then clean/process into data/processed/.

Usage:
    python scripts/run_pipeline.py

Requires FRED_API_KEY environment variable for inflation, treasury, and VIX ingestion.
Set it in a ``.env`` file at the project root or export it in your shell.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Resolve project root (parent of scripts/)
_ROOT = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(_ROOT / ".env")

# Ensure src/ and scripts/ are importable
for _dir in [str(_ROOT / "src"), str(_ROOT / "scripts")]:
    if _dir not in sys.path:
        sys.path.insert(0, _dir)


def _check_fred_api_key() -> None:
    """Fail fast if FRED_API_KEY is not set."""
    if os.getenv("FRED_API_KEY") is None:
        print(
            "ERROR: FRED_API_KEY environment variable is not set.\n"
            "Export it before running the pipeline:\n"
            "  export FRED_API_KEY='your-api-key-here'\n"
            "See README for setup instructions.",
            file=sys.stderr,
        )
        sys.exit(1)


def _run_step(label: str, func: callable) -> None:
    """Run *func*, printing status before and after."""
    print(f"  {label} ...", end=" ", flush=True)
    t0 = time.time()
    func()
    elapsed = time.time() - t0
    print(f"done ({elapsed:.1f}s)")


def main() -> None:
    _check_fred_api_key()

    # --- Ingestion (raw data) ---------------------------------------------
    print("[1/3] Ingesting raw data")

    from ingest_inflation import main as ingest_inflation_main
    from ingest_treasury import main as ingest_treasury_main
    from ingest_vix import main as ingest_vix_main
    from ingest_spx import main as ingest_spx_main
    from ingest_sectors import main as ingest_sectors_main

    _run_step("Inflation (CPIAUCSL from FRED)", ingest_inflation_main)
    _run_step("Treasury (DGS2, DGS10, FEDFUNDS from FRED)", ingest_treasury_main)
    _run_step("VIX (VIXCLS from FRED)", ingest_vix_main)
    _run_step("S&P 500 (Yahoo Finance)", ingest_spx_main)
    _run_step("Sector ETFs (Yahoo Finance)", ingest_sectors_main)

    # --- Cleaning / processing --------------------------------------------
    print("[2/3] Processing raw data into cleaned datasets")

    from process_inflation import main as process_inflation_main
    from process_treasury import main as process_treasury_main
    from process_vix import main as process_vix_main
    from process_spx import main as process_spx_main
    from process_sectors import main as process_sectors_main

    _run_step("Inflation → inflation_processed.csv", process_inflation_main)
    _run_step("Treasury → treasury_processed.csv", process_treasury_main)
    _run_step("VIX → vix_processed.csv", process_vix_main)
    _run_step("S&P 500 → spx_processed.csv", process_spx_main)
    _run_step("Sectors → sectors_processed.csv", process_sectors_main)

    # --- Summary ----------------------------------------------------------
    print("[3/3] Pipeline complete")
    print("  Raw files:       data/raw/")
    print("  Processed files: data/processed/")


if __name__ == "__main__":
    main()
