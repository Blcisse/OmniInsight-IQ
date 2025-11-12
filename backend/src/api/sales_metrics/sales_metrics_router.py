from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_db
from src.app.models.sales import SaleORM


router = APIRouter(prefix="/sales", tags=["Sales Intelligence"])


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


@router.get("")
async def list_sales(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    product_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    start_date, end_date = _parse_dates(start, end)
    conditions = [
        SaleORM.date >= start_date,
        SaleORM.date <= end_date,
    ]
    if region:
        conditions.append(SaleORM.region == region)
    if product_id:
        conditions.append(SaleORM.product_id == product_id)

    stmt = (
        select(SaleORM)
        .where(and_(*conditions))
        .order_by(SaleORM.date.asc())
        .limit(limit)
        .offset(offset)
    )
    res = await db.execute(stmt)
    rows = res.scalars().all()
    return [
        {
            "id": r.id,
            "date": r.date,
            "product_id": r.product_id,
            "region": r.region,
            "units_sold": r.units_sold,
            "revenue": float(r.revenue),
        }
        for r in rows
    ]


@router.post("")
async def create_sale(
    payload: dict,
    db: AsyncSession = Depends(get_db),
):
    required = {"product_id", "date", "units_sold", "revenue"}
    missing = required - set(payload.keys())
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing fields: {', '.join(sorted(missing))}")

    sale = SaleORM(
        product_id=str(payload.get("product_id")),
        date=str(payload.get("date")),
        region=str(payload.get("region")) if payload.get("region") is not None else None,
        units_sold=int(payload.get("units_sold")),
        revenue=float(payload.get("revenue")),
    )
    db.add(sale)
    await db.commit()
    await db.refresh(sale)
    return {
        "id": sale.id,
        "date": sale.date,
        "product_id": sale.product_id,
        "region": sale.region,
        "units_sold": sale.units_sold,
        "revenue": float(sale.revenue),
    }


@router.get("/metrics")
async def sales_metrics(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    product_id: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    start_date, end_date = _parse_dates(start, end)

    conditions = [
        SaleORM.date >= start_date,
        SaleORM.date <= end_date,
    ]
    if product_id:
        conditions.append(SaleORM.product_id == product_id)
    if region:
        conditions.append(SaleORM.region == region)

    ts_stmt = (
        select(
            SaleORM.date,
            func.coalesce(func.sum(SaleORM.units_sold), 0).label("units"),
            func.coalesce(func.sum(SaleORM.revenue), 0.0).label("revenue"),
        )
        .where(and_(*conditions))
        .group_by(SaleORM.date)
        .order_by(SaleORM.date.asc())
    )
    res = await db.execute(ts_stmt)
    rows = res.all()

    timeseries = [
        {"date": d, "units_sold": int(u or 0), "revenue": float(r or 0.0)} for d, u, r in rows
    ]

    total_units = sum(int(u or 0) for _, u, _ in rows)
    total_revenue = float(sum(float(r or 0.0) for _, _, r in rows))
    days = max(1, len(rows))

    return {
        "filters": {
            "start": start_date,
            "end": end_date,
            "product_id": product_id,
            "region": region,
        },
        "totals": {"units_sold": total_units, "revenue": total_revenue},
        "aggregates": {
            "avg_daily_units": total_units / days,
            "avg_daily_revenue": total_revenue / days,
        },
        "timeseries": timeseries,
    }


@router.get("/metrics.csv", response_class=PlainTextResponse)
async def sales_metrics_csv(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    product_id: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> str:
    start_date, end_date = _parse_dates(start, end)

    conditions = [
        SaleORM.date >= start_date,
        SaleORM.date <= end_date,
    ]
    if product_id:
        conditions.append(SaleORM.product_id == product_id)
    if region:
        conditions.append(SaleORM.region == region)

    ts_stmt = (
        select(
            SaleORM.date,
            func.coalesce(func.sum(SaleORM.units_sold), 0).label("units"),
            func.coalesce(func.sum(SaleORM.revenue), 0.0).label("revenue"),
        )
        .where(and_(*conditions))
        .group_by(SaleORM.date)
        .order_by(SaleORM.date.asc())
    )
    res = await db.execute(ts_stmt)
    rows = res.all()

    header = "date,units_sold,revenue"
    out = [header]
    for d, u, r in rows:
        out.append(f"{d},{int(u or 0)},{float(r or 0.0)}")
    return "\n".join(out) + "\n"
