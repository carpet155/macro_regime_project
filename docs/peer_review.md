# Peer Review of `macro_regime_project`

This document reviews the project repository as it stands at the end of the cleanup phase, ahead of the April 29 submission. The review covers configuration, documentation, repository structure, the Python package in `src/`, the scripts in `scripts/`, the tests in `tests/`, the notebooks in `notebooks/`, and the data pipeline in `data/`.

**Reviewer:** Alaa Hayajneh (`TheCEOBOSS`)
**Review date:** April 28, 2026
**Reviewed against:** `main` branch
**Scope:** Project-wide review covering all top-level directories and their contents

---

## Summary

The project is in good shape ahead of submission. The team has built out the ingestion-to-analysis pipeline cleanly, the regime classification logic is well-tested, and most documentation is in place. The findings below are split between **issues that should be fixed before April 29** (critical) and **suggestions that would improve the project but are not blockers** (nice-to-have).

| Area | Status | Critical findings | Suggestions |
|---|---|---:|---:|
| `pyproject.toml` and dependencies | ✅ Good | 0 | 1 |
| Root `README.md` | ⚠️ Has broken links | 1 | 2 |
| `SETUP.md` | ✅ Strong | 0 | 2 |
| Repository structure | ✅ Clean | 0 | 0 |
| `src/macro_regime/` package | ✅ Good | 0 | 2 |
| `scripts/` directory | ✅ Good | 0 | 1 |
| `tests/` directory | ✅ Good | 0 | 1 |
| `notebooks/` directory | ✅ Good | 0 | 1 |
| `data/` pipeline | ✅ Good | 0 | 1 |
| Issue tracker hygiene | ⚠️ Minor drift | 0 | 1 |

**Critical: 1.** **Suggestions: 12.** The single critical finding is a quick fix and is documented in detail below.

---

## 1. `pyproject.toml` and dependencies

The build configuration is clean and modern. Uses the standard `setuptools` build backend with a src-layout (`package-dir = {"" = "src"}`), pins runtime dependencies with sensible lower bounds (`pandas>=2.0`, `numpy>=1.24`, `fredapi>=0.5`, `yfinance>=0.2`, `requests>=2.28`, `matplotlib>=3.7`), and includes a well-chosen `[dev]` extras group (`pytest`, `pytest-cov`, `black`, `ruff`).

**Suggestion (low):** `requirements.txt` exists alongside `pyproject.toml`. These can drift over time. Either remove `requirements.txt` and standardize on `pip install -e .`, or add a comment to it noting that `pyproject.toml` is the source of truth.

---

## 2. Root `README.md`

The README has the right structure: project title, group members, goals, getting started, data sources, and notes on data provenance.

### ⚠️ Critical finding: Data source links are broken

In the **Raw Macro Data** section, each bullet point has two links:
1. A link to a path under `docs/data/raw/` (e.g. `docs/data/raw/CPIAUCSL.csv`)
2. A link to the FRED series page

The first link in each bullet (the `docs/data/raw/...` path) is **broken**. The raw data lives in `data/raw/`, not `docs/data/raw/`. Clicking those links from the rendered README produces a 404.

**Recommended fix:** Either change the broken links to point to `data/raw/CPIAUCSL.csv` etc., or remove the in-repo links entirely and keep only the FRED page links.

This is a pre-submission must-fix because it's the very first thing a grader will click on.

### Suggestions

- **Goals section has minor copy issues:** "vrs," should be "vs.", and "in an well-organized" should be "in a well-organized." Worth a quick proofread pass on the whole file before submission.
- **Installation block is too thin:** It shows `git clone`, `cd`, and `pip install -e ".[dev]"` but does not mention prerequisites (Python 3.9+, FRED API key) or post-install verification. The detailed steps in `SETUP.md` cover this, but the README should at least link to `SETUP.md` so a new reader knows to go there. Consider adding: "For full setup instructions including the FRED API key, see [SETUP.md](SETUP.md)."

---

## 3. `SETUP.md`

This is the strongest documentation file in the repo. It walks new contributors through Git installation (Mac and Windows), Python installation, finding and claiming an issue, the branching workflow, committing, pushing, and creating a pull request. The "Helpful Commands" reference table at the end is a particularly nice touch for first-time GitHub users.

### Suggestions

- **Section 3 is dated:** "I have deleted all the old branches before today, sorry." This was a real-time message during development. For a final submission document, recommend rewording to something more permanent like "Each feature is developed on its own branch off of `main`. The repository's branch protection requires all merges to go through pull requests."
- **Section 5 numbering restarts:** Steps are numbered "1, 2, 3, 4, 5, 6" but then later text says "After Step 6" with no clearly visible Step 6. The numbering can be made consistent in a quick pass.

