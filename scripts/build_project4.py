"""Build Project 4 healthcare dataset, analysis assets, notebook, and report."""
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
from src.healthcare_analysis import validate_healthcare_data,clean_healthcare_data,calculate_healthcare_kpis,save_json

DATA_DIR=ROOT/"data"/"project4_healthcare"; VIZ_DIR=ROOT/"visualizations"/"project4_healthcare"; REPORT_DIR=ROOT/"reports"; NB_DIR=ROOT/"notebooks"
for d in [DATA_DIR,VIZ_DIR,REPORT_DIR,NB_DIR]: d.mkdir(parents=True,exist_ok=True)


def generate_data(n=1800,seed=168):
    rng=np.random.default_rng(seed); condition=rng.choice(["Diabetes","Hypertension","Respiratory Infection","Cardiac Condition"],n,p=[.29,.27,.25,.19]); severity=rng.choice(["Mild","Moderate","Severe"],n,p=[.36,.45,.19]); treatment=rng.choice(["Standard Care","Medication A","Medication B","Combined Therapy"],n,p=[.29,.24,.22,.25])
    sev_num=pd.Series(severity).map({"Mild":1,"Moderate":2,"Severe":3}).to_numpy(); tx_effect=pd.Series(treatment).map({"Standard Care":10,"Medication A":14,"Medication B":13,"Combined Therapy":18}).to_numpy()
    age=np.clip(rng.normal(54+5*(condition=="Cardiac Condition"),17,n),18,92).round().astype(int); comorb=np.clip(rng.poisson(1.2+0.012*(age-40)),0,6)
    baseline=np.clip(38+13*sev_num+.12*(age-45)+2*comorb+rng.normal(0,8,n),15,98); improvement=np.clip(tx_effect-2.2*(sev_num-1)-.7*comorb+rng.normal(0,7,n),-12,38); follow=np.clip(baseline-improvement,0,100)
    los=np.clip(np.round(1+1.8*sev_num+.035*age+1.1*comorb+rng.normal(0,2,n)),1,30); cost=np.clip(7000+5200*los+pd.Series(treatment).map({"Standard Care":0,"Medication A":9000,"Medication B":12000,"Combined Therapy":22000}).to_numpy()+rng.normal(0,7000,n),5000,None)
    logit=-3.7+.7*sev_num+.025*(age-50)+.35*comorb-.055*improvement; prob=1/(1+np.exp(-logit)); readmit=np.where(rng.random(n)<prob,"Yes","No")
    satisfaction=np.clip(6.2+.09*improvement-.09*los+rng.normal(0,1.2,n),1,10)
    df=pd.DataFrame({"patient_id":[f"PAT-{i:05d}" for i in range(1,n+1)],"admission_date":rng.choice(pd.date_range("2024-01-01","2024-12-31"),n).astype('datetime64[D]').astype(str),"hospital":rng.choice(["Central Hospital","City Medical","Regional Care","Community Hospital"],n),"age":age,"gender":rng.choice(["Female","Male"],n,p=[.51,.49]),"condition":condition,"severity":severity,"treatment":treatment,"baseline_score":np.round(baseline,1),"followup_score":np.round(follow,1),"length_of_stay_days":los.astype(float),"treatment_cost_inr":np.round(cost,0),"readmitted_30d":readmit,"satisfaction_score":np.round(satisfaction,1)})
    for row,col in [(80,"satisfaction_score"),(475,"length_of_stay_days"),(1200,"treatment_cost_inr")]: df.loc[row,col]=np.nan
    return pd.concat([df,df.iloc[[200,1400]]],ignore_index=True)


