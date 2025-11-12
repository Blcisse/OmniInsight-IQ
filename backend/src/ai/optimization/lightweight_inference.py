from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

try:
    from src.api.model_inference.model_service import load_trained_model, predict
except Exception:  # pragma: no cover
    from ...api.model_inference.model_service import load_trained_model, predict  # type: ignore

from .model_cacher import retrieve_cached_model, store_model_in_memory


def run_light_inference(
    model_name: str,
    batch_inputs: List[Dict[str, Any]],
    *,
    version: Optional[str] = None,
    models_dir: str = "models",
    framework: Optional[str] = None,
    feature_order: Optional[List[str]] = None,
    use_cache: bool = True,
) -> Tuple[List[Any], Optional[List[Any]], Dict[str, Any]]:
    """Fast-path inference that reuses cached model instances when possible."""
    model = retrieve_cached_model(model_name, version=version) if use_cache else None
    if model is None:
        model = load_trained_model(models_dir=models_dir, model_name=model_name, version=version)
        if use_cache:
            store_model_in_memory(model_name, model, version=version)
    preds, proba, meta = predict(
        model=model,
        records=batch_inputs,
        framework=framework,
        feature_order=feature_order,
        return_proba=False,
    )
    return preds, proba, meta


def auto_scale_inference_workers(
    *,
    target_qps: float,
    avg_latency_ms: float,
    max_workers: int = 64,
) -> Dict[str, Any]:
    """Suggest a concurrency level based on Little's Law-style reasoning.

    workers ~= target_qps * avg_latency_seconds
    """
    if target_qps <= 0 or avg_latency_ms <= 0:
        return {"workers": 1, "note": "invalid input, defaulting to 1"}
    workers = math.ceil(target_qps * (avg_latency_ms / 1000.0))
    workers = max(1, min(int(workers), int(max_workers)))
    return {"workers": workers, "target_qps": target_qps, "avg_latency_ms": avg_latency_ms}

