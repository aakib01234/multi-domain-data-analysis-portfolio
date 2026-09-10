"""Validation, cleaning, and descriptive healthcare outcome analysis."""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

REQUIRED_COLUMNS={"patient_id","admission_date","hospital","age","gender","condition","severity","treatment","baseline_score","followup_score","length_of_stay_days","treatment_cost_inr","readmitted_30d","satisfaction_score"}


def validate_healthcare_data(df:pd.DataFrame)->dict:
    missing_cols=sorted(REQUIRED_COLUMNS-set(df.columns)); age=pd.to_numeric(df.get("age"),errors="coerce")
    base=pd.to_numeric(df.get("baseline_score"),errors="coerce"); follow=pd.to_numeric(df.get("followup_score"),errors="coerce")
    los=pd.to_numeric(df.get("length_of_stay_days"),errors="coerce"); cost=pd.to_numeric(df.get("treatment_cost_inr"),errors="coerce"); sat=pd.to_numeric(df.get("satisfaction_score"),errors="coerce")
    return {"rows":int(len(df)),"columns":int(len(df.columns)),"missing_required_columns":missing_cols,
      "duplicate_patient_ids":int(df.duplicated("patient_id").sum()) if "patient_id" in df else 0,
      "missing_values":{c:int(n) for c,n in df.isna().sum().items() if n>0},
      "invalid_age_rows":int((~age.between(0,110)&age.notna()).sum()),"invalid_baseline_rows":int((~base.between(0,100)&base.notna()).sum()),
      "invalid_followup_rows":int((~follow.between(0,100)&follow.notna()).sum()),"invalid_stay_rows":int((((los<0)|(~np.isfinite(los)))&los.notna()).sum()),
      "invalid_cost_rows":int((cost<0).sum()),"invalid_satisfaction_rows":int((~sat.between(1,10)&sat.notna()).sum())}


def clean_healthcare_data(df:pd.DataFrame)->pd.DataFrame:
    missing=REQUIRED_COLUMNS-set(df.columns)
    if missing: raise ValueError(f"Missing required columns: {sorted(missing)}")
    out=df.copy().drop_duplicates("patient_id",keep="first"); out["admission_date"]=pd.to_datetime(out.admission_date,errors="coerce")
    numeric=["age","baseline_score","followup_score","length_of_stay_days","treatment_cost_inr","satisfaction_score"]
    for col in numeric: out[col]=pd.to_numeric(out[col],errors="coerce")
    out=out.dropna(subset=["patient_id","admission_date","condition","severity","treatment","age","baseline_score","followup_score"])
    out=out[out.age.between(0,110)&out.baseline_score.between(0,100)&out.followup_score.between(0,100)]
    for col in ["length_of_stay_days","treatment_cost_inr","satisfaction_score"]:
      out[col]=out.groupby(["condition","severity"])[col].transform(lambda s:s.fillna(s.median()))
    out=out[(out.length_of_stay_days>=0)&(out.treatment_cost_inr>=0)]; out.satisfaction_score=out.satisfaction_score.clip(1,10)
    out["readmitted_30d"]=out.readmitted_30d.astype(str).str.strip().str.title().map({"Yes":"Yes","No":"No"})
    out=out.dropna(subset=["readmitted_30d"])
    out["clinical_improvement"]=out.baseline_score-out.followup_score
    out["improvement_pct"]=np.where(out.baseline_score>0,out.clinical_improvement/out.baseline_score*100,0)
    out["favourable_outcome"]=np.where((out.clinical_improvement>=10)&(out.readmitted_30d=="No"),"Yes","No")
    out["age_group"]=pd.cut(out.age,[0,17,39,59,79,110],labels=["0-17","18-39","40-59","60-79","80+"])
    out["admission_month"]=out.admission_date.dt.to_period("M").astype(str)
    return out.sort_values(["admission_date","patient_id"]).reset_index(drop=True)


def calculate_healthcare_kpis(df:pd.DataFrame)->dict:
    tx=df.groupby("treatment").clinical_improvement.mean().sort_values(ascending=False); cond=df.groupby("condition").clinical_improvement.mean().sort_values(ascending=False)
    return {"patients":int(df.patient_id.nunique()),"average_age":round(float(df.age.mean()),2),"mean_clinical_improvement":round(float(df.clinical_improvement.mean()),2),
      "median_clinical_improvement":round(float(df.clinical_improvement.median()),2),"favourable_outcome_rate_pct":round(float((df.favourable_outcome=="Yes").mean()*100),2),
      "readmission_rate_pct":round(float((df.readmitted_30d=="Yes").mean()*100),2),"average_length_of_stay_days":round(float(df.length_of_stay_days.mean()),2),
      "median_treatment_cost_inr":round(float(df.treatment_cost_inr.median()),2),"average_satisfaction":round(float(df.satisfaction_score.mean()),2),
      "highest_improvement_treatment":str(tx.index[0]),"highest_treatment_improvement":round(float(tx.iloc[0]),2),"highest_improvement_condition":str(cond.index[0]),
      "cost_improvement_correlation":round(float(df.treatment_cost_inr.corr(df.clinical_improvement)),3),"stay_readmission_correlation":round(float(df.length_of_stay_days.corr((df.readmitted_30d=="Yes").astype(int))),3)}


def save_json(data:dict,path:str|Path): Path(path).parent.mkdir(parents=True,exist_ok=True); Path(path).write_text(json.dumps(data,indent=2),encoding="utf-8")
