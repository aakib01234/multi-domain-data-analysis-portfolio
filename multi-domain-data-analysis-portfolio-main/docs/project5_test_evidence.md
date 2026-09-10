# Project 5 Testing Evidence

| Test | Purpose | Expected result |
|---|---|---|
| Duplicate validation | Detect repeated ticker-date observations | Pass |
| Return and drawdown logic | Verify duplicate removal, daily return, and drawdown | Pass |
| Asset/portfolio reconciliation | Verify known total return and portfolio aggregation | Pass |

Run `python -m pytest -q`. With all five projects, the portfolio should report fifteen passing tests.

