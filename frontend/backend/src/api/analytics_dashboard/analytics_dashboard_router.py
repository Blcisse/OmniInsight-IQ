from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

try:
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None  # type: ignore

from .schemas import (
    ForecastSeriesInput,
    ClusterDistributionInput,
    ClusterVisualsInput,
    AnomalySeriesInput,
    AnomalySummaryInput,
    RecommendationScoresInput,
    RecommendationTrendsInput,
    HeatmapInput,
)

from src.visuals.analytics_dashboard.forecast_view import (
    recharts_forecast_series,
)
from src.visuals.analytics_dashboard.cluster_view import (
    recharts_cluster_distribution,
    get_cluster_visuals,
    generate_cluster_insights,
)
from src.visuals.analytics_dashboard.anomaly_view import (
    recharts_anomaly_series,
    anomaly_summary_plot,
)
from src.visuals.analytics_dashboard.recommendation_view import (
    recharts_item_scores,
    recharts_rec_trends,
    get_recommendation_heatmap,
)


router = APIRouter(prefix="/analytics-dashboard", tags=["Analytics Dashboard"])


@router.post("/forecast/series")
def forecast_series(payload: ForecastSeriesInput) -> Dict[str, Any]:
    try:
        if pd is None:
            raise RuntimeError("pandas not installed")
        history_df = pd.DataFrame.from_records(payload.history)
        return recharts_forecast_series(history_df, payload.date_col, payload.target_col, payload.forecast)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cluster/distribution")
def cluster_distribution(payload: ClusterDistributionInput) -> Dict[str, Any]:
    return recharts_cluster_distribution(payload.labels)


@router.post("/cluster/visuals")
def cluster_visuals(payload: ClusterVisualsInput) -> Dict[str, Any]:
    try:
        if pd is None:
            raise RuntimeError("pandas not installed")
        df = pd.DataFrame.from_records(payload.df)
        # Return Plotly JSON for now
        fig = get_cluster_visuals(
            cluster_id=payload.cluster_id,
            df=df,
            feature_cols=payload.feature_cols,
            labels=payload.labels,
            lib="plotly",
        )
        return {"figure": fig.to_json()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cluster/insights")
def cluster_insights(payload: ClusterVisualsInput) -> Dict[str, Any]:
    try:
        if pd is None:
            raise RuntimeError("pandas not installed")
        df = pd.DataFrame.from_records(payload.df)
        out = generate_cluster_insights(df=df, feature_cols=payload.feature_cols, labels=payload.labels)
        return out
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/anomaly/series")
def anomaly_series(payload: AnomalySeriesInput) -> Dict[str, Any]:
    try:
        if pd is None:
            raise RuntimeError("pandas not installed")
        history_df = pd.DataFrame.from_records(payload.history)
        anomalies_df = pd.DataFrame.from_records(payload.anomalies)
        return recharts_anomaly_series(history_df, payload.date_col, payload.value_col, anomalies_df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/anomaly/summary")
def anomaly_summary(payload: AnomalySummaryInput) -> Dict[str, Any]:
    try:
        if pd is None:
            raise RuntimeError("pandas not installed")
        anomalies_df = pd.DataFrame.from_records(payload.anomalies)
        # reuse summary plot to build recharts-friendly data
        data = anomaly_summary_plot(anomalies_df, date_col=payload.date_col, score_col=payload.score_col, lib="recharts")
        return {"series": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/recommendation/item-scores")
def recommendation_item_scores(payload: RecommendationScoresInput) -> Dict[str, Any]:
    try:
        return {"series": recharts_item_scores([(r.get("item"), float(r.get("score", 0))) for r in payload.recommendations])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/recommendation/trends")
def recommendation_trends(payload: RecommendationTrendsInput) -> Dict[str, Any]:
    try:
        if pd is None:
            raise RuntimeError("pandas not installed")
        df = pd.DataFrame.from_records(payload.df)
        return recharts_rec_trends(df, date_col=payload.date_col, metric_col=payload.metric_col, by_col=payload.by_col)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/recommendation/heatmap")
def recommendation_heatmap(payload: HeatmapInput) -> Dict[str, Any]:
    try:
        if pd is None:
            raise RuntimeError("pandas not installed")
        df = pd.DataFrame.from_records(payload.rows)
        vis = get_recommendation_heatmap(df, lib="recharts")
        return vis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

