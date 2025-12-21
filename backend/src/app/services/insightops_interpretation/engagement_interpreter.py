"""Deterministic engagement interpretation rules for InsightOps."""

from typing import Any, Dict, Optional


def interpret_engagement(
    health_score: Optional[float],
    avg_per_day: Optional[float],
    last_day_value: Optional[float],
) -> Dict[str, Any]:
    """
    Classify engagement health using simple, rule-based thresholds.

    Rules:
    - health_score >= 70 -> healthy (severity 10)
    - 40 <= health_score < 70 -> watch (severity 40)
    - health_score < 40 -> critical (severity 80)
    """
    score = health_score or 0
    if score >= 70:
        status = "healthy"
        severity = 10
        message = "Engagement is healthy with strong recent activity."
    elif score >= 40:
        status = "watch"
        severity = 40
        message = "Engagement is steady but should be monitored for softening."
    else:
        status = "critical"
        severity = 80
        message = "Engagement is low; immediate action recommended."

    return {
        "status": status,
        "message": message,
        "severity": severity,
        "health_score": score,
        "average_per_day": avg_per_day,
        "last_day_value": last_day_value,
    }
