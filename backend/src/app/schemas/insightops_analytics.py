from __future__ import annotations

from datetime import date
from typing import List

from pydantic import BaseModel, ConfigDict


class SeriesPoint(BaseModel):
    date: date
    value: float

    model_config = ConfigDict(from_attributes=True)


class SeriesResponse(BaseModel):
    org_id: str
    key: str
    start_date: date
    end_date: date
    points: List[SeriesPoint]

    model_config = ConfigDict(from_attributes=True)


class DeltaSummary(BaseModel):
    latest_value: float | None
    previous_value: float | None
    absolute_delta: float | None
    percent_delta: float | None
    rolling_avg_7d_latest: float | None


class EngagementSummary(BaseModel):
    total: float
    average_per_day: float
    last_day_value: float | None
    health_score: float


class Anomaly(BaseModel):
    type: str
    severity: str
    description: str
    date: date

    model_config = ConfigDict(from_attributes=True)


class AnomalyResponse(BaseModel):
    org_id: str
    anomalies: List[Anomaly]

    model_config = ConfigDict(from_attributes=True)
