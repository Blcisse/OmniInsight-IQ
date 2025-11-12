from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple
import json
import pandas as pd
import numpy as np

try:
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier  # type: ignore
except Exception:  # pragma: no cover
    RandomForestRegressor = None  # type: ignore
    RandomForestClassifier = None  # type: ignore

from ..storage_handler import get_redis_client


def evaluate_feature_importance(
    df: pd.DataFrame,
    target: str,
    *,
    task: Optional[str] = None,
    random_state: int = 42,
) -> Dict[str, float]:
    """Return feature importance mapping.

    Uses RandomForest when available; otherwise falls back to variance-based ranking.
    """
    if target not in df.columns:
        raise KeyError(f"Missing target column: {target}")
    X = df.drop(columns=[target])
    y = df[target]
    # Keep numeric columns for the model path
    X_num = X.select_dtypes(include=[np.number])

    if RandomForestRegressor and RandomForestClassifier and X_num.shape[1] > 0:
        if task is None:
            task = "classification" if (y.dtype == object or y.nunique() < 20) else "regression"
        model = (
            RandomForestClassifier(random_state=random_state)
            if task == "classification"
            else RandomForestRegressor(random_state=random_state)
        )
        model.fit(X_num, y)
        importances = model.feature_importances_
        return {col: float(val) for col, val in zip(X_num.columns, importances)}

    # Fallback: variance of numeric columns
    variances = X_num.var(ddof=1).fillna(0.0).to_dict()
    return {k: float(v) for k, v in variances.items()}


def prune_low_value_features(
    df: pd.DataFrame,
    importance: Dict[str, float],
    *,
    threshold: Optional[float] = None,
    top_k: Optional[int] = None,
) -> Tuple[pd.DataFrame, List[str]]:
    """Drop features with low importance.

    If top_k is provided, keep only the top_k features by importance.
    Otherwise, drop those strictly below `threshold` (default percentile 25th of non-zero values).
    Returns (reduced_df, dropped_features).
    """
    if not importance:
        return df.copy(), []
    items = sorted(importance.items(), key=lambda kv: kv[1], reverse=True)
    if top_k is not None:
        keep = {name for name, _ in items[: max(1, int(top_k))]}
    else:
        vals = [v for _, v in items if v > 0]
        if not vals:
            keep = set(k for k, _ in items)  # nothing to drop
        else:
            thr = threshold if threshold is not None else float(np.percentile(vals, 25))
            keep = {name for name, val in items if val >= thr}

    drop = [c for c in df.columns if c not in keep and c in importance]
    out = df.drop(columns=drop, errors="ignore")
    return out, drop


def store_feature_stats(
    stats: Dict[str, Any],
    *,
    redis_url: Optional[str] = None,
    key: Optional[str] = None,
    path: Optional[str] = None,
) -> Dict[str, Any]:
    """Persist feature stats to Redis (preferred) or to a local JSON file.

    Provide either `key` for Redis or a filesystem `path` for JSON output.
    """
    if key:
        r = get_redis_client(redis_url)
        r.set(key, json.dumps(stats))
        return {"backend": "redis", "key": key}
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        return {"backend": "file", "path": path}
    # Nothing persisted; return stats for further handling
    return {"backend": "none", "size": len(json.dumps(stats))}

