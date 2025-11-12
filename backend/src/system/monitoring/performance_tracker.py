from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Iterator
import time

from ...data_pipeline.storage_handler import get_redis_client


def _perf_key(model_name: str) -> str:
    return f"perf:{model_name}"


def record_metric(model_name: str, metric_name: str, value: Any, *, redis_url: Optional[str] = None) -> Dict[str, Any]:
    """Record a single metric data point in Redis (as a list of JSON lines).
    
    Returns the metric info even if Redis is not available (graceful degradation).
    """
    r = get_redis_client(redis_url)
    if r is None:
        # Redis not available - return metric info but don't store
        return {"model": model_name, "metric": metric_name, "value": value}
    
    try:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "metric": metric_name,
            "value": value,
        }
        r.rpush(_perf_key(model_name), json.dumps(payload))
        # Optional list cap
        cap = int(os.getenv("PERF_LIST_CAP", "1000") or 0)
        if cap:
            r.ltrim(_perf_key(model_name), -cap, -1)
    except Exception:
        # Redis operation failed - continue without storing
        pass
    return {"model": model_name, "metric": metric_name, "value": value}


def get_recent_metrics(model_name: str, *, count: int = 100, redis_url: Optional[str] = None) -> List[Dict[str, Any]]:
    r = get_redis_client(redis_url)
    if r is None:
        return []
    
    try:
        raw = r.lrange(_perf_key(model_name), -count, -1)
        out: List[Dict[str, Any]] = []
        for line in raw:
            try:
                out.append(json.loads(line))
            except Exception:
                continue
        return out
    except Exception:
        return []


def aggregate_metrics(model_name: str, *, window: int = 200, redis_url: Optional[str] = None) -> Dict[str, Any]:
    """Aggregate recent metrics for a model (mean, min, max per metric_name)."""
    points = get_recent_metrics(model_name, count=window, redis_url=redis_url)
    buckets: Dict[str, List[float]] = {}
    for p in points:
        try:
            m = str(p.get("metric"))
            v = float(p.get("value"))
        except Exception:
            continue
        buckets.setdefault(m, []).append(v)

    summary: Dict[str, Any] = {}
    for m, vals in buckets.items():
        if not vals:
            continue
        summary[m] = {
            "count": len(vals),
            "mean": sum(vals) / len(vals),
            "min": min(vals),
            "max": max(vals),
        }
    return {"model": model_name, "metrics": summary}


class _LatencyContext:
    def __init__(self, model_name: str, redis_url: Optional[str] = None) -> None:
        self.model_name = model_name
        self.redis_url = redis_url
        self._t0 = 0.0

    def __enter__(self):
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        dt_ms = (time.perf_counter() - self._t0) * 1000.0
        record_metric(self.model_name, "latency_ms", dt_ms, redis_url=self.redis_url)
        if exc is not None:
            # also log an error occurrence
            record_metric(self.model_name, "error", 1.0, redis_url=self.redis_url)
        return False


def track_inference_latency(model_name: str, *, redis_url: Optional[str] = None) -> _LatencyContext:
    """Context manager to measure and record inference latency in milliseconds.

    Usage:
      with track_inference_latency("my_model"):
          run_inference()
    Errors inside the context will also record an 'error' metric = 1.0.
    """
    return _LatencyContext(model_name, redis_url=redis_url)


def log_model_errors(model_name: str, error: Optional[str] = None, *, redis_url: Optional[str] = None) -> Dict[str, Any]:
    """Record an error occurrence for a model and return a summary."""
    record_metric(model_name, "error", 1.0, redis_url=redis_url)
    if error:
        # Also push a log line entry list for errors
        r = get_redis_client(redis_url)
        if r is not None:
            try:
                r.rpush(f"errors:{model_name}", json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "error": error}))
            except Exception:
                pass  # Redis not available or operation failed
    return {"model": model_name, "logged": True}


def report_performance_trends(model_name: str, *, window: int = 200, redis_url: Optional[str] = None) -> Dict[str, Any]:
    """Return aggregated metrics and recent points for simple trend analysis."""
    agg = aggregate_metrics(model_name, window=window, redis_url=redis_url)
    recent = get_recent_metrics(model_name, count=window, redis_url=redis_url)
    return {"model": model_name, "aggregate": agg.get("metrics", {}), "recent": recent}
