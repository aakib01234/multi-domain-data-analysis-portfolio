import pandas as pd
from src.healthcare_analysis import validate_healthcare_data,clean_healthcare_data,calculate_healthcare_kpis


def sample_healthcare():
    rows=[
      {"patient_id":"P1","admission_date":"2024-01-01","hospital":"Central","age":50,"gender":"Female","condition":"Diabetes","severity":"Moderate","treatment":"Medication A","baseline_score":70,"followup_score":50,"length_of_stay_days":4,"treatment_cost_inr":30000,"readmitted_30d":"No","satisfaction_score":8},
      {"patient_id":"P2","admission_date":"2024-01-02","hospital":"City","age":65,"gender":"Male","condition":"Hypertension","severity":"Severe","treatment":"Medication B","baseline_score":80,"followup_score":75,"length_of_stay_days":7,"treatment_cost_inr":50000,"readmitted_30d":"Yes","satisfaction_score":6}]
    return pd.DataFrame(rows+[rows[0]])


def test_healthcare_validation_duplicate(): assert validate_healthcare_data(sample_healthcare())["duplicate_patient_ids"]==1


def test_healthcare_cleaning_and_outcome():
    clean=clean_healthcare_data(sample_healthcare()); assert len(clean)==2
    assert clean.loc[clean.patient_id=="P1","clinical_improvement"].iloc[0]==20
    assert clean.loc[clean.patient_id=="P1","favourable_outcome"].iloc[0]=="Yes"
    assert clean.loc[clean.patient_id=="P2","favourable_outcome"].iloc[0]=="No"


def test_healthcare_kpis():
    k=calculate_healthcare_kpis(clean_healthcare_data(sample_healthcare())); assert k["patients"]==2
    assert k["mean_clinical_improvement"]==12.5 and k["readmission_rate_pct"]==50

