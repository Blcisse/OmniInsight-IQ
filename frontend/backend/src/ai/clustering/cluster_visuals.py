from __future__ import annotations

from typing import Iterable, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline

from .cluster_model import build_feature_matrix


def plot_clusters_2d(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    pipeline: Pipeline,
    *,
    title: Optional[str] = None,
):
    """Project features to 2D with PCA and scatter plot colored by cluster label."""
    X, _, _ = build_feature_matrix(df, feature_cols)
    # Get labels from fitted KMeans inside pipeline
    try:
        labels = pipeline.named_steps["kmeans"].labels_
    except Exception as e:
        raise ValueError("Provided pipeline must contain a fitted 'kmeans' step") from e

    scaler = pipeline.named_steps.get("scale")
    X_scaled = scaler.transform(X) if scaler is not None else X
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X_scaled)

    plt.figure(figsize=(6, 5))
    scatter = plt.scatter(coords[:, 0], coords[:, 1], c=labels, cmap="tab10", s=24, alpha=0.8)
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    if title:
        plt.title(title)
    plt.colorbar(scatter, label="Cluster")
    plt.tight_layout()
    return plt


def plot_elbow(results):
    """Plot inertia vs k for elbow method results."""
    ks = [r["k"] for r in results]
    inertia = [r["inertia"] for r in results]
    plt.figure(figsize=(6, 4))
    plt.plot(ks, inertia, marker="o")
    plt.xlabel("k (clusters)")
    plt.ylabel("Inertia")
    plt.title("Elbow Curve")
    plt.grid(True, linestyle=":", alpha=0.5)
    plt.tight_layout()
    return plt


def plot_clusters(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    pipeline: Pipeline,
    *,
    title: Optional[str] = None,
):
    """Alias for plot_clusters_2d for a simpler API name."""
    return plot_clusters_2d(df, feature_cols, pipeline, title=title)


def plot_cluster_distribution(labels):
    """Plot a simple bar chart of cluster label distribution."""
    labels = np.asarray(labels)
    unique, counts = np.unique(labels, return_counts=True)
    plt.figure(figsize=(6, 4))
    plt.bar(unique, counts)
    plt.xlabel("Cluster")
    plt.ylabel("Count")
    plt.title("Cluster Distribution")
    plt.tight_layout()
    return plt
