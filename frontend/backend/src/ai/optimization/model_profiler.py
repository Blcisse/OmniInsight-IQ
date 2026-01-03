from __future__ import annotations

import statistics
import time
from typing import Any, Dict, List, Optional

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # type: ignore

import pandas as pd

try:
    from src.api.model_inference.model_service import load_trained_model, predict
except Exception:  # pragma: no cover
    from ...api.model_inference.model_service import load_trained_model, predict  # type: ignore


def _now_ms() -> float:
    return time.perf_counter() * 1000.0


def analyze_model_latency(latencies_ms: List[float]) -> Dict[str, float]:
    if not latencies_ms:
        return {"count": 0, "min_ms": 0.0, "max_ms": 0.0, "avg_ms": 0.0, "p50_ms": 0.0, "p90_ms": 0.0, "p99_ms": 0.0}
    vals = sorted(latencies_ms)
    n = len(vals)
    def pct(p: float) -> float:
        idx = min(n - 1, max(0, int(round(p * (n - 1)))))
        return float(vals[idx])

    return {
        "count": float(n),
        "min_ms": float(vals[0]),
        "max_ms": float(vals[-1]),
        "avg_ms": float(sum(vals) / n),
        "p50_ms": pct(0.50),
        "p90_ms": pct(0.90),
        "p99_ms": pct(0.99),
    }


def benchmark_model_performance(
    model_name: str,
    sample_records: List[Dict[str, Any]],
    *,
    iterations: int = 10,
    models_dir: str = "models",
    framework: Optional[str] = None,
    feature_order: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Load a model and benchmark inference latency over a number of iterations.

    Returns statistics including latency distribution and (if available) memory snapshot.
    """
    model = load_trained_model(models_dir=models_dir, model_name=model_name, version=None)
    # Warm-up
    predict(model=model, records=sample_records, framework=framework, feature_order=feature_order)

    latencies: List[float] = []
    for _ in range(max(1, iterations)):
        t0 = _now_ms()
        predict(model=model, records=sample_records, framework=framework, feature_order=feature_order)
        latencies.append(_now_ms() - t0)

    stats = analyze_model_latency(latencies)
    mem_info: Dict[str, Any] = {}
    if psutil is not None:
        try:
            p = psutil.Process()
            mi = p.memory_info()
            mem_info = {"rss_mb": mi.rss / (1024 * 1024), "vms_mb": mi.vms / (1024 * 1024)}
        except Exception:
            mem_info = {}

    return {"model": model_name, "iterations": iterations, "latency": stats, "memory": mem_info}


def generate_model_report(result: Dict[str, Any]) -> str:
    lat = result.get("latency", {})
    mem = result.get("memory", {})
    lines = [
        f"Model: {result.get('model')}",
        f"Iterations: {result.get('iterations')}",
        f"Avg latency: {lat.get('avg_ms', 0):.2f} ms (p50 {lat.get('p50_ms', 0):.2f}, p90 {lat.get('p90_ms', 0):.2f}, p99 {lat.get('p99_ms', 0):.2f})",
    ]
    if mem:
        lines.append(f"Memory RSS: {mem.get('rss_mb', 0):.2f} MB; VMS: {mem.get('vms_mb', 0):.2f} MB")
    return "\n".join(lines)

