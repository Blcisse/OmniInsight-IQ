from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .performance_tracker import record_metric, aggregate_metrics

logger = logging.getLogger("model_monitor")
logger.setLevel(logging.INFO)


def monitor_model_performance(model_name: str, metrics: Dict[str, Any], *, redis_url: Optional[str] = None) -> Dict[str, Any]:
    """Record a batch of performance metrics and log them.

    Example metrics: {
      "latency_ms": 12.3,
      "throughput_qps": 45.1,
      "accuracy": 0.91
    }
    Returns a lightweight summary (names + count recorded).
    """
    if not metrics:
        return {"model": model_name, "recorded": 0}
    recorded = 0
    for name, value in metrics.items():
        try:
            record_metric(model_name, name, value, redis_url=redis_url)
            recorded += 1
        except Exception as e:
            logger.warning("Failed recording metric %s for %s: %s", name, model_name, e)
    logger.info("Recorded %d metrics for model '%s'", recorded, model_name)
    return {"model": model_name, "recorded": recorded, "metrics": list(metrics.keys())}


def generate_health_report(model_name: str, *, window: int = 200, redis_url: Optional[str] = None) -> Dict[str, Any]:
    """Generate a simple health report from recent metrics.

    Heuristics:
      - status="degraded" if latency_ms mean > 500 or error_rate > 0.05
      - status="healthy" otherwise when data present; "unknown" when no data
    """
    try:
        agg = aggregate_metrics(model_name, window=window, redis_url=redis_url)
        metrics = agg.get("metrics", {})
        status = "unknown"
        if metrics:
            latency = metrics.get("latency_ms", {}).get("mean")
            error_rate = metrics.get("error_rate", {}).get("mean")
            if latency is not None and float(latency) > 500:
                status = "degraded"
            elif error_rate is not None and float(error_rate) > 0.05:
                status = "degraded"
            else:
                status = "healthy"
        report = {"model": model_name, "status": status, "summary": metrics}
        logger.info("Health report for %s: %s", model_name, status)
        return report
    except Exception as e:
        logger.error("Failed generating health report for %s: %s", model_name, e)
        return {"model": model_name, "status": "error", "error": str(e)}

