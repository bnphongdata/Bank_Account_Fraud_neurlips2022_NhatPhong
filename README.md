# Bank Account Fraud Analysis (NeurIPS 2022)

Data analysis and fraud detection suite on the NeurIPS 2022 Bank Account Fraud (BAF) dataset.

---

## Project Structure

```text
BAF/
│
├── data/
│   ├── raw/                  # Raw source files (Base.csv, Variant I-V.csv)
│   ├── processed/            # Cleaned Parquet exports (clean_base.parquet)
│   └── external/             # Lookup dictionaries and metadata
│
├── notebooks/                # Exploratory analysis & deep-dive notebooks
│   ├── 01_eda_and_cleaning.ipynb
│   └── 02_fraud_deep_dive.ipynb
│
├── src/                      # Reusable modules
│   ├── data/                 # Loading utilities with PyArrow/DuckDB (load_data.py)
│   ├── features/             # Sentinel handling & feature engineering (clean_and_engineer.py)
│   └── visualization/        # Plotting helpers and chart exports (visualize.py)
│
├── reports/                  # Analysis reports and exported figures
│   ├── figures/              # Generated high-resolution charts
│   └── fraud_analysis_report.md
│
├── sql/                      # Standalone SQL scripts (DuckDB / PostgreSQL)
│   ├── 01_data_profiling.sql
│   ├── 02_data_cleaning.sql
│   └── 03_fraud_analysis_queries.sql
│
├── config/                   # Configuration files
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Environment Setup
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run Data Processing
```powershell
python -m src.features.clean_and_engineer
```

### 3. Generate Report Charts
```powershell
python -m src.visualization.generate_report_charts
```
