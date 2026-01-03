from __future__ import annotations

from typing import Iterable, Dict, Any

import numpy as np
import pandas as pd

try:
    import plotly.graph_objects as go
except Exception:  # pragma: no cover
    go = None  # type: ignore

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None  # type: ignore

from sklearn.decomposition import PCA


def plotly_cluster_scatter(df: pd.DataFrame, feature_cols: Iterable[str], labels: Iterable[int]):
    """Return a Plotly 2D PCA scatter colored by cluster label."""
    if go is None:
        raise RuntimeError("plotly is not installed")
    X = df[list(feature_cols)].dropna().to_numpy(dtype=float)
    lab = np.asarray(list(labels))
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=coords[:, 0], y=coords[:, 1], mode="markers", marker=dict(color=lab, colorscale="Turbo"), name="clusters"))
    fig.update_layout(title="Clusters (PCA)", xaxis_title="PC1", yaxis_title="PC2", template="plotly_white")
    return fig


def matplotlib_cluster_scatter(df: pd.DataFrame, feature_cols: Iterable[str], labels: Iterable[int]):
    """Return a Matplotlib PCA scatter."""
    if plt is None:
        raise RuntimeError("matplotlib is not installed")
    X = df[list(feature_cols)].dropna().to_numpy(dtype=float)
    lab = np.asarray(list(labels))
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)
    plt.figure(figsize=(6, 5))
    sc = plt.scatter(coords[:, 0], coords[:, 1], c=lab, cmap="tab10", s=24, alpha=0.8)
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.title("Clusters (PCA)")
    plt.colorbar(sc, label="Cluster")
    plt.tight_layout()
    return plt


def recharts_cluster_distribution(labels: Iterable[int]) -> Dict[str, Any]:
    """Return distribution data for Recharts bar or pie charts."""
    lab = np.asarray(list(labels))
    unique, counts = np.unique(lab, return_counts=True)
    data = [{"cluster": int(u), "count": int(c)} for u, c in zip(unique, counts)]
    return {"data": data}


def get_cluster_visuals(
    cluster_id: int,
    *,
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    labels: Iterable[int],
    lib: str = "plotly",
    title: str | None = None,
):
    """Return a cluster scatter highlighting a specific cluster.

    - lib="plotly": returns a Plotly Figure with highlighted cluster points
    - lib="matplotlib": returns a Matplotlib plot handle
    - lib="recharts": returns distribution data including the requested cluster
    """
    lab = np.asarray(list(labels))
    mask = lab == int(cluster_id)
    X = df[list(feature_cols)].dropna().to_numpy(dtype=float)

    # Project to 2D
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)

    lib = (lib or "plotly").lower()
    if lib == "plotly":
        if go is None:
            raise RuntimeError("plotly is not installed")
        fig = go.Figure()
        # background others
        fig.add_trace(
            go.Scatter(
                x=coords[~mask, 0],
                y=coords[~mask, 1],
                mode="markers",
                marker=dict(color="#d1d5db"),
                name="Others",
            )
        )
        # highlighted cluster
        fig.add_trace(
            go.Scatter(
                x=coords[mask, 0],
                y=coords[mask, 1],
                mode="markers",
                marker=dict(color="#ef4444"),
                name=f"Cluster {cluster_id}",
            )
        )
        fig.update_layout(title=title or f"Cluster {cluster_id}", xaxis_title="PC1", yaxis_title="PC2", template="plotly_white")
        return fig

    if lib == "matplotlib":
        if plt is None:
            raise RuntimeError("matplotlib is not installed")
        plt.figure(figsize=(6, 5))
        plt.scatter(coords[~mask, 0], coords[~mask, 1], c="#d1d5db", s=20, label="Others")
        plt.scatter(coords[mask, 0], coords[mask, 1], c="#ef4444", s=24, label=f"Cluster {cluster_id}")
        plt.xlabel("PC1")
        plt.ylabel("PC2")
        plt.title(title or f"Cluster {cluster_id}")
        plt.legend()
        plt.tight_layout()
        return plt

    if lib == "recharts":
        dist = recharts_cluster_distribution(labels)
        return dist

    raise ValueError(f"Unknown visualization library: {lib}")


def generate_cluster_insights(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    labels: Iterable[int],
    top_n: int = 3,
) -> Dict[str, Any]:
    """Compute per-cluster summaries and top differentiating features.

    Returns a dict with keys:
      - clusters: List[{ cluster, count, feature_means: {feature: mean}, top_features: [(feature, zscore), ...] }]
      - global_means: { feature: mean }
    """
    cols = list(feature_cols)
    work = df[cols].copy()
    work = work.dropna(axis=0, how="any")
    lab = np.asarray(list(labels))
    if len(lab) != len(work):
        # Align length if labels were computed before NA drop
        lab = lab[: len(work)]

    global_means = work.mean().to_dict()
    global_stds = work.std(ddof=1).replace(0, np.nan)

    clusters: List[Dict[str, Any]] = []
    for c in sorted(np.unique(lab)):
        mask = lab == c
        grp = work[mask]
        means = grp.mean()
        # z-score of cluster mean vs overall distribution (per feature)
        zscores = ((means - work.mean()) / global_stds).replace([np.inf, -np.inf], np.nan).fillna(0.0)
        top = (
            zscores.abs().sort_values(ascending=False).head(max(1, top_n)).index.tolist()
        )
        top_list = [(f, float(zscores[f])) for f in top]
        clusters.append(
            {
                "cluster": int(c),
                "count": int(mask.sum()),
                "feature_means": {k: float(v) for k, v in means.items()},
                "top_features": top_list,
            }
        )

    return {"clusters": clusters, "global_means": {k: float(v) for k, v in global_means.items()}}