def charts(df):
    sns.set_theme(style="whitegrid"); plt.rcParams.update({"figure.dpi":140,"axes.titleweight":"bold","axes.titlesize":14}); paths=[]
    def save(name): p=VIZ_DIR/name; plt.tight_layout(); plt.savefig(p,bbox_inches="tight",facecolor="white"); plt.close(); paths.append(p)
    imp=df.groupby(["condition","treatment"],as_index=False).clinical_improvement.mean()
    plt.figure(figsize=(12,6)); sns.barplot(data=imp,x="condition",y="clinical_improvement",hue="treatment"); plt.xticks(rotation=15); plt.ylabel("Mean score improvement"); plt.xlabel(""); plt.title("Clinical Improvement by Condition and Treatment"); save("01_treatment_improvement.png")
    outcome=df.groupby(["severity","treatment"],as_index=False).favourable_outcome.apply(lambda s:(s=="Yes").mean()*100)
    plt.figure(figsize=(10,6)); sns.barplot(data=outcome,x="severity",y="favourable_outcome",hue="treatment",order=["Mild","Moderate","Severe"]); plt.ylabel("Favourable outcome rate (%)"); plt.xlabel(""); plt.title("Favourable Outcomes by Baseline Severity"); save("02_favourable_outcomes.png")
    plt.figure(figsize=(10,6)); sns.boxplot(data=df,x="severity",y="length_of_stay_days",hue="severity",order=["Mild","Moderate","Severe"],palette="Blues",legend=False,showfliers=False); plt.ylabel("Length of stay (days)"); plt.xlabel(""); plt.title("Length of Stay by Severity"); save("03_length_of_stay.png")
    readmit=df.groupby(["treatment","severity"],as_index=False).readmitted_30d.apply(lambda s:(s=="Yes").mean()*100)
    plt.figure(figsize=(11,6)); sns.barplot(data=readmit,x="treatment",y="readmitted_30d",hue="severity"); plt.ylabel("30-day readmission rate (%)"); plt.xlabel(""); plt.xticks(rotation=12); plt.title("Readmission by Treatment and Severity"); save("04_readmission_rates.png")
    sample=df.sample(min(1000,len(df)),random_state=4)
    plt.figure(figsize=(10,6)); sns.scatterplot(data=sample,x="treatment_cost_inr",y="clinical_improvement",hue="severity",alpha=.55,s=28); plt.xlabel("Treatment cost (INR)"); plt.ylabel("Clinical improvement"); plt.title("Cost and Clinical Improvement"); save("05_cost_improvement.png")
    return paths


