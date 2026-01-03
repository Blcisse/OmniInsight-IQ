from __future__ import annotations

from typing import List, Tuple, Optional, Dict, Any

import pandas as pd

try:
    import plotly.graph_objects as go
except Exception:  # pragma: no cover
    go = None  # type: ignore

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None  # type: ignore

from src.ai.recommendation_engine.rec_visualizer import (
    item_scores_frame,
    plot_recommendation_impact as prepare_impact,
    show_rec_trends as prepare_trends,
    cooccurrence_heatmap_data,
)


def plotly_item_scores(recommendations: List[Tuple[str, float]], *, title: Optional[str] = None):
    """Return a Plotly bar of recommended items and scores."""
    if go is None:
        raise RuntimeError("plotly is not installed")
    df = item_scores_frame(recommendations)
    fig = go.Figure(go.Bar(x=df["item"], y=df["score"]))
    fig.update_layout(title=title or "Recommended Items", xaxis_title="Item", yaxis_title="Score", template="plotly_white")
    return fig


def matplotlib_item_scores(recommendations: List[Tuple[str, float]], *, title: Optional[str] = None):
    """Return a Matplotlib bar for item scores."""
    if plt is None:
        raise RuntimeError("matplotlib is not installed")
    df = item_scores_frame(recommendations)
    plt.figure(figsize=(8, 4))
    plt.bar(df["item"], df["score"])
    plt.xticks(rotation=30, ha="right")
    if title:
        plt.title(title)
    plt.ylabel("Score")
    plt.tight_layout()
    return plt


def plotly_rec_impact(df: pd.DataFrame, *, date_col: str, baseline_col: str, with_rec_col: str, title: Optional[str] = None):
    """Return a Plotly line chart for recommendation impact over time."""
    if go is None:
        raise RuntimeError("plotly is not installed")
    g = prepare_impact(df, date_col=date_col, baseline_col=baseline_col, with_rec_col=with_rec_col)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=g[date_col], y=g["baseline"], mode="lines", name="Baseline"))
    fig.add_trace(go.Scatter(x=g[date_col], y=g["with_rec"], mode="lines", name="With Rec"))
    fig.add_trace(go.Scatter(x=g[date_col], y=g["delta"], mode="lines", name="Delta", line=dict(dash="dash")))
    fig.update_layout(title=title or "Recommendation Impact", xaxis_title="Date", yaxis_title="Value", template="plotly_white")
    return fig


def recharts_item_scores(recommendations: List[Tuple[str, float]]) -> List[Dict[str, Any]]:
    """Return [{ item, score }] for Recharts bar chart."""
    return item_scores_frame(recommendations).to_dict(orient="records")


def recharts_rec_trends(df: pd.DataFrame, *, date_col: str, metric_col: str, by_col: Optional[str] = None) -> Dict[str, Any]:
    """Return trend data suitable for Recharts line charts."""
    tdf = prepare_trends(df, date_col=date_col, metric_col=metric_col, by_col=by_col)
    if by_col:
        # group into series per category
        series: Dict[str, List[Dict[str, Any]]] = {}
        for key, grp in tdf.groupby(by_col):
            series[str(key)] = [{"date": d.strftime("%Y-%m-%d"), "metric": float(v)} for d, v in zip(grp[date_col], grp["metric"]) ]
        return {"series": series}
    return {
        "series": [{"date": d.strftime("%Y-%m-%d"), "metric": float(v)} for d, v in zip(tdf[date_col], tdf["metric"]) ]
    }


def get_recommendation_heatmap(
    co: pd.DataFrame,
    *,
    title: Optional[str] = None,
    lib: str = "plotly",
):
    """Visualize a co-occurrence heatmap for recommendations.

    - plotly: returns a Heatmap Figure
    - matplotlib: returns a Matplotlib image
    - recharts: returns matrix + labels via cooccurrence_heatmap_data
    """
    lib = (lib or "plotly").lower()
    data = cooccurrence_heatmap_data(co)
    if lib == "plotly":
        if go is None:
            raise RuntimeError("plotly is not installed")
        fig = go.Figure(go.Heatmap(z=data["matrix"], x=data["x_labels"], y=data["y_labels"], colorscale="Blues"))
        fig.update_layout(title=title or "Co-occurrence Heatmap", xaxis_title="Item", yaxis_title="Item", template="plotly_white")
        return fig
    if lib == "matplotlib":
        if plt is None:
            raise RuntimeError("matplotlib is not installed")
        plt.figure(figsize=(6, 5))
        plt.imshow(data["matrix"], cmap="Blues", aspect="auto")
        plt.colorbar(label="Co-occurrence")
        plt.xticks(ticks=np.arange(len(data["x_labels"])), labels=data["x_labels"], rotation=90)
        plt.yticks(ticks=np.arange(len(data["y_labels"])), labels=data["y_labels"])
        plt.title(title or "Co-occurrence Heatmap")
        plt.tight_layout()
        return plt
    if lib == "recharts":
        return data
    raise ValueError(f"Unknown visualization library: {lib}")


def visualize_rec_performance(
    df: pd.DataFrame,
    *,
    date_col: str,
    metrics: List[str],
    lib: str = "plotly",
    title: Optional[str] = None,
):
    """Visualize recommendation performance metrics over time.

    df is expected to contain a date column and one or more metric columns
    (e.g., ['precision@k', 'recall@k', 'map@k']).
    - plotly: returns multi-line Figure
    - matplotlib: returns a multi-line plot
    - recharts: returns { series: {metric: [{date, value}] } }
    """
    work = df[[date_col] + metrics].dropna().copy()
    work[date_col] = pd.to_datetime(work[date_col])
    work = work.sort_values(date_col)
    lib = (lib or "plotly").lower()

    if lib == "plotly":
        if go is None:
            raise RuntimeError("plotly is not installed")
        fig = go.Figure()
        for m in metrics:
            fig.add_trace(go.Scatter(x=work[date_col], y=work[m], mode="lines", name=m))
        fig.update_layout(title=title or "Recommendation Performance", xaxis_title="Date", yaxis_title="Metric", template="plotly_white")
        return fig

    if lib == "matplotlib":
        if plt is None:
            raise RuntimeError("matplotlib is not installed")
        plt.figure(figsize=(8, 4))
        for m in metrics:
            plt.plot(work[date_col], work[m], label=m)
        if title:
            plt.title(title)
        plt.xlabel("Date")
        plt.ylabel("Metric")
        plt.legend()
        plt.tight_layout()
        return plt

    if lib == "recharts":
        series: Dict[str, List[Dict[str, Any]]] = {}
        for m in metrics:
            series[m] = [{"date": d.strftime("%Y-%m-%d"), "value": float(v)} for d, v in zip(work[date_col], work[m])]
        return {"series": series}

    raise ValueError(f"Unknown visualization library: {lib}")
