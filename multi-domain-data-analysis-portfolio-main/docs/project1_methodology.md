# Project 1 Methodology - Supermarket Sales Analysis

## Business objective

Understand which categories, products, customer groups, branches, days, and hours generate the most revenue and profit, then convert those findings into inventory and promotion decisions.

## Dataset

The project uses a reproducible simulated dataset covering 1 January to 31 March 2024. Transactions represent three Indian branches and six product categories. Demand weights, weekend traffic, evening traffic, member discounts, category margins, and customer ratings are modelled to resemble realistic retail behaviour.

## Data-quality workflow

1. Verify required columns.
2. Count missing values and duplicated invoice IDs.
3. Validate numeric ranges for price, quantity, discount, and rating.
4. Remove duplicate invoices.
5. Convert dates and numeric fields to appropriate data types.
6. Impute missing ratings with the median.
7. Reject unusable rows with invalid price, quantity, date, or product fields.
8. Re-run validation on the cleaned dataset.

## Feature engineering

- Gross sales = unit price x quantity
- Discount amount = gross sales x discount percentage
- Net sales = gross sales - discount amount
- Total cost = cost price x quantity
- Profit = net sales - total cost
- Profit margin = profit / net sales
- Calendar and time fields: weekday, month, hour, and time slot

## Statistical methods

Descriptive statistics include count, mean, median, standard deviation, minimum, quartiles, and maximum. Pearson correlation is used to study quantity-sales and discount-sales relationships. Grouped aggregation is used for category, product, branch, customer, weekday, hourly, and monthly comparisons.

## Limitations

The data is simulated and cannot establish causal effects. Correlation does not prove that discounts caused sales changes. Recommendations should be tested through controlled promotions before full implementation.

