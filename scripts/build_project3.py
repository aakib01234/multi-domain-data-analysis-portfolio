"""Build Project 3 weather data, charts, notebook, validation, and PDF report."""
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
from src.weather_analysis import validate_weather_data,clean_weather_data,calculate_weather_kpis,save_json

DATA_DIR=ROOT/"data"/"project3_weather"; VIZ_DIR=ROOT/"visualizations"/"project3_weather"; REPORT_DIR=ROOT/"reports"; NB_DIR=ROOT/"notebooks"
for d in [DATA_DIR,VIZ_DIR,REPORT_DIR,NB_DIR]: d.mkdir(parents=True,exist_ok=True)


def generate_data(seed=126):
    rng=np.random.default_rng(seed); dates=pd.date_range("2022-01-01","2024-12-31",freq="D")
    profiles={"Delhi":("North",25,12,650,7),"Mumbai":("West",27,3.5,2200,7),"Bengaluru":("South",23,3,970,5),"Kolkata":("East",26,6,1750,7),"Chennai":("South",28,4,1400,10),"Jaipur":("Northwest",26,11,560,7)}
    rows=[]
    for city,(region,base,amp,annual_rain,monsoon_start) in profiles.items():
      for date in dates:
        doy=date.dayofyear; seasonal=np.sin(2*np.pi*(doy-105)/365.25)
        mean=base+amp*seasonal+rng.normal(0,1.8); spread=max(5,rng.normal(11 if city in ["Delhi","Jaipur"] else 7,1.3))
        month=date.month
        if city=="Chennai": rain_weight=4.0 if month in [10,11,12] else 1.2 if month in [6,7,8,9] else .25
        else: rain_weight=4.2 if month in [monsoon_start,monsoon_start+1,monsoon_start+2] else 1.1 if month in [6,9,10] else .2
        rainy=rng.random()<min(.72,(annual_rain/365/10)*rain_weight)
        rain=float(rng.gamma(1.6,11*rain_weight)) if rainy else 0.0
        humidity=np.clip(48+rain_weight*6+(8 if rainy else 0)-.35*(mean-25)+rng.normal(0,8),20,100)
        wind=np.clip(rng.gamma(2.5,4)+(5 if rainy else 0),0,65)
        if rain>=64.5: condition="Heavy Rain"
        elif rain>10: condition="Rain"
        elif rain>.1: condition="Light Rain"
        elif humidity>82: condition="Cloudy"
        else: condition="Clear"
        rows.append({"date":date.date().isoformat(),"city":city,"region":region,"temperature_max_c":round(mean+spread/2,1),"temperature_min_c":round(mean-spread/2,1),"rainfall_mm":round(rain,1),"humidity_pct":round(humidity,1),"wind_speed_kmh":round(wind,1),"weather_condition":condition})
    df=pd.DataFrame(rows)
    for row,col in [(125,"rainfall_mm"),(1777,"humidity_pct"),(3999,"wind_speed_kmh")]: df.loc[row,col]=np.nan
    return pd.concat([df,df.iloc[[321,4700]]],ignore_index=True)


def make_charts(df):
    sns.set_theme(style="whitegrid"); plt.rcParams.update({"figure.dpi":140,"axes.titleweight":"bold","axes.titlesize":14}); paths=[]
    def save(name): p=VIZ_DIR/name; plt.tight_layout(); plt.savefig(p,bbox_inches="tight",facecolor="white"); plt.close(); paths.append(p)
    monthly=df.groupby(["month_num","city"],as_index=False).temperature_mean_c.mean()
    plt.figure(figsize=(11,6)); sns.lineplot(data=monthly,x="month_num",y="temperature_mean_c",hue="city",marker="o"); plt.xticks(range(1,13)); plt.xlabel("Month"); plt.ylabel("Mean temperature (C)"); plt.title("Monthly Temperature Patterns by City"); save("01_monthly_temperature.png")
    rain=df.groupby("month_num",as_index=False).rainfall_mm.sum()
    plt.figure(figsize=(10,5)); ax=sns.barplot(data=rain,x="month_num",y="rainfall_mm",hue="month_num",palette="Blues",legend=False); plt.xlabel("Month"); plt.ylabel("Total rainfall (mm)"); plt.title("Rainfall Distribution by Month"); save("02_monthly_rainfall.png")
    season=df.pivot_table(index="city",columns="season",values="temperature_mean_c",aggfunc="mean").reindex(columns=["Winter","Summer","Monsoon","Post-Monsoon"])
    plt.figure(figsize=(9,5)); sns.heatmap(season,annot=True,fmt=".1f",cmap="YlOrRd",cbar_kws={"label":"Mean temperature (C)"}); plt.title("City and Seasonal Temperature Heatmap"); save("03_seasonal_heatmap.png")
    events=df.groupby("city")[["heatwave_day","heavy_rain_day","cold_day","high_wind_day"]].sum().rename(columns=lambda x:x.replace('_day','').replace('_',' ').title()).reset_index().melt("city",var_name="Event",value_name="Days")
    plt.figure(figsize=(11,6)); sns.barplot(data=events,x="city",y="Days",hue="Event"); plt.title("Extreme Weather Indicators by City"); plt.xlabel(""); plt.ylabel("Observation-days"); plt.xticks(rotation=15); save("04_extreme_events.png")
    sample=df.sample(min(1800,len(df)),random_state=3)
    plt.figure(figsize=(9,6)); sns.scatterplot(data=sample,x="humidity_pct",y="rainfall_mm",hue="season",alpha=.5,s=25); plt.yscale("symlog",linthresh=1); plt.xlabel("Humidity (%)"); plt.ylabel("Rainfall (mm, symlog scale)"); plt.title("Humidity and Rainfall Relationship"); save("05_humidity_rainfall.png")
    return paths


