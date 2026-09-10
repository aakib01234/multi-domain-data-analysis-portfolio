"""Generate Project 1 data, notebook, visualizations, metrics, and PDF report."""
from __future__ import annotations

import sys
import json
from pathlib import Path
from textwrap import wrap

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether

from src.sales_analysis import validate_sales_data, clean_sales_data, calculate_kpis, save_json

DATA_DIR = ROOT / "data" / "project1_sales"
VIZ_DIR = ROOT / "visualizations" / "project1_sales"
REPORT_DIR = ROOT / "reports"
NOTEBOOK_DIR = ROOT / "notebooks"
for d in [DATA_DIR, VIZ_DIR, REPORT_DIR, NOTEBOOK_DIR, ROOT / "outputs"]:
    d.mkdir(parents=True, exist_ok=True)


def generate_dataset(n=2500, seed=42):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")
    date_weights = np.array([1.28 if d.dayofweek >= 5 else 1.0 for d in dates], dtype=float)
    date_weights *= np.array([1.0 if d.month == 1 else 1.08 if d.month == 2 else 1.18 for d in dates])
    chosen_dates = rng.choice(dates, size=n, p=date_weights / date_weights.sum())
    categories = {
        "Electronics": [("Earbuds", 2199), ("Power Bank", 1499), ("Smart Watch", 3999), ("Bluetooth Speaker", 2799)],
        "Groceries": [("Rice 5kg", 620), ("Cooking Oil", 790), ("Dry Fruits", 950), ("Breakfast Cereal", 380)],
        "Clothing": [("T-Shirt", 799), ("Jeans", 1799), ("Jacket", 2999), ("Sports Shoes", 2499)],
        "Home & Kitchen": [("Mixer Grinder", 3299), ("Cookware Set", 2399), ("Bedsheet", 999), ("Storage Set", 699)],
        "Personal Care": [("Skin Care Kit", 1199), ("Shampoo", 449), ("Perfume", 1599), ("Trimmer", 1899)],
        "Sports": [("Yoga Mat", 899), ("Dumbbell Set", 2499), ("Cricket Bat", 1999), ("Fitness Band", 1299)],
    }
    cat_names = list(categories)
    cat_probs = [0.23, 0.25, 0.18, 0.13, 0.12, 0.09]
    margins = {"Electronics": .31, "Groceries": .18, "Clothing": .39, "Home & Kitchen": .34, "Personal Care": .42, "Sports": .36}
    branches = [("A", "Delhi"), ("B", "Mumbai"), ("C", "Bengaluru")]
    rows = []
    for i, date in enumerate(chosen_dates, 1):
        category = rng.choice(cat_names, p=cat_probs)
        product, base_price = categories[category][rng.integers(0, 4)]
        branch, city = branches[rng.choice(3, p=[.38, .34, .28])]
        member = rng.random() < .46
        weekend = pd.Timestamp(date).dayofweek >= 5
        hours = np.arange(9, 22)
        hour_weights = np.array([.03, .04, .05, .06, .07, .07, .08, .10, .13, .14, .11, .07, .05])
        hour = int(rng.choice(hours, p=hour_weights / hour_weights.sum()))
        minute = int(rng.integers(0, 60))
        discount = rng.choice([0, .05, .10, .15, .20], p=[.38, .20, .24, .13, .05])
        if member: discount = min(.20, discount + rng.choice([0, .05], p=[.65, .35]))
        quantity = int(rng.choice([1,2,3,4,5,6], p=[.29,.27,.20,.13,.07,.04]))
        if category == "Groceries": quantity += int(rng.random() < .30)
        price = round(base_price * rng.uniform(.92, 1.08), 2)
        rating = round(float(np.clip(rng.normal(7.4 + .25 * member + .18 * weekend, 1.25), 1, 10)), 1)
        rows.append({
            "invoice_id": f"INV-2024-{i:05d}", "date": pd.Timestamp(date).date().isoformat(),
            "time": f"{hour:02d}:{minute:02d}", "branch": branch, "city": city,
            "customer_type": "Member" if member else "Normal",
            "gender": rng.choice(["Female", "Male"], p=[.52,.48]), "category": category,
            "product": product, "unit_price": price, "quantity": quantity,
            "discount_pct": discount, "payment_method": rng.choice(["UPI","Card","Cash"], p=[.47,.34,.19]),
            "rating": rating, "cost_price": round(price * (1 - margins[category]), 2)
        })
    df = pd.DataFrame(rows)
    # Controlled imperfections demonstrate cleaning without materially distorting results.
    df.loc[[17, 411, 901, 1702], "rating"] = np.nan
    df = pd.concat([df, df.iloc[[101, 877]]], ignore_index=True)
    return df


