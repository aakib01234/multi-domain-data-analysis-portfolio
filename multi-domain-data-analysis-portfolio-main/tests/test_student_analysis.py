import pandas as pd
from src.student_analysis import validate_student_data, clean_student_data, calculate_student_kpis


def sample_students():
    rows = [
        {"student_id":"S1","school":"North","grade":10,"section":"A","gender":"Female","age":15,"attendance_pct":90,"study_hours_daily":3,"internet_access":"Yes","parent_education":"Graduate","mathematics":80,"science":70,"english":60,"social_science":50,"computer":90},
        {"student_id":"S2","school":"South","grade":10,"section":"B","gender":"Male","age":16,"attendance_pct":60,"study_hours_daily":1,"internet_access":"No","parent_education":"Secondary","mathematics":35,"science":45,"english":55,"social_science":65,"computer":75},
    ]
    return pd.DataFrame(rows + [rows[0]])


def test_validation_detects_duplicate():
    assert validate_student_data(sample_students())["duplicate_student_ids"] == 1


def test_cleaning_and_feature_engineering():
    clean = clean_student_data(sample_students())
    assert len(clean) == 2
    assert clean.loc[clean.student_id == "S1", "average_score"].iloc[0] == 70
    assert clean.loc[clean.student_id == "S2", "result"].iloc[0] == "Fail"
    assert clean.loc[clean.student_id == "S2", "at_risk"].iloc[0] == "Yes"


def test_kpi_reconciliation():
    kpis = calculate_student_kpis(clean_student_data(sample_students()))
    assert kpis["students"] == 2
    assert kpis["overall_pass_rate_pct"] == 50
    assert kpis["at_risk_students"] == 1

