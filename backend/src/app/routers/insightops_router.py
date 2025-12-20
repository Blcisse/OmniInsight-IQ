from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..services.insightops import (
    fetch_engagement_signals,
    fetch_exec_summaries,
    fetch_kpis,
)
from ..schemas.insightops_analytics import (
    Anomaly,
    AnomalyResponse,
    DeltaSummary,
    EngagementSummary,
    SeriesResponse,
)
from ..services.insightops_analytics import DEFAULT_LOOKBACK_DAYS, DEFAULT_ORG_ID, compute_kpi_delta, get_kpi_series
from ..services.insightops_engagement import aggregate_signals, compute_engagement_health, get_signal_series
from ..services.insightops_anomalies import get_anomalies

router = APIRouter(prefix="/insightops", tags=["InsightOps"])


class KpiDaily(BaseModel):
    id: UUID
    kpi_date: date
    org_id: str
    metric_key: str
    metric_value: float
    metric_unit: str | None = None
    region: str | None = None
    segment: str | None = None
    channel: str | None = None
    product: str | None = None
    source: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class EngagementSignalDaily(BaseModel):
    id: UUID
    signal_date: date
    org_id: str
    signal_key: str
    signal_value: float
    region: str | None = None
    segment: str | None = None
    channel: str | None = None
    product: str | None = None
    source: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ExecSummary(BaseModel):
    id: UUID
    period_start: date
    period_end: date
    org_id: str
    summary_type: str
    summary_text: str
    model_name: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


@router.get("/health")
async def insightops_health() -> dict:
    return {"domain": "insightops-studio", "status": "ok"}


@router.get("/analytics/kpis/summary", response_model=list[KpiDaily])
async def list_kpis(
    org_id: str = Query(DEFAULT_ORG_ID, description="Organization identifier to filter KPIs"),
    start_date: date | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    metric_key: str | None = Query(None, description="Filter to a single KPI metric_key"),
    db: AsyncSession = Depends(get_db),
) -> list[KpiDaily]:
    try:
        records = await fetch_kpis(db, org_id=org_id, start_date=start_date, end_date=end_date, metric_key=metric_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return records


@router.get("/analytics/engagement/signals", response_model=list[EngagementSignalDaily])
async def list_engagement_signals(
    org_id: str = Query(DEFAULT_ORG_ID, description="Organization identifier to filter engagement signals"),
    start_date: date | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    signal_key: str | None = Query(None, description="Filter to a single engagement signal_key"),
    db: AsyncSession = Depends(get_db),
) -> list[EngagementSignalDaily]:
    try:
        records = await fetch_engagement_signals(
            db, org_id=org_id, start_date=start_date, end_date=end_date, signal_key=signal_key
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return records


@router.get("/analytics/executive-summaries", response_model=list[ExecSummary])
async def list_executive_summaries(
    org_id: str = Query(DEFAULT_ORG_ID, description="Organization identifier to filter summaries"),
    period_start: date | None = Query(None, description="Inclusive start of summary period (YYYY-MM-DD)"),
    period_end: date | None = Query(None, description="Inclusive end of summary period (YYYY-MM-DD)"),
    summary_type: str | None = Query(None, description="Optional summary type (e.g., manager, board)"),
    db: AsyncSession = Depends(get_db),
) -> list[ExecSummary]:
    try:
        records = await fetch_exec_summaries(
            db,
            org_id=org_id,
            period_start=period_start,
            period_end=period_end,
            summary_type=summary_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return records


@router.get("/analytics/kpis/series", response_model=SeriesResponse)
async def kpi_series(
    org_id: str = Query(DEFAULT_ORG_ID, description="Organization identifier to filter KPIs"),
    metric_key: str = Query("revenue", description="KPI metric key"),
    start_date: str | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    lookback_days: int = Query(DEFAULT_LOOKBACK_DAYS, description="Lookback window if dates not provided"),
    db: AsyncSession = Depends(get_db),
) -> SeriesResponse:
    try:
        series = await get_kpi_series(
            db=db,
            org_id=org_id or DEFAULT_ORG_ID,
            metric_key=metric_key,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return series


@router.get("/analytics/kpis/delta", response_model=DeltaSummary)
async def kpi_summary(
    org_id: str = Query(DEFAULT_ORG_ID, description="Organization identifier to filter KPIs"),
    metric_key: str = Query("revenue", description="KPI metric key"),
    start_date: str | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    lookback_days: int = Query(DEFAULT_LOOKBACK_DAYS, description="Lookback window if dates not provided"),
    db: AsyncSession = Depends(get_db),
) -> DeltaSummary:
    try:
        series = await get_kpi_series(
            db=db,
            org_id=org_id or DEFAULT_ORG_ID,
            metric_key=metric_key,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return compute_kpi_delta(series.points)


@router.get("/analytics/engagement/series", response_model=SeriesResponse)
async def engagement_series(
    org_id: str = Query(DEFAULT_ORG_ID, description="Organization identifier to filter engagement signals"),
    signal_key: str = Query("touches", description="Engagement signal key"),
    start_date: str | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    lookback_days: int = Query(DEFAULT_LOOKBACK_DAYS, description="Lookback window if dates not provided"),
    db: AsyncSession = Depends(get_db),
) -> SeriesResponse:
    try:
        series = await get_signal_series(
            db=db,
            org_id=org_id or DEFAULT_ORG_ID,
            signal_key=signal_key,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return series


@router.get("/analytics/engagement/summary", response_model=EngagementSummary)
async def engagement_summary(
    org_id: str = Query(DEFAULT_ORG_ID, description="Organization identifier to filter engagement signals"),
    signal_key: str = Query("touches", description="Engagement signal key"),
    start_date: str | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    lookback_days: int = Query(DEFAULT_LOOKBACK_DAYS, description="Lookback window if dates not provided"),
    db: AsyncSession = Depends(get_db),
) -> EngagementSummary:
    try:
        series = await get_signal_series(
            db=db,
            org_id=org_id or DEFAULT_ORG_ID,
            signal_key=signal_key,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    aggregates = aggregate_signals(series.points)
    health = compute_engagement_health(series.points)

    return EngagementSummary(
        total=aggregates.total,
        average_per_day=aggregates.average_per_day,
        last_day_value=aggregates.last_day_value,
        health_score=health,
    )


@router.get("/analytics/anomalies", response_model=AnomalyResponse)
async def analytics_anomalies(
    org_id: str = Query(DEFAULT_ORG_ID, description="Organization identifier"),
    metric_key: str | None = Query("revenue", description="Optional KPI metric key to analyze"),
    signal_key: str | None = Query(None, description="Optional engagement signal key to analyze (overrides metric_key)"),
    start_date: str | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    lookback_days: int = Query(DEFAULT_LOOKBACK_DAYS, description="Lookback window if dates not provided"),
    db: AsyncSession = Depends(get_db),
) -> AnomalyResponse:
    metric_to_use = None if signal_key else metric_key
    try:
        anomalies = await get_anomalies(
            db=db,
            org_id=org_id or DEFAULT_ORG_ID,
            metric_key=metric_to_use,
            signal_key=signal_key,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return anomalies