def notebook():
    def md(s): return {"cell_type":"markdown","metadata":{},"source":s.splitlines(True)}
    def code(s): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":s.splitlines(True)}
    cells=[md("# Project 4 - Healthcare Treatment Effectiveness Analysis\n\n**Domain:** Healthcare  \n**Data:** Simulated and de-identified  \n**Purpose:** Descriptive portfolio analysis, not clinical guidance."),md("## 1. Setup and loading"),code("from pathlib import Path\nimport sys,pandas as pd,numpy as np\nROOT=Path.cwd() if (Path.cwd()/'src').exists() else Path.cwd().parent\nsys.path.insert(0,str(ROOT))\nfrom src.healthcare_analysis import validate_healthcare_data,clean_healthcare_data,calculate_healthcare_kpis\nraw=pd.read_csv(ROOT/'data/project4_healthcare/healthcare_raw.csv')\nraw.head()"),md("## 2. Data quality and cleaning"),code("raw_validation=validate_healthcare_data(raw)\npd.Series(raw_validation)"),code("patients=clean_healthcare_data(raw)\nprint(f'{len(raw):,} raw rows -> {len(patients):,} cleaned encounters')\nvalidate_healthcare_data(patients)"),md("## 3. Descriptive statistics and KPIs"),code("kpis=calculate_healthcare_kpis(patients)\npd.Series(kpis).to_frame('Value')"),code("patients[['age','baseline_score','followup_score','clinical_improvement','length_of_stay_days','treatment_cost_inr','satisfaction_score']].describe().round(2)"),md("## 4. Stratified treatment outcomes"),code("patients.groupby(['condition','severity','treatment']).agg(patients=('patient_id','count'),baseline=('baseline_score','mean'),improvement=('clinical_improvement','mean'),favourable_rate=('favourable_outcome',lambda s:(s=='Yes').mean()*100),readmission_rate=('readmitted_30d',lambda s:(s=='Yes').mean()*100)).round(2)"),md("## 5. Cost, stay, and experience"),code("patients.groupby('treatment').agg(cost_median=('treatment_cost_inr','median'),stay_mean=('length_of_stay_days','mean'),satisfaction_mean=('satisfaction_score','mean')).round(2)"),md("## 6. Correlations"),code("patients[['age','baseline_score','clinical_improvement','length_of_stay_days','treatment_cost_inr','satisfaction_score']].corr().round(3)"),md("## 7. Subgroup checks"),code("patients.groupby(['age_group','gender'],observed=True).agg(patients=('patient_id','count'),improvement=('clinical_improvement','mean'),readmission=('readmitted_30d',lambda s:(s=='Yes').mean()*100)).round(2)"),md("## 8. Visualizations"),code("from IPython.display import display,Image\nfor chart in sorted((ROOT/'visualizations/project4_healthcare').glob('*.png')): display(Image(filename=str(chart),width=850))"),md("## 9. Recommendations\n1. Compare treatments within condition and severity.\n2. Review high-readmission groups clinically.\n3. Balance improvement, safety, stay, cost, and experience.\n4. Audit missingness and subgroup representation.\n5. Require clinician oversight and risk adjustment for real use."),md("## 10. Safety and limitations\nThis simulated observational analysis cannot establish treatment causality and must not guide patient care.")]
    nb={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3"}},"nbformat":4,"nbformat_minor":5}; p=NB_DIR/"04_healthcare_treatment_analysis.ipynb"; p.write_text(json.dumps(nb,indent=1),encoding="utf-8"); return p


def pdf(df,k,imgs):
    p=REPORT_DIR/"04_healthcare_treatment_report.pdf"; navy=colors.HexColor('#0F172A'); teal=colors.HexColor('#0F766E'); pale=colors.HexColor('#F0FDFA'); styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='T',parent=styles['Title'],fontSize=22,leading=28,alignment=TA_CENTER,textColor=navy)); styles.add(ParagraphStyle(name='H',parent=styles['Heading2'],fontSize=15,leading=19,textColor=teal,spaceBefore=8,spaceAfter=7)); styles.add(ParagraphStyle(name='B',parent=styles['BodyText'],fontSize=9.5,leading=14,textColor=navy,spaceAfter=6))
    doc=SimpleDocTemplate(str(p),pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,topMargin=17*mm,bottomMargin=16*mm)
    story=[Spacer(1,17*mm),Paragraph("HEALTHCARE TREATMENT EFFECTIVENESS",styles['T']),Paragraph("Executive Report | Simulated De-identified Data",ParagraphStyle(name='S',parent=styles['Heading2'],alignment=TA_CENTER,textColor=teal)),Spacer(1,11*mm)]
    tab=[["PATIENT ENCOUNTERS",f"{k['patients']:,}"],["MEAN IMPROVEMENT",f"{k['mean_clinical_improvement']:.1f} points"],["FAVOURABLE OUTCOMES",f"{k['favourable_outcome_rate_pct']:.1f}%"],["30-DAY READMISSION",f"{k['readmission_rate_pct']:.1f}%"]]
    story += [Table(tab,colWidths=[65*mm,68*mm],style=[('BACKGROUND',(0,0),(-1,-1),pale),('TEXTCOLOR',(0,0),(0,-1),teal),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#99F6E4')),('PADDING',(0,0),(-1,-1),9)]),Spacer(1,12*mm),Paragraph("Executive Summary",styles['H']),Paragraph(f"This report analyses {k['patients']:,} simulated patient encounters. Mean clinical improvement is {k['mean_clinical_improvement']:.1f} points, the favourable-outcome rate is {k['favourable_outcome_rate_pct']:.1f}%, and 30-day readmission is {k['readmission_rate_pct']:.1f}%.",styles['B']),Paragraph("Treatment comparisons are stratified because age, baseline severity, condition, and comorbidity can influence both treatment selection and outcomes. Findings are descriptive associations, not causal estimates or clinical recommendations.",styles['B']),PageBreak(),Paragraph("1. Methodology and Safety",styles['H']),Paragraph("Clinical improvement equals baseline severity score minus follow-up score; lower severity is better. A favourable outcome requires at least 10 points of improvement and no 30-day readmission. Data quality checks cover duplicates, ranges, missingness, and required fields.",styles['B']),Paragraph("The dataset is fully simulated and excludes direct identifiers. Real healthcare use would require validated clinical definitions, risk adjustment, clinician oversight, privacy governance, and fairness review.",styles['B'])]
    stat=[["Metric","Value"],["Average age",f"{k['average_age']:.1f}"],["Median improvement",f"{k['median_clinical_improvement']:.1f}"],["Average stay",f"{k['average_length_of_stay_days']:.1f} days"],["Median cost",f"INR {k['median_treatment_cost_inr']:,.0f}"],["Average satisfaction",f"{k['average_satisfaction']:.1f} / 10"],["Cost-improvement correlation",f"{k['cost_improvement_correlation']:.3f}"]]
    story += [Spacer(1,5*mm),Table(stat,colWidths=[92*mm,55*mm],style=[('BACKGROUND',(0,0),(-1,0),navy),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#CBD5E1')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,pale]),('PADDING',(0,0),(-1,-1),7)]),PageBreak()]
    titles=["2. Improvement by Condition and Treatment","3. Favourable Outcomes by Severity","4. Length of Stay","5. Readmission Patterns","6. Cost and Improvement"]
    notes=["Condition-stratified improvement reduces, but does not eliminate, confounding from different patient mixes.","Outcome rates vary by severity, reinforcing the need to compare clinically similar groups.","Stay distributions increase with severity and should be interpreted alongside clinical need, not as efficiency alone.","Readmission differences may reflect severity and selection; investigate with risk-adjusted clinical review.","Cost and improvement show wide variation. Higher cost cannot be assumed to cause better outcomes."]
    for title,img,note in zip(titles,imgs,notes): story += [Paragraph(title,styles['H']),Image(str(img),width=172*mm,height=94*mm),Paragraph(note,styles['B']),PageBreak()]
    story += [Paragraph("7. Recommendations and Limitations",styles['H'])]
    for h,b in [("Stratified review","Compare outcomes within the same condition and baseline severity."),("Readmission review","Use structured clinical review for high-readmission groups; do not automate treatment changes."),("Balanced scorecard","Monitor improvement, readmission, stay, cost, and satisfaction together."),("Data governance","Audit definitions, missingness, coding consistency, privacy, and subgroup representation."),("Clinical oversight","Require clinicians, ethics review, and risk adjustment before any real-world application.")]: story += [Paragraph(f"<b>{h}:</b> {b}",styles['B']),Spacer(1,2*mm)]
    story += [Paragraph("Limitations",styles['H']),Paragraph("The data is simulated and observational. Treatment allocation is not randomised, residual confounding remains, and thresholds are portfolio definitions. Results must not be used for diagnosis, treatment selection, or patient-level decisions.",styles['B'])]
    def footer(canvas,doc): canvas.saveState(); canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor('#64748B')); canvas.drawString(16*mm,9*mm,'Multi-Domain Data Analysis Portfolio'); canvas.drawRightString(194*mm,9*mm,f'Page {doc.page}'); canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer); return p


def main():
    raw=generate_data(); raw.to_csv(DATA_DIR/"healthcare_raw.csv",index=False); clean=clean_healthcare_data(raw); clean.to_csv(DATA_DIR/"healthcare_cleaned.csv",index=False)
    save_json(validate_healthcare_data(raw),DATA_DIR/"raw_validation_report.json"); save_json(validate_healthcare_data(clean),DATA_DIR/"clean_validation_report.json"); k=calculate_healthcare_kpis(clean); save_json(k,DATA_DIR/"analysis_metrics.json")
    imgs=charts(clean); nb=notebook(); report=pdf(clean,k,imgs); print(f"Created {len(clean):,} cleaned encounters, {len(imgs)} charts, notebook={nb.name}, report={report.name}")


if __name__=='__main__': main()
