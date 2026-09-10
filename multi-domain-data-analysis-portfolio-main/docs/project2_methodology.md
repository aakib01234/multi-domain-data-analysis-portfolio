# Project 2 Methodology - Student Performance Analysis

## Objective

Measure academic performance, compare subjects, quantify pass/fail outcomes, study attendance and study-hour relationships, and identify students who may benefit from early intervention.

## Dataset

The reproducible simulated dataset represents 1,200 students across four schools, grades 9-12, and five subjects. Scores are influenced by attendance, study time, grade, internet access, and controlled random variation. The simulation is designed for portfolio demonstration and contains no personal data.

## Data quality and transformation

The workflow validates required fields, duplicates, missing values, score ranges, attendance, and study hours. Duplicate student IDs are removed. Missing subject scores are imputed using grade-level medians. Derived fields include overall average, median, subjects passed, result, performance band, and at-risk status.

## Definitions

- Subject pass threshold: 40 marks
- Overall result: Pass only when all five subjects are at or above 40
- At risk: attendance below 75%, any subject failure, or average score below 50
- Correlation: Pearson correlation coefficient

## Limitations

This is simulated observational data. Correlation does not prove causation. Risk flags are screening signals, not final judgements, and should be reviewed by teachers with appropriate context.

