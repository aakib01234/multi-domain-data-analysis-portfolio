import pandas as pd
from src.finance_analysis import validate_market_data,clean_market_data,asset_metrics,equal_weight_portfolio


def sample_market():
    rows=[]
    for ticker,prices in {"AAA":[100,110,121],"BBB":[200,200,220]}.items():
      for date,price in zip(pd.date_range("2024-01-01",periods=3,freq="B"),prices): rows.append({"date":date.date().isoformat(),"ticker":ticker,"sector":"Test","close":price,"volume":1000})
    return pd.DataFrame(rows+[rows[0]])


def test_market_validation_duplicate(): assert validate_market_data(sample_market())["duplicate_ticker_dates"]==1


def test_cleaning_returns_and_drawdown():
    clean=clean_market_data(sample_market()); assert len(clean)==6
    aaa=clean[clean.ticker=="AAA"]; assert round(aaa.daily_return.iloc[-1],2)==.10 and aaa.drawdown.min()==0


def test_asset_and_portfolio_metrics():
    clean=clean_market_data(sample_market()); m=asset_metrics(clean,risk_free_rate=0); _,p=equal_weight_portfolio(clean,risk_free_rate=0)
    assert round(m.loc[m.ticker=="AAA","total_return_pct"].iloc[0],6)==21
    assert p["portfolio_total_return_pct"]>15
