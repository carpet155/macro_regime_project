import pytest

from macro_regime import pipeline


def test_run_full_pipeline_orchestrates_all_stages(monkeypatch, tmp_path):
    calls = []

    def record(stage_name, result):
        def _inner():
            calls.append(stage_name)
            return result

        return _inner

    monkeypatch.setattr(
        pipeline,
        "ensure_pipeline_directories",
        record("directories", [tmp_path / "raw"]),
    )
    monkeypatch.setattr(
        pipeline,
        "ingest_all",
        record("ingest", [tmp_path / "raw" / "SP500.csv"]),
    )
    monkeypatch.setattr(
        pipeline,
        "process_all",
        record("process", [tmp_path / "processed" / "features" / "spx_processed.csv"]),
    )
    monkeypatch.setattr(
        pipeline,
        "merge_master",
        record("master", tmp_path / "processed" / "base" / "master_df.csv"),
    )
    monkeypatch.setattr(
        pipeline,
        "build_panel_output",
        record("panel", tmp_path / "processed" / "base" / "master_panel_df.csv"),
    )
    monkeypatch.setattr(
        pipeline,
        "build_analysis_outputs",
        record("analysis", [tmp_path / "processed" / "analysis" / "avg_return_summary.csv"]),
    )

    outputs = pipeline.run_full_pipeline()

    assert calls == [
        "directories",
        "ingest",
        "process",
        "master",
        "panel",
        "analysis",
    ]
    assert outputs["master"].name == "master_df.csv"
    assert outputs["panel"].name == "master_panel_df.csv"
    assert outputs["analysis"][0].name == "avg_return_summary.csv"


def test_run_stage_adds_stage_context_to_errors():
    def fail():
        raise ValueError("bad input")

    with pytest.raises(pipeline.PipelineStageError, match="Example stage failed: bad input"):
        pipeline._run_stage("Example stage", fail)


def test_require_files_reports_missing_expected_outputs(tmp_path):
    missing = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="test stage did not create expected"):
        pipeline._require_files([missing], "test stage")
