from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def summarize_anomalies(
    anomalies: pd.DataFrame,
    *,
    date_col: Optional[str] = None,
    value_col: Optional[str] = None,
    score_col: Optional[str] = None,
) -> Dict[str, Any]:
    """Summarize anomalies with counts, date range, and top-k extremes.

    - date_col: if provided, computes min/max dates
    - value_col: for top extremes by absolute deviation/score
    - score_col: optional metric to sort by (e.g., z_score)
    """
    if anomalies is None or anomalies.empty:
        return {"count": 0, "date_min": None, "date_max": None, "top": []}

    count = int(len(anomalies))
    date_min = anomalies[date_col].min().isoformat() if date_col and pd.api.types.is_datetime64_any_dtype(anomalies[date_col]) else None
    date_max = anomalies[date_col].max().isoformat() if date_col and pd.api.types.is_datetime64_any_dtype(anomalies[date_col]) else None

    # Determine ranking column
    if score_col and score_col in anomalies.columns:
        rank_series = anomalies[score_col].abs()
    elif value_col and value_col in anomalies.columns:
        rank_series = anomalies[value_col].abs()
    else:
        rank_series = pd.Series(np.ones(count), index=anomalies.index)

    order = rank_series.sort_values(ascending=False).index[:10]
    top_rows = anomalies.loc[order]
    top = top_rows.to_dict(orient="records")

    return {"count": count, "date_min": date_min, "date_max": date_max, "top": top}


def generate_anomaly_report(
    summary: Dict[str, Any],
    *,
    title: str = "Anomaly Report",
) -> str:
    """Create a simple text report from a summary dict."""
    lines = [title, ""]
    lines.append(f"Total anomalies: {summary.get('count', 0)}")
    if summary.get("date_min") and summary.get("date_max"):
        lines.append(f"Date range: {summary['date_min']} to {summary['date_max']}")
    lines.append("Top anomalies:")
    for i, row in enumerate(summary.get("top", []), start=1):
        lines.append(f"  {i}. {row}")
    return "\n".join(lines)


def export_anomalies(anomalies: pd.DataFrame, path: str | Path, *, format: str = "csv") -> Path:
    """Export anomalies DataFrame to CSV or JSON."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if format.lower() == "json":
        with out.open("w", encoding="utf-8") as f:
            json.dump(anomalies.to_dict(orient="records"), f, indent=2)
        return out
    anomalies.to_csv(out, index=False)
    return out


def export_anomaly_summary(
    summary: Dict[str, Any],
    path: str | Path,
    *,
    format: str = "txt",
    title: str = "Anomaly Report",
) -> Path:
    """Export an anomaly summary to a file (txt or json).

    - format="txt": writes a human-readable report using generate_anomaly_report
    - format="json": writes the summary dict as JSON
    Returns the written Path.
    """
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fmt = format.lower()
    if fmt == "json":
        with out.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        return out
    # default to text report
    report = generate_anomaly_report(summary, title=title)
    with out.open("w", encoding="utf-8") as f:
        f.write(report)
    return out


def plot_anomalies_timeseries(
    history: pd.DataFrame,
    date_col: str,
    value_col: str,
    anomalies: pd.DataFrame,
    *,
    title: Optional[str] = None,
):
    """Plot time series with anomalies highlighted."""
    df = history[[date_col, value_col]].dropna().copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    plt.figure(figsize=(8, 4))
    plt.plot(df[date_col], df[value_col], label="History")
    if not anomalies.empty and date_col in anomalies.columns:
        # Normalize anomaly dates to datetime
        ad = pd.to_datetime(anomalies[date_col])
        av = anomalies[value_col] if value_col in anomalies.columns else None
        plt.scatter(ad, av if av is not None else [np.nan] * len(ad), color="red", s=24, label="Anomaly")
    plt.xlabel("Date")
    plt.ylabel(value_col)
    if title:
        plt.title(title)
    plt.legend()
    plt.tight_layout()
    return plt
