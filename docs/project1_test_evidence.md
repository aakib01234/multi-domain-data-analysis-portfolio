# Project 1 Testing Evidence

## Automated unit tests

| Test | Purpose | Result |
|---|---|---|
| Duplicate and missing-value detection | Confirms validation identifies duplicate invoice IDs and missing ratings | Pass |
| Cleaning and feature engineering | Confirms duplicates are removed and revenue/profit features are correct | Pass |
| KPI reconciliation | Confirms transaction count, total sales, and total profit reconcile to known sample data | Pass |

Run with `pytest -q`. Expected result: `3 passed`.

## Build validation

- Raw rows: 2,502, including two controlled duplicate records
- Cleaned rows: 2,500
- Missing ratings after cleaning: 0
- Duplicate invoice IDs after cleaning: 0
- Invalid price, quantity, discount, and rating rows after cleaning: 0
- Visualization exports: 5
- PDF pages: 8

