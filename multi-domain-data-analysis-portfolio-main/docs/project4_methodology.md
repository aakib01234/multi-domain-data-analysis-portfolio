# Project 4 Methodology - Healthcare Treatment Effectiveness Analysis

## Objective

Compare clinical improvement, favourable outcomes, length of stay, 30-day readmission, treatment cost, and satisfaction across diagnoses and treatment groups.

## Dataset and privacy

The dataset contains 1,800 reproducible simulated patient encounters from 2024. Patient IDs are synthetic, and the project contains no names, addresses, contact information, dates of birth, or real protected health information.

## Outcome definitions

- Clinical improvement = baseline severity score - follow-up severity score
- Improvement percentage = clinical improvement / baseline score
- Favourable outcome = improvement of at least 10 points and no 30-day readmission
- Readmission rate = percentage marked readmitted within 30 days

Lower clinical severity scores are better. Thresholds are analytical portfolio definitions, not clinical guidance.

## Data quality

The pipeline validates required fields, duplicate patient IDs, dates, age, score ranges, nonnegative stay/cost, satisfaction range, and missingness. Missing operational values are imputed using condition-severity medians; records missing core clinical fields are excluded.

## Analytical safeguards

Treatment groups may differ in baseline severity, age, comorbidity, and selection. Comparisons are stratified by condition and severity where practical. Findings are descriptive associations and must not be interpreted as causal treatment recommendations.

