from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from pathlib import Path

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..models.sales import SaleORM
from ..models.marketing import CampaignORM
from ...lib.mlModels.regressionModel import linear_regression_forecast


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def get_processed_data_path() -> Optional[Path]:
    """Get path to processed data, returns None if not available."""
    try:
        base_dir = Path(__file__).parent.parent.parent.parent.parent
        processed_path = base_dir / "data" / "processed" / "food_analytics_summary.json"
        if processed_path.exists():
            return processed_path
    except Exception:
        pass
    return None


def get_fallback_analytics() -> Dict:
    """Get fallback analytics from processed food data if database is empty."""
    import json
    summary_path = get_processed_data_path()
    if summary_path:
        try:
            with open(summary_path) as f:
                summary = json.load(f)
            # Convert food data metrics to sales-like format for compatibility
            return {
                "total_sales": summary.get("avg_calories", 0) * summary.get("total_foods", 0) * 0.1,  # Mock conversion
                "avg_order_value": summary.get("avg_calories", 0) * 0.1,
                "orders_count": summary.get("total_foods", 0),
                "by_day": [
                    {"date": (datetime.now() - timedelta(days=i)).date().isoformat(), "sales": summary.get("avg_calories", 0) * 10}
                    for i in range(6, -1, -1)
                ],
            }
        except Exception:
            pass
    return {
        "total_sales": 0.0,
        "avg_order_value": 0.0,
        "orders_count": 0,
        "by_day": [],
    }


class AggregateResponse(BaseModel):
    total_sales: float
    avg_order_value: float
    orders_count: int
    by_day: List[Dict[str, float]]


class PredictResponse(BaseModel):
    model: str
    generated_at: datetime
    horizon_days: int
    forecast: List[float]
    confidence: float


class AggregateMetrics(BaseModel):
    total_revenue: float
    avg_roi: float
    orders_count: int
    revenue_by_day: List[Dict[str, float]]
    revenue_growth_pct: float


@router.get("/", response_model=AggregateResponse)
async def get_aggregates(
    use_processed: bool = Query(False, description="Use processed data as fallback"),
    db: AsyncSession = Depends(get_db)
) -> AggregateResponse:
    """Get aggregate analytics. Falls back to processed data if database is empty and use_processed=true."""
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

    # Use processed data fallback if database is empty and flag is set
    if use_processed and (orders_count == 0 or total_sales == 0):
        fallback = get_fallback_analytics()
        return AggregateResponse(
            total_sales=fallback["total_sales"],
            avg_order_value=fallback["avg_order_value"],
            orders_count=fallback["orders_count"],
            by_day=fallback["by_day"],
        )

    avg_order_value = float(total_sales) / orders_count if orders_count else 0.0

    return AggregateResponse(
        total_sales=float(total_sales),
        avg_order_value=avg_order_value,
        orders_count=int(orders_count),
        by_day=by_day,
    )


@router.get("/aggregate", response_model=AggregateMetrics)
async def analytics_aggregate(
    use_processed: bool = Query(False, description="Use processed data as fallback"),
    db: AsyncSession = Depends(get_db)
) -> AggregateMetrics:
    """Get aggregate metrics. Falls back to processed data if database is empty and use_processed=true."""
    # Total revenue from sales
    total_rev_q = select(func.coalesce(func.sum(SaleORM.revenue), 0.0))
    total_revenue = float((await db.execute(total_rev_q)).scalar_one())

    # Average ROI across campaigns (simple arithmetic mean of ROI column)
    avg_roi_q = select(func.coalesce(func.avg(CampaignORM.roi), 0.0))
    avg_roi = float((await db.execute(avg_roi_q)).scalar_one())

    # Orders count (rows in sales)
    orders_count = int((await db.execute(select(func.count(SaleORM.id)))).scalar_one())

    # Use processed data fallback if database is empty
    if use_processed and orders_count == 0:
        fallback = get_fallback_analytics()
        return AggregateMetrics(
            total_revenue=fallback["total_sales"],
            avg_roi=0.0,
            orders_count=fallback["orders_count"],
            revenue_by_day=fallback["by_day"],
            revenue_growth_pct=5.0,  # Mock growth
        )

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
    window: str = "24h",
    use_processed: bool = Query(False, description="Use processed data as fallback"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, float | int]:
    """Get live analytics metrics.
    
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

    # Use processed data fallback if database is empty
    if use_processed and orders_count == 0:
        fallback = get_fallback_analytics()
        return {
            "window": window,
            "since": start,
            "total_revenue": fallback["total_sales"],
            "orders_count": fallback["orders_count"],
            "avg_order_value": fallback["avg_order_value"],
        }

    avg_order_value = total_revenue / orders_count if orders_count else 0.0

    return {
        "window": window,
        "since": start,
        "total_revenue": total_revenue,
        "orders_count": orders_count,
        "avg_order_value": avg_order_value,
    }


@router.get("/predict", response_model=PredictResponse)
async def get_prediction(
    horizon_days: int = 7,
    use_processed: bool = Query(False, description="Use processed data for forecast"),
    db: AsyncSession = Depends(get_db)
) -> PredictResponse:
    """Use DB-backed regression model to produce forecast."""
    # Fetch recent sales data
    sales_q = (
        select(SaleORM.date, SaleORM.revenue)
        .order_by(SaleORM.date.desc())
        .limit(30)
    )
    sales_res = await db.execute(sales_q)
    sales_rows = [(d, float(r)) for d, r in sales_res.all()]

    # Use processed data if database is empty and flag is set
    if use_processed and len(sales_rows) == 0:
        fallback = get_fallback_analytics()
        # Create mock sales data from processed food data
        sales_rows = fallback["by_day"]

    if len(sales_rows) < 2:
        # Return empty forecast if insufficient data
        return PredictResponse(
            model="linear_regression",
            generated_at=datetime.utcnow(),
            horizon_days=horizon_days,
            forecast=[0.0] * horizon_days,
            confidence=0.0,
        )

    # Prepare data for forecasting
    dates = [row[0] for row in sales_rows]
    values = [row[1] for row in sales_rows]

    # Run forecast
    forecast_values, confidence = linear_regression_forecast(
        dates=dates,
        values=values,
        horizon_days=horizon_days,
    )

    return PredictResponse(
        model="linear_regression",
        generated_at=datetime.utcnow(),
        horizon_days=horizon_days,
        forecast=forecast_values,
        confidence=confidence,
    )
