from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # type: ignore

_START_TIME = time.time()

# Prometheus optional setup
_PROM_AVAILABLE = False
try:
    from prometheus_client import CollectorRegistry, Histogram, Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST, start_http_server  # type: ignore

    _PROM_AVAILABLE = True
except Exception:  # pragma: no cover
    CollectorRegistry = None  # type: ignore
    Histogram = None  # type: ignore
    Gauge = None  # type: ignore
    Counter = None  # type: ignore
    generate_latest = None  # type: ignore
    CONTENT_TYPE_LATEST = "text/plain"  # type: ignore
    start_http_server = None  # type: ignore

_registry: Optional[CollectorRegistry] = None
_latency_hist: Any = None
_cpu_gauge: Any = None
_mem_gauge: Any = None


def _ensure_prometheus() -> bool:
    global _registry, _latency_hist, _cpu_gauge, _mem_gauge
    if not _PROM_AVAILABLE:
        return False
    if _registry is None:
        _registry = CollectorRegistry()
        _latency_hist = Histogram(
            "inference_latency_ms",
            "Inference latency in milliseconds",
            ["model"],
            registry=_registry,
            buckets=(5, 10, 20, 50, 100, 200, 500, 1000, float("inf")),
        )
        _cpu_gauge = Gauge("system_cpu_percent", "CPU usage percent", registry=_registry)
        _mem_gauge = Gauge("system_mem_percent", "Memory usage percent", registry=_registry)
    return True


def collect_system_metrics() -> Dict[str, Any]:
    """Collect basic system metrics (CPU, memory, uptime)."""
    uptime = time.time() - _START_TIME
    cpu = None
    mem = None
    loadavg = None
    if psutil is not None:
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            try:
                loadavg = os.getloadavg()  # type: ignore[attr-defined]
            except Exception:
                loadavg = None
        except Exception:
            cpu = None
            mem = None
    # Update gauges if using Prometheus
    if _ensure_prometheus() and cpu is not None and mem is not None:
        try:
            _cpu_gauge.set(float(cpu))
            _mem_gauge.set(float(mem))
        except Exception:
            pass

    return {
        "uptime_sec": float(uptime),
        "cpu_percent": float(cpu) if cpu is not None else None,
        "mem_percent": float(mem) if mem is not None else None,
        "load_avg": tuple(loadavg) if loadavg else None,
    }


def track_inference_latency(model_name: str, latency_ms: float) -> None:
    """Record an inference latency metric (Prometheus when available)."""
    if _ensure_prometheus():
        try:
            _latency_hist.labels(model=model_name).observe(float(latency_ms))
        except Exception:
            pass


def export_metrics_to_prometheus(start_http: bool = False, port: int = 9464) -> Dict[str, Any]:
    """Expose metrics for Prometheus scraping.

    - start_http=True: starts an HTTP server on the given port (non-blocking)
    - otherwise returns a dict with content-type and text payload
    """
    if not _ensure_prometheus():
        return {"content_type": CONTENT_TYPE_LATEST, "payload": b""}
    if start_http and start_http_server is not None:
        try:
            start_http_server(port, registry=_registry)
            return {"started": True, "port": port}
        except Exception as e:
            return {"started": False, "error": str(e)}
    payload = generate_latest(_registry) if generate_latest else b""
    return {"content_type": CONTENT_TYPE_LATEST, "payload": payload}

