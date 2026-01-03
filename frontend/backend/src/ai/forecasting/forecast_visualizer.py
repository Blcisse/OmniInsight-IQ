from __future__ import annotations

from typing import List, Dict, Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_forecast(
    history: pd.DataFrame,
    date_col: str,
    target_col: str,
    forecast: List[Dict[str, float]],
    *,
    title: Optional[str] = None,
) -> go.Figure:
    """Interactive Plotly visualization combining history and forecast.

    Returns a Plotly Figure object suitable for embedding in notebooks or apps.
    """
    df = history[[date_col, target_col]].dropna().copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[target_col],
            mode="lines",
            name="History",
        )
    )

    if forecast:
        f_dates = [pd.to_datetime(f["date"]) for f in forecast]
        f_vals = [f["prediction"] for f in forecast]
        fig.add_trace(
            go.Scatter(
                x=f_dates,
                y=f_vals,
                mode="lines",
                line=dict(dash="dash"),
                name="Forecast",
            )
        )

    fig.update_layout(
        title=title or "Forecast",
        xaxis_title="Date",
        yaxis_title=target_col,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=50, b=40),
    )

    return fig


def plot_forecast_trends(
    metric: str,
    history: pd.DataFrame,
    date_col: str,
    *,
    rolling: Optional[int] = 7,
    title: Optional[str] = None,
) -> go.Figure:
    """Plot historical trends for a given metric with optional rolling mean.

    - metric: column name to plot from `history`
    - history: DataFrame with at least [date_col, metric]
    - rolling: window size for simple moving average (None to disable)
    Returns a Plotly Figure.
    """
    if metric not in history.columns:
        raise KeyError(f"Metric '{metric}' not found in history columns")

    df = history[[date_col, metric]].dropna().copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[date_col], y=df[metric], mode="lines", name=metric))

    if rolling and rolling > 1:
        df["roll"] = df[metric].rolling(rolling, min_periods=max(1, rolling // 2)).mean()
        fig.add_trace(
            go.Scatter(x=df[date_col], y=df["roll"], mode="lines", name=f"{metric} ({rolling}d MA)", line=dict(dash="dot"))
        )

    fig.update_layout(
        title=title or f"{metric} Trend",
        xaxis_title="Date",
        yaxis_title=metric,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig


def display_forecast_dashboard(
    history: pd.DataFrame,
    date_col: str,
    target_col: str,
    forecast: List[Dict[str, float]],
    *,
    rolling: Optional[int] = 7,
    title: Optional[str] = None,
) -> go.Figure:
    """Build a compact dashboard figure with history + rolling mean and forecast.

    Top: history line and rolling average. Bottom: forecast bars with dashed
    overlay line. Returns a Plotly Figure with two stacked subplots.
    """
    df = history[[date_col, target_col]].dropna().copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)

    f_dates = [pd.to_datetime(f["date"]) for f in forecast] if forecast else []
    f_vals = [f["prediction"] for f in forecast] if forecast else []

    fig = make_subplots(rows=2, cols=1, shared_xaxes=False, vertical_spacing=0.12,
                        subplot_titles=("History", "Forecast"))

    # History with optional rolling mean
    fig.add_trace(go.Scatter(x=df[date_col], y=df[target_col], mode="lines", name="History"), row=1, col=1)
    if rolling and rolling > 1:
        roll = df[target_col].rolling(rolling, min_periods=max(1, rolling // 2)).mean()
        fig.add_trace(
            go.Scatter(x=df[date_col], y=roll, mode="lines", name=f"{rolling}d MA", line=dict(dash="dot")),
            row=1, col=1,
        )

    # Forecast bars + dashed line
    if f_dates:
        fig.add_trace(go.Bar(x=f_dates, y=f_vals, name="Forecast", marker_color="#60a5fa"), row=2, col=1)
        fig.add_trace(
            go.Scatter(x=f_dates, y=f_vals, mode="lines", name="Forecast (line)", line=dict(dash="dash")),
            row=2, col=1,
        )

    fig.update_layout(
        title=title or "Forecast Dashboard",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=60, b=40),
        barmode="overlay",
    )
    fig.update_yaxes(title_text=target_col, row=1, col=1)
    fig.update_yaxes(title_text=target_col, row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    return fig
