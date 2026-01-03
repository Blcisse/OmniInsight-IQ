from __future__ import annotations

from typing import List, Dict, Any

from ...core.utils import load_mock_data


def detect_sales_anomalies(threshold: float = 2.0) -> List[Dict[str, Any]]:
    """Simulate anomaly detection over sales time series.

    Loads `analytics.json` by_day sales, computes mean and std, and flags days
    where |value - mean| > threshold * std as anomalies. If std is 0 or data
    is insufficient, returns an empty list.
    """
    data = load_mock_data("analytics.json")
    series = data.get("by_day", [])
    values = [float(p.get("sales", 0.0)) for p in series]

    if len(values) < 3:
        return []

    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    std = var ** 0.5

    if std == 0:
        return []

    anomalies: List[Dict[str, Any]] = []
    for point in series:
        val = float(point.get("sales", 0.0))
        z = abs(val - mean) / std if std else 0.0
        if z > threshold:
            anomalies.append({
                "date": point.get("date"),
                "sales": val,
                "z_score": z,
                "mean": mean,
                "std": std,
                "threshold": threshold,
            })

    return anomalies

