from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.insightops import IoExecSummaryORM
from ..schemas.insightops_executive_brief import ExecutiveBriefResponse


def _infer_period(brief: ExecutiveBriefResponse, period_start: Optional[date], period_end: Optional[date]) -> tuple[date, date]:
    """Infer a reporting period from the brief window if not explicitly supplied."""
    end = period_end or brief.generated_at.date()
    start = period_start or (end - timedelta(days=brief.window_days))
    return start, end


def _compose_summary_text(brief: ExecutiveBriefResponse) -> str:
    """Create a deterministic paragraph from insights/risks/opportunities."""
    insights_part = "; ".join(insight.summary for insight in brief.insights) or "No insights captured."
    risks_part = (
        "; ".join(risk.description for risk in brief.risks)
        if brief.risks
        else "No risks identified."
    )
    opps_part = (
        "; ".join(opportunity.description for opportunity in brief.opportunities)
        if brief.opportunities
        else "No opportunities identified."
    )
    return f"Insights: {insights_part}. Risks: {risks_part}. Opportunities: {opps_part}."


async def save_exec_brief(
    db: AsyncSession,
    org_id: str,
    brief: ExecutiveBriefResponse,
    summary_type: str = "board",
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
) -> IoExecSummaryORM:
    start, end = _infer_period(brief, period_start, period_end)
    record = IoExecSummaryORM(
        org_id=org_id,
        summary_type=summary_type,
        period_start=start,
        period_end=end,
        summary_text=_compose_summary_text(brief),
        payload_json=brief.model_dump(),
        model_name=None,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_latest_exec_summary(
    db: AsyncSession,
    org_id: str,
    summary_type: str = "board",
    include_payload: bool = False,
) -> IoExecSummaryORM | None:
    stmt = (
        select(IoExecSummaryORM)
        .where(
            IoExecSummaryORM.org_id == org_id,
            IoExecSummaryORM.summary_type == summary_type,
        )
        .order_by(desc(IoExecSummaryORM.created_at))
        .limit(1)
    )
    result = await db.execute(stmt)
    record = result.scalars().first()
    if record and not include_payload:
        record.payload_json = None
    return record


async def list_exec_summaries(
    db: AsyncSession,
    org_id: str,
    summary_type: str = "board",
    limit: int = 20,
    include_payload: bool = False,
) -> list[IoExecSummaryORM]:
    stmt = (
        select(IoExecSummaryORM)
        .where(
            IoExecSummaryORM.org_id == org_id,
            IoExecSummaryORM.summary_type == summary_type,
        )
        .order_by(desc(IoExecSummaryORM.created_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    records = list(result.scalars().all())
    if not include_payload:
        for record in records:
            record.payload_json = None
    return records
