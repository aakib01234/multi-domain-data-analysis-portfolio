"""Reusable data quality and analysis functions for supermarket sales."""
from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "invoice_id", "date", "time", "branch", "city", "customer_type",
    "gender", "category", "product", "unit_price", "quantity",
    "discount_pct", "payment_method", "rating", "cost_price"
}


def validate_sales_data(df: pd.DataFrame) -> dict:
    """Return an auditable data-quality report without modifying the input."""
    missing_columns = sorted(REQUIRED_COLUMNS - set(df.columns))
    duplicate_invoices = int(df.duplicated(subset=["invoice_id"]).sum()) if "invoice_id" in df else 0
    missing_values = {k: int(v) for k, v in df.isna().sum().items() if v > 0}
    invalid_quantity = int((pd.to_numeric(df.get("quantity"), errors="coerce") <= 0).sum())
    invalid_price = int((pd.to_numeric(df.get("unit_price"), errors="coerce") <= 0).sum())
    invalid_discount = int((~pd.to_numeric(df.get("discount_pct"), errors="coerce").between(0, 0.50)).sum())
    invalid_rating = int((~pd.to_numeric(df.get("rating"), errors="coerce").between(1, 10)).sum())
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing_required_columns": missing_columns,
        "duplicate_invoice_ids": duplicate_invoices,
        "missing_values": missing_values,
        "invalid_quantity_rows": invalid_quantity,
        "invalid_price_rows": invalid_price,
        "invalid_discount_rows": invalid_discount,
        "invalid_rating_rows": invalid_rating,
    }


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean sales records and engineer analysis-ready fields."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    out = df.copy()
    out = out.drop_duplicates(subset=["invoice_id"], keep="first")
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    numeric = ["unit_price", "quantity", "discount_pct", "rating", "cost_price"]
    for col in numeric:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["rating"] = out["rating"].fillna(out["rating"].median()).clip(1, 10)
    out["discount_pct"] = out["discount_pct"].fillna(0).clip(0, 0.50)
    out = out.dropna(subset=["date", "unit_price", "quantity", "cost_price", "category", "product"])
    out = out[(out["unit_price"] > 0) & (out["quantity"] > 0) & (out["cost_price"] > 0)]
    out["quantity"] = out["quantity"].astype(int)
    out["gross_sales"] = out["unit_price"] * out["quantity"]
    out["discount_amount"] = out["gross_sales"] * out["discount_pct"]
    out["net_sales"] = out["gross_sales"] - out["discount_amount"]
    out["total_cost"] = out["cost_price"] * out["quantity"]
    out["profit"] = out["net_sales"] - out["total_cost"]
    out["profit_margin_pct"] = np.where(out["net_sales"] > 0, out["profit"] / out["net_sales"] * 100, 0)
    out["weekday"] = out["date"].dt.day_name()
    out["month"] = out["date"].dt.month_name()
    out["hour"] = pd.to_datetime(out["time"], format="%H:%M", errors="coerce").dt.hour
    out["time_slot"] = pd.cut(out["hour"], bins=[-1, 11, 15, 18, 24], labels=["Morning", "Afternoon", "Evening", "Night"])
    return out.sort_values(["date", "time", "invoice_id"]).reset_index(drop=True)


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate headline and statistical KPIs."""
    daily = df.groupby("date")["net_sales"].sum()
    category = df.groupby("category")["net_sales"].sum().sort_values(ascending=False)
    weekday = df.groupby("weekday")["net_sales"].mean().sort_values(ascending=False)
    hour = df.groupby("hour")["net_sales"].sum().sort_values(ascending=False)
    return {
        "total_sales": round(float(df["net_sales"].sum()), 2),
        "total_profit": round(float(df["profit"].sum()), 2),
        "transactions": int(df["invoice_id"].nunique()),
        "average_transaction_value": round(float(df["net_sales"].mean()), 2),
        "median_transaction_value": round(float(df["net_sales"].median()), 2),
        "average_rating": round(float(df["rating"].mean()), 2),
        "overall_profit_margin_pct": round(float(df["profit"].sum() / df["net_sales"].sum() * 100), 2),
        "best_category": str(category.index[0]),
        "best_category_sales": round(float(category.iloc[0]), 2),
        "best_weekday": str(weekday.index[0]),
        "peak_hour": int(hour.index[0]),
        "best_sales_day": str(daily.idxmax().date()),
        "best_sales_day_value": round(float(daily.max()), 2),
        "quantity_sales_correlation": round(float(df["quantity"].corr(df["net_sales"])), 3),
        "discount_sales_correlation": round(float(df["discount_pct"].corr(df["net_sales"])), 3),
    }


def save_json(data: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

