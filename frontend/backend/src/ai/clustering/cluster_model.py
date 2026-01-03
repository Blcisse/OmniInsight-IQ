from __future__ import annotations

from typing import Iterable, List, Tuple, Optional, Dict, Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def build_feature_matrix(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    drop_na: bool = True,
) -> Tuple[np.ndarray, List[str], pd.DataFrame]:
    """Extract a numeric matrix X from DataFrame columns.

    Returns (X, feature_names, clean_df). If drop_na is True, rows with any NA
    in the selected features are dropped.
    """
    cols = list(feature_cols)
    work = df[cols].copy()
    if drop_na:
        work = work.dropna(axis=0, how="any")
    X = work.to_numpy(dtype=float)
    return X, cols, work


def train_kmeans(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    n_clusters: int = 4,
    random_state: int = 42,
) -> Tuple[Pipeline, List[int], Dict[str, Any]]:
    """Train a KMeans clustering pipeline with scaling.

    Returns (pipeline, labels, meta) with meta including inertia and silhouette.
    """
    X, cols, _ = build_feature_matrix(df, feature_cols)
    k = max(1, min(n_clusters, len(X)))
    pipe = Pipeline(
        steps=[
            ("scale", StandardScaler()),
            ("kmeans", KMeans(n_clusters=k, n_init="auto", random_state=random_state)),
        ]
    )
    pipe.fit(X)
    labels = pipe.named_steps["kmeans"].labels_.tolist()
    inertia = float(pipe.named_steps["kmeans"].inertia_)
    try:
        sil = float(silhouette_score(X, labels)) if k > 1 and len(X) > k else np.nan
    except Exception:
        sil = np.nan
    meta = {"inertia": inertia, "silhouette": sil, "features": cols}
    return pipe, labels, meta


def elbow_curve(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    k_range: Iterable[int] = range(1, 11),
    random_state: int = 42,
) -> List[Dict[str, float]]:
    """Compute inertia across a range of k for elbow method visualization."""
    X, _, _ = build_feature_matrix(df, feature_cols)
    results: List[Dict[str, float]] = []
    for k in k_range:
        k = int(k)
        if k < 1 or k > len(X):
            continue
        km = KMeans(n_clusters=k, n_init="auto", random_state=random_state)
        km.fit(StandardScaler().fit_transform(X))
        results.append({"k": float(k), "inertia": float(km.inertia_)})
    return results


def run_kmeans(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    n_clusters: int = 4,
    random_state: int = 42,
) -> Tuple[Pipeline, List[int], Dict[str, Any]]:
    """Convenience wrapper around train_kmeans."""
    return train_kmeans(df, feature_cols, n_clusters=n_clusters, random_state=random_state)


def run_dbscan(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    *,
    eps: float = 0.5,
    min_samples: int = 5,
) -> Tuple[Pipeline, List[int], Dict[str, Any]]:
    """Fit a DBSCAN clustering pipeline.

    Meta includes cluster_count (excluding noise) and noise_count (# of -1 labels).
    Silhouette is reported when there are at least 2 clusters (excluding noise).
    """
    X, cols, _ = build_feature_matrix(df, feature_cols)
    pipe = Pipeline(steps=[("scale", StandardScaler()), ("dbscan", DBSCAN(eps=eps, min_samples=min_samples))])
    pipe.fit(X)
    labels = pipe.named_steps["dbscan"].labels_.tolist()
    unique = set(labels)
    cluster_count = len([c for c in unique if c != -1])
    noise_count = sum(1 for l in labels if l == -1)
    try:
        sil = float(silhouette_score(StandardScaler().fit_transform(X), labels)) if cluster_count >= 2 else float("nan")
    except Exception:
        sil = float("nan")
    meta = {
        "algorithm": "dbscan",
        "eps": float(eps),
        "min_samples": int(min_samples),
        "cluster_count": int(cluster_count),
        "noise_count": int(noise_count),
        "silhouette": sil,
        "features": cols,
        "inertia": None,
    }
    return pipe, labels, meta


def predict_cluster(pipeline: Pipeline, df: pd.DataFrame, feature_cols: Iterable[str]) -> Tuple[List[int], pd.DataFrame]:
    """Predict cluster labels for new data using a fitted pipeline.

    Supports pipelines with a 'kmeans' step. Returns (labels, clean_df) where
    clean_df is the DataFrame of rows actually used (after dropping NA in features).
    """
    X, cols, clean = build_feature_matrix(df, feature_cols, drop_na=True)
    # Prefer scaled data if scaler exists
    scaler = pipeline.named_steps.get("scale")
    if "kmeans" in pipeline.named_steps:
        X_in = scaler.transform(X) if scaler is not None else X
        labels = pipeline.named_steps["kmeans"].predict(X_in).tolist()
        return labels, clean
    raise NotImplementedError("predict_cluster currently supports KMeans pipelines only")


def summarize_clusters(
    df: pd.DataFrame,
    labels: List[int],
    feature_cols: Iterable[str],
) -> pd.DataFrame:
    """Summarize clusters with counts and mean of each feature.

    Uses the same NA handling as training (rows with NA in features are dropped).
    """
    X, cols, clean = build_feature_matrix(df, feature_cols, drop_na=True)
    if len(labels) != len(clean):
        raise ValueError("Length of labels must match number of rows used after NA filtering")
    work = clean.copy()
    work["cluster"] = labels
    rows: List[Dict[str, Any]] = []
    for cluster_id, grp in work.groupby("cluster"):
        row: Dict[str, Any] = {"cluster": int(cluster_id), "count": int(len(grp))}
        for c in cols:
            row[f"{c}_mean"] = float(np.mean(grp[c].values)) if len(grp) else float("nan")
        rows.append(row)
    out = pd.DataFrame(rows).sort_values("cluster").reset_index(drop=True)
    return out
