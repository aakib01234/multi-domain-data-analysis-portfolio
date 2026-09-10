# Multi-Domain Data Analysis Portfolio

An end-to-end Python portfolio demonstrating data validation, cleaning, transformation, statistical analysis, visualization, insight generation, testing, and executive reporting across five domains.

## Portfolio at a glance

- **5 complete analytical projects** across retail, education, weather, healthcare, and finance
- **15 automated tests** covering validation, transformation, classification, and KPI reconciliation
- **25 professional visualizations** with at least five chart types per project
- **5 executed Jupyter notebooks** plus reusable Python analysis modules
- **5 project reports** and a cross-project executive summary PDF
- **1 presentation deck** for internship submission and demonstration

## Current Progress

| Project | Domain | Status |
|---|---|---|
| 1. Supermarket Sales Analysis | Retail | Complete |
| 2. Student Performance Analysis | Education | Complete |
| 3. Weather Data Analysis | Weather | Complete |
| 4. Healthcare Analysis | Healthcare | Complete |
| 5. Finance Analysis | Finance | Complete |

## Navigation

| # | Project | Notebook | PDF report | Key analytical focus |
|---|---|---|---|---|
| 1 | Supermarket Sales | `notebooks/01_supermarket_sales_analysis.ipynb` | `reports/01_supermarket_sales_report.pdf` | Revenue, products, customers, time patterns, profit |
| 2 | Student Performance | `notebooks/02_student_performance_analysis.ipynb` | `reports/02_student_performance_report.pdf` | Pass rates, subjects, attendance, risk indicators |
| 3 | Weather Data | `notebooks/03_weather_data_analysis.ipynb` | `reports/03_weather_analysis_report.pdf` | Temperature, rainfall, seasons, extreme indicators |
| 4 | Healthcare Treatment | `notebooks/04_healthcare_treatment_analysis.ipynb` | `reports/04_healthcare_treatment_report.pdf` | Improvement, outcomes, readmission, cost, safeguards |
| 5 | Stock Market Portfolio | `notebooks/05_stock_market_portfolio_analysis.ipynb` | `reports/05_stock_market_portfolio_report.pdf` | Return, volatility, Sharpe ratio, drawdown, correlation |

## Repository structure

```text
multi-domain-data-analysis-portfolio/
├── data/               # Raw, cleaned, validation, and metric files
├── notebooks/          # Five complete Jupyter analyses
├── reports/            # Project reports and portfolio summary
├── visualizations/     # 25 exported PNG charts
├── src/                # Reusable validation and analysis functions
├── scripts/            # Reproducible project build scripts
├── tests/              # Automated validation and KPI tests
├── docs/               # Methodology, recommendations, and guides
├── presentation/       # Final internship presentation deck
├── README.md
├── portfolio_overview.md
├── pytest.ini
└── requirements.txt
```

## Complete setup and verification

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/build_project1.py
python scripts/build_project2.py
python scripts/build_project3.py
python scripts/build_project4.py
python scripts/build_project5.py
python -m pytest -q
```

Expected test result: `15 passed`.

## Project 1: Supermarket Sales Analysis

This analysis studies 2,500 simulated supermarket transactions from January to March 2024. It identifies revenue patterns, product/category performance, customer behaviour, peak shopping periods, discount effects, and profitability opportunities.

### Key deliverables

- Executed Jupyter notebook: `notebooks/01_supermarket_sales_analysis.ipynb`
- Raw and cleaned datasets in `data/project1_sales/`
- Five publication-ready charts in `visualizations/project1_sales/`
- Professional PDF report: `reports/01_supermarket_sales_report.pdf`
- Reusable analysis code in `src/sales_analysis.py`
- Validation and unit tests in `tests/`

### Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/build_project1.py
pytest -q
jupyter notebook notebooks/01_supermarket_sales_analysis.ipynb
```

The datasets are simulated for learning and portfolio demonstration. A fixed random seed makes every build reproducible.

## Responsible-use statement

All datasets are simulated. The healthcare project contains no real patient data and does not provide clinical guidance. The finance project uses fictional assets and is not investment advice. Weather thresholds are simplified analytical rules rather than official warnings. Correlation findings are described as associations, not causal effects.

## Project 2: Student Performance Analysis

This project analyses academic results, attendance, study habits, subject performance, and student risk indicators for 1,200 simulated secondary-school students.

- Notebook: `notebooks/02_student_performance_analysis.ipynb`
- Data: `data/project2_students/`
- Charts: `visualizations/project2_students/`
- Report: `reports/02_student_performance_report.pdf`
- Tests: `tests/test_student_analysis.py`

## Project 3: Weather Data Analysis

This project analyses three years of daily weather observations across six Indian cities, covering temperature trends, seasonal patterns, rainfall distribution, humidity, wind, and extreme-weather events.

- Notebook: `notebooks/03_weather_data_analysis.ipynb`
- Data: `data/project3_weather/`
- Charts: `visualizations/project3_weather/`
- Report: `reports/03_weather_analysis_report.pdf`
- Tests: `tests/test_weather_analysis.py`

## Project 4: Healthcare Treatment Effectiveness Analysis

This project studies simulated, de-identified patient encounters to compare clinical improvement, favourable outcomes, length of stay, readmission, cost, and satisfaction across conditions and treatments.

- Notebook: `notebooks/04_healthcare_treatment_analysis.ipynb`
- Data: `data/project4_healthcare/`
- Charts: `visualizations/project4_healthcare/`
- Report: `reports/04_healthcare_treatment_report.pdf`
- Tests: `tests/test_healthcare_analysis.py`

## Project 5: Stock Market and Portfolio Risk Analysis

This project analyses three years of reproducible simulated daily prices for five fictional assets. It covers returns, volatility, Sharpe ratio, drawdown, asset correlation, and an equal-weight portfolio.

- Notebook: `notebooks/05_stock_market_portfolio_analysis.ipynb`
- Data: `data/project5_finance/`
- Charts: `visualizations/project5_finance/`
- Report: `reports/05_stock_market_portfolio_report.pdf`
- Tests: `tests/test_finance_analysis.py`