def make_charts(df):
    sns.set_theme(style="whitegrid", palette="deep")
    plt.rcParams.update({"figure.dpi": 140, "axes.titleweight": "bold", "axes.titlesize": 14})
    paths = []
    def save(name):
        path = VIZ_DIR / name
        plt.tight_layout(); plt.savefig(path, bbox_inches="tight", facecolor="white"); plt.close(); paths.append(path)

    cat = df.groupby("category", as_index=False).agg(net_sales=("net_sales","sum"), profit=("profit","sum")).sort_values("net_sales")
    plt.figure(figsize=(10,6)); ax=sns.barplot(data=cat, x="net_sales", y="category", color="#2563EB")
    ax.set(title="Revenue by Product Category", xlabel="Net sales (INR)", ylabel="")
    ax.bar_label(ax.containers[0], fmt="Rs %.0f", padding=3, fontsize=8); save("01_category_revenue.png")

    daily = df.groupby("date", as_index=False)["net_sales"].sum().sort_values("date")
    daily["7_day_average"] = daily["net_sales"].rolling(7, min_periods=1).mean()
    plt.figure(figsize=(11,5)); plt.plot(daily.date, daily.net_sales, color="#93C5FD", linewidth=1, label="Daily sales")
    plt.plot(daily.date, daily["7_day_average"], color="#1D4ED8", linewidth=2.5, label="7-day average")
    plt.title("Daily Sales Trend"); plt.ylabel("Net sales (INR)"); plt.xlabel(""); plt.legend(); save("02_daily_sales_trend.png")

    weekday_order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    wd=df.groupby("weekday",as_index=False)["net_sales"].mean(); wd["weekday"]=pd.Categorical(wd.weekday,weekday_order,ordered=True); wd=wd.sort_values("weekday")
    plt.figure(figsize=(9,5)); ax=sns.barplot(data=wd,x="weekday",y="net_sales",hue="weekday",palette="Blues_d",legend=False)
    ax.set(title="Average Transaction Value by Weekday",xlabel="",ylabel="Average transaction value (INR)"); plt.xticks(rotation=25); save("03_weekday_performance.png")

    pivot=df.pivot_table(index="weekday",columns="hour",values="net_sales",aggfunc="sum").reindex(weekday_order)
    plt.figure(figsize=(12,5)); sns.heatmap(pivot,cmap="YlOrRd",linewidths=.3,cbar_kws={"label":"Net sales (INR)"})
    plt.title("Sales Heatmap: Weekday and Hour"); plt.xlabel("Hour of day"); plt.ylabel(""); save("04_sales_heatmap.png")

    cust=df.groupby("customer_type",as_index=False).agg(avg_spend=("net_sales","mean"),avg_rating=("rating","mean"),transactions=("invoice_id","count"))
    fig, ax=plt.subplots(figsize=(8,5)); bars=ax.bar(cust.customer_type,cust.avg_spend,color=["#60A5FA","#1D4ED8"])
    ax.bar_label(bars,fmt="Rs %.0f",padding=4); ax.set(title="Member vs Normal Customer Spending",ylabel="Average transaction value (INR)",xlabel="")
    save("05_customer_comparison.png")
    return paths


