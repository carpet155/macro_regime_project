"""Thin script wrapper for the package-level full pipeline.

Usage:
    python scripts/run_pipeline.py

The implementation lives in ``macro_regime.pipeline`` so the same workflow is
available through ``python -m macro_regime.pipeline`` and package imports.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from macro_regime.pipeline import main


if __name__ == "__main__":
    raise SystemExit(main())
