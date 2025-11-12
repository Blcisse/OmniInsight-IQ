from __future__ import annotations

import os
from typing import Optional, List, Dict, Any

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse


router = APIRouter(prefix="/api/reports", tags=["reports-csv"])


def _load_csv(filename: str) -> pd.DataFrame:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
    path = os.path.join(base, "data", "raw", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"CSV not found: {filename}")
    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {e}")
    return df


@router.get("/foods")
def foods_report(
    metric: str = Query(..., description="Column name to aggregate, e.g., 'Protein' or 'Caloric Value'"),
    q: Optional[str] = Query(None, description="Substring to filter 'food' column (case-insensitive)"),
    top: int = Query(10, ge=1, le=100),
    file: str = Query("FOOD-DATA-GROUP1.csv", description="CSV file in data/raw"),
) -> Dict[str, Any]:
    df = _load_csv(file)
    if "food" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain a 'food' column")
    if metric not in df.columns:
        raise HTTPException(status_code=400, detail=f"Metric column '{metric}' not found in CSV")

    data = df[["food", metric]].copy()
    if q:
        data = data[data["food"].str.contains(q, case=False, na=False)]

    # Coerce metric to numeric
    data[metric] = pd.to_numeric(data[metric], errors="coerce").fillna(0.0)
    total_count = int(len(data))
    summary = {
        "sum": float(data[metric].sum()),
        "mean": float(data[metric].mean()) if total_count else 0.0,
        "min": float(data[metric].min()) if total_count else 0.0,
        "max": float(data[metric].max()) if total_count else 0.0,
    }

    ranked = data.sort_values(metric, ascending=False).head(top)
    top_rows = [{"food": r["food"], "value": float(r[metric])} for _, r in ranked.iterrows()]
    series = [{"label": r["food"], "value": float(r[metric])} for _, r in ranked.iterrows()]

    return {
        "file": file,
        "metric": metric,
        "query": q,
        "total_count": total_count,
        "summary": summary,
        "top": top_rows,
        "series": series,
    }


@router.get("/foods.csv", response_class=PlainTextResponse)
def foods_report_csv(
    metric: str = Query(...),
    q: Optional[str] = Query(None),
    top: int = Query(10, ge=1, le=100),
    file: str = Query("FOOD-DATA-GROUP1.csv"),
) -> str:
    df = _load_csv(file)
    if "food" not in df.columns or metric not in df.columns:
        raise HTTPException(status_code=400, detail="Missing required columns in CSV")
    data = df[["food", metric]].copy()
    if q:
        data = data[data["food"].str.contains(q, case=False, na=False)]
    data[metric] = pd.to_numeric(data[metric], errors="coerce").fillna(0.0)
    ranked = data.sort_values(metric, ascending=False).head(top)
    lines = ["food,value"]
    for _, r in ranked.iterrows():
        lines.append(f"{r['food']},{float(r[metric])}")
    return "\n".join(lines) + "\n"