def notebook():
    def md(s): return {"cell_type":"markdown","metadata":{},"source":s.splitlines(True)}
    def code(s): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":s.splitlines(True)}
    cells=[md("# Project 3 - Weather Data Analysis\n\n**Domain:** Weather  \n**Period:** 2022-2024  \n**Scope:** Six Indian cities; simulated daily data."),md("## 1. Setup and loading"),code("from pathlib import Path\nimport sys,pandas as pd,numpy as np\nROOT=Path.cwd() if (Path.cwd()/'src').exists() else Path.cwd().parent\nsys.path.insert(0,str(ROOT))\nfrom src.weather_analysis import validate_weather_data,clean_weather_data,calculate_weather_kpis\nraw=pd.read_csv(ROOT/'data/project3_weather/weather_daily_raw.csv')\nraw.head()"),md("## 2. Data quality"),code("raw_validation=validate_weather_data(raw)\npd.Series(raw_validation)"),code("weather=clean_weather_data(raw)\nprint(f'{len(raw):,} raw rows -> {len(weather):,} clean observations')\nvalidate_weather_data(weather)"),md("## 3. Descriptive statistics and KPIs"),code("kpis=calculate_weather_kpis(weather)\npd.Series(kpis).to_frame('Value')"),code("weather[['temperature_max_c','temperature_min_c','temperature_mean_c','rainfall_mm','humidity_pct','wind_speed_kmh']].describe().round(2)"),md("## 4. Temperature and seasonal analysis"),code("weather.groupby(['city','season']).temperature_mean_c.agg(['mean','median','min','max']).round(2)"),code("weather.groupby(['year','city']).temperature_mean_c.mean().unstack().round(2)"),md("## 5. Rainfall distribution"),code("weather.groupby(['city','season']).rainfall_mm.agg(['sum','mean','median','max']).round(2)"),md("## 6. Extreme events"),code("weather.groupby('city')[['heatwave_day','heavy_rain_day','cold_day','high_wind_day','extreme_event']].sum().astype(int)"),md("## 7. Correlation"),code("weather[['temperature_mean_c','temperature_range_c','rainfall_mm','humidity_pct','wind_speed_kmh']].corr().round(3)"),md("## 8. Visualizations"),code("from IPython.display import display,Image\nfor chart in sorted((ROOT/'visualizations/project3_weather').glob('*.png')): display(Image(filename=str(chart),width=850))"),md("## 9. Recommendations\n1. Prepare city-specific heat and rainfall response calendars.\n2. Inspect drainage before peak rainfall months.\n3. Trigger heat readiness as temperatures approach 40 C.\n4. Use local, not portfolio-wide, thresholds.\n5. Replace simulated data with verified official observations for operational use."),md("## 10. Limitations\nThe data is simulated and thresholds are analytical portfolio rules. Correlation is descriptive and does not establish causality.")]
    nb={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3"}},"nbformat":4,"nbformat_minor":5}; p=NB_DIR/"03_weather_data_analysis.ipynb"; p.write_text(json.dumps(nb,indent=1),encoding="utf-8"); return p


def make_pdf(df,k,imgs):
    p=REPORT_DIR/"03_weather_analysis_report.pdf"; navy=colors.HexColor('#0F172A'); blue=colors.HexColor('#0284C7'); pale=colors.HexColor('#F0F9FF'); styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='T',parent=styles['Title'],fontSize=24,leading=30,alignment=TA_CENTER,textColor=navy)); styles.add(ParagraphStyle(name='H',parent=styles['Heading2'],fontSize=15,leading=19,textColor=blue,spaceBefore=8,spaceAfter=7)); styles.add(ParagraphStyle(name='B',parent=styles['BodyText'],fontSize=9.5,leading=14,textColor=navy,spaceAfter=6))
    doc=SimpleDocTemplate(str(p),pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,topMargin=17*mm,bottomMargin=16*mm)
    story=[Spacer(1,18*mm),Paragraph("WEATHER DATA ANALYSIS",styles['T']),Paragraph("Executive Report | 2022-2024",ParagraphStyle(name='S',parent=styles['Heading2'],alignment=TA_CENTER,textColor=blue)),Spacer(1,12*mm)]
    table=[["OBSERVATIONS",f"{k['observations']:,}"],["CITIES",str(k['cities'])],["MEAN TEMPERATURE",f"{k['mean_temperature_c']:.1f} C"],["EXTREME INDICATORS",f"{k['extreme_event_days']:,}"]]
    story += [Table(table,colWidths=[60*mm,68*mm],style=[('BACKGROUND',(0,0),(-1,-1),pale),('TEXTCOLOR',(0,0),(0,-1),blue),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#BAE6FD')),('PADDING',(0,0),(-1,-1),9)]),Spacer(1,13*mm),Paragraph("Executive Summary",styles['H']),Paragraph(f"This report analyses {k['observations']:,} daily city observations across {k['cities']} Indian cities from {k['start_date']} to {k['end_date']}. {k['warmest_city']} has the highest mean temperature ({k['warmest_city_mean_c']:.1f} C), while {k['wettest_city']} records the greatest accumulated rainfall.",styles['B']),Paragraph(f"The dataset contains {k['heatwave_days']:,} heatwave indicators, {k['heavy_rain_days']:,} heavy-rain indicators, and {k['cold_days']:,} cold-day indicators. These are portfolio thresholds rather than official city warnings.",styles['B']),PageBreak(),Paragraph("1. Methodology",styles['H']),Paragraph("The pipeline validates schema, duplicates, dates, measurement ranges, and minimum/maximum temperature ordering. Missing rainfall, humidity, and wind observations are imputed with city-month medians. Calendar, season, temperature range, and four extreme-event flags are engineered.",styles['B']),Paragraph("Statistical Summary",styles['H'])]
    stat=[["Metric","Value"],["Median temperature",f"{k['median_temperature_c']:.2f} C"],["Rainy observations",f"{k['rainy_days']:,}"],["Maximum daily rainfall",f"{k['max_daily_rainfall_mm']:.1f} mm"],["Rainfall-humidity correlation",f"{k['rainfall_humidity_correlation']:.3f}"],["Temperature-humidity correlation",f"{k['temperature_humidity_correlation']:.3f}"]]
    story += [Table(stat,colWidths=[92*mm,55*mm],style=[('BACKGROUND',(0,0),(-1,0),navy),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#CBD5E1')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,pale]),('PADDING',(0,0),(-1,-1),7)]),PageBreak()]
    titles=["2. Temperature Trends","3. Rainfall Distribution","4. Seasonal Patterns","5. Extreme Weather Indicators","6. Humidity and Rainfall"]
    notes=["City lines show distinct annual cycles and why local seasonal baselines are more useful than a single portfolio average.","Rainfall is concentrated in a limited set of months, supporting seasonal drainage, supply, and staffing preparation.","The heatmap makes city-season differences explicit and highlights locations with relatively stable or volatile temperatures.","Counts compare analytical heat, heavy-rain, cold, and high-wind indicators. They measure exposure in this simulated dataset, not official disaster declarations.","The scatter plot shows how humidity and rainfall coexist across seasons; the nonlinear distribution and many dry days limit simple interpretation."]
    for title,img,note in zip(titles,imgs,notes): story += [Paragraph(title,styles['H']),Image(str(img),width=172*mm,height=94*mm),Paragraph(note,styles['B']),PageBreak()]
    story += [Paragraph("7. Recommendations and Limitations",styles['H'])]
    for h,b in [("Seasonal readiness","Build separate city calendars for heat, rainfall, and maintenance preparations."),("Drainage planning","Inspect drainage and emergency supplies before the highest-rainfall months."),("Heat preparedness","Trigger communication and staffing reviews as forecasts approach 40 C."),("Local thresholds","Avoid applying one threshold or portfolio average to every city."),("Operational validation","Replace simulated observations with verified meteorological data and official local definitions before real decisions.")]: story += [Paragraph(f"<b>{h}:</b> {b}",styles['B']),Spacer(1,2*mm)]
    story += [Paragraph("Limitations",styles['H']),Paragraph("This dataset is simulated for portfolio practice and is not an official weather record. The extreme-event thresholds are simplified analytical rules. Correlations are descriptive, and three years is too short for climate-change attribution.",styles['B'])]
    def footer(canvas,doc): canvas.saveState(); canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor('#64748B')); canvas.drawString(16*mm,9*mm,'Multi-Domain Data Analysis Portfolio'); canvas.drawRightString(194*mm,9*mm,f'Page {doc.page}'); canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer); return p


def main():
    raw=generate_data(); raw.to_csv(DATA_DIR/"weather_daily_raw.csv",index=False); clean=clean_weather_data(raw); clean.to_csv(DATA_DIR/"weather_daily_cleaned.csv",index=False)
    save_json(validate_weather_data(raw),DATA_DIR/"raw_validation_report.json"); save_json(validate_weather_data(clean),DATA_DIR/"clean_validation_report.json"); k=calculate_weather_kpis(clean); save_json(k,DATA_DIR/"analysis_metrics.json")
    imgs=make_charts(clean); nb=notebook(); report=make_pdf(clean,k,imgs); print(f"Created {len(clean):,} cleaned observations, {len(imgs)} charts, notebook={nb.name}, report={report.name}")


if __name__=='__main__': main()
