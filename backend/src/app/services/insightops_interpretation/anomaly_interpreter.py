"""Rule-based anomaly interpretation for InsightOps."""

from typing import Any, Dict, List, Optional


def interpret_anomalies(anomalies: Optional[List[dict]]) -> Dict[str, Any]:
    """
    Summarize anomaly risk using deterministic thresholds.

    Rules:
    - Empty list -> risk none, severity 0
    - Otherwise: risk present, count anomalies, severity is max provided or default 60
    """
    if not anomalies:
        return {
            "risk": "none",
            "count": 0,
            "severity": 0,
            "message": "No anomalies detected.",
        }

    count = len(anomalies)
    max_severity = 0
    for anomaly in anomalies:
        severity = anomaly.get("severity")
        if isinstance(severity, (int, float)):
            severity_value = int(severity)
        elif isinstance(severity, str):
            severity_map = {"info": 20, "warning": 60, "critical": 90}
            severity_value = severity_map.get(severity.lower(), 60)
        else:
            severity_value = 60
        max_severity = max(max_severity, severity_value)

    return {
        "risk": "present",
        "count": count,
        "severity": max_severity or 60,
        "message": f"{count} anomaly{'ies' if count != 1 else ''} detected.",
    }
