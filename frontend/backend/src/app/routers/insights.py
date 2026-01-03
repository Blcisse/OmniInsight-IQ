from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ...lib.mlModels.insightEngine import generate_insights


router = APIRouter(prefix="/api/insights", tags=["insights"])


class Insight(BaseModel):
    id: int
    title: str
    category: str
    recommendation: str
    impact: str
    confidence: float


_insights: List[Insight] = [
    Insight(
        id=1,
        title="Boost retargeting budget",
        category="marketing",
        recommendation="Increase retargeting spend by 15% on high-intent audience segments where ROAS > 4.0.",
        impact="high",
        confidence=0.86,
    ),
    Insight(
        id=2,
        title="Bundle accessories with laptops",
        category="sales",
        recommendation="Offer a 10% accessory bundle discount at checkout for laptop purchasers to raise AOV.",
        impact="medium",
        confidence=0.78,
    ),
    Insight(
        id=3,
        title="Improve mobile funnel",
        category="analytics",
        recommendation="Optimize mobile PDP load time and simplify checkout to reduce bounce rate by ~8%.",
        impact="medium",
        confidence=0.74,
    ),
]


@router.get("/", response_model=List[Insight])
def get_insights() -> List[Insight]:
    return _insights


@router.get("/aggregate")
async def get_combined_insights(
    horizon_days: int = 7, db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Return combined multi-layer recommendations from the insight engine."""
    return await generate_insights(db=db, horizon_days=horizon_days)
