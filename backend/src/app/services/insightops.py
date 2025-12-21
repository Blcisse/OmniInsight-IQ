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
from .insightops_analytics import DEFAULT_LOOKBACK_DAYS, DEFAULT_ORG_ID
from .insightops_analytics.kpis import compute_kpi_delta as _compute_kpi_delta
from .insightops_analytics.kpis import get_kpi_series as _get_kpi_series
from .insightops_anomalies import get_anomalies as _get_anomalies
from .insightops_engagement import (
    aggregate_signals as _aggregate_signals,
    compute_engagement_health as _compute_engagement_health,
    get_signal_series as _get_signal_series,
)
from .insightops_interpretation.anomaly_interpreter import interpret_anomalies
from .insightops_interpretation.engagement_interpreter import interpret_engagement
from .insightops_interpretation.kpi_interpreter import interpret_kpi
from .insightops_interpretation.scoring import compute_priority_score

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


# Facade helpers expected by tests and router wrappers
async def get_kpi_series(
    db: AsyncSession,
    org_id: str = DEFAULT_ORG_ID,
    metric_key: str = "revenue",
    start_date: str | None = None,
    end_date: str | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
):
    return await _get_kpi_series(
        db=db,
        org_id=org_id,
        metric_key=metric_key,
        start_date=start_date,
        end_date=end_date,
        lookback_days=lookback_days,
    )


async def get_kpi_summary(
    db: AsyncSession,
    org_id: str = DEFAULT_ORG_ID,
    metric_key: str = "revenue",
    start_date: str | None = None,
    end_date: str | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
):
    series = await get_kpi_series(
        db=db,
        org_id=org_id,
        metric_key=metric_key,
        start_date=start_date,
        end_date=end_date,
        lookback_days=lookback_days,
    )
    return _compute_kpi_delta(series.points)


async def get_engagement_series(
    db: AsyncSession,
    org_id: str = DEFAULT_ORG_ID,
    signal_key: str = "touches",
    start_date: str | None = None,
    end_date: str | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
):
    return await _get_signal_series(
        db=db,
        org_id=org_id,
        signal_key=signal_key,
        start_date=start_date,
        end_date=end_date,
        lookback_days=lookback_days,
    )


async def get_engagement_summary(
    db: AsyncSession,
    org_id: str = DEFAULT_ORG_ID,
    signal_key: str = "touches",
    start_date: str | None = None,
    end_date: str | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
):
    series = await get_engagement_series(
        db=db,
        org_id=org_id,
        signal_key=signal_key,
        start_date=start_date,
        end_date=end_date,
        lookback_days=lookback_days,
    )
    aggregates = _aggregate_signals(series.points)
    health = _compute_engagement_health(series.points)
    return aggregates.model_copy(update={"health_score": health})


async def get_anomalies(
    db: AsyncSession,
    org_id: str = DEFAULT_ORG_ID,
    metric_key: str | None = "revenue",
    signal_key: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
):
    metric_to_use = None if signal_key else metric_key
    return await _get_anomalies(
        db=db,
        org_id=org_id,
        metric_key=metric_to_use,
        signal_key=signal_key,
        start_date=start_date,
        end_date=end_date,
        lookback_days=lookback_days,
    )


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


# Interpretation façades (service-layer only; no API changes)
async def get_interpreted_kpi_summary(
    db: AsyncSession,
    org_id: str = DEFAULT_ORG_ID,
    metric_key: str = "revenue",
    start_date: str | None = None,
    end_date: str | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
):
    base_summary = await get_kpi_summary(
        db=db,
        org_id=org_id,
        metric_key=metric_key,
        start_date=start_date,
        end_date=end_date,
        lookback_days=lookback_days,
    )
    interpretation = interpret_kpi(
        base_summary.latest_value,
        base_summary.previous_value,
        base_summary.percent_delta,
        base_summary.rolling_avg_7d_latest,
    )
    priority = compute_priority_score(
        kpi_sev=interpretation["severity"],
        engagement_sev=0,
        anomaly_sev=0,
    )
    return {"summary": base_summary, "interpretation": interpretation, "priority": priority}


async def get_interpreted_engagement_summary(
    db: AsyncSession,
    org_id: str = DEFAULT_ORG_ID,
    signal_key: str = "touches",
    start_date: str | None = None,
    end_date: str | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
):
    base_summary = await get_engagement_summary(
        db=db,
        org_id=org_id,
        signal_key=signal_key,
        start_date=start_date,
        end_date=end_date,
        lookback_days=lookback_days,
    )
    interpretation = interpret_engagement(
        base_summary.health_score,
        base_summary.average_per_day,
        base_summary.last_day_value,
    )
    priority = compute_priority_score(
        kpi_sev=0,
        engagement_sev=interpretation["severity"],
        anomaly_sev=0,
    )
    return {"summary": base_summary, "interpretation": interpretation, "priority": priority}


async def get_interpreted_anomaly_summary(
    db: AsyncSession,
    org_id: str = DEFAULT_ORG_ID,
    metric_key: str | None = "revenue",
    signal_key: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
):
    anomaly_response = await get_anomalies(
        db=db,
        org_id=org_id,
        metric_key=metric_key,
        signal_key=signal_key,
        start_date=start_date,
        end_date=end_date,
        lookback_days=lookback_days,
    )
    interpretation = interpret_anomalies(anomaly_response.anomalies)
    priority = compute_priority_score(
        kpi_sev=0,
        engagement_sev=0,
        anomaly_sev=interpretation["severity"],
    )
    return {"anomalies": anomaly_response, "interpretation": interpretation, "priority": priority}
