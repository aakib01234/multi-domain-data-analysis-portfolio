"""Validation, cleaning, feature engineering, and KPIs for weather analysis."""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

REQUIRED_COLUMNS={"date","city","region","temperature_max_c","temperature_min_c","rainfall_mm","humidity_pct","wind_speed_kmh","weather_condition"}


def validate_weather_data(df: pd.DataFrame) -> dict:
    missing_cols=sorted(REQUIRED_COLUMNS-set(df.columns))
    dates=pd.to_datetime(df.get("date"),errors="coerce")
    rain=pd.to_numeric(df.get("rainfall_mm"),errors="coerce")
    humid=pd.to_numeric(df.get("humidity_pct"),errors="coerce")
    wind=pd.to_numeric(df.get("wind_speed_kmh"),errors="coerce")
    tmax=pd.to_numeric(df.get("temperature_max_c"),errors="coerce")
    tmin=pd.to_numeric(df.get("temperature_min_c"),errors="coerce")
    return {"rows":int(len(df)),"columns":int(len(df.columns)),"missing_required_columns":missing_cols,
      "duplicate_city_dates":int(df.duplicated(["city","date"]).sum()) if {"city","date"}.issubset(df) else 0,
      "missing_values":{c:int(n) for c,n in df.isna().sum().items() if n>0},"invalid_dates":int(dates.isna().sum()),
      "negative_rainfall_rows":int((rain<0).sum()),"invalid_humidity_rows":int((~humid.between(0,100)&humid.notna()).sum()),
      "negative_wind_rows":int((wind<0).sum()),"invalid_temperature_order_rows":int((tmin>tmax).sum())}


def clean_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    missing=REQUIRED_COLUMNS-set(df.columns)
    if missing: raise ValueError(f"Missing required columns: {sorted(missing)}")
    out=df.copy().drop_duplicates(["city","date"],keep="first")
    out["date"]=pd.to_datetime(out["date"],errors="coerce")
    numeric=["temperature_max_c","temperature_min_c","rainfall_mm","humidity_pct","wind_speed_kmh"]
    for col in numeric: out[col]=pd.to_numeric(out[col],errors="coerce")
    out=out.dropna(subset=["date","city","temperature_max_c","temperature_min_c"])
    out=out[out.temperature_min_c<=out.temperature_max_c]
    for col in ["rainfall_mm","humidity_pct","wind_speed_kmh"]:
        out[col]=out.groupby(["city",out.date.dt.month])[col].transform(lambda s:s.fillna(s.median()))
    out["rainfall_mm"]=out.rainfall_mm.clip(lower=0); out["humidity_pct"]=out.humidity_pct.clip(0,100); out["wind_speed_kmh"]=out.wind_speed_kmh.clip(lower=0)
    out["temperature_mean_c"]=(out.temperature_max_c+out.temperature_min_c)/2
    out["temperature_range_c"]=out.temperature_max_c-out.temperature_min_c
    out["year"]=out.date.dt.year; out["month_num"]=out.date.dt.month; out["month"]=out.date.dt.month_name(); out["day_of_year"]=out.date.dt.dayofyear
    out["season"]=np.select([out.month_num.isin([12,1,2]),out.month_num.isin([3,4,5]),out.month_num.isin([6,7,8,9])],["Winter","Summer","Monsoon"],default="Post-Monsoon")
    out["heavy_rain_day"]=out.rainfall_mm>=64.5
    out["heatwave_day"]=out.temperature_max_c>=40
    out["cold_day"]=out.temperature_min_c<=5
    out["high_wind_day"]=out.wind_speed_kmh>=40
    out["extreme_event"]=out[["heavy_rain_day","heatwave_day","cold_day","high_wind_day"]].any(axis=1)
    return out.sort_values(["date","city"]).reset_index(drop=True)


def calculate_weather_kpis(df: pd.DataFrame) -> dict:
    city_temp=df.groupby("city").temperature_mean_c.mean().sort_values(ascending=False)
    city_rain=df.groupby("city").rainfall_mm.sum().sort_values(ascending=False)
    wet=df.loc[df.rainfall_mm.idxmax()]
    return {"observations":int(len(df)),"cities":int(df.city.nunique()),"start_date":str(df.date.min().date()),"end_date":str(df.date.max().date()),
      "mean_temperature_c":round(float(df.temperature_mean_c.mean()),2),"median_temperature_c":round(float(df.temperature_mean_c.median()),2),
      "total_rainfall_mm":round(float(df.rainfall_mm.sum()),2),"rainy_days":int((df.rainfall_mm>0.1).sum()),"extreme_event_days":int(df.extreme_event.sum()),
      "heatwave_days":int(df.heatwave_day.sum()),"heavy_rain_days":int(df.heavy_rain_day.sum()),"cold_days":int(df.cold_day.sum()),
      "warmest_city":str(city_temp.index[0]),"warmest_city_mean_c":round(float(city_temp.iloc[0]),2),"wettest_city":str(city_rain.index[0]),"wettest_city_rainfall_mm":round(float(city_rain.iloc[0]),2),
      "wettest_observation_date":str(wet.date.date()),"wettest_observation_city":str(wet.city),"max_daily_rainfall_mm":round(float(wet.rainfall_mm),2),
      "temperature_humidity_correlation":round(float(df.temperature_mean_c.corr(df.humidity_pct)),3),"rainfall_humidity_correlation":round(float(df.rainfall_mm.corr(df.humidity_pct)),3)}


def save_json(data:dict,path:str|Path):
    Path(path).parent.mkdir(parents=True,exist_ok=True); Path(path).write_text(json.dumps(data,indent=2),encoding="utf-8")

