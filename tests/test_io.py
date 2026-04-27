import pandas as pd
import pytest

from macro_regime import io as io_module
from macro_regime.io import (
    load_csv,
    load_master_df,
    load_raw_csv,
    save_csv,
    save_processed_csv,
)


def test_save_csv_creates_parent_dirs_and_roundtrips(tmp_path):
    path = tmp_path / "nested" / "out.csv"
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})

    save_csv(df, path)

    assert path.is_file()
    pd.testing.assert_frame_equal(load_csv(path), df)


def test_save_csv_index_flag_is_respected(tmp_path):
    path = tmp_path / "indexed.csv"
    df = pd.DataFrame({"a": [1, 2]}, index=pd.Index([10, 11], name="idx"))

    save_csv(df, path, index=True)

    loaded = load_csv(path)
    assert "idx" in loaded.columns


def test_load_csv_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_csv(tmp_path / "does_not_exist.csv")


def test_save_processed_csv_and_load_raw_csv_use_config_dirs(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    monkeypatch.setattr(io_module, "RAW_DIR", raw_dir)
    monkeypatch.setattr(io_module, "PROCESSED_DIR", processed_dir)

    processed_df = pd.DataFrame({"a": [1, 2]})
    written_path = save_processed_csv(processed_df, "p.csv")
    assert written_path == processed_dir / "p.csv"
    assert written_path.is_file()

    raw_df = pd.DataFrame({"x": [9]})
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_df.to_csv(raw_dir / "r.csv", index=False)
    pd.testing.assert_frame_equal(load_raw_csv("r.csv"), raw_df)


def test_load_master_df_loads_canonical_file(tmp_path):
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    pd.DataFrame(
        {
            "date": ["2020-01-02"],
            "ticker": ["XLK"],
            "sector_return": [0.01],
        }
    ).to_csv(processed_dir / "master_df.csv", index=False)

    result = load_master_df(processed_dir)

    assert result.loc[0, "ticker"] == "XLK"
    assert pd.api.types.is_datetime64_any_dtype(result["date"])


def test_load_master_df_missing_required_column_raises(tmp_path):
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    pd.DataFrame({"date": ["2020-01-02"], "ticker": ["XLK"]}).to_csv(
        processed_dir / "master_df.csv",
        index=False,
    )

    with pytest.raises(ValueError, match="missing required column"):
        load_master_df(processed_dir)


def test_load_master_df_duplicate_rows_raises(tmp_path):
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    pd.DataFrame(
        {
            "date": ["2020-01-02", "2020-01-02"],
            "ticker": ["XLK", "XLK"],
            "sector_return": [0.01, 0.02],
        }
    ).to_csv(processed_dir / "master_df.csv", index=False)

    with pytest.raises(ValueError, match="duplicate"):
        load_master_df(processed_dir)
