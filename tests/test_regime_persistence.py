def test_basic():
    import pandas as pd
    from macro_regime.analysis import regime_run_segments

    df = pd.DataFrame({
        "date": pd.date_range("2020-01-01", periods=5),
        "regime": ["A", "A", "B", "B", "A"],
    })

    segments = regime_run_segments(df, "regime", "date")

    assert len(segments) == 3