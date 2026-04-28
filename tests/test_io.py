import pandas as pd
import pytest

from macro_regime.io import load_master_df


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

