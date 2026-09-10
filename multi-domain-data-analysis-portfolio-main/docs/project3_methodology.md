# Project 3 Methodology - Weather Data Analysis

## Objective

Analyse temperature trends, seasonal patterns, rainfall distribution, humidity relationships, and extreme-weather exposure across six Indian cities.

## Dataset

The reproducible simulated dataset contains daily observations from 1 January 2022 to 31 December 2024 for Delhi, Mumbai, Bengaluru, Kolkata, Chennai, and Jaipur. City-specific seasonal temperature, monsoon rainfall, humidity, and wind patterns are modelled for portfolio practice. The data is not an official meteorological record.

## Quality workflow

The pipeline checks required fields, duplicate city-date combinations, missing values, invalid dates, negative rainfall/wind, humidity outside 0-100%, and impossible minimum/maximum temperature ordering. Missing weather measures are imputed using city-month medians.

## Definitions

- Heavy rain day: rainfall at or above 64.5 mm
- Heatwave indicator: maximum temperature at or above 40 C
- Cold day: minimum temperature at or below 5 C
- High-wind day: wind speed at or above 40 km/h
- Extreme event: any of the four indicators is true

Thresholds are analytical portfolio rules, not location-specific official warnings.

## Statistical methods

The analysis uses mean, median, totals, grouped seasonal/monthly trends, rolling patterns, distributions, and Pearson correlations. Correlation is descriptive and does not establish causality.

