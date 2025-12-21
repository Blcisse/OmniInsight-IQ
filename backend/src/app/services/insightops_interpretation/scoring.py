"""Shared priority scoring utilities for InsightOps interpretation."""

from typing import Dict


def _clamp_score(value: float) -> int:
    """Clamp and round a score to 0–100."""
    return int(max(0, min(100, round(value))))


def compute_priority_score(kpi_sev: float, engagement_sev: float, anomaly_sev: float) -> Dict[str, object]:
    """
    Compute a deterministic priority score from severity inputs.

    Formula (hard-locked):
        score = round(0.5 * kpi_sev + 0.3 * engagement_sev + 0.2 * anomaly_sev)
        clamp to 0–100
    Level mapping:
        < 30 -> low
        30–69 -> medium
        >= 70 -> high
    """
    weighted = 0.5 * kpi_sev + 0.3 * engagement_sev + 0.2 * anomaly_sev
    score = _clamp_score(weighted)

    if score < 30:
        level = "low"
    elif score < 70:
        level = "medium"
    else:
        level = "high"

    return {"priority_score": score, "level": level}