---

## 4. Repository structure

The src-layout is correct and standard:

```
data/raw/        Raw ingested datasets
data/processed/  Cleaned, business-day-indexed datasets
docs/            Project documentation and analysis narrative
notebooks/       Jupyter notebooks
scripts/         Ingestion and processing entry points
src/macro_regime/ Importable Python package
tests/           Unit and integration tests
```

This matches the layout declared in `pyproject.toml` (`[tool.setuptools] package-dir = {"" = "src"}`). Everything is where it should be. **No action required.**

---

## 5. `src/macro_regime/` package

The core importable package contains the reusable logic — the regime classifiers, the data cleaning utilities, and the analysis functions. Issues #64-67 (regime feature engineering) and #66 (combined regime) are all marked complete, and the unit tests in `tests/` exercise this code.

### Suggestions

- **Module-level docstrings:** Issue #90 (Docstrings) is marked complete on the tracker. As part of this review, I recommend a final spot-check that every module in `src/macro_regime/` has a top-of-file docstring describing the module's purpose, the public functions it exposes, and any external dependencies it requires (e.g., FRED API). Class and function docstrings should follow a consistent style (the project's `[dev]` extras include `ruff`, which can enforce this with the `D` rule group if enabled).
- **Type hints:** Where present they are helpful; where missing, adding them on public function signatures (return types in particular) would make the package easier to read for a grader skimming through.

---

## 6. `scripts/` directory

The scripts handle data ingestion and processing. Each script is a self-contained entry point (`python scripts/ingest_inflation.py`, etc.). Issue #139 (Unify ingestion scripts) is marked complete, which suggests duplicate logic has been pulled into shared helpers.

### Suggestions

- **Idempotency check:** Verify that running the same ingestion script twice in a row produces identical output (no side effects, deterministic output filenames, no appending to existing files). If the scripts already do this, no action; if not, a one-line note in each script header would help.

---

## 7. `tests/` directory

The test suite covers the regime classification logic and the pipeline functions. Issues #61, #62, #81, and #82 are all complete. Issue #93 (Run full test suite and fix failures) is still **Not Started** as of April 28 — this should be the highest-priority remaining task before submission.

### Suggestions

- **Run the full suite end-to-end once before submission.** Even if individual test files pass in isolation, a fresh `pytest tests/` from the project root on a clean clone verifies that imports work, that no test depends on hidden state, and that the `pyproject.toml` install actually produces an importable package. This is exactly what issue #93 is for, and it should not be skipped.

---

## 8. `notebooks/` directory

GitHub reports the repo is 64.5% Jupyter Notebook by content size, which is expected — the notebooks are where the analysis is presented. Issue #92 (Exploratory analysis notebook) is complete.

### Suggestion

- **Restart-and-run-all check:** Before submission, open each notebook, click "Restart Kernel and Run All," and verify it runs cleanly from top to bottom. Notebooks committed mid-edit can have stale cell outputs that don't match the current code, which is confusing for graders.

---

## 9. `data/` pipeline

The pipeline cleanly separates raw ingestion (`data/raw/`) from processed analysis-ready data (`data/processed/`). The `data/README.md` documents the pipeline well. Raw CSVs are committed for reproducibility, which is the right call for a graded project.

### Suggestion

- **Document the date range** of the processed datasets in `data/README.md` (e.g., "Processed data spans 2010-01-04 to 2026-04-15"). This saves a grader from having to load the data to understand its scope.

---

## 10. Issue tracker hygiene

A spot-check of GitHub issues against the Excel tracker shows generally good alignment. A few issues had ownership drift earlier in the project (one person assigned in Excel, no one assigned on GitHub), but this has largely been resolved.

### Suggestion

- **Final reconciliation pass on April 28:** Before submission, make one final pass through all closed issues to confirm the GitHub assignee matches the Excel tracker, and that every closed issue has a linked merged PR. This will be cross-referenced in issue #98 (Contribution balance).

---

## Pre-Submission Action Items

In priority order:

1. **[Critical]** Fix the broken `docs/data/raw/...` links in `README.md` — change to `data/raw/...` or remove the in-repo links.
2. **[High]** Run the full test suite (issue #93) and resolve any failures.
3. **[High]** Restart-and-run-all every notebook in `notebooks/` to confirm clean execution.
4. **[Medium]** Quick proofread pass on `README.md` for the typos noted above.
5. **[Medium]** Update Section 3 of `SETUP.md` to remove dated language.
6. **[Low]** Add a `[SETUP.md](SETUP.md)` link from the README's Installation section.
7. **[Low]** Confirm `requirements.txt` and `pyproject.toml` runtime dependencies match.

The project is well-positioned for submission. The single critical issue is a 30-second fix. Everything else is polish.
