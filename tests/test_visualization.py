from src.macro_regime.visualization import plot_regime_overlay
import matplotlib.pyplot as plt

print("Testing visualization function...")

try:
    # Use "sector_return" because that is the name in your DataFrame
    # Ensure "XLK" (or another ticker) is valid in your data
    fig, ax = plot_regime_overlay(
        value_col="sector_return", 
        regime_col="macro_regime", 
        sector="XLK", 
        title="XLK Sector Returns with Macro Regimes"
    )
    plt.show()
    print("Success! Plot window should be open.")
except Exception as e:
    print(f"An error occurred: {e}")