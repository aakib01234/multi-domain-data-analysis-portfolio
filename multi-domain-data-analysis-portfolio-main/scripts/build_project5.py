"""Build Project 5 simulated stock-market and portfolio analysis."""
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
from src.finance_analysis import validate_market_data,clean_market_data,asset_metrics,equal_weight_portfolio,calculate_finance_kpis,save_json

DATA_DIR=ROOT/"data"/"project5_finance"; VIZ_DIR=ROOT/"visualizations"/"project5_finance"; REPORT_DIR=ROOT/"reports"; NB_DIR=ROOT/"notebooks"
for d in [DATA_DIR,VIZ_DIR,REPORT_DIR,NB_DIR]: d.mkdir(parents=True,exist_ok=True)


def generate_data(seed=210):
    rng=np.random.default_rng(seed); dates=pd.date_range("2022-01-03","2024-12-31",freq="B"); tickers=["AURORA","NOVA","ORBIT","PRISM","ZENITH"]; sectors=["Consumer","Technology","Financials","Healthcare","Energy"]
    mu=np.array([.09,.16,.11,.12,.08])/252; vol=np.array([.18,.29,.22,.17,.25])/np.sqrt(252); corr=np.array([[1,.35,.28,.24,.30],[.35,1,.42,.30,.25],[.28,.42,1,.38,.32],[.24,.30,.38,1,.22],[.30,.25,.32,.22,1]])
    cov=np.outer(vol,vol)*corr; returns=rng.multivariate_normal(mu,cov,size=len(dates)); start=np.array([180,320,140,250,210],dtype=float); prices=start*np.exp(np.cumsum(returns-.5*vol**2,axis=0))
    frames=[]
    for i,(ticker,sector) in enumerate(zip(tickers,sectors)):
      volume=rng.lognormal(mean=np.log([900000,1400000,1100000,700000,1250000][i]),sigma=.35,size=len(dates)).astype(int)
      frames.append(pd.DataFrame({"date":dates.date.astype(str),"ticker":ticker,"sector":sector,"close":np.round(prices[:,i],2),"volume":volume}))
    df=pd.concat(frames,ignore_index=True).sort_values(["date","ticker"]).reset_index(drop=True); df.loc[[145,1300],"close"]=np.nan; df.loc[2600,"volume"]=np.nan
    return pd.concat([df,df.iloc[[500,3000]]],ignore_index=True)


def charts(df):
    sns.set_theme(style="whitegrid"); plt.rcParams.update({"figure.dpi":140,"axes.titleweight":"bold","axes.titlesize":14}); paths=[]
    def save(name): p=VIZ_DIR/name; plt.tight_layout(); plt.savefig(p,bbox_inches="tight",facecolor="white"); plt.close(); paths.append(p)
    prices=df.pivot(index="date",columns="ticker",values="close"); norm=prices/prices.iloc[0]*100
    plt.figure(figsize=(11,6)); sns.lineplot(data=norm); plt.ylabel("Indexed price (start = 100)"); plt.xlabel(""); plt.title("Normalized Asset Price Performance"); save("01_normalized_prices.png")
    cumulative=(1+df.pivot(index="date",columns="ticker",values="daily_return").fillna(0)).cumprod()-1
    plt.figure(figsize=(11,6)); sns.lineplot(data=cumulative*100); plt.axhline(0,color="#475569",lw=.8); plt.ylabel("Cumulative return (%)"); plt.xlabel(""); plt.title("Cumulative Returns"); save("02_cumulative_returns.png")
    metrics=asset_metrics(df)
    plt.figure(figsize=(9,6)); ax=sns.scatterplot(data=metrics,x="annualized_volatility_pct",y="annualized_return_pct",hue="ticker",s=130); [ax.text(r.annualized_volatility_pct+.2,r.annualized_return_pct+.2,r.ticker,fontsize=8) for _,r in metrics.iterrows()]; plt.xlabel("Annualized volatility (%)"); plt.ylabel("Annualized return (%)"); plt.title("Risk and Return Profile"); save("03_risk_return.png")
    draw=df.pivot(index="date",columns="ticker",values="drawdown")*100
    plt.figure(figsize=(11,6)); sns.lineplot(data=draw); plt.ylabel("Drawdown (%)"); plt.xlabel(""); plt.title("Peak-to-Trough Drawdowns"); save("04_drawdowns.png")
    corr=df.pivot(index="date",columns="ticker",values="daily_return").corr()
    plt.figure(figsize=(8,6)); sns.heatmap(corr,annot=True,fmt=".2f",cmap="RdYlBu_r",vmin=-1,vmax=1,square=True); plt.title("Daily Return Correlation Matrix"); save("05_return_correlations.png")
    return paths


