"""Validation, cleaning, and statistical analysis for student performance data."""
from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd

SUBJECTS = ["mathematics", "science", "english", "social_science", "computer"]
REQUIRED_COLUMNS = {
    "student_id", "school", "grade", "section", "gender", "age",
    "attendance_pct", "study_hours_daily", "internet_access",
    "parent_education", *SUBJECTS
}


def validate_student_data(df: pd.DataFrame) -> dict:
    """Return an auditable data-quality report."""
    missing_cols = sorted(REQUIRED_COLUMNS - set(df.columns))
    duplicate_ids = int(df.duplicated("student_id").sum()) if "student_id" in df else 0
    missing = {c: int(n) for c, n in df.isna().sum().items() if n > 0}
    invalid_scores = 0
    for col in SUBJECTS:
        if col in df:
            values = pd.to_numeric(df[col], errors="coerce")
            invalid_scores += int((~values.between(0, 100) & values.notna()).sum())
    attendance = pd.to_numeric(df.get("attendance_pct"), errors="coerce")
    study = pd.to_numeric(df.get("study_hours_daily"), errors="coerce")
    return {
        "rows": int(len(df)), "columns": int(len(df.columns)),
        "missing_required_columns": missing_cols,
        "duplicate_student_ids": duplicate_ids, "missing_values": missing,
        "invalid_score_values": invalid_scores,
        "invalid_attendance_rows": int((~attendance.between(0, 100) & attendance.notna()).sum()),
        "invalid_study_hours_rows": int((~study.between(0, 16) & study.notna()).sum()),
    }


def clean_student_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean records and create performance/risk features."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    out = df.copy().drop_duplicates("student_id", keep="first")
    numeric = ["age", "attendance_pct", "study_hours_daily", *SUBJECTS]
    for col in numeric:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    for col in SUBJECTS:
        out[col] = out.groupby("grade")[col].transform(lambda s: s.fillna(s.median()))
        out[col] = out[col].clip(0, 100)
    out["attendance_pct"] = out["attendance_pct"].fillna(out["attendance_pct"].median()).clip(0, 100)
    out["study_hours_daily"] = out["study_hours_daily"].fillna(out["study_hours_daily"].median()).clip(0, 16)
    out = out.dropna(subset=["student_id", "school", "grade", "gender", "age"])
    out["average_score"] = out[SUBJECTS].mean(axis=1)
    out["median_score"] = out[SUBJECTS].median(axis=1)
    out["subjects_passed"] = (out[SUBJECTS] >= 40).sum(axis=1)
    out["result"] = np.where(out[SUBJECTS].ge(40).all(axis=1), "Pass", "Fail")
    out["performance_band"] = pd.cut(out["average_score"], [-1, 39, 59, 74, 89, 100], labels=["Critical", "Average", "Good", "Very Good", "Excellent"])
    out["at_risk"] = np.where((out["attendance_pct"] < 75) | (out["result"] == "Fail") | (out["average_score"] < 50), "Yes", "No")
    return out.sort_values("student_id").reset_index(drop=True)


def calculate_student_kpis(df: pd.DataFrame) -> dict:
    subject_avg = df[SUBJECTS].mean().sort_values(ascending=False)
    subject_pass = (df[SUBJECTS].ge(40).mean() * 100).sort_values(ascending=False)
    return {
        "students": int(df.student_id.nunique()),
        "overall_average": round(float(df.average_score.mean()), 2),
        "overall_median": round(float(df.average_score.median()), 2),
        "overall_pass_rate_pct": round(float((df.result == "Pass").mean() * 100), 2),
        "at_risk_students": int((df.at_risk == "Yes").sum()),
        "at_risk_rate_pct": round(float((df.at_risk == "Yes").mean() * 100), 2),
        "average_attendance_pct": round(float(df.attendance_pct.mean()), 2),
        "top_subject": str(subject_avg.index[0]).replace("_", " ").title(),
        "top_subject_average": round(float(subject_avg.iloc[0]), 2),
        "lowest_subject": str(subject_avg.index[-1]).replace("_", " ").title(),
        "lowest_subject_average": round(float(subject_avg.iloc[-1]), 2),
        "highest_subject_pass_rate_pct": round(float(subject_pass.iloc[0]), 2),
        "attendance_score_correlation": round(float(df.attendance_pct.corr(df.average_score)), 3),
        "study_hours_score_correlation": round(float(df.study_hours_daily.corr(df.average_score)), 3),
    }


def save_json(data: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

