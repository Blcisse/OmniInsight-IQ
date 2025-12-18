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

router = APIRouter(prefix="/insightops", tags=["InsightOps"])
DEFAULT_ORG_ID = "demo_org"


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
from fastapi import APIRouter


router = APIRouter(prefix="/insightops", tags=["InsightOps"])


@router.get("/health")
async def insightops_health() -> dict:
    return {"domain": "insightops-studio", "status": "ok"}


@router.get("/kpis", response_model=list[KpiDaily])
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


@router.get("/engagement", response_model=list[EngagementSignalDaily])
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


@router.get("/executive-summaries", response_model=list[ExecSummary])
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
