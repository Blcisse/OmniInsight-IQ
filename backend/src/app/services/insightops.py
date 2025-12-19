from __future__ import annotations

from datetime import date, timedelta
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.insightops import (
    IoEngagementSignalDailyORM,
    IoExecSummaryORM,
    IoKpiDailyORM,
)

DEFAULT_WINDOW_DAYS = 14


def resolve_date_window(
    start_date: date | None, end_date: date | None, window_days: int = DEFAULT_WINDOW_DAYS
) -> tuple[date, date]:
    """Return a safe date window, defaulting to a rolling period when params are missing."""
    effective_end = end_date or date.today()
    effective_start = start_date or (effective_end - timedelta(days=window_days))

    if effective_start > effective_end:
        raise ValueError("start_date cannot be after end_date")

    return effective_start, effective_end


async def fetch_kpis(
    db: AsyncSession,
    org_id: str,
    start_date: date | None,
    end_date: date | None,
    metric_key: str | None = None,
) -> Sequence[IoKpiDailyORM]:
    start, end = resolve_date_window(start_date, end_date)

    stmt = (
        select(IoKpiDailyORM)
        .where(
            IoKpiDailyORM.org_id == org_id,
            IoKpiDailyORM.kpi_date >= start,
            IoKpiDailyORM.kpi_date <= end,
        )
        .order_by(IoKpiDailyORM.kpi_date.asc(), IoKpiDailyORM.metric_key.asc())
    )

    if metric_key:
        stmt = stmt.where(IoKpiDailyORM.metric_key == metric_key)

    result = await db.execute(stmt)
    return result.scalars().all()


async def fetch_engagement_signals(
    db: AsyncSession,
    org_id: str,
    start_date: date | None,
    end_date: date | None,
    signal_key: str | None = None,
) -> Sequence[IoEngagementSignalDailyORM]:
    start, end = resolve_date_window(start_date, end_date)

    stmt = (
        select(IoEngagementSignalDailyORM)
        .where(
            IoEngagementSignalDailyORM.org_id == org_id,
            IoEngagementSignalDailyORM.signal_date >= start,
            IoEngagementSignalDailyORM.signal_date <= end,
        )
        .order_by(IoEngagementSignalDailyORM.signal_date.asc(), IoEngagementSignalDailyORM.signal_key.asc())
    )

    if signal_key:
        stmt = stmt.where(IoEngagementSignalDailyORM.signal_key == signal_key)

    result = await db.execute(stmt)
    return result.scalars().all()


async def fetch_exec_summaries(
    db: AsyncSession,
    org_id: str,
    period_start: date | None,
    period_end: date | None,
    summary_type: str | None = None,
) -> Sequence[IoExecSummaryORM]:
    start, end = resolve_date_window(period_start, period_end)

    stmt = (
        select(IoExecSummaryORM)
        .where(
            IoExecSummaryORM.org_id == org_id,
            IoExecSummaryORM.period_start >= start,
            IoExecSummaryORM.period_end <= end,
        )
        .order_by(IoExecSummaryORM.period_start.asc())
    )

    if summary_type:
        stmt = stmt.where(IoExecSummaryORM.summary_type == summary_type)

    result = await db.execute(stmt)
    return result.scalars().all()
