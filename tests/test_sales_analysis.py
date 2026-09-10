import pandas as pd
from src.sales_analysis import clean_sales_data, validate_sales_data, calculate_kpis


def sample_data():
    return pd.DataFrame([
        {"invoice_id":"A1","date":"2024-01-01","time":"10:00","branch":"A","city":"Delhi","customer_type":"Member","gender":"Female","category":"Groceries","product":"Rice","unit_price":100,"quantity":2,"discount_pct":0.10,"payment_method":"UPI","rating":8,"cost_price":60},
        {"invoice_id":"A1","date":"2024-01-01","time":"10:00","branch":"A","city":"Delhi","customer_type":"Member","gender":"Female","category":"Groceries","product":"Rice","unit_price":100,"quantity":2,"discount_pct":0.10,"payment_method":"UPI","rating":8,"cost_price":60},
        {"invoice_id":"A2","date":"2024-01-02","time":"18:00","branch":"B","city":"Mumbai","customer_type":"Normal","gender":"Male","category":"Electronics","product":"Earbuds","unit_price":1000,"quantity":1,"discount_pct":0,"payment_method":"Card","rating":None,"cost_price":650},
    ])


def test_validation_detects_duplicate_and_missing_rating():
    result = validate_sales_data(sample_data())
    assert result["duplicate_invoice_ids"] == 1
    assert result["missing_values"]["rating"] == 1


def test_cleaning_removes_duplicate_and_engineers_metrics():
    cleaned = clean_sales_data(sample_data())
    assert len(cleaned) == 2
    assert {"net_sales", "profit", "weekday", "time_slot"}.issubset(cleaned.columns)
    assert cleaned.loc[cleaned.invoice_id == "A1", "net_sales"].iloc[0] == 180


def test_kpis_are_consistent():
    cleaned = clean_sales_data(sample_data())
    kpis = calculate_kpis(cleaned)
    assert kpis["transactions"] == 2
    assert kpis["total_sales"] == 1180
    assert kpis["total_profit"] == 410
