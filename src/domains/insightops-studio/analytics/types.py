from __future__ import annotations

from datetime import date
from typing import List

from pydantic import BaseModel, ConfigDict


class DateWindow(BaseModel):
    start_date: date
    end_date: date

    model_config = ConfigDict(from_attributes=True)


class MetricSeriesPoint(BaseModel):
    date: date
    value: float

    model_config = ConfigDict(from_attributes=True)


class SeriesResponse(BaseModel):
    org_id: str
    key: str
    points: List[MetricSeriesPoint]

    model_config = ConfigDict(from_attributes=True)
