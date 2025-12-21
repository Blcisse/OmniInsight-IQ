"""Deterministic KPI interpretation rules for InsightOps."""

from typing import Any, Dict, Optional


Severity = {
    "declining": 70,
    "stable": 40,
    "improving": 10,
    "unknown": 0,
}


def _format_percent(value: Optional[float]) -> str:
    """Format a percent value with one decimal place; fall back to placeholder."""
    if value is None:
        return "—"
    return f"{value:.1f}%"


def interpret_kpi(
    latest: Optional[float],
    previous: Optional[float],
    percent_delta: Optional[float],
    rolling_avg_7d: Optional[float],
) -> Dict[str, Any]:
    """
    Interpret KPI movement using deterministic, rule-based thresholds.

    Trend rules (hard-locked):
    - percent_delta is None -> unknown
    - percent_delta <= -5 -> declining
    - -5 < percent_delta < 5 -> stable
    - percent_delta >= 5 -> improving
    """
    if percent_delta is None:
        trend = "unknown"
    elif percent_delta <= -5:
        trend = "declining"
    elif percent_delta < 5:
        trend = "stable"
    else:
        trend = "improving"

    if trend == "declining":
        message = (
            f"Performance declining ({_format_percent(percent_delta)} vs prior period)."
        )
    elif trend == "stable":
        message = "Performance stable within ±5% of the prior period."
    elif trend == "improving":
        message = (
            f"Performance improving ({_format_percent(percent_delta)} vs prior period)."
        )
    else:
        message = "Trend unavailable; insufficient change data."

    # Severity mapping (hard-locked)
    severity = Severity[trend]

    return {"trend": trend, "message": message, "severity": severity}
