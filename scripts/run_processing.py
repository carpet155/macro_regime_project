"""Run all ``process_*.py`` scripts in order (raw -> processed)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
PROCESSING_SCRIPTS: list[Path] = [
    SCRIPTS_DIR / "process_inflation.py",
    SCRIPTS_DIR / "process_sectors.py",
    SCRIPTS_DIR / "process_spx.py",
    SCRIPTS_DIR / "process_treasury.py",
    SCRIPTS_DIR / "process_vix.py",
]


def run_script(path: Path) -> None:
    """Execute ``path`` with ``sys.executable``; raise on non-zero exit."""
    name = path.name
    print(f"Running {name}...", flush=True)
    try:
        subprocess.run(
            [sys.executable, str(path)],
            check=True,
            cwd=str(path.parent.parent),
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Processing script failed: {name} (exit code {e.returncode})") from e
    print(f"Completed {name}", flush=True)


def main() -> None:
    for script in PROCESSING_SCRIPTS:
        if not script.is_file():
            raise FileNotFoundError(f"Missing processing script: {script}")
        run_script(script)
    print("All processing scripts completed successfully.", flush=True)


if __name__ == "__main__":
    main()
