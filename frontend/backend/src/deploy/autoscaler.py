from __future__ import annotations

import math
from typing import Dict, List, Tuple, Optional
import time


def compute_desired_replicas(
    *,
    target_qps: float,
    avg_latency_ms: float,
    max_replicas: int = 50,
    min_replicas: int = 1,
) -> int:
    """Suggest replica count based on throughput and latency (Little's Law heuristic)."""
    if target_qps <= 0 or avg_latency_ms <= 0:
        return max(min_replicas, 1)
    replicas = math.ceil(target_qps * (avg_latency_ms / 1000.0))
    return max(min_replicas, min(int(replicas), int(max_replicas)))


def autoscale_summary(target_qps: float, avg_latency_ms: float) -> Dict[str, float]:
    r = compute_desired_replicas(target_qps=target_qps, avg_latency_ms=avg_latency_ms)
    return {"replicas": float(r), "target_qps": float(target_qps), "avg_latency_ms": float(avg_latency_ms)}


def analyze_cpu_usage(samples: List[float], *, window: int = 60) -> Dict[str, float]:
    """Analyze CPU usage samples (%) and return mean/max over the window.

    samples: list of recent CPU percentages (0-100)
    window: number of most recent samples to include
    """
    if not samples:
        return {"mean": 0.0, "max": 0.0, "n": 0.0}
    buf = samples[-max(1, int(window)) :]
    mean = sum(buf) / len(buf)
    return {"mean": float(mean), "max": float(max(buf)), "n": float(len(buf))}


def trigger_auto_scale(
    *,
    current_replicas: int,
    cpu_mean: float,
    scale_up_threshold: float = 70.0,
    scale_down_threshold: float = 30.0,
    step: int = 1,
    max_replicas: int = 50,
    min_replicas: int = 1,
) -> Dict[str, int]:
    """Decide scaling action based on CPU thresholds.

    Returns {'desired_replicas': N, 'delta': +/-step}
    """
    desired = current_replicas
    if cpu_mean >= scale_up_threshold:
        desired = min(max_replicas, current_replicas + max(1, step))
    elif cpu_mean <= scale_down_threshold:
        desired = max(min_replicas, current_replicas - max(1, step))
    return {"desired_replicas": int(desired), "delta": int(desired - current_replicas)}


def downscale_idle_nodes(
    node_metrics: List[Tuple[str, float]],
    *,
    idle_threshold: float = 10.0,
    min_active: int = 1,
) -> List[str]:
    """Return a list of node IDs that are safe candidates for downscaling.

    node_metrics: list of (node_id, cpu_percent) tuples
    idle_threshold: consider nodes with CPU <= threshold as idle
    min_active: keep at least this many active nodes
    """
    idle = [nid for nid, cpu in node_metrics if cpu <= idle_threshold]
    # Ensure we keep at least min_active nodes running
    keep = max(0, min_active)
    if len(node_metrics) - len(idle) < keep:
        cut = keep - (len(node_metrics) - len(idle))
        idle = idle[:-cut] if cut < len(idle) else []
    return idle
