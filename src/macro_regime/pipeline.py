"""End-to-end pipeline orchestration for the macro regime project.

This module is the package-level source of truth for reproducing the project
outputs. It coordinates the existing ingestion, processing, build, and analysis
steps so users can run the project with one command after installing the package.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - python-dotenv is listed as a dependency.
    load_dotenv = None

from macro_regime.build import build_master_df
from macro_regime.config import (
    PROCESSED_ANALYSIS_DIR,
    PROCESSED_BASE_DIR,
    PROCESSED_DIR,
    PROCESSED_FEATURES_DIR,
    PROJECT_ROOT,
    RAW_DIR,
    RAW_FILES,
)
from macro_regime.io import MASTER_DF_FILENAME, save_csv
from macro_regime.panel import build_wide_panel_df
from macro_regime.regimes import assign_all_regimes


SCRIPTS_DIR = PROJECT_ROOT / "scripts"

INGESTION_SCRIPTS = [
    "ingest_spx.py",
    "ingest_sectors.py",
    "ingest_vix.py",
    "ingest_treasury.py",
    "ingest_inflation.py",
]

PROCESSING_SCRIPTS = [
    "process_inflation.py",
    "process_sectors.py",
    "process_spx.py",
    "process_treasury.py",
    "process_vix.py",
]

ANALYSIS_SCRIPTS = [
    "build_pivot_tables.py",
    "compute_avg_returns_by_regime.py",
]

FEATURE_OUTPUTS = [
    "inflation_processed.csv",
    "sectors_processed.csv",
    "sector_returns_processed.csv",
    "spx_processed.csv",
    "treasury_processed.csv",
    "vix_processed.csv",
]

ANALYSIS_OUTPUTS = [
    "pivot_sector_by_inflation_regime.csv",
    "pivot_sector_by_rate_regime.csv",
    "pivot_sector_by_vix_regime.csv",
    "pivot_sector_by_combined_regime.csv",
    "avg_return_by_inflation_regime.csv",
    "avg_return_by_rate_regime.csv",
    "avg_return_by_vix_regime.csv",
    "avg_return_by_combined_regime.csv",
    "annualized_return_by_inflation_regime.csv",
    "annualized_return_by_rate_regime.csv",
    "annualized_return_by_vix_regime.csv",
    "annualized_return_by_combined_regime.csv",
    "avg_return_summary.csv",
]


class PipelineStageError(RuntimeError):
    """Raised when a named pipeline stage fails."""


def _load_project_env() -> None:
    """Load ``.env`` from the project root when python-dotenv is available."""
    if load_dotenv is not None:
        load_dotenv(PROJECT_ROOT / ".env")


def _run_stage(stage_name: str, func: Any) -> Any:
    """Run one pipeline stage and re-raise failures with stage context."""
    print(f"\n=== {stage_name} ===", flush=True)
    try:
        result = func()
    except PipelineStageError:
        raise
    except Exception as exc:
        raise PipelineStageError(f"{stage_name} failed: {exc}") from exc
    print(f"Completed: {stage_name}", flush=True)
    return result


def _run_python_script(script_name: str) -> None:
    """Run one existing project script with the current Python interpreter."""
    script_path = SCRIPTS_DIR / script_name
    if not script_path.is_file():
        raise FileNotFoundError(f"Missing script: {script_path}")

    try:
        subprocess.run(
            [sys.executable, str(script_path)],
            cwd=PROJECT_ROOT,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Script {script_name} failed with exit code {exc.returncode}"
        ) from exc


def _require_files(paths: list[Path], stage_name: str) -> None:
    """Validate that expected files exist and are not empty."""
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            f"{stage_name} did not create expected file(s): "
            f"{[str(path) for path in missing]}"
        )

    empty = [path for path in paths if path.stat().st_size == 0]
    if empty:
        raise ValueError(
            f"{stage_name} created empty file(s): {[str(path) for path in empty]}"
        )


def _require_columns(df: pd.DataFrame, columns: set[str], stage_name: str) -> None:
    """Validate that a DataFrame is non-empty and has required columns."""
    if df.empty:
        raise ValueError(f"{stage_name} produced an empty DataFrame")

    missing = sorted(columns.difference(df.columns))
    if missing:
        raise ValueError(f"{stage_name} missing required column(s): {missing}")


def ensure_pipeline_directories() -> list[Path]:
    """Create directories used by the full pipeline and return them."""
    directories = [
        RAW_DIR,
        PROCESSED_DIR,
        PROCESSED_FEATURES_DIR,
        PROCESSED_BASE_DIR,
        PROCESSED_ANALYSIS_DIR,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    return directories


def check_fred_api_key() -> None:
    """Fail clearly if FRED ingestion cannot run because ``FRED_API_KEY`` is missing."""
    _load_project_env()
    if not os.getenv("FRED_API_KEY"):
        raise EnvironmentError(
            "FRED_API_KEY is not set. Set it before running the full pipeline, "
            "for example: export FRED_API_KEY='your-api-key-here'."
        )


def ingest_all() -> list[Path]:
    """Download all raw inputs into ``data/raw/`` using existing ingestion scripts."""
    check_fred_api_key()
    ensure_pipeline_directories()

    for script_name in INGESTION_SCRIPTS:
        _run_python_script(script_name)

    raw_paths = [RAW_DIR / filename for filename in RAW_FILES.values()]
    _require_files(raw_paths, "ingestion")
    return raw_paths


def process_all() -> list[Path]:
    """Process raw inputs into cleaned feature CSVs under ``data/processed/features/``."""
    ensure_pipeline_directories()

    for script_name in PROCESSING_SCRIPTS:
        _run_python_script(script_name)

    feature_paths = [PROCESSED_FEATURES_DIR / filename for filename in FEATURE_OUTPUTS]
    _require_files(feature_paths, "processing")
    return feature_paths


def merge_master() -> Path:
    """Build the canonical long-form master dataset and save it under ``base/``.

    The saved master includes the regime columns used by downstream analysis:
    ``inflation_regime``, ``rate_regime``, ``macro_regime``, and ``vix_regime``.
    """
    ensure_pipeline_directories()

    master = build_master_df(str(PROCESSED_DIR))
    _require_columns(
        master,
        {"date", "ticker", "sector_return", "cpi", "fedfunds", "vix"},
        "master merge",
    )

    master = assign_all_regimes(master)
    _require_columns(
        master,
        {
            "date",
            "ticker",
            "sector_return",
            "inflation_regime",
            "rate_regime",
            "macro_regime",
            "vix_regime",
        },
        "regime assignment",
    )

    output_path = PROCESSED_BASE_DIR / MASTER_DF_FILENAME
    save_csv(master, output_path, index=False)
    _require_files([output_path], "master export")
    return output_path


def build_panel_output() -> Path:
    """Build the wide panel CSV under ``data/processed/base/``."""
    ensure_pipeline_directories()

    panel = build_wide_panel_df(str(PROCESSED_DIR))
    if panel.empty:
        raise ValueError("panel build produced an empty DataFrame")

    output_path = PROCESSED_BASE_DIR / "master_panel_df.csv"
    save_csv(panel, output_path, index=True)
    _require_files([output_path], "panel export")
    return output_path


def build_analysis_outputs() -> list[Path]:
    """Build regime pivot tables and average-return summaries under ``analysis/``."""
    ensure_pipeline_directories()

    for script_name in ANALYSIS_SCRIPTS:
        _run_python_script(script_name)

    analysis_paths = [PROCESSED_ANALYSIS_DIR / filename for filename in ANALYSIS_OUTPUTS]
    _require_files(analysis_paths, "analysis export")
    return analysis_paths


def run_full_pipeline(
    *,
    run_ingestion: bool = True,
    run_processing: bool = True,
) -> dict[str, Any]:
    """Run the full project pipeline from raw ingestion through analysis outputs.

    Parameters
    ----------
    run_ingestion:
        When True, download raw data into ``data/raw/`` before processing.
        Set to False only when raw files already exist locally.
    run_processing:
        When True, rebuild cleaned feature CSVs from raw files.
        Set to False only when feature files already exist locally.

    Returns
    -------
    dict
        Paths produced by each stage. All outputs are written under the
        canonical ``data/raw`` and ``data/processed`` directories.
    """
    outputs: dict[str, Any] = {}

    _run_stage("Create pipeline directories", ensure_pipeline_directories)

    if run_ingestion:
        outputs["raw"] = _run_stage("Ingest raw data", ingest_all)

    if run_processing:
        outputs["features"] = _run_stage("Process raw data", process_all)

    outputs["master"] = _run_stage("Build master dataset", merge_master)
    outputs["panel"] = _run_stage("Build panel dataset", build_panel_output)
    outputs["analysis"] = _run_stage("Build analysis outputs", build_analysis_outputs)

    print("\nFull pipeline completed successfully.", flush=True)
    print(f"Master dataset: {outputs['master']}", flush=True)
    print(f"Panel dataset:  {outputs['panel']}", flush=True)
    print(f"Analysis dir:   {PROCESSED_ANALYSIS_DIR}", flush=True)
    return outputs


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point for ``python -m macro_regime.pipeline``."""
    parser = argparse.ArgumentParser(description="Run the full macro regime pipeline.")
    parser.add_argument(
        "--skip-ingestion",
        action="store_true",
        help="Use existing files in data/raw/ instead of downloading raw data.",
    )
    parser.add_argument(
        "--skip-processing",
        action="store_true",
        help="Use existing files in data/processed/features/ instead of rebuilding them.",
    )
    args = parser.parse_args(argv)

    run_full_pipeline(
        run_ingestion=not args.skip_ingestion,
        run_processing=not args.skip_processing,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
