"""Validation, cleaning, and portfolio statistics for simulated market data."""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

REQUIRED_COLUMNS={"date","ticker","sector","close","volume"}
TRADING_DAYS=252


def validate_market_data(df:pd.DataFrame)->dict:
    missing_cols=sorted(REQUIRED_COLUMNS-set(df.columns)); close=pd.to_numeric(df.get("close"),errors="coerce"); volume=pd.to_numeric(df.get("volume"),errors="coerce"); dates=pd.to_datetime(df.get("date"),errors="coerce")
    return {"rows":int(len(df)),"columns":int(len(df.columns)),"missing_required_columns":missing_cols,
      "duplicate_ticker_dates":int(df.duplicated(["ticker","date"]).sum()) if {"ticker","date"}.issubset(df) else 0,
      "missing_values":{c:int(df[c].isna().sum()) for c in REQUIRED_COLUMNS if c in df and df[c].isna().sum()>0},"invalid_dates":int(dates.isna().sum()),
      "nonpositive_price_rows":int((close<=0).sum()),"negative_volume_rows":int((volume<0).sum())}


def clean_market_data(df:pd.DataFrame)->pd.DataFrame:
    missing=REQUIRED_COLUMNS-set(df.columns)
    if missing: raise ValueError(f"Missing required columns: {sorted(missing)}")
    out=df.copy().drop_duplicates(["ticker","date"],keep="first"); out["date"]=pd.to_datetime(out.date,errors="coerce")
    out["close"]=pd.to_numeric(out.close,errors="coerce"); out["volume"]=pd.to_numeric(out.volume,errors="coerce")
    out=out.dropna(subset=["date","ticker","sector"]).sort_values(["ticker","date"])
    out["close"]=out.groupby("ticker").close.ffill(); out["volume"]=out.groupby("ticker").volume.transform(lambda s:s.fillna(s.median()))
    out=out[(out.close>0)&(out.volume>=0)].copy(); out["volume"]=out.volume.astype(int)
    out["daily_return"]=out.groupby("ticker").close.pct_change(fill_method=None)
    out["cumulative_return"]=(1+out.daily_return.fillna(0)).groupby(out.ticker).cumprod()-1
    out["rolling_volatility_21d"]=out.groupby("ticker").daily_return.transform(lambda s:s.rolling(21).std()*np.sqrt(TRADING_DAYS))
    out["rolling_peak"]=out.groupby("ticker").close.cummax(); out["drawdown"]=out.close/out.rolling_peak-1
    return out.reset_index(drop=True)


def asset_metrics(df:pd.DataFrame,risk_free_rate:float=.06)->pd.DataFrame:
    rows=[]
    for ticker,g in df.groupby("ticker"):
      g=g.sort_values("date"); r=g.daily_return.dropna(); years=max((g.date.max()-g.date.min()).days/365.25,1/TRADING_DAYS)
      total=g.close.iloc[-1]/g.close.iloc[0]-1; annual=(1+total)**(1/years)-1; vol=r.std()*np.sqrt(TRADING_DAYS)
      sharpe=((r.mean()-risk_free_rate/TRADING_DAYS)/r.std()*np.sqrt(TRADING_DAYS)) if r.std()>0 else np.nan
      rows.append({"ticker":ticker,"sector":g.sector.iloc[0],"start_price":g.close.iloc[0],"end_price":g.close.iloc[-1],"total_return_pct":total*100,"annualized_return_pct":annual*100,"annualized_volatility_pct":vol*100,"sharpe_ratio":sharpe,"max_drawdown_pct":g.drawdown.min()*100,"average_daily_volume":g.volume.mean()})
    return pd.DataFrame(rows).sort_values("annualized_return_pct",ascending=False).reset_index(drop=True)


def equal_weight_portfolio(df:pd.DataFrame,risk_free_rate:float=.06)->tuple[pd.DataFrame,dict]:
    returns=df.pivot(index="date",columns="ticker",values="daily_return").dropna(); p=returns.mean(axis=1); curve=(1+p).cumprod(); years=max((curve.index.max()-curve.index.min()).days/365.25,1/TRADING_DAYS)
    total=curve.iloc[-1]-1; annual=(1+total)**(1/years)-1; vol=p.std()*np.sqrt(TRADING_DAYS); sharpe=(p.mean()-risk_free_rate/TRADING_DAYS)/p.std()*np.sqrt(TRADING_DAYS); dd=curve/curve.cummax()-1
    series=pd.DataFrame({"daily_return":p,"portfolio_value":curve,"drawdown":dd})
    metrics={"portfolio_total_return_pct":round(float(total*100),2),"portfolio_annualized_return_pct":round(float(annual*100),2),"portfolio_annualized_volatility_pct":round(float(vol*100),2),"portfolio_sharpe_ratio":round(float(sharpe),3),"portfolio_max_drawdown_pct":round(float(dd.min()*100),2)}
    return series,metrics


def calculate_finance_kpis(df:pd.DataFrame)->dict:
    assets=asset_metrics(df); _,portfolio=equal_weight_portfolio(df); best=assets.iloc[0]; risk=assets.sort_values("annualized_volatility_pct").iloc[0]
    return {"observations":int(len(df)),"assets":int(df.ticker.nunique()),"start_date":str(df.date.min().date()),"end_date":str(df.date.max().date()),
      "best_asset":str(best.ticker),"best_asset_annualized_return_pct":round(float(best.annualized_return_pct),2),"lowest_volatility_asset":str(risk.ticker),"lowest_volatility_pct":round(float(risk.annualized_volatility_pct),2),**portfolio}


def save_json(data:dict,path:str|Path): Path(path).parent.mkdir(parents=True,exist_ok=True); Path(path).write_text(json.dumps(data,indent=2),encoding="utf-8")
