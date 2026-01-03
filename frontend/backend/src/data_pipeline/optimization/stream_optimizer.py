from __future__ import annotations

import time
from typing import Any, Callable, Deque, Dict, Iterable, List, Optional, Tuple
from collections import deque


def enable_data_streaming(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return normalized streaming config with sensible defaults.

    Defaults:
      - batch_size: 500
      - max_queue: 10_000
      - ack: False
    """
    cfg = {"batch_size": 500, "max_queue": 10_000, "ack": False}
    if config:
        cfg.update({k: v for k, v in config.items() if v is not None})
    return cfg


def handle_stream_batches(
    iterable: Iterable[Any],
    *,
    batch_size: int = 500,
    handler: Optional[Callable[[List[Any]], None]] = None,
) -> int:
    """Consume an iterable in batches and optionally call `handler` per batch.

    Returns the total number of processed records.
    """
    total = 0
    batch: List[Any] = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= max(1, int(batch_size)):
            if handler:
                handler(batch)
            total += len(batch)
            batch = []
    if batch:
        if handler:
            handler(batch)
        total += len(batch)
    return total


def monitor_stream_health(
    timestamps: Iterable[float],
    *,
    window_seconds: int = 60,
) -> Dict[str, float]:
    """Compute simple throughput metrics given event timestamps (time.time()).

    Returns events_per_sec in the given window and moving averages.
    """
    now = time.time()
    ts = [t for t in timestamps if now - t <= window_seconds]
    if not ts:
        return {"events_per_sec": 0.0, "count": 0.0, "window": float(window_seconds)}
    ts.sort()
    duration = max(1e-6, ts[-1] - ts[0])
    eps = len(ts) / duration if duration > 0 else float("inf")
    return {"events_per_sec": float(eps), "count": float(len(ts)), "window": float(window_seconds)}

