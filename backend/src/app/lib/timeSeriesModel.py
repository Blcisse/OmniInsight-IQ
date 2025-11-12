from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Dict, Optional

import math
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.sales import SaleORM


async def arima_like_forecast(
    db: AsyncSession,
    horizon_days: int = 7,
    seasonality: Optional[int] = 7,
) -> List[Dict[str, float]]:
    """Lightweight ARIMA/Prophet-style mock forecaster over daily revenue.

    This is a simplified time-series model intended for environments where
    heavyweight deps (statsmodels/prophet) are not available. It:
      - Aggregates revenue by day (ascending)
      - Computes a baseline trend using simple moving average
      - Adds a seasonal component using the last full season if available
      - Extends the series for `horizon_days`
    """
    # Load daily revenue series
    by_day_q = (
        select(SaleORM.date, func.coalesce(func.sum(SaleORM.revenue), 0.0).label("sales"))
        .group_by(SaleORM.date)
        .order_by(SaleORM.date.asc())
    )
    res = await db.execute(by_day_q)
    series = [(d, float(s)) for d, s in res.all()]

    if not series:
        start = datetime.utcnow().date() + timedelta(days=1)
        return [
            {"date": (start + timedelta(days=i)).isoformat(), "predicted_sales": 0.0}
            for i in range(horizon_days)
        ]

    values = [v for _, v in series]
    n = len(values)

    # Trend via simple moving average over min(7, n)
    win = min(7, n)
    def sma(idx: int) -> float:
        start = max(0, idx - win + 1)
        window = values[start: idx + 1]
        return sum(window) / len(window)

    trend = [sma(i) for i in range(n)]

    # Seasonal component: last `seasonality` residuals (if available)
    seasonal = [0.0] * n
    if seasonality and n > seasonality:
        residuals = [values[i] - trend[i] for i in range(n)]
        last_season = residuals[-seasonality:]
    else:
        last_season = [0.0] * (seasonality or 0)

    # Forecast future points using last trend slope and repeating seasonality
    try:
        last_date = datetime.fromisoformat(series[-1][0]).date()
    except Exception:
        last_date = datetime.utcnow().date()

    # Approximate slope from last two trend points
    slope = 0.0
    if n >= 2:
        slope = (trend[-1] - trend[-2])

    forecast: List[Dict[str, float]] = []
    for i in range(horizon_days):
        # linear trend extension
        base = trend[-1] + (i + 1) * slope
        # add repeating seasonal residual pattern
        seas = last_season[i % len(last_season)] if last_season else 0.0
        value = max(base + seas, 0.0)
        forecast.append({
            "date": (last_date + timedelta(days=i + 1)).isoformat(),
            "predicted_sales": float(value),
        })

    return forecast

