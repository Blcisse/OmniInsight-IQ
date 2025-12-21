from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ExecutiveInsight(BaseModel):
    title: str
    summary: str
    severity: int
    category: str

    model_config = ConfigDict(from_attributes=True)


class ExecutiveRisk(BaseModel):
    title: str
    description: str
    severity: int
    mitigation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ExecutiveOpportunity(BaseModel):
    title: str
    description: str
    confidence: int

    model_config = ConfigDict(from_attributes=True)


class ExecutiveBriefResponse(BaseModel):
    org_id: str
    generated_at: datetime
    window_days: int
    priority_score: int
    priority_level: str
    insights: List[ExecutiveInsight]
    risks: List[ExecutiveRisk]
    opportunities: List[ExecutiveOpportunity]
    notes: List[str]
    saved: bool | None = None
    summary_id: str | None = None
    summary_type: str | None = None

    model_config = ConfigDict(from_attributes=True)
