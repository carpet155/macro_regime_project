# Regime-based Analysis of Sector Returns Under Varying Macroeconomic Conditions

This project analyzes the impact between the macro environment under different economic conditions and various stock market sectors. The goal is to examine the volatility of these sectors in distinct regimes such as; high inflation + rising rates and low inflation + falling rates. 

---

## Group Members 

Charles Stewart, Gianna Gatling, Muhammad Rashid, Leo Lee, David Okorie, Ethan Ooi, Goretty Bustamente Pinares, Alaa Hayajneh, Shlok Rawal, Ishan Srivastava, Benjamin Davis, Adam Lucas, Bithynia Solomon, Nemmo Ciccone, Peter Burhouse, Morgan Simmons, Shikha Raghuram, Amita Pavuloori. 

---

## Project Goals 

- Define and classify macroeconomic regimes of interest (e.g., high vs. low inflation, rising vs. falling interest rates).
- Build a clean merged dataset combining economic indicators and stock market sector-level data.
- Evaluate how sector returns differ across defined macroeconomic regimes, identifying consistent performance trends.
- Identify and analyze changes in sector volatility under economic stress conditions vs. stable economic conditions.
- Apply NumPy and Pandas for numerical and statistical computations in an efficient Python workflow.

---

## Getting Started

### 1. Installation & Setup
Clone the repository and navigate into the project directory:
```bash
git clone [https://github.com/carpet155/macro_regime_project.git](https://github.com/carpet155/macro_regime_project.git)
cd macro_regime_project


### 2. Environment Configuration

### Using pip:
pip install -r requirements.txt

### Using Conda:
conda create --name macro_regime python=3.9
conda activate macro_regime
pip install -r requirements.txt

### 3. Data Ingestion
#### to fetch the raw data 
python scripts/ingest_inflation.py
python scripts/ingest_spx.py
python scripts/ingest_sectors.py
python scripts/ingest_treasury.py
python scripts/ingest_vix.py


### 4. Running the Analysis

jupyter notebook notebooks/explore.ipynb

## Data Sources

CPI (inflation): https://fred.stlouisfed.org/series/CPIAUCSL
Federal Funds Rate: https://fred.stlouisfed.org/series/FEDFUNDS
2-Year Treasury Yield: https://fred.stlouisfed.org/series/DGS2
10-Year Treasury Yield: https://fred.stlouisfed.org/series/DGS10
VIX: https://fred.stlouisfed.org/series/VIXCLS
S&P500: https://finance.yahoo.com/quote/%5EGSPC/history/?period1=-1325583000&period2=1773804185

### Data Sources NOTE
We need to focus on writing and creating python functions to retrieve the financial data. We DO NOT need to seek raw data from outside sources.