def notebook():
    def md(s): return {"cell_type":"markdown","metadata":{},"source":s.splitlines(True)}
    def code(s): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":s.splitlines(True)}
    cells=[md("# Project 5 - Stock Market and Portfolio Risk Analysis\n\n**Domain:** Finance  \n**Data:** Simulated fictional assets  \n**Purpose:** Educational portfolio analysis; not investment advice."),md("## 1. Setup and loading"),code("from pathlib import Path\nimport sys,pandas as pd,numpy as np\nROOT=Path.cwd() if (Path.cwd()/'src').exists() else Path.cwd().parent\nsys.path.insert(0,str(ROOT))\nfrom src.finance_analysis import validate_market_data,clean_market_data,asset_metrics,equal_weight_portfolio,calculate_finance_kpis\nraw=pd.read_csv(ROOT/'data/project5_finance/market_prices_raw.csv')\nraw.head()"),md("## 2. Data validation and cleaning"),code("raw_validation=validate_market_data(raw)\npd.Series(raw_validation)"),code("market=clean_market_data(raw)\nprint(f'{len(raw):,} raw rows -> {len(market):,} cleaned observations')\nvalidate_market_data(market)"),md("## 3. Descriptive statistics and KPIs"),code("kpis=calculate_finance_kpis(market)\npd.Series(kpis).to_frame('Value')"),code("market.groupby('ticker')[['close','volume','daily_return','rolling_volatility_21d','drawdown']].describe().round(4)"),md("## 4. Asset metrics"),code("metrics=asset_metrics(market,risk_free_rate=.06)\nmetrics.round(3)"),md("## 5. Equal-weight portfolio"),code("portfolio,portfolio_metrics=equal_weight_portfolio(market,risk_free_rate=.06)\npd.Series(portfolio_metrics).to_frame('Value')"),md("## 6. Correlation and diversification"),code("returns=market.pivot(index='date',columns='ticker',values='daily_return')\nreturns.corr().round(3)"),md("## 7. Trend statistics"),code("market.assign(year=market.date.dt.year).groupby(['year','ticker']).daily_return.apply(lambda r:((1+r.dropna()).prod()-1)*100).unstack().round(2)"),md("## 8. Visualizations"),code("from IPython.display import display,Image\nfor chart in sorted((ROOT/'visualizations/project5_finance').glob('*.png')): display(Image(filename=str(chart),width=850))"),md("## 9. Portfolio insights\n1. Evaluate return with volatility and drawdown.\n2. Use correlation for diversification, recognising it is unstable.\n3. Compare all assets over the same period.\n4. Add fees, taxes, dividends, and realistic rebalancing before practical use.\n5. Treat results as educational, not investment advice."),md("## 10. Assumptions and limitations\n252 trading days, 6% annual risk-free rate, equal weights, daily rebalancing, no fees/taxes/slippage/dividends. Simulated past performance does not predict future results.")]
    nb={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3"}},"nbformat":4,"nbformat_minor":5}; p=NB_DIR/"05_stock_market_portfolio_analysis.ipynb"; p.write_text(json.dumps(nb,indent=1),encoding="utf-8"); return p


def pdf(k,imgs,metrics):
    p=REPORT_DIR/"05_stock_market_portfolio_report.pdf"; navy=colors.HexColor('#0F172A'); gold=colors.HexColor('#B45309'); pale=colors.HexColor('#FFFBEB'); styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='T',parent=styles['Title'],fontSize=23,leading=29,alignment=TA_CENTER,textColor=navy)); styles.add(ParagraphStyle(name='H',parent=styles['Heading2'],fontSize=15,leading=19,textColor=gold,spaceBefore=8,spaceAfter=7)); styles.add(ParagraphStyle(name='B',parent=styles['BodyText'],fontSize=9.5,leading=14,textColor=navy,spaceAfter=6))
    doc=SimpleDocTemplate(str(p),pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,topMargin=17*mm,bottomMargin=16*mm)
    story=[Spacer(1,18*mm),Paragraph("STOCK MARKET & PORTFOLIO RISK",styles['T']),Paragraph("Executive Report | Simulated Data | 2022-2024",ParagraphStyle(name='S',parent=styles['Heading2'],alignment=TA_CENTER,textColor=gold)),Spacer(1,12*mm)]
    tab=[["ASSETS",str(k['assets'])],["PORTFOLIO RETURN",f"{k['portfolio_annualized_return_pct']:.1f}% annualised"],["PORTFOLIO VOLATILITY",f"{k['portfolio_annualized_volatility_pct']:.1f}%"],["MAX DRAWDOWN",f"{k['portfolio_max_drawdown_pct']:.1f}%"]]
    story += [Table(tab,colWidths=[68*mm,68*mm],style=[('BACKGROUND',(0,0),(-1,-1),pale),('TEXTCOLOR',(0,0),(0,-1),gold),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#FDE68A')),('PADDING',(0,0),(-1,-1),9)]),Spacer(1,12*mm),Paragraph("Executive Summary",styles['H']),Paragraph(f"The report analyses {k['observations']:,} daily price observations across {k['assets']} fictional assets from {k['start_date']} to {k['end_date']}. The equal-weight portfolio produced a {k['portfolio_annualized_return_pct']:.1f}% annualised return with {k['portfolio_annualized_volatility_pct']:.1f}% annualised volatility and a Sharpe ratio of {k['portfolio_sharpe_ratio']:.2f}.",styles['B']),Paragraph(f"{k['best_asset']} has the highest asset annualised return ({k['best_asset_annualized_return_pct']:.1f}%), while {k['lowest_volatility_asset']} has the lowest measured volatility ({k['lowest_volatility_pct']:.1f}%). These are simulated historical results and not forecasts or recommendations.",styles['B']),PageBreak(),Paragraph("1. Methodology and Assumptions",styles['H']),Paragraph("Daily returns are percentage changes in closing price. Annualised volatility uses 252 trading days. Sharpe ratio uses a 6% annual risk-free assumption. Maximum drawdown measures the largest peak-to-trough decline. The portfolio is equal-weighted and analytically rebalanced daily.",styles['B']),Paragraph("The analysis excludes fees, taxes, bid-ask spreads, slippage, dividends, corporate actions, liquidity constraints, and rebalancing costs. All assets and prices are fictional.",styles['B'])]
    table_data=[["Asset","Ann. Return","Volatility","Sharpe","Max Drawdown"]]+[[r.ticker,f"{r.annualized_return_pct:.1f}%",f"{r.annualized_volatility_pct:.1f}%",f"{r.sharpe_ratio:.2f}",f"{r.max_drawdown_pct:.1f}%"] for _,r in metrics.iterrows()]
    story += [Spacer(1,5*mm),Table(table_data,colWidths=[38*mm,30*mm,30*mm,25*mm,32*mm],style=[('BACKGROUND',(0,0),(-1,0),navy),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('ALIGN',(1,1),(-1,-1),'RIGHT'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#CBD5E1')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,pale]),('PADDING',(0,0),(-1,-1),6)]),PageBreak()]
    titles=["2. Normalized Price Performance","3. Cumulative Returns","4. Risk and Return","5. Drawdown Analysis","6. Asset Correlations"]
    notes=["Indexing every asset to 100 supports like-for-like performance comparison despite different starting prices.","Cumulative returns reveal compounding and periods of divergence among fictional assets.","Return should be evaluated alongside volatility; the upper-left area is preferable in historical risk-return terms.","Drawdown shows loss depth from prior peaks and highlights risk that volatility alone may not communicate.","Lower correlation can improve diversification, but historical relationships may change sharply during market stress."]
    for title,img,note in zip(titles,imgs,notes): story += [Paragraph(title,styles['H']),Image(str(img),width=172*mm,height=94*mm),Paragraph(note,styles['B']),PageBreak()]
    story += [Paragraph("7. Portfolio Insights and Limitations",styles['H'])]
    for h,b in [("Risk-adjusted evaluation","Compare return, volatility, Sharpe ratio, and drawdown rather than return alone."),("Diversification","Use correlations to assess concentration, while stress-testing correlation increases."),("Comparable periods","Use identical dates, pricing frequency, and assumptions for every asset."),("Implementation realism","Add fees, taxes, spreads, dividends, slippage, and realistic rebalancing."),("Decision boundary","Treat this as educational analysis of simulated data, not investment advice.")]: story += [Paragraph(f"<b>{h}:</b> {b}",styles['B']),Spacer(1,2*mm)]
    story += [Paragraph("Limitations",styles['H']),Paragraph("Simulated past performance does not predict future results. Model parameters drive the generated outcomes. Risk-free rates and correlations are not constant in real markets, and the frictionless daily-rebalancing portfolio is not directly investable.",styles['B'])]
    def footer(canvas,doc): canvas.saveState(); canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor('#64748B')); canvas.drawString(16*mm,9*mm,'Multi-Domain Data Analysis Portfolio'); canvas.drawRightString(194*mm,9*mm,f'Page {doc.page}'); canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer); return p


def main():
    raw=generate_data(); raw.to_csv(DATA_DIR/"market_prices_raw.csv",index=False); clean=clean_market_data(raw); clean.to_csv(DATA_DIR/"market_prices_cleaned.csv",index=False)
    save_json(validate_market_data(raw),DATA_DIR/"raw_validation_report.json"); save_json(validate_market_data(clean),DATA_DIR/"clean_validation_report.json"); k=calculate_finance_kpis(clean); save_json(k,DATA_DIR/"analysis_metrics.json")
    metrics=asset_metrics(clean); metrics.to_csv(DATA_DIR/"asset_metrics.csv",index=False); _,portfolio=equal_weight_portfolio(clean); save_json(portfolio,DATA_DIR/"portfolio_metrics.json")
    imgs=charts(clean); nb=notebook(); report=pdf(k,imgs,metrics); print(f"Created {len(clean):,} cleaned observations, {len(imgs)} charts, notebook={nb.name}, report={report.name}")


if __name__=='__main__': main()
