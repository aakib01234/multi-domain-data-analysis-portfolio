# Project 5 Methodology - Stock Market and Portfolio Risk Analysis

## Objective

Measure price performance, daily returns, annualised return and volatility, Sharpe ratio, drawdown, correlations, and equal-weight portfolio behaviour.

## Dataset

The reproducible simulated dataset contains business-day closing prices and volumes from 2022 through 2024 for five fictional assets: AURORA, NOVA, ORBIT, PRISM, and ZENITH. No values represent real securities or investment performance.

## Definitions and assumptions

- Daily return = current close / prior close - 1
- Total return = ending close / starting close - 1
- Annualised return = compounded annual growth rate over elapsed calendar years
- Annualised volatility = daily-return standard deviation x square root of 252
- Sharpe ratio = annualised excess daily return divided by annualised volatility
- Risk-free rate assumption = 6% per year
- Maximum drawdown = largest peak-to-trough percentage decline
- Portfolio = equal weights, daily rebalanced for analytical simplicity; no fees, taxes, slippage, dividends, or corporate actions

## Quality workflow

The pipeline checks schema, ticker-date duplicates, dates, positive prices, nonnegative volume, and missingness. Prices are forward-filled only within ticker after sorting; volume is imputed with ticker median. Returns begin after the first valid observation.

## Limitations

Simulated historical analysis does not predict future returns. Daily rebalancing, frictionless trading, and a constant risk-free rate are simplifying assumptions. Results are educational and not investment advice.

