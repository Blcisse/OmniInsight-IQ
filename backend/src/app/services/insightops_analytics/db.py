from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .constants import ALLOWED_KPI_KEYS, ALLOWED_SIGNAL_KEYS


async def fetch_kpi_series(
    db: AsyncSession,
    org_id: str,
    metric_key: str,
    start_date: date,
    end_date: date,
) -> List[Dict[str, Any]]:
    if metric_key not in ALLOWED_KPI_KEYS:
        raise ValueError(f"Unsupported metric_key '{metric_key}'. Allowed: {sorted(ALLOWED_KPI_KEYS)}")

    stmt = text(
        """
        SELECT kpi_date AS date, metric_value AS value
        FROM io_kpi_daily
        WHERE org_id = :org_id
          AND metric_key = :metric_key
          AND kpi_date BETWEEN :start_date AND :end_date
        ORDER BY kpi_date ASC
        """
    )
    result = await db.execute(
        stmt,
        {
            "org_id": org_id,
            "metric_key": metric_key,
            "start_date": start_date,
            "end_date": end_date,
        },
    )
    return [dict(row) for row in result.mappings().all()]


async def fetch_signal_series(
    db: AsyncSession,
    org_id: str,
    signal_key: str,
    start_date: date,
    end_date: date,
) -> List[Dict[str, Any]]:
    if signal_key not in ALLOWED_SIGNAL_KEYS:
        raise ValueError(f"Unsupported signal_key '{signal_key}'. Allowed: {sorted(ALLOWED_SIGNAL_KEYS)}")

    stmt = text(
        """
        SELECT signal_date AS date, signal_value AS value
        FROM io_engagement_signal_daily
        WHERE org_id = :org_id
          AND signal_key = :signal_key
          AND signal_date BETWEEN :start_date AND :end_date
        ORDER BY signal_date ASC
        """
    )
    result = await db.execute(
        stmt,
        {
            "org_id": org_id,
            "signal_key": signal_key,
            "start_date": start_date,
            "end_date": end_date,
        },
    )
    return [dict(row) for row in result.mappings().all()]
