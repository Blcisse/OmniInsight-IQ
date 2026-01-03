from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..models.marketing import CampaignORM, ConversionORM


router = APIRouter(prefix="/api/marketing", tags=["marketing"])


class CampaignMetric(BaseModel):
    id: int
    campaign_name: str
    channel: str
    budget: float
    spend: float
    impressions: int
    clicks: int
    roi: float


class ConversionDatum(BaseModel):
    campaign_id: int
    date: str
    conversions: int
    revenue: float


@router.get("/campaign-metrics", response_model=List[CampaignMetric])
async def get_campaign_metrics(
    channel: Optional[str] = None,
    min_roi: Optional[float] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> List[CampaignMetric]:
    stmt = select(CampaignORM)
    conditions = []
    if channel:
        conditions.append(CampaignORM.channel == channel)
    if min_roi is not None:
        conditions.append(CampaignORM.roi >= min_roi)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.order_by(CampaignORM.id.asc()).limit(limit).offset(offset)
    res = await db.execute(stmt)
    rows = res.scalars().all()
    return [
        CampaignMetric(
            id=r.id,
            campaign_name=r.campaign_name,
            channel=r.channel,
            budget=r.budget,
            spend=r.spend,
            impressions=r.impressions,
            clicks=r.clicks,
            roi=r.roi,
        )
        for r in rows
    ]


@router.get("/conversions", response_model=List[ConversionDatum])
async def get_conversions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> List[ConversionDatum]:
    stmt = select(ConversionORM)
    conditions = []
    if start_date:
        conditions.append(ConversionORM.date >= start_date)
    if end_date:
        conditions.append(ConversionORM.date <= end_date)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.order_by(ConversionORM.date.asc()).limit(limit).offset(offset)
    res = await db.execute(stmt)
    rows = res.scalars().all()
    return [
        ConversionDatum(
            campaign_id=r.campaign_id,
            date=r.date,
            conversions=r.conversions,
            revenue=r.revenue,
        )
        for r in rows
    ]
