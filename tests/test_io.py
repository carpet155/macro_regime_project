import pandas as pd
import pytest

import macro_regime.io as io
from macro_regime.io import (
    load_csv,
    load_master_df,
    load_processed_csv,
    load_raw_csv,
    save_csv,
    save_processed_csv,
    save_raw_csv,
)


def _sample_df():
    return pd.DataFrame({"date": ["2020-01-02"], "value": [1.5]})


def test_save_csv_creates_parent_directory_and_writes_file(tmp_path):
    df = _sample_df()
    path = tmp_path / "nested" / "example.csv"

    save_csv(df, path)

    assert path.is_file()
    result = pd.read_csv(path)
    pd.testing.assert_frame_equal(result, df)


def test_load_csv_reads_existing_file(tmp_path):
    df = _sample_df()
    path = tmp_path / "example.csv"
    df.to_csv(path, index=False)

    result = load_csv(path)

    pd.testing.assert_frame_equal(result, df)


def test_load_csv_missing_file_raises(tmp_path):
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="File not found"):
        load_csv(missing_path)


def test_save_raw_csv_writes_to_raw_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "RAW_DIR", tmp_path / "raw")
    df = _sample_df()

    path = save_raw_csv(df, "example_raw.csv")

    assert path == tmp_path / "raw" / "example_raw.csv"
    assert path.is_file()
    pd.testing.assert_frame_equal(pd.read_csv(path), df)


def test_load_raw_csv_reads_from_raw_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "RAW_DIR", tmp_path / "raw")
    df = _sample_df()
    raw_path = tmp_path / "raw" / "example_raw.csv"
    raw_path.parent.mkdir(parents=True)
    df.to_csv(raw_path, index=False)

    result = load_raw_csv("example_raw.csv")

    pd.testing.assert_frame_equal(result, df)


def test_save_processed_csv_writes_to_processed_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "PROCESSED_DIR", tmp_path / "processed")
    df = _sample_df()

    path = save_processed_csv(df, "example_processed.csv")

    assert path == tmp_path / "processed" / "example_processed.csv"
    assert path.is_file()
    pd.testing.assert_frame_equal(pd.read_csv(path), df)


def test_load_processed_csv_reads_from_processed_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(io, "PROCESSED_DIR", tmp_path / "processed")
    df = _sample_df()
    processed_path = tmp_path / "processed" / "example_processed.csv"
    processed_path.parent.mkdir(parents=True)
    df.to_csv(processed_path, index=False)

    result = load_processed_csv("example_processed.csv")

    pd.testing.assert_frame_equal(result, df)


def test_load_master_df_loads_canonical_file(tmp_path):
    processed_dir = tmp_path / "processed"
    (processed_dir / "base").mkdir(parents=True)
    pd.DataFrame(
        {
            "date": ["2020-01-02"],
            "ticker": ["XLK"],
            "sector_return": [0.01],
        }
    ).to_csv(processed_dir / "base" / "master_df.csv", index=False)

    result = load_master_df(processed_dir)

    assert result.loc[0, "ticker"] == "XLK"
    assert pd.api.types.is_datetime64_any_dtype(result["date"])


def test_load_master_df_missing_required_column_raises(tmp_path):
    processed_dir = tmp_path / "processed"
    (processed_dir / "base").mkdir(parents=True)
    pd.DataFrame({"date": ["2020-01-02"], "ticker": ["XLK"]}).to_csv(
        processed_dir / "base" / "master_df.csv",
        index=False,
    )

    with pytest.raises(ValueError, match="missing required column"):
        load_master_df(processed_dir)

