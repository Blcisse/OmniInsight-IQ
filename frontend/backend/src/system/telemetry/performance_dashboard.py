from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

try:
    import plotly.graph_objects as go  # type: ignore
except Exception:  # pragma: no cover
    go = None  # type: ignore


def generate_performance_overview(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Return a compact overview from aggregate metrics.

    Expects e.g.: { 'latency_ms': {'mean': .., 'p90': ..}, 'error_rate': {'mean': ..} }
    """
    overview = {}
    for k, v in metrics.items():
        if isinstance(v, dict):
            overview[k] = {m: float(x) for m, x in v.items() if isinstance(x, (int, float))}
    return overview


def visualize_api_latency_trends(df: pd.DataFrame, *, time_col: str = "ts", value_col: str = "latency_ms") -> Any:
    """Return a Plotly figure JSON string (if Plotly available) or a DataFrame dict."""
    df2 = df.copy()
    df2[time_col] = pd.to_datetime(df2[time_col])
    df2 = df2.sort_values(time_col)
    if go is None:
        return df2.to_dict(orient="records")
    fig = go.Figure(go.Scatter(x=df2[time_col], y=df2[value_col], mode="lines", name="latency"))
    fig.update_layout(title="API Latency Trends", xaxis_title="Time", yaxis_title="Latency (ms)", template="plotly_white")
    return fig.to_json()


def model_performance_heatmap(matrix: List[List[float]], x_labels: List[str], y_labels: List[str]) -> Any:
    """Return a Plotly heatmap JSON if Plotly is available; else raw dict."""
    if go is None:
        return {"matrix": matrix, "x": x_labels, "y": y_labels}
    fig = go.Figure(go.Heatmap(z=matrix, x=x_labels, y=y_labels, colorscale="Viridis"))
    fig.update_layout(title="Model Performance Heatmap", xaxis_title="Metric", yaxis_title="Model", template="plotly_white")
    return fig.to_json()

