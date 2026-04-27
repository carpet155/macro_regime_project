"""
One-time migration helper: refactor data/processed/ into subfolders.

This script moves existing CSVs from the legacy flat `data/processed/` layout into:

  data/processed/base/
  data/processed/features/
  data/processed/analysis/
  data/processed/final/

This script is **optional developer-only cleanup** for reorganizing existing local files.
It is **NOT** required for first-time reproducibility: a fresh clone should run the
pipeline scripts to generate outputs directly into the new folder structure.

It is intentionally conservative:
- Creates directories if needed
- Moves files only if the source exists and the destination does NOT exist
- Prints a clear report of actions

Run from repo root (optional):
  python scripts/migrate_processed_structure.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MovePlan:
    src: Path
    dst: Path


def _plans(processed_root: Path) -> list[MovePlan]:
    base = processed_root / "base"
    features = processed_root / "features"
    analysis = processed_root / "analysis"
    final = processed_root / "final"

    # Explicit required structure from the refactor request.
    plans: list[MovePlan] = [
        # Base datasets
        MovePlan(processed_root / "master_df.csv", base / "master_df.csv"),
        MovePlan(processed_root / "master_panel_df.csv", base / "master_panel_df.csv"),
        # Feature/intermediate processed files
        MovePlan(processed_root / "inflation_processed.csv", features / "inflation_processed.csv"),
        MovePlan(processed_root / "sectors_processed.csv", features / "sectors_processed.csv"),
        MovePlan(processed_root / "sector_returns_processed.csv", features / "sector_returns_processed.csv"),
        MovePlan(processed_root / "spx_processed.csv", features / "spx_processed.csv"),
        MovePlan(processed_root / "treasury_processed.csv", features / "treasury_processed.csv"),
        MovePlan(processed_root / "vix_processed.csv", features / "vix_processed.csv"),
        # Analysis outputs (combined regime explicitly; also sweep similar files)
        MovePlan(processed_root / "avg_return_by_combined_regime.csv", analysis / "avg_return_by_combined_regime.csv"),
        MovePlan(processed_root / "annualized_return_by_combined_regime.csv", analysis / "annualized_return_by_combined_regime.csv"),
        MovePlan(processed_root / "pivot_sector_by_combined_regime.csv", analysis / "pivot_sector_by_combined_regime.csv"),
        MovePlan(processed_root / "avg_return_summary.csv", analysis / "avg_return_summary.csv"),
        # Final/presentation tables (only move if they already exist)
        MovePlan(processed_root / "table_avg_return_by_macro_regime.csv", final / "table_avg_return_by_macro_regime.csv"),
        MovePlan(processed_root / "table_volatility_by_macro_regime.csv", final / "table_volatility_by_macro_regime.csv"),
    ]

    # Move any other regime-specific analysis outputs if present
    for pattern in [
        "avg_return_by_*_regime.csv",
        "annualized_return_by_*_regime.csv",
        "pivot_sector_by_*_regime.csv",
    ]:
        for src in processed_root.glob(pattern):
            dst = analysis / src.name
            # Avoid duplicates for the explicit combined moves above
            if any(p.src == src for p in plans):
                continue
            plans.append(MovePlan(src, dst))

    return plans


def migrate(processed_root: Path = Path("data/processed")) -> int:
    processed_root = Path(processed_root)
    processed_root.mkdir(parents=True, exist_ok=True)

    # Ensure target folders exist
    for sub in ["base", "features", "analysis", "final"]:
        (processed_root / sub).mkdir(parents=True, exist_ok=True)

    moved = 0
    skipped = 0
    missing = 0

    for plan in _plans(processed_root):
        if not plan.src.exists():
            missing += 1
            continue
        plan.dst.parent.mkdir(parents=True, exist_ok=True)

        if plan.dst.exists():
            skipped += 1
            print(f"SKIP (dst exists) {plan.src} -> {plan.dst}")
            continue

        plan.src.rename(plan.dst)
        moved += 1
        print(f"MOVED {plan.src} -> {plan.dst}")

    print("\nMigration summary")
    print(f"  moved  : {moved}")
    print(f"  skipped: {skipped} (destination already existed)")
    print(f"  missing: {missing} (source file not present)")
    return 0


if __name__ == "__main__":
    raise SystemExit(migrate())

