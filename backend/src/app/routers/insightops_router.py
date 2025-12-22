from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..services import (
    insightops_analytics,
    insightops_anomalies,
    insightops_engagement,
    insightops_executive_brief,
)
from ..services import insightops_exec_persistence as exec_persistence
from ..services.insightops import fetch_engagement_signals, fetch_kpis
from ..schemas.insightops_analytics import Anomaly, AnomalyResponse, DeltaSummary, EngagementSummary, SeriesResponse
from ..schemas.insightops_executive_brief import ExecutiveBriefResponse

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
    payload_json: dict | None = None
    model_name: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


@router.get("/health")
async def insightops_health() -> dict:
    return {"domain": "insightops-studio", "status": "ok"}


@router.get("/kpis", response_model=list[KpiDaily])
async def list_kpis(
    org_id: str = Query(
        insightops_analytics.DEFAULT_ORG_ID, description="Organization identifier to filter KPIs"
    ),
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


@router.get("/engagement", response_model=list[EngagementSignalDaily])
async def list_engagement_signals(
    org_id: str = Query(
        insightops_analytics.DEFAULT_ORG_ID, description="Organization identifier to filter engagement signals"
    ),
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


@router.get("/analytics/kpis/series", response_model=SeriesResponse)
async def kpi_series(
    org_id: str = Query(
        insightops_analytics.DEFAULT_ORG_ID, description="Organization identifier to filter KPIs"
    ),
    metric_key: str = Query("revenue", description="KPI metric key"),
    start_date: str | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    lookback_days: int = Query(
        insightops_analytics.DEFAULT_LOOKBACK_DAYS, description="Lookback window if dates not provided"
    ),
    db: AsyncSession = Depends(get_db),
) -> SeriesResponse:
    try:
        series = await insightops_analytics.get_kpi_series(
            db=db,
            org_id=org_id or insightops_analytics.DEFAULT_ORG_ID,
            metric_key=metric_key,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return series


@router.get("/analytics/kpis/summary", response_model=DeltaSummary)
async def kpi_summary(
    org_id: str = Query(
        insightops_analytics.DEFAULT_ORG_ID, description="Organization identifier to filter KPIs"
    ),
    metric_key: str = Query("revenue", description="KPI metric key"),
    start_date: str | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    lookback_days: int = Query(
        insightops_analytics.DEFAULT_LOOKBACK_DAYS, description="Lookback window if dates not provided"
    ),
    db: AsyncSession = Depends(get_db),
) -> DeltaSummary:
    try:
        series = await insightops_analytics.get_kpi_series(
            db=db,
            org_id=org_id or insightops_analytics.DEFAULT_ORG_ID,
            metric_key=metric_key,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return insightops_analytics.compute_kpi_delta(series.points)


@router.get("/analytics/engagement/series", response_model=SeriesResponse)
async def engagement_series(
    org_id: str = Query(
        insightops_analytics.DEFAULT_ORG_ID, description="Organization identifier to filter engagement signals"
    ),
    signal_key: str = Query("touches", description="Engagement signal key"),
    start_date: str | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    lookback_days: int = Query(
        insightops_analytics.DEFAULT_LOOKBACK_DAYS, description="Lookback window if dates not provided"
    ),
    db: AsyncSession = Depends(get_db),
) -> SeriesResponse:
    try:
        series = await insightops_engagement.get_signal_series(
            db=db,
            org_id=org_id or insightops_analytics.DEFAULT_ORG_ID,
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
    org_id: str = Query(
        insightops_analytics.DEFAULT_ORG_ID, description="Organization identifier to filter engagement signals"
    ),
    signal_key: str = Query("touches", description="Engagement signal key"),
    start_date: str | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    lookback_days: int = Query(
        insightops_analytics.DEFAULT_LOOKBACK_DAYS, description="Lookback window if dates not provided"
    ),
    db: AsyncSession = Depends(get_db),
) -> EngagementSummary:
    try:
        series = await insightops_engagement.get_signal_series(
            db=db,
            org_id=org_id or insightops_analytics.DEFAULT_ORG_ID,
            signal_key=signal_key,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    aggregates = insightops_engagement.aggregate_signals(series.points)
    health = insightops_engagement.compute_engagement_health(series.points)

    return EngagementSummary(
        total=aggregates.total,
        average_per_day=aggregates.average_per_day,
        last_day_value=aggregates.last_day_value,
        health_score=health,
    )


@router.get("/analytics/anomalies", response_model=AnomalyResponse)
async def analytics_anomalies(
    org_id: str = Query(
        insightops_analytics.DEFAULT_ORG_ID, description="Organization identifier"
    ),
    metric_key: str | None = Query("revenue", description="Optional KPI metric key to analyze"),
    signal_key: str | None = Query(None, description="Optional engagement signal key to analyze (overrides metric_key)"),
    start_date: str | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    lookback_days: int = Query(
        insightops_analytics.DEFAULT_LOOKBACK_DAYS, description="Lookback window if dates not provided"
    ),
    db: AsyncSession = Depends(get_db),
) -> AnomalyResponse:
    metric_to_use = None if signal_key else metric_key
    try:
        anomalies = await insightops_anomalies.get_anomalies(
            db=db,
            org_id=org_id or insightops_analytics.DEFAULT_ORG_ID,
            metric_key=metric_to_use,
            signal_key=signal_key,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return anomalies


@router.get("/executive-brief", response_model=ExecutiveBriefResponse)
async def executive_brief(
    org_id: str = Query(
        insightops_analytics.DEFAULT_ORG_ID, description="Organization identifier for the executive brief"
    ),
    window_days: int = Query(
        insightops_analytics.DEFAULT_LOOKBACK_DAYS, description="Rolling window (days) used for summaries"
    ),
    persist: bool = Query(False, description="Persist the generated brief to io_exec_summary"),
    summary_type: str = Query("board", description="Summary type label to persist"),
    db: AsyncSession = Depends(get_db),
) -> ExecutiveBriefResponse:
    try:
        brief = await insightops_executive_brief.build_executive_brief(
            db=db,
            org_id=org_id or insightops_analytics.DEFAULT_ORG_ID,
            window_days=window_days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if persist:
        record = await exec_persistence.save_exec_brief(
            db=db,
            org_id=org_id or insightops_analytics.DEFAULT_ORG_ID,
            brief=brief,
            summary_type=summary_type,
        )
        return brief.model_copy(update={"saved": True, "summary_id": str(record.id), "summary_type": summary_type})

    return brief


@router.get("/executive-summaries/latest", response_model=ExecSummary)
async def latest_executive_summary(
    org_id: str = Query(
        insightops_analytics.DEFAULT_ORG_ID, description="Organization identifier to filter summaries"
    ),
    summary_type: str = Query("board", description="Summary type label"),
    include_payload: bool = Query(False, description="Include stored payload_json if available"),
    db: AsyncSession = Depends(get_db),
) -> ExecSummary:
    record = await exec_persistence.get_latest_exec_summary(
        db=db,
        org_id=org_id or insightops_analytics.DEFAULT_ORG_ID,
        summary_type=summary_type,
        include_payload=include_payload,
    )
    if not record:
        raise HTTPException(status_code=404, detail="No executive summaries found")
    return record


@router.get("/executive-summaries", response_model=list[ExecSummary])
async def list_executive_summaries(
    org_id: str = Query(
        insightops_analytics.DEFAULT_ORG_ID, description="Organization identifier to filter summaries"
    ),
    summary_type: str = Query("board", description="Summary type label"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of summaries to return"),
    include_payload: bool = Query(False, description="Include stored payload_json if available"),
    db: AsyncSession = Depends(get_db),
) -> list[ExecSummary]:
    records = await exec_persistence.list_exec_summaries(
        db=db,
        org_id=org_id or insightops_analytics.DEFAULT_ORG_ID,
        summary_type=summary_type,
        limit=limit,
        include_payload=include_payload,
    )
    return records