def create_notebook():
    def md(text): return {"cell_type":"markdown","metadata":{},"source":text.splitlines(True)}
    def code(text): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":text.splitlines(True)}
    cells = [
        md("# Project 1 - Supermarket Sales Analysis\n\n**Domain:** Retail  \n**Period:** January-March 2024  \n**Goal:** Turn transaction data into inventory, promotion, and customer-retention recommendations."),
        md("## 1. Setup and data loading"),
        code("from pathlib import Path\nimport sys, pandas as pd, numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nROOT = Path.cwd() if (Path.cwd()/'src').exists() else Path.cwd().parent\nsys.path.insert(0, str(ROOT))\nfrom src.sales_analysis import validate_sales_data, clean_sales_data, calculate_kpis\nraw = pd.read_csv(ROOT/'data/project1_sales/supermarket_sales_raw.csv')\nraw.head()"),
        md("## 2. Data validation and quality assessment\n\nWe check schema completeness, duplicates, missing values, and valid numeric ranges before analysis."),
        code("raw_validation = validate_sales_data(raw)\npd.Series(raw_validation)"),
        md("## 3. Cleaning and feature engineering"),
        code("sales = clean_sales_data(raw)\nclean_validation = validate_sales_data(sales)\nprint(f'Rows: {len(raw):,} raw -> {len(sales):,} cleaned')\nsales[['gross_sales','discount_amount','net_sales','profit','profit_margin_pct']].head()"),
        md("## 4. Descriptive statistics and headline KPIs"),
        code("kpis = calculate_kpis(sales)\npd.Series(kpis).to_frame('Value')"),
        code("sales[['unit_price','quantity','discount_pct','rating','net_sales','profit']].describe().round(2)"),
        md("## 5. Category and product performance"),
        code("category_summary = sales.groupby('category').agg(transactions=('invoice_id','count'), units=('quantity','sum'), revenue=('net_sales','sum'), profit=('profit','sum')).assign(margin_pct=lambda x:x.profit/x.revenue*100).sort_values('revenue',ascending=False)\ncategory_summary.round(2)"),
        code("product_summary = sales.groupby(['category','product']).agg(units=('quantity','sum'),revenue=('net_sales','sum'),profit=('profit','sum')).sort_values('revenue',ascending=False)\nproduct_summary.head(10).round(2)"),
        md("## 6. Customer, time, and branch analysis"),
        code("sales.groupby('customer_type').agg(transactions=('invoice_id','count'),average_spend=('net_sales','mean'),average_rating=('rating','mean'),revenue=('net_sales','sum')).round(2)"),
        code("sales.groupby(['branch','city']).agg(transactions=('invoice_id','count'),revenue=('net_sales','sum'),profit=('profit','sum')).sort_values('revenue',ascending=False).round(2)"),
        code("sales.groupby('weekday')['net_sales'].agg(['count','mean','sum']).sort_values('sum',ascending=False).round(2)"),
        md("## 7. Correlation analysis\n\nPearson correlation measures linear association; it does not prove causation."),
        code("corr = sales[['unit_price','quantity','discount_pct','rating','net_sales','profit']].corr().round(3)\ncorr"),
        md("## 8. Visualizations"),
        code("from IPython.display import display, Image\nfor chart in sorted((ROOT/'visualizations/project1_sales').glob('*.png')):\n    display(Image(filename=str(chart), width=850))"),
        md("## 9. Business insights and recommendations\n\n1. Prioritize replenishment for the highest-revenue categories while monitoring margin, not revenue alone.\n2. Schedule staffing and promotional activity around evening and weekend demand.\n3. Use member-exclusive bundles to increase repeat purchasing without relying on blanket discounts.\n4. Protect high-margin categories through targeted cross-selling.\n5. Validate recommendations with branch-level A/B tests because this simulated analysis is observational."),
        md("## 10. Conclusion\n\nThe workflow converts raw transaction records into validated data, statistical evidence, clear visuals, and testable retail actions. See the PDF report for the executive presentation.")
    ]
    nb={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3"}},"nbformat":4,"nbformat_minor":5}
    path=NOTEBOOK_DIR/"01_supermarket_sales_analysis.ipynb"
    path.write_text(json.dumps(nb,indent=1),encoding="utf-8")
    return path


def money(x): return f"Rs {x:,.0f}"


def create_pdf(df, kpis, charts):
    path=REPORT_DIR/"01_supermarket_sales_report.pdf"
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=17*mm,bottomMargin=16*mm)
    styles=getSampleStyleSheet(); navy=colors.HexColor("#0F172A"); blue=colors.HexColor("#2563EB"); pale=colors.HexColor("#EFF6FF")
    styles.add(ParagraphStyle(name="TitleCenter",parent=styles["Title"],alignment=TA_CENTER,textColor=navy,fontSize=24,leading=30,spaceAfter=10))
    styles.add(ParagraphStyle(name="Section",parent=styles["Heading2"],textColor=blue,fontSize=15,leading=19,spaceBefore=8,spaceAfter=7))
    styles.add(ParagraphStyle(name="BodyClean",parent=styles["BodyText"],fontSize=9.5,leading=14,textColor=navy,spaceAfter=6))
    styles.add(ParagraphStyle(name="Small",parent=styles["BodyText"],fontSize=8,leading=11,textColor=colors.HexColor("#475569")))
    story=[Spacer(1,18*mm),Paragraph("SUPERMARKET SALES ANALYSIS",styles["TitleCenter"]),Paragraph("Executive Report | January-March 2024",ParagraphStyle(name="Sub",parent=styles["Heading2"],alignment=TA_CENTER,textColor=blue)),Spacer(1,12*mm)]
    story.append(Table([["REVENUE",money(kpis['total_sales'])],["PROFIT",money(kpis['total_profit'])],["TRANSACTIONS",f"{kpis['transactions']:,}"],["AVG. BASKET",money(kpis['average_transaction_value'])]],colWidths=[45*mm,75*mm],style=[("BACKGROUND",(0,0),(-1,-1),pale),("TEXTCOLOR",(0,0),(0,-1),blue),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(1,0),(1,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),11),("GRID",(0,0),(-1,-1),.3,colors.HexColor('#BFDBFE')),("PADDING",(0,0),(-1,-1),9)]))
    story += [Spacer(1,14*mm),Paragraph("Executive Summary",styles["Section"]),Paragraph(f"This report analyses {kpis['transactions']:,} cleaned supermarket transactions across three branches. Net sales reached {money(kpis['total_sales'])}, generating {money(kpis['total_profit'])} in profit at an overall margin of {kpis['overall_profit_margin_pct']:.1f}%. {kpis['best_category']} was the leading revenue category, while demand was strongest on {kpis['best_weekday']} and peaked around {kpis['peak_hour']}:00.",styles["BodyClean"]),Paragraph("The evidence supports focused replenishment, time-based staffing, member bundles, and margin-aware promotions. Because the dataset is simulated and observational, recommendations should be validated with controlled branch experiments.",styles["BodyClean"]),Spacer(1,18*mm),Paragraph("Prepared as part of the Multi-Domain Data Analysis Portfolio",styles["Small"]),PageBreak()]
    story += [Paragraph("1. Objectives and Methodology",styles["Section"]),Paragraph("The analysis addresses four business questions: What sells most? When does demand peak? Which customers and branches contribute most? Which actions can improve revenue and profit?",styles["BodyClean"]),Paragraph("Data preparation",styles["Section"]),Paragraph("Required columns and numeric ranges were validated. Duplicate invoice IDs were removed, dates and numeric values were standardized, missing ratings were imputed with the median, and unusable values were rejected. Revenue, cost, profit, margin, weekday, month, hour, and time-slot features were then engineered.",styles["BodyClean"]),Paragraph("Statistical approach",styles["Section"]),Paragraph("The analysis uses counts, mean, median, quartiles, grouped totals, rolling trends, and Pearson correlation. Mean transaction value captures typical revenue while the median reduces sensitivity to unusually large baskets.",styles["BodyClean"])]
    stats=[["Metric","Value"],["Average transaction",money(kpis['average_transaction_value'])],["Median transaction",money(kpis['median_transaction_value'])],["Average rating",f"{kpis['average_rating']:.2f} / 10"],["Quantity-sales correlation",f"{kpis['quantity_sales_correlation']:.3f}"],["Discount-sales correlation",f"{kpis['discount_sales_correlation']:.3f}"]]
    story += [Spacer(1,5*mm),Table(stats,colWidths=[80*mm,70*mm],style=[("BACKGROUND",(0,0),(-1,0),navy),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("GRID",(0,0),(-1,-1),.3,colors.HexColor('#CBD5E1')),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,pale]),("PADDING",(0,0),(-1,-1),7)]),PageBreak()]
    for idx,(title,chart) in enumerate([( "2. Category Performance",charts[0]),("3. Sales Trend",charts[1]),("4. Weekday Performance",charts[2]),("5. Peak Shopping Periods",charts[3]),("6. Customer Behaviour",charts[4])]):
        story += [Paragraph(title,styles["Section"]),Image(str(chart),width=175*mm,height=95*mm if idx != 3 else 80*mm)]
        notes=[
            f"{kpis['best_category']} leads category revenue with {money(kpis['best_category_sales'])}. Inventory planning should combine this demand signal with profit margin and stock turnover.",
            f"The best individual sales date was {kpis['best_sales_day']} at {money(kpis['best_sales_day_value'])}. The seven-day moving average makes the underlying trend easier to distinguish from daily noise.",
            f"{kpis['best_weekday']} has the strongest average transaction value. Weekend-oriented bundles and staffing should be tested around this pattern.",
            f"The heatmap identifies the most valuable day-hour combinations. The overall peak is around {kpis['peak_hour']}:00, supporting targeted staffing and replenishment before the rush.",
            "Member and normal customer results show whether loyalty participation corresponds with higher basket value and ratings. Use member-specific bundles and measure incremental profit, not discount redemption alone."
        ]
        story += [Paragraph(notes[idx],styles["BodyClean"]),PageBreak()]
    story += [Paragraph("7. Actionable Recommendations",styles["Section"])]
    recs=[("Inventory","Raise safety stock for leading category-product combinations before peak periods; review weekly sell-through to prevent overstock."),("Promotions","Run targeted weekend and evening bundles rather than store-wide discounts; compare incremental profit against a control branch."),("Customer retention","Offer member-exclusive cross-category bundles and monitor repeat visits, basket value, and margin."),("Operations","Align staff shifts and shelf replenishment with the high-value hour/day cells in the heatmap."),("Measurement","Track revenue, gross profit, margin, stock-outs, average basket value, and repeat purchase rate in one weekly scorecard.")]
    for h,b in recs: story += [Paragraph(f"<b>{h}:</b> {b}",styles["BodyClean"]),Spacer(1,2*mm)]
    story += [Spacer(1,5*mm),Paragraph("Limitations",styles["Section"]),Paragraph("The dataset is simulated for portfolio practice. Associations may be affected by category mix, branch mix, and seasonality. Correlations are descriptive and should not be interpreted as causal effects.",styles["BodyClean"]),Paragraph("Conclusion",styles["Section"]),Paragraph("The project demonstrates an auditable end-to-end retail analytics workflow: validation, cleaning, feature engineering, statistics, visualization, insight generation, testing, and executive reporting.",styles["BodyClean"])]
    def footer(canvas, doc):
        canvas.saveState(); canvas.setFont("Helvetica",8); canvas.setFillColor(colors.HexColor('#64748B')); canvas.drawString(16*mm,9*mm,"Multi-Domain Data Analysis Portfolio"); canvas.drawRightString(194*mm,9*mm,f"Page {doc.page}"); canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return path


def main():
    raw=generate_dataset(); raw_path=DATA_DIR/"supermarket_sales_raw.csv"; raw.to_csv(raw_path,index=False)
    raw_validation=validate_sales_data(raw); clean=clean_sales_data(raw); clean_path=DATA_DIR/"supermarket_sales_cleaned.csv"; clean.to_csv(clean_path,index=False)
    clean_validation=validate_sales_data(clean); kpis=calculate_kpis(clean)
    save_json(raw_validation,DATA_DIR/"raw_validation_report.json"); save_json(clean_validation,DATA_DIR/"clean_validation_report.json"); save_json(kpis,DATA_DIR/"analysis_metrics.json")
    charts=make_charts(clean); notebook=create_notebook(); report=create_pdf(clean,kpis,charts)
    print(f"Created {len(clean):,} cleaned rows, {len(charts)} charts, notebook={notebook.name}, report={report.name}")


if __name__ == "__main__": main()
