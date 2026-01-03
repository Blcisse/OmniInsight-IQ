from __future__ import annotations

from typing import List, Tuple, Optional, Dict, Any, Iterable

import numpy as np
import pandas as pd


def item_scores_frame(recommendations: List[Tuple[str, float]]) -> pd.DataFrame:
    """Return a DataFrame of items and scores sorted descending.

    Useful for downstream visualization with any plotting library.
    Columns: ['item', 'score']
    """
    if not recommendations:
        return pd.DataFrame(columns=["item", "score"])
    items = [str(i) for i, _ in recommendations]
    scores = [float(s) for _, s in recommendations]
    df = pd.DataFrame({"item": items, "score": scores})
    return df.sort_values("score", ascending=False).reset_index(drop=True)


def cooccurrence_heatmap_data(
    co: pd.DataFrame,
    *,
    normalize: bool = False,
) -> Dict[str, Any]:
    """Prepare heatmap-friendly data from a co-occurrence matrix.

    Returns a dictionary with:
      - 'matrix': np.ndarray of values (optionally row-normalized)
      - 'x_labels': list of column labels
      - 'y_labels': list of row labels
    """
    if co is None or co.empty:
        return {"matrix": np.zeros((0, 0)), "x_labels": [], "y_labels": []}

    mat = co.values.astype(float)
    if normalize and mat.size:
        row_sums = mat.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        mat = mat / row_sums

    return {
        "matrix": mat,
        "x_labels": [str(c) for c in co.columns],
        "y_labels": [str(i) for i in co.index],
    }


def plot_recommendation_impact(
    df: pd.DataFrame,
    *,
    date_col: str,
    baseline_col: str,
    with_rec_col: str,
    rolling: Optional[int] = 7,
) -> pd.DataFrame:
    """Prepare impact-over-time data comparing baseline vs. with-recommendations.

    Returns a DataFrame with columns:
      [date, baseline, with_rec, delta, pct_change, baseline_roll?, with_rec_roll?, delta_roll?, pct_change_roll?]
    Only uses Pandas/NumPy so the caller can visualize with any library.
    """
    work = df[[date_col, baseline_col, with_rec_col]].dropna().copy()
    work[date_col] = pd.to_datetime(work[date_col])
    g = work.groupby(date_col, as_index=False).sum(numeric_only=True)
    g = g.rename(columns={baseline_col: "baseline", with_rec_col: "with_rec"})
    g["delta"] = g["with_rec"] - g["baseline"]
    with np.errstate(divide="ignore", invalid="ignore"):
        g["pct_change"] = (g["delta"] / g["baseline"]) * 100.0
    if rolling and rolling > 1:
        g = g.sort_values(date_col)
        g["baseline_roll"] = g["baseline"].rolling(rolling, min_periods=max(1, rolling // 2)).mean()
        g["with_rec_roll"] = g["with_rec"].rolling(rolling, min_periods=max(1, rolling // 2)).mean()
        g["delta_roll"] = g["with_rec_roll"] - g["baseline_roll"]
        with np.errstate(divide="ignore", invalid="ignore"):
            g["pct_change_roll"] = (g["delta_roll"] / g["baseline_roll"]) * 100.0
    return g.sort_values(date_col).reset_index(drop=True)


def show_rec_trends(
    df: pd.DataFrame,
    *,
    date_col: str,
    metric_col: str,
    by_col: Optional[str] = None,
    rolling: Optional[int] = 7,
) -> pd.DataFrame:
    """Prepare trend data for recommendation-related metrics.

    - If by_col is provided, returns a long-format DataFrame with grouped trends
      and optional rolling means per group.
    - Otherwise returns aggregated global trend with optional rolling mean.
    Output columns include: [date, metric, (by), metric_roll?].
    """
    work = df[[date_col, metric_col] + ([by_col] if by_col else [])].dropna().copy()
    work[date_col] = pd.to_datetime(work[date_col])
    if by_col:
        grouped = work.groupby([date_col, by_col], as_index=False)[metric_col].sum()
        grouped = grouped.rename(columns={metric_col: "metric"}).sort_values([by_col, date_col])
        if rolling and rolling > 1:
            grouped["metric_roll"] = (
                grouped.sort_values([by_col, date_col])
                .groupby(by_col)["metric"]
                .rolling(rolling, min_periods=max(1, rolling // 2))
                .mean()
                .reset_index(level=0, drop=True)
            )
        return grouped.reset_index(drop=True)
    agg = work.groupby(date_col, as_index=False)[metric_col].sum().rename(columns={metric_col: "metric"})
    agg = agg.sort_values(date_col)
    if rolling and rolling > 1:
        agg["metric_roll"] = agg["metric"].rolling(rolling, min_periods=max(1, rolling // 2)).mean()
    return agg.reset_index(drop=True)
