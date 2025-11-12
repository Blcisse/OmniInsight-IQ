from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Dict

import numpy as np
from sklearn.linear_model import LinearRegression
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.sales import SaleORM


async def linear_regression_forecast(
    db: AsyncSession, horizon_days: int = 7
) -> List[Dict[str, float]]:
    """Train a simple linear regression on daily revenue from the DB and forecast.

    - Aggregates sales revenue by day from PostgreSQL via AsyncSession
    - Fits scikit-learn LinearRegression on (day_index -> revenue)
    - Forecasts the next `horizon_days` points
    """
    # Load daily series from DB (ascending by date)
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

    y = np.array([v for _, v in series], dtype=float)
    X = np.arange(len(y)).reshape(-1, 1)

    model = LinearRegression()
    with np.errstate(all="ignore"):
        model.fit(X, y)

    # Forecast indices continue from last observed index
    last_idx = len(y) - 1
    future_idx = np.arange(last_idx + 1, last_idx + 1 + horizon_days).reshape(-1, 1)
    y_pred = model.predict(future_idx)

    # Start date = day after last observed date
    try:
        last_date = datetime.fromisoformat(series[-1][0]).date()
    except Exception:
        last_date = datetime.utcnow().date()
    start = last_date + timedelta(days=1)

    forecast: List[Dict[str, float]] = []
    for i, val in enumerate(y_pred.tolist()):
        forecast.append(
            {"date": (start + timedelta(days=i)).isoformat(), "predicted_sales": float(max(val, 0.0))}
        )

    return forecast
