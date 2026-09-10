"""Build the complete Student Performance Analysis project."""
from __future__ import annotations

import json, sys
from pathlib import Path
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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

from src.student_analysis import SUBJECTS, validate_student_data, clean_student_data, calculate_student_kpis, save_json

DATA_DIR=ROOT/"data"/"project2_students"; VIZ_DIR=ROOT/"visualizations"/"project2_students"
REPORT_DIR=ROOT/"reports"; NOTEBOOK_DIR=ROOT/"notebooks"
for d in [DATA_DIR,VIZ_DIR,REPORT_DIR,NOTEBOOK_DIR]: d.mkdir(parents=True,exist_ok=True)


def generate_data(n=1200, seed=84):
    rng=np.random.default_rng(seed)
    attendance=np.clip(rng.normal(82,10,n),45,100)
    study=np.clip(rng.gamma(2.5,0.9,n),0.2,7)
    internet=rng.choice(["Yes","No"],n,p=[.79,.21])
    grade=rng.choice([9,10,11,12],n)
    latent=24 + .38*attendance + 4.2*study + np.where(internet=="Yes",2.2,0) - (grade-9)*.8
    offsets={"mathematics":-3,"science":0,"english":3,"social_science":2,"computer":5}
    data={
        "student_id":[f"STU-{i:04d}" for i in range(1,n+1)],
        "school":rng.choice(["North Academy","South Public","East Model","West Senior"],n,p=[.27,.25,.24,.24]),
        "grade":grade,"section":rng.choice(list("ABC"),n),"gender":rng.choice(["Female","Male"],n,p=[.51,.49]),
        "age":grade+rng.choice([5,6],n,p=[.72,.28]),"attendance_pct":np.round(attendance,1),
        "study_hours_daily":np.round(study,1),"internet_access":internet,
        "parent_education":rng.choice(["Primary","Secondary","Graduate","Postgraduate"],n,p=[.16,.37,.34,.13])
    }
    for subject,offset in offsets.items():
        data[subject]=np.round(np.clip(latent+offset+rng.normal(0,10,n),0,100),1)
    df=pd.DataFrame(data)
    for row,col in [(25,"mathematics"),(316,"science"),(711,"english"),(943,"attendance_pct")]: df.loc[row,col]=np.nan
    return pd.concat([df,df.iloc[[110,765]]],ignore_index=True)


def charts(df):
    sns.set_theme(style="whitegrid"); plt.rcParams.update({"figure.dpi":140,"axes.titleweight":"bold","axes.titlesize":14})
    paths=[]
    def save(name):
        p=VIZ_DIR/name; plt.tight_layout(); plt.savefig(p,bbox_inches="tight",facecolor="white"); plt.close(); paths.append(p)
    avgs=df[SUBJECTS].mean().sort_values(); labels=[x.replace('_',' ').title() for x in avgs.index]
    plt.figure(figsize=(9,5)); ax=plt.barh(labels,avgs.values,color="#7C3AED"); plt.bar_label(ax,fmt="%.1f",padding=4); plt.xlim(0,100); plt.xlabel("Average marks"); plt.title("Average Score by Subject"); save("01_subject_averages.png")
    rates=(df[SUBJECTS].ge(40).mean()*100).sort_values(); labels=[x.replace('_',' ').title() for x in rates.index]
    plt.figure(figsize=(9,5)); ax=plt.barh(labels,rates.values,color="#10B981"); plt.bar_label(ax,fmt="%.1f%%",padding=4); plt.xlim(0,105); plt.xlabel("Pass rate (%)"); plt.title("Subject-wise Pass Rates"); save("02_subject_pass_rates.png")
    sample=df.sample(min(700,len(df)),random_state=1)
    plt.figure(figsize=(9,5)); sns.regplot(data=sample,x="attendance_pct",y="average_score",scatter_kws={"alpha":.35,"s":22,"color":"#7C3AED"},line_kws={"color":"#DC2626"}); plt.title("Attendance and Academic Performance"); plt.xlabel("Attendance (%)"); plt.ylabel("Average score"); save("03_attendance_correlation.png")
    plt.figure(figsize=(9,5)); sns.histplot(data=df,x="average_score",hue="result",bins=24,kde=True,palette={"Pass":"#10B981","Fail":"#EF4444"},alpha=.45); plt.title("Student Performance Distribution"); plt.xlabel("Average score"); save("04_score_distribution.png")
    corr=df[["attendance_pct","study_hours_daily",*SUBJECTS,"average_score"]].corr()
    plt.figure(figsize=(10,7)); sns.heatmap(corr,annot=True,fmt=".2f",cmap="Purples",vmin=-1,vmax=1); plt.title("Performance Correlation Matrix"); save("05_correlation_heatmap.png")
    return paths


