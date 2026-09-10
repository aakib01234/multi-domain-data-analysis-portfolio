import pandas as pd
from src.weather_analysis import validate_weather_data,clean_weather_data,calculate_weather_kpis


def sample_weather():
    rows=[
      {"date":"2024-05-01","city":"Delhi","region":"North","temperature_max_c":42,"temperature_min_c":27,"rainfall_mm":0,"humidity_pct":32,"wind_speed_kmh":12,"weather_condition":"Clear"},
      {"date":"2024-07-01","city":"Mumbai","region":"West","temperature_max_c":31,"temperature_min_c":26,"rainfall_mm":80,"humidity_pct":88,"wind_speed_kmh":22,"weather_condition":"Heavy Rain"}]
    return pd.DataFrame(rows+[rows[0]])


def test_validation_detects_duplicate(): assert validate_weather_data(sample_weather())["duplicate_city_dates"]==1


def test_cleaning_and_extreme_flags():
    clean=clean_weather_data(sample_weather()); assert len(clean)==2
    assert bool(clean.loc[clean.city=="Delhi","heatwave_day"].iloc[0])
    assert bool(clean.loc[clean.city=="Mumbai","heavy_rain_day"].iloc[0])
    assert clean.loc[clean.city=="Delhi","temperature_mean_c"].iloc[0]==34.5


def test_weather_kpis():
    k=calculate_weather_kpis(clean_weather_data(sample_weather())); assert k["observations"]==2
    assert k["extreme_event_days"]==2 and k["max_daily_rainfall_mm"]==80

