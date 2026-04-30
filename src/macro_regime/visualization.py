"""
Visualization Module.
Fits at the tail end of the pipeline to produce graphical representations of the analyzed data and macroeconomic regimes.

Key Responsibilities:
- Overlays categorical macro regimes as background shading on continuous time-series plots.
- Manages matplotlib figures, axes, and colormaps for consistent styling.
- Exports generated plots to local directories for reporting.

Key Functions:
- `plot_regime_overlay`: Main entrypoint for generating time-series plots with regime shading.

Inputs/Outputs:
- Consumes: pd.DataFrame (master data), formatting strings, and optional output paths.
- Returns: Tuple containing matplotlib Figure and Axes objects.
"""

import matplotlib.pyplot as plt
import pandas as pd
from macro_regime.io import load_master_df
from macro_regime.regimes import assign_all_regimes

def plot_regime_overlay(df=None, value_col="sector_return", regime_col="macro_regime", 
                        sector=None, date_col="date", output_path=None, title=None):
    """
    Plots a time-series with macro regime background shading.
    """
    # 1. Load data if not provided
    if df is None:
        df = load_master_df()
    
    # 2. Ensure regimes exist
    if regime_col not in df.columns:
        df = assign_all_regimes(df)
        
    # 3. Sort by date
    df = df.sort_values(by=date_col)
    
    # 4. Filter by sector if provided
    if sector:
        df = df[df['ticker'] == sector]
    
    # 5. Setup Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot the value line
    ax.plot(df[date_col], df[value_col], label=f"{sector or 'Market'} {value_col}", color='black', alpha=0.7)
    
    # 6. Shade Regimes
    # Get unique regimes and assign colors
    regimes = df[regime_col].unique()
    colors = plt.cm.tab10.colors # Use a qualitative colormap
    regime_colors = {regime: colors[i % len(colors)] for i, regime in enumerate(regimes)}
    
    # Iterate through the dataframe to identify spans
    # For efficiency, we just plot the spans regime by regime
    for regime in regimes:
        # Create a mask for this regime
        mask = df[regime_col] == regime
        # To identify continuous chunks, we use the diff trick
        # This is a bit advanced but standard for this type of plotting
        is_regime = mask.astype(int)
        
        # This part assumes daily data for simplicity; 
        # using axvspan on start/end of each continuous block is robust
        for start, end in _get_continuous_blocks(df[date_col][mask]):
            ax.axvspan(start, end, color=regime_colors[regime], alpha=0.2, label=regime)

    # 7. Formatting
    ax.set_title(title or f"{value_col} over {regime_col}")
    ax.set_xlabel("Date")
    ax.set_ylabel(value_col)
    
    # Handle Legend (remove duplicate labels)
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())
    
    if output_path:
        plt.savefig(output_path)
        print(f"Plot saved to {output_path}")
        
    return fig, ax

def _get_continuous_blocks(dates):
    """Helper to group continuous dates into ranges."""
    if len(dates) == 0:
        return []
    
    # Convert to datetime if not already
    dates = pd.to_datetime(dates).sort_values()
    
    blocks = []
    start = dates.iloc[0]
    prev = dates.iloc[0]
    
    for current in dates.iloc[1:]:
        # If the gap is more than 1 day (or whatever frequency), start new block
        if (current - prev).days > 7: # Threshold for 'continuous' regime
            blocks.append((start, prev))
            start = current
        prev = current
    blocks.append((start, prev))
    return blocks