def notebook():
    def md(s): return {"cell_type":"markdown","metadata":{},"source":s.splitlines(True)}
    def code(s): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":s.splitlines(True)}
    cells=[
      md("# Project 2 - Student Performance Analysis\n\n**Domain:** Education  \n**Objective:** Analyse pass/fail rates, subject performance, attendance impact, and student risk."),
      md("## 1. Setup and data loading"),
      code("from pathlib import Path\nimport sys, pandas as pd, numpy as np\nROOT=Path.cwd() if (Path.cwd()/'src').exists() else Path.cwd().parent\nsys.path.insert(0,str(ROOT))\nfrom src.student_analysis import SUBJECTS, validate_student_data, clean_student_data, calculate_student_kpis\nraw=pd.read_csv(ROOT/'data/project2_students/student_performance_raw.csv')\nraw.head()"),
      md("## 2. Validation and cleaning"),code("raw_validation=validate_student_data(raw)\npd.Series(raw_validation)"),
      code("students=clean_student_data(raw)\nprint(f'{len(raw):,} raw rows -> {len(students):,} clean students')\nvalidate_student_data(students)"),
      md("## 3. Descriptive statistics and KPIs"),code("kpis=calculate_student_kpis(students)\npd.Series(kpis).to_frame('Value')"),code("students[['attendance_pct','study_hours_daily',*SUBJECTS,'average_score']].describe().round(2)"),
      md("## 4. Subject and pass/fail analysis"),code("subject_summary=pd.DataFrame({'average':students[SUBJECTS].mean(),'median':students[SUBJECTS].median(),'pass_rate_pct':students[SUBJECTS].ge(40).mean()*100}).round(2)\nsubject_summary"),code("students['result'].value_counts().to_frame('students').assign(rate_pct=lambda x:x.students/len(students)*100).round(2)"),
      md("## 5. Attendance, study habits, and subgroup analysis"),code("students.groupby(pd.cut(students.attendance_pct,[0,60,75,85,100]))['average_score'].agg(['count','mean','median']).round(2)"),code("students.groupby(['grade','gender']).agg(students=('student_id','count'),average_score=('average_score','mean'),pass_rate=('result',lambda s:(s=='Pass').mean()*100)).round(2)"),
      md("## 6. Correlation analysis\nPearson correlation describes linear association and does not prove causality."),code("students[['attendance_pct','study_hours_daily',*SUBJECTS,'average_score']].corr().round(3)"),
      md("## 7. At-risk students"),code("risk=students[students.at_risk=='Yes'][['student_id','grade','attendance_pct','average_score','subjects_passed','result']]\nrisk.head(15)"),
      md("## 8. Visualizations"),code("from IPython.display import display, Image\nfor chart in sorted((ROOT/'visualizations/project2_students').glob('*.png')):\n    display(Image(filename=str(chart),width=850))"),
      md("## 9. Recommendations\n1. Use attendance alerts before students fall below 75%.\n2. Provide subject-specific tutoring based on failed subjects.\n3. Review at-risk progress every two weeks.\n4. Provide supervised digital access where needed.\n5. Measure pass conversion and risk-exit rates."),
      md("## 10. Ethical note\nRisk flags should support teachers, not replace judgement or penalise students. No real personal data is used in this simulated portfolio project.")]
    nb={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3"}},"nbformat":4,"nbformat_minor":5}
    p=NOTEBOOK_DIR/"02_student_performance_analysis.ipynb"; p.write_text(json.dumps(nb,indent=1),encoding="utf-8"); return p


def pdf_report(df,k,imgs):
    p=REPORT_DIR/"02_student_performance_report.pdf"; navy=colors.HexColor('#111827'); purple=colors.HexColor('#7C3AED'); pale=colors.HexColor('#F5F3FF')
    styles=getSampleStyleSheet(); styles.add(ParagraphStyle(name="T",parent=styles['Title'],fontSize=24,leading=30,alignment=TA_CENTER,textColor=navy)); styles.add(ParagraphStyle(name="H",parent=styles['Heading2'],fontSize=15,leading=19,textColor=purple,spaceBefore=8,spaceAfter=7)); styles.add(ParagraphStyle(name="B",parent=styles['BodyText'],fontSize=9.5,leading=14,textColor=navy,spaceAfter=6))
    doc=SimpleDocTemplate(str(p),pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,topMargin=17*mm,bottomMargin=16*mm)
    story=[Spacer(1,18*mm),Paragraph("STUDENT PERFORMANCE ANALYSIS",styles['T']),Paragraph("Executive Report | Education Domain",ParagraphStyle(name='S',parent=styles['Heading2'],alignment=TA_CENTER,textColor=purple)),Spacer(1,12*mm)]
    table=[["STUDENTS",f"{k['students']:,}"],["AVERAGE SCORE",f"{k['overall_average']:.1f}"],["PASS RATE",f"{k['overall_pass_rate_pct']:.1f}%"],["AT-RISK STUDENTS",f"{k['at_risk_students']:,} ({k['at_risk_rate_pct']:.1f}%)"]]
    story += [Table(table,colWidths=[55*mm,70*mm],style=[('BACKGROUND',(0,0),(-1,-1),pale),('TEXTCOLOR',(0,0),(0,-1),purple),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#DDD6FE')),('PADDING',(0,0),(-1,-1),9)]),Spacer(1,13*mm),Paragraph("Executive Summary",styles['H']),Paragraph(f"The analysis covers {k['students']:,} cleaned student records. Overall average performance is {k['overall_average']:.1f}, with an all-subject pass rate of {k['overall_pass_rate_pct']:.1f}%. {k['top_subject']} is the strongest subject ({k['top_subject_average']:.1f}), while {k['lowest_subject']} requires the greatest academic support ({k['lowest_subject_average']:.1f}).",styles['B']),Paragraph(f"Attendance has a correlation of {k['attendance_score_correlation']:.3f} with average score, while daily study hours correlate at {k['study_hours_score_correlation']:.3f}. These associations support early outreach and targeted tutoring, but do not establish causation.",styles['B']),PageBreak()]
    story += [Paragraph("1. Methodology and Definitions",styles['H']),Paragraph("Records were checked for schema completeness, duplicate IDs, missing data, and valid ranges. Missing scores were imputed using grade-level medians. Student averages, medians, subject passes, overall result, performance band, and risk status were engineered.",styles['B']),Paragraph("A subject is passed at 40 marks. A student passes overall only when all five subjects are passed. At-risk status is assigned when attendance is below 75%, any subject is failed, or the overall average is below 50.",styles['B'])]
    stat=[["Metric","Value"],["Overall median",f"{k['overall_median']:.2f}"],["Average attendance",f"{k['average_attendance_pct']:.2f}%"],["Attendance-score correlation",f"{k['attendance_score_correlation']:.3f}"],["Study-hours correlation",f"{k['study_hours_score_correlation']:.3f}"]]
    story += [Spacer(1,5*mm),Table(stat,colWidths=[90*mm,55*mm],style=[('BACKGROUND',(0,0),(-1,0),navy),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#D1D5DB')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,pale]),('PADDING',(0,0),(-1,-1),7)]),PageBreak()]
    titles=["2. Subject Performance","3. Subject Pass Rates","4. Attendance Impact","5. Score Distribution","6. Correlation Analysis"]
    notes=[f"{k['top_subject']} leads average performance; {k['lowest_subject']} should receive targeted curriculum and tutoring review.","Subject pass rates reveal where average marks may hide a meaningful lower-performing group.","The fitted line shows the direction of the attendance-performance relationship. It is an association, not proof that attendance alone causes higher scores.","The distribution compares passing and failing students and highlights the score range where intervention may have the greatest impact.","The matrix compares academic and behavioural variables, helping prioritise factors for further investigation."]
    for title,img,note in zip(titles,imgs,notes): story += [Paragraph(title,styles['H']),Image(str(img),width=172*mm,height=94*mm),Paragraph(note,styles['B']),PageBreak()]
    story += [Paragraph("7. Recommendations and Safeguards",styles['H'])]
    for h,b in [("Attendance alerts","Contact students before attendance falls below 75%, focusing on barriers and support."),("Targeted tutoring",f"Prioritise {k['lowest_subject']} and students failing individual subjects."),("Progress reviews","Review each at-risk student's attendance, subject scores, and study plan every two weeks."),("Access support","Offer supervised computer and library access where home internet is limited."),("Evaluation","Measure attendance improvement, subject gain, pass conversion, and risk-exit rate.")]: story += [Paragraph(f"<b>{h}:</b> {b}",styles['B']),Spacer(1,2*mm)]
    story += [Paragraph("Ethical note",styles['H']),Paragraph("Risk flags are screening aids, not final judgements. Teachers should review context, avoid punitive use, protect privacy, and monitor whether the rule affects groups unfairly. The portfolio dataset is simulated and contains no real personal information.",styles['B'])]
    def footer(canvas,doc): canvas.saveState(); canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor('#6B7280')); canvas.drawString(16*mm,9*mm,'Multi-Domain Data Analysis Portfolio'); canvas.drawRightString(194*mm,9*mm,f'Page {doc.page}'); canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer); return p


def main():
    raw=generate_data(); raw.to_csv(DATA_DIR/"student_performance_raw.csv",index=False)
    clean=clean_student_data(raw); clean.to_csv(DATA_DIR/"student_performance_cleaned.csv",index=False)
    save_json(validate_student_data(raw),DATA_DIR/"raw_validation_report.json"); save_json(validate_student_data(clean),DATA_DIR/"clean_validation_report.json")
    k=calculate_student_kpis(clean); save_json(k,DATA_DIR/"analysis_metrics.json")
    imgs=charts(clean); nb=notebook(); report=pdf_report(clean,k,imgs)
    print(f"Created {len(clean):,} cleaned students, {len(imgs)} charts, notebook={nb.name}, report={report.name}")


if __name__=="__main__": main()
