import pandas as pd
from src.ai.clustering.cluster_model import train_kmeans, summarize_clusters


def test_clustering_and_summary():
    # Two obvious clusters
    df = pd.DataFrame({
        "units": [1, 2, 1, 2, 100, 110, 95, 105],
        "revenue": [10, 20, 12, 18, 1000, 1100, 950, 1050],
        "roi": [1.0, 1.1, 0.9, 1.2, 3.0, 2.8, 3.2, 3.1],
    })
    pipe, labels, meta = train_kmeans(df, ["units", "revenue", "roi"], n_clusters=2)
    summary = summarize_clusters(df, labels, ["units", "revenue", "roi"])  # type: ignore
    assert len(summary) >= 2
    assert {"cluster", "count"}.issubset(summary.columns)

