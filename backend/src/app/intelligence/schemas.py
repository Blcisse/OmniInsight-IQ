from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SignalCorrelation(BaseModel):
    kpi_key: str
    signal_key: Optional[str] = None
    anomaly_key: Optional[str] = None
    correlation_score: float = Field(..., description="Signed strength between -1 and 1")
    confidence: float = Field(..., ge=0.0, le=1.0)


class PrimaryDriver(str, Enum):
    KPI_TREND = "KPI_TREND"
    ENGAGEMENT = "ENGAGEMENT"
    ANOMALY = "ANOMALY"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class DriverAttribution(BaseModel):
    primary_driver: PrimaryDriver = PrimaryDriver.UNKNOWN
    supporting_factors: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)


class PrioritizedInsight(BaseModel):
    title: str
    impact_score: int = Field(..., ge=0, le=100)
    urgency_score: int = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0.0, le=1.0)
    explainability_notes: List[str] = Field(default_factory=list)


class SynthesisBlock(BaseModel):
    situation: str
    evidence: str
    risk: str
    opportunity: str
    recommended_focus: str
