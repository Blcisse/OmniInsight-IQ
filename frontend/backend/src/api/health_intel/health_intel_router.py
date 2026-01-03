from __future__ import annotations

from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_db
from src.app.models.sales import SaleORM


router = APIRouter(prefix="/health-intel", tags=["Health Intelligence"])


@router.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


def _parse_dates(start: Optional[str], end: Optional[str]) -> tuple[str, str]:
    if not end:
        end_date = date.today()
    else:
        end_date = date.fromisoformat(end)
    if not start:
        start_date = end_date - timedelta(days=30)
    else:
        start_date = date.fromisoformat(start)
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start must be <= end")
    return (start_date.isoformat(), end_date.isoformat())


@router.get("/products/metrics")
async def product_metrics(
    product_id: str = Query(..., description="Product identifier"),
    start: Optional[str] = Query(None, description="ISO start date"),
    end: Optional[str] = Query(None, description="ISO end date"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    start_date, end_date = _parse_dates(start, end)

    # Timeseries rows
    ts_stmt = (
        select(
            SaleORM.date,
            func.coalesce(func.sum(SaleORM.units_sold), 0).label("units"),
            func.coalesce(func.sum(SaleORM.revenue), 0.0).label("revenue"),
        )
        .where(SaleORM.product_id == product_id)
        .where(SaleORM.date >= start_date)
        .where(SaleORM.date <= end_date)
        .group_by(SaleORM.date)
        .order_by(SaleORM.date.asc())
    )
    res = await db.execute(ts_stmt)
    rows = res.all()
    timeseries = [
        {"date": d, "units_sold": int(u or 0), "revenue": float(r or 0.0)} for d, u, r in rows
    ]

    # Totals / aggregates
    total_units = sum(r[1] or 0 for r in rows)
    total_revenue = float(sum((r[2] or 0.0) for r in rows))
    days = max(1, len(rows))
    avg_daily_units = total_units / days
    avg_daily_revenue = total_revenue / days

    return {
        "product_id": product_id,
        "window": {"start": start_date, "end": end_date},
        "totals": {"units_sold": int(total_units), "revenue": float(total_revenue)},
        "aggregates": {
            "avg_daily_units": float(avg_daily_units),
            "avg_daily_revenue": float(avg_daily_revenue),
        },
        "timeseries": timeseries,
    }


@router.get("/products/metrics.csv", response_class=PlainTextResponse)
async def product_metrics_csv(
    product_id: str = Query(...),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> str:
    start_date, end_date = _parse_dates(start, end)

    ts_stmt = (
        select(
            SaleORM.date,
            func.coalesce(func.sum(SaleORM.units_sold), 0).label("units"),
            func.coalesce(func.sum(SaleORM.revenue), 0.0).label("revenue"),
        )
        .where(SaleORM.product_id == product_id)
        .where(SaleORM.date >= start_date)
        .where(SaleORM.date <= end_date)
        .group_by(SaleORM.date)
        .order_by(SaleORM.date.asc())
    )
    res = await db.execute(ts_stmt)
    rows = res.all()

    # Build CSV
    out = ["date,product_id,units_sold,revenue"]
    for d, u, r in rows:
        out.append(f"{d},{product_id},{int(u or 0)},{float(r or 0.0)}")
    return "\n".join(out) + "\n"

