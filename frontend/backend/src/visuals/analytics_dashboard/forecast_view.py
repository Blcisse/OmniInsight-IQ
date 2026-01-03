from __future__ import annotations

from typing import List, Dict, Optional

import pandas as pd

try:
    import plotly.graph_objects as go
except Exception:  # pragma: no cover
    go = None  # type: ignore

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None  # type: ignore

from src.ai.forecasting.forecast_visualizer import (
    plot_forecast as plotly_plot_forecast,
    display_forecast_dashboard,
)


def plotly_forecast(history: pd.DataFrame, date_col: str, target_col: str, forecast: List[Dict[str, float]], *, title: Optional[str] = None):
    """Return a Plotly Figure combining history and forecast."""
    if go is None:
        raise RuntimeError("plotly is not installed")
    return plotly_plot_forecast(history, date_col, target_col, forecast, title=title)


def plotly_forecast_dashboard(history: pd.DataFrame, date_col: str, target_col: str, forecast: List[Dict[str, float]], *, title: Optional[str] = None):
    """Return a Plotly dashboard Figure with history + MA and forecast."""
    if go is None:
        raise RuntimeError("plotly is not installed")
    return display_forecast_dashboard(history, date_col, target_col, forecast, title=title)


def matplotlib_forecast(history: pd.DataFrame, date_col: str, target_col: str, forecast: List[Dict[str, float]], *, title: Optional[str] = None):
    """Return a Matplotlib plot handle for server-side generation."""
    if plt is None:
        raise RuntimeError("matplotlib is not installed")
    df = history[[date_col, target_col]].dropna().copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    plt.figure(figsize=(8, 4))
    plt.plot(df[date_col], df[target_col], label="History")
    if forecast:
        f_dates = pd.to_datetime([f["date"] for f in forecast])
        f_vals = [float(f["prediction"]) for f in forecast]
        plt.plot(f_dates, f_vals, label="Forecast", linestyle="--")
    if title:
        plt.title(title)
    plt.xlabel("Date")
    plt.ylabel(target_col)
    plt.legend()
    plt.tight_layout()
    return plt


def recharts_forecast_series(history: pd.DataFrame, date_col: str, target_col: str, forecast: List[Dict[str, float]]) -> Dict[str, List[Dict[str, float]]]:
    """Prepare JSON series suitable for Recharts on the frontend."""
    df = history[[date_col, target_col]].dropna().copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    hist_series = [{"date": d.strftime("%Y-%m-%d"), "value": float(v)} for d, v in zip(df[date_col], df[target_col])]
    fc_series = [{"date": str(item["date"]), "value": float(item["prediction"])} for item in forecast]
    return {"history": hist_series, "forecast": fc_series}


def get_forecast_chart(
    metric: str,
    *,
    history: pd.DataFrame,
    date_col: str,
    forecast: List[Dict[str, float]],
    lib: str = "plotly",
    title: Optional[str] = None,
):
    """High-level helper to get a forecast visualization for a metric.

    - lib="plotly": returns a Plotly Figure
    - lib="matplotlib": returns a Matplotlib plot handle
    - lib="recharts": returns JSON-friendly series for frontend Recharts
    """
    lib = (lib or "plotly").lower()
    if lib == "plotly":
        return plotly_forecast(history, date_col, metric, forecast, title=title)
    if lib == "matplotlib":
        return matplotlib_forecast(history, date_col, metric, forecast, title=title)
    if lib == "recharts":
        return recharts_forecast_series(history, date_col, metric, forecast)
    raise ValueError(f"Unknown visualization library: {lib}")


def export_forecast_visual(
    visual_obj,
    path: str,
    *,
    format: Optional[str] = None,
) -> str:
    """Export a forecast visual to disk.

    Accepts:
      - Plotly Figure: format html (default) or png (requires kaleido)
      - Matplotlib plot: format inferred from file extension or `format`
      - Recharts data (dict): exported as JSON
    Returns the written path.
    """
    from pathlib import Path
    import json

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fmt = (format or out.suffix.lstrip(".") or "html").lower()

    # Plotly Figure
    if go is not None and isinstance(visual_obj, getattr(go, "Figure", ())):
        if fmt == "html":
            visual_obj.write_html(str(out))
            return str(out)
        # try static export
        visual_obj.write_image(str(out))  # may require kaleido
        return str(out)

    # Matplotlib
    if plt is not None and hasattr(visual_obj, "savefig"):
        visual_obj.savefig(str(out), format=fmt if fmt else None, bbox_inches="tight")
        return str(out)

    # Fallback: JSON dump (e.g., recharts data)
    with out.open("w", encoding="utf-8") as f:
        json.dump(visual_obj, f, indent=2)
    return str(out)
