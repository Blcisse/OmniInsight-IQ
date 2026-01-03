from __future__ import annotations

from typing import Any, Dict, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from .regressionModel import linear_regression_forecast
from .clusteringModel import kmeans_segments, mock_customer_segments
from .anomalyDetection import detect_sales_anomalies


async def generate_insights(db: AsyncSession, horizon_days: int = 7) -> Dict[str, Any]:
    """Aggregate outputs from regression, clustering, and anomaly detection.

    Returns a combined payload with:
      - forecast: next N days predicted sales + model metadata
      - clusters: product-level clusters (fallback to mock if unavailable)
      - anomalies: detected sales anomalies from recent series
      - generated_at: ISO timestamp
    """
    # Forecast using DB-backed regression
    forecast = await linear_regression_forecast(db=db, horizon_days=horizon_days)

    # Clusters (product-level). If DB has no rows or sklearn missing, fall back.
    try:
        clusters = await kmeans_segments(db=db, n_clusters=4, entity="product")
    except Exception:
        clusters = mock_customer_segments()

    # Anomalies from mock analytics.json if available; tolerate failure
    try:
        anomalies = detect_sales_anomalies()
    except Exception:
        anomalies = []

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "forecast": forecast,
        "clusters": clusters,
        "anomalies": anomalies,
        "meta": {
            "horizon_days": horizon_days,
            "models": [
                "linear_regression_forecast",
                "kmeans_segments",
                "detect_sales_anomalies",
            ],
        },
    }

