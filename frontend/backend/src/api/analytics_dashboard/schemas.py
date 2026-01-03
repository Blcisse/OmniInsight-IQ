from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ForecastSeriesInput(BaseModel):
    history: List[Dict[str, Any]]
    forecast: List[Dict[str, Any]]
    date_col: str = "date"
    target_col: str = "target"


class ClusterDistributionInput(BaseModel):
    labels: List[int]


class ClusterVisualsInput(BaseModel):
    df: List[Dict[str, Any]]
    feature_cols: List[str]
    labels: List[int]
    cluster_id: int


class AnomalySeriesInput(BaseModel):
    history: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    date_col: str = "date"
    value_col: str = "value"


class AnomalySummaryInput(BaseModel):
    anomalies: List[Dict[str, Any]]
    date_col: str = "date"
    score_col: Optional[str] = None


class RecommendationScoresInput(BaseModel):
    recommendations: List[Dict[str, Any]]  # expects { item, score }


class RecommendationTrendsInput(BaseModel):
    df: List[Dict[str, Any]]
    date_col: str = "date"
    metric_col: str = "metric"
    by_col: Optional[str] = None


class HeatmapInput(BaseModel):
    rows: List[Dict[str, Any]]  # tabular records; build DataFrame

