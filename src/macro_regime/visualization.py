import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_regime_overlay(value_col="return", regime_col="macro_regime", sector=None, date_col="date"):
    path = "data/processed/base/master_df.csv"
    
    # 1. Load data
    df = pd.read_csv(path)
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    
    # 2. Filter if a sector is requested
    if sector:
        if 'ticker' in df.columns:
            df = df[df['ticker'] == sector].copy()
    
    # 3. Initialize plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df[date_col], df[value_col], label=sector or "Market", color='black', alpha=0.7)
    
    # 4. Shade regimes
    df['block_id'] = (df[regime_col] != df[regime_col].shift()).cumsum()
    for _, block in df.groupby(['block_id', regime_col]):
        regime = block[regime_col].iloc[0]
        ax.axvspan(block[date_col].min(), block[date_col].max(), alpha=0.2, label=regime)
            
    ax.set_title(f"{sector or 'Market'} Performance by {regime_col}")
    
    # Remove duplicate legend entries
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())
    
    return fig, ax