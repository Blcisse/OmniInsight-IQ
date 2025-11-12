from __future__ import annotations

from typing import Dict, Any

import pandas as pd

try:
    import plotly.graph_objects as go
except Exception:  # pragma: no cover
    go = None  # type: ignore

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None  # type: ignore

from src.ai.anomaly_detection.anomaly_reporter import plot_anomalies_timeseries


def matplotlib_anomaly_timeseries(history: pd.DataFrame, date_col: str, value_col: str, anomalies: pd.DataFrame, *, title: str | None = None):
    """Return a Matplotlib plot with anomalies highlighted."""
    if plt is None:
        raise RuntimeError("matplotlib is not installed")
    return plot_anomalies_timeseries(history, date_col, value_col, anomalies, title=title)


def plotly_anomaly_timeseries(history: pd.DataFrame, date_col: str, value_col: str, anomalies: pd.DataFrame, *, title: str | None = None):
    """Build an interactive Plotly line with anomaly markers."""
    if go is None:
        raise RuntimeError("plotly is not installed")
    df = history[[date_col, value_col]].dropna().copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[date_col], y=df[value_col], mode="lines", name="Series"))
    if not anomalies.empty and date_col in anomalies.columns:
        ad = pd.to_datetime(anomalies[date_col])
        av = anomalies[value_col] if value_col in anomalies.columns else None
        fig.add_trace(go.Scatter(x=ad, y=av, mode="markers", name="Anomaly", marker=dict(color="red", size=8)))
    fig.update_layout(title=title or "Anomalies", xaxis_title="Date", yaxis_title=value_col, template="plotly_white")
    return fig


def recharts_anomaly_series(history: pd.DataFrame, date_col: str, value_col: str, anomalies: pd.DataFrame) -> Dict[str, Any]:
    """Return series data for Recharts: line plus anomaly points."""
    df = history[[date_col, value_col]].dropna().copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    series = [{"date": d.strftime("%Y-%m-%d"), "value": float(v)} for d, v in zip(df[date_col], df[value_col])]
    ann = []
    if not anomalies.empty and date_col in anomalies.columns:
        ad = pd.to_datetime(anomalies[date_col])
        av = anomalies[value_col] if value_col in anomalies.columns else None
        for d, v in zip(ad, (av if av is not None else [None] * len(ad))):
            ann.append({"date": d.strftime("%Y-%m-%d"), "value": float(v) if v is not None else None})
    return {"series": series, "anomalies": ann}


def _parse_time_range(time_range) -> int:
    """Return number of days represented by time_range.

    Accepts an int (days) or a string like '7d'. Defaults to 7 if invalid.
    """
    try:
        if isinstance(time_range, int):
            return max(1, time_range)
        s = str(time_range).strip().lower()
        if s.endswith("d"):
            return max(1, int(s[:-1]))
        return max(1, int(s))
    except Exception:
        return 7


def get_anomaly_chart(
    time_range,
    *,
    history: pd.DataFrame,
    date_col: str,
    value_col: str,
    anomalies: pd.DataFrame,
    lib: str = "plotly",
    title: str | None = None,
):
    """Return an anomaly visualization for the last N days.

    - time_range: int days or string like '7d'
    - lib: 'plotly' | 'matplotlib' | 'recharts'
    """
    days = _parse_time_range(time_range)
    df = history[[date_col, value_col]].dropna().copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    if df.empty:
        if lib == "recharts":
            return {"series": [], "anomalies": []}
        raise ValueError("history is empty")

    cutoff = df[date_col].iloc[-1] - pd.Timedelta(days=days)
    df_recent = df[df[date_col] > cutoff]

    an = anomalies.copy() if anomalies is not None else pd.DataFrame()
    if not an.empty and date_col in an.columns:
        an = an.copy()
        an[date_col] = pd.to_datetime(an[date_col])
        an = an[an[date_col] > cutoff]

    lib = (lib or "plotly").lower()
    if lib == "plotly":
        return plotly_anomaly_timeseries(df_recent, date_col, value_col, an, title=title)
    if lib == "matplotlib":
        return matplotlib_anomaly_timeseries(df_recent, date_col, value_col, an, title=title)
    if lib == "recharts":
        return recharts_anomaly_series(df_recent, date_col, value_col, an)
    raise ValueError(f"Unknown visualization library: {lib}")


def anomaly_summary_plot(
    anomalies: pd.DataFrame,
    *,
    date_col: str,
    score_col: str | None = None,
    lib: str = "plotly",
    title: str | None = None,
):
    """Plot anomalies per day (count) with optional average score.

    - plotly: returns a Figure with bars (count) and optional line (avg score)
    - matplotlib: returns a Matplotlib plot
    - recharts: returns list of {date, count, avg_score?}
    """
    if anomalies is None or anomalies.empty or date_col not in anomalies.columns:
        if lib == "recharts":
            return []
        raise ValueError("No anomalies or missing date column")

    df = anomalies.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    grp = df.groupby(df[date_col].dt.date)
    counts = grp.size().rename("count").to_frame()
    if score_col and score_col in df.columns:
        counts["avg_score"] = grp[score_col].mean()
    counts = counts.reset_index().rename(columns={"index": "date"})

    lib = (lib or "plotly").lower()
    if lib == "plotly":
        if go is None:
            raise RuntimeError("plotly is not installed")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=counts["date"], y=counts["count"], name="Anomaly Count"))
        if "avg_score" in counts.columns:
            fig.add_trace(
                go.Scatter(x=counts["date"], y=counts["avg_score"], mode="lines", name="Avg Score", yaxis="y2")
            )
            fig.update_layout(
                yaxis2=dict(overlaying="y", side="right", title="Avg Score"),
            )
        fig.update_layout(title=title or "Anomaly Summary", xaxis_title="Date", yaxis_title="Count", template="plotly_white")
        return fig

    if lib == "matplotlib":
        if plt is None:
            raise RuntimeError("matplotlib is not installed")
        fig, ax1 = plt.subplots(figsize=(8, 4))
        ax1.bar(counts["date"], counts["count"], color="#60a5fa", label="Anomaly Count")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Count")
        if "avg_score" in counts.columns:
            ax2 = ax1.twinx()
            ax2.plot(counts["date"], counts["avg_score"], color="#ef4444", label="Avg Score")
            ax2.set_ylabel("Avg Score")
        if title:
            ax1.set_title(title)
        fig.tight_layout()
        return plt

    if lib == "recharts":
        out = counts.copy()
        out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
        return out.to_dict(orient="records")

    raise ValueError(f"Unknown visualization library: {lib}")
