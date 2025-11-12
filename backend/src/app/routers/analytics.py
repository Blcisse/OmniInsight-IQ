from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..models.sales import SaleORM
from ..models.marketing import CampaignORM
from ...lib.mlModels.regressionModel import linear_regression_forecast


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


class AggregateResponse(BaseModel):
    total_sales: float
    avg_order_value: float
    orders_count: int
    by_day: List[Dict[str, float]]


class PredictResponse(BaseModel):
    model: str
    generated_at: datetime
    horizon_days: int
    forecast: List[Dict[str, float]]
    confidence: float


class AggregateMetrics(BaseModel):
    total_revenue: float
    avg_roi: float
    orders_count: int
    revenue_by_day: List[Dict[str, float]]
    revenue_growth_pct: float


@router.get("/", response_model=AggregateResponse)
async def get_aggregates(db: AsyncSession = Depends(get_db)) -> AggregateResponse:
    total_q = select(func.coalesce(func.sum(SaleORM.revenue), 0.0))
    count_q = select(func.count(SaleORM.id))
    by_day_q = (
        select(SaleORM.date, func.coalesce(func.sum(SaleORM.revenue), 0.0).label("sales"))
        .group_by(SaleORM.date)
        .order_by(SaleORM.date.asc())
        .limit(7)
    )

    total_sales = (await db.execute(total_q)).scalar_one()
    orders_count = (await db.execute(count_q)).scalar_one()
    by_day_res = await db.execute(by_day_q)
    by_day = [{"date": d, "sales": float(s)} for d, s in by_day_res.all()]

    avg_order_value = float(total_sales) / orders_count if orders_count else 0.0

    return AggregateResponse(
        total_sales=float(total_sales),
        avg_order_value=avg_order_value,
        orders_count=int(orders_count),
        by_day=by_day,
    )


@router.get("/aggregate", response_model=AggregateMetrics)
async def analytics_aggregate(db: AsyncSession = Depends(get_db)) -> AggregateMetrics:
    # Total revenue from sales
    total_rev_q = select(func.coalesce(func.sum(SaleORM.revenue), 0.0))
    total_revenue = float((await db.execute(total_rev_q)).scalar_one())

    # Average ROI across campaigns (simple arithmetic mean of ROI column)
    avg_roi_q = select(func.coalesce(func.avg(CampaignORM.roi), 0.0))
    avg_roi = float((await db.execute(avg_roi_q)).scalar_one())

    # Orders count (rows in sales)
    orders_count = int((await db.execute(select(func.count(SaleORM.id)))).scalar_one())

    # Revenue by day (last 7 days ascending)
    by_day_q = (
        select(SaleORM.date, func.coalesce(func.sum(SaleORM.revenue), 0.0).label("sales"))
        .group_by(SaleORM.date)
        .order_by(SaleORM.date.asc())
        .limit(7)
    )
    by_day_res = await db.execute(by_day_q)
    revenue_by_day = [{"date": d, "sales": float(s)} for d, s in by_day_res.all()]

    # Compute simple growth percent from first to last day
    if len(revenue_by_day) >= 2 and revenue_by_day[0]["sales"] > 0:
        first = revenue_by_day[0]["sales"]
        last = revenue_by_day[-1]["sales"]
        revenue_growth_pct = ((last - first) / first) * 100.0
    else:
        revenue_growth_pct = 0.0

    return AggregateMetrics(
        total_revenue=total_revenue,
        avg_roi=avg_roi,
        orders_count=orders_count,
        revenue_by_day=revenue_by_day,
        revenue_growth_pct=revenue_growth_pct,
    )


@router.get("/live")
async def analytics_live(
    window: str = "24h", db: AsyncSession = Depends(get_db)
) -> Dict[str, float | int]:
    """Return live summaries for the last 24h or last 7d.

    Assumes `SaleORM.date` is ISO date string (YYYY-MM-DD). For a production
    system using TIMESTAMP columns, switch to proper datetime comparisons.
    """
    now = datetime.utcnow()
    if window == "7d":
        start = (now - timedelta(days=7)).date().isoformat()
    else:  # default 24h
        start = (now - timedelta(days=1)).date().isoformat()

    # Filter sales by date >= start
    total_q = select(func.coalesce(func.sum(SaleORM.revenue), 0.0)).where(SaleORM.date >= start)
    count_q = select(func.count(SaleORM.id)).where(SaleORM.date >= start)

    total_revenue = float((await db.execute(total_q)).scalar_one())
    orders_count = int((await db.execute(count_q)).scalar_one())

    avg_order_value = total_revenue / orders_count if orders_count else 0.0

    return {
        "window": window,
        "since": start,
        "total_revenue": total_revenue,
        "orders_count": orders_count,
        "avg_order_value": avg_order_value,
    }


@router.get("/predict", response_model=PredictResponse)
async def get_prediction(horizon_days: int = 7, db: AsyncSession = Depends(get_db)) -> PredictResponse:
    # Use DB-backed regression model to produce forecast
    forecast = await linear_regression_forecast(db=db, horizon_days=horizon_days)

    # Confidence heuristic: inverse of coefficient of variation on recent 7 days
    # Recompute recent series for variability metric
    by_day_q = (
        select(SaleORM.date, func.coalesce(func.sum(SaleORM.revenue), 0.0).label("sales"))
        .group_by(SaleORM.date)
        .order_by(SaleORM.date.asc())
    )
    res = await db.execute(by_day_q)
    series = [{"date": d, "sales": float(s)} for d, s in res.all()]
    recent = [p["sales"] for p in series[-7:]] if series else []
    if len(recent) >= 2:
        mean = sum(recent) / len(recent)
        var = sum((x - mean) ** 2 for x in recent) / (len(recent) - 1)
        std = var ** 0.5
        cv = std / mean if mean else 1.0
        confidence = max(0.1, min(0.95, 1.0 / (1.0 + cv)))
    else:
        confidence = 0.5

    return PredictResponse(
        model="dummy-linear-regression",
        generated_at=datetime.utcnow(),
        horizon_days=horizon_days,
        forecast=forecast,
        confidence=confidence,
    )
