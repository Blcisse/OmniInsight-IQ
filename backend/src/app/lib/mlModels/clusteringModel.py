from __future__ import annotations

from typing import List, Dict, Any, Optional, Sequence

import numpy as np
from sklearn.cluster import KMeans
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.sales import SaleORM
from ...models.marketing import CampaignORM


async def kmeans_segments(
    db: AsyncSession,
    n_clusters: int = 4,
    entity: str = "product",
) -> List[Dict[str, Any]]:
    """Cluster products or campaigns by ROI, sales volume, and engagement.

    entity: "product" (aggregates by product_id from sales) or "campaign"
    Features used:
      - sales_volume: SUM(units_sold)
      - revenue: SUM(revenue)
      - roi: for campaigns, AVG(roi); for products, revenue proxy per unit
      - engagement: for campaigns, clicks/impressions proxy if available
    Returns clusters with centroids and members summary counts.
    """
    if entity == "campaign":
        # Assemble campaign feature matrix
        stmt = select(
            CampaignORM.id,
            func.coalesce(CampaignORM.impressions, 0).label("impressions"),
            func.coalesce(CampaignORM.clicks, 0).label("clicks"),
            func.coalesce(CampaignORM.spend, 0.0).label("spend"),
            func.coalesce(CampaignORM.roi, 0.0).label("roi"),
        )
        res = await db.execute(stmt)
        rows = res.all()
        if not rows:
            return []
        X = []
        ids = []
        for cid, impressions, clicks, spend, roi in rows:
            engagement = (clicks / impressions) if impressions else 0.0
            X.append([float(impressions), float(clicks), float(spend), float(roi), float(engagement)])
            ids.append(int(cid))
    else:
        # Aggregate by product_id from sales
        stmt = (
            select(
                SaleORM.product_id,
                func.coalesce(func.sum(SaleORM.units_sold), 0).label("units"),
                func.coalesce(func.sum(SaleORM.revenue), 0.0).label("revenue"),
            )
            .group_by(SaleORM.product_id)
        )
        res = await db.execute(stmt)
        rows = res.all()
        if not rows:
            return []
        X = []
        ids = []
        for pid, units, revenue in rows:
            roi_proxy = float(revenue) / float(units) if units else float(revenue)
            X.append([float(units), float(revenue), float(roi_proxy)])
            ids.append(str(pid))

    X_arr = np.array(X, dtype=float)
    # Normalize features to comparable scale
    eps = 1e-9
    means = X_arr.mean(axis=0)
    stds = X_arr.std(axis=0) + eps
    X_norm = (X_arr - means) / stds

    k = min(n_clusters, len(X_norm))
    model = KMeans(n_clusters=k, n_init="auto", random_state=42)
    labels = model.fit_predict(X_norm)

    clusters: List[Dict[str, Any]] = []
    for c in range(k):
        idxs = np.where(labels == c)[0].tolist()
        members = [ids[i] for i in idxs]
        centroid = (model.cluster_centers_[c] * stds + means).tolist()
        clusters.append(
            {
                "cluster": c,
                "size": len(idxs),
                "centroid": centroid,
                "members": members[:50],  # cap for payload size
            }
        )

    return clusters


def mock_customer_segments() -> List[Dict[str, Any]]:
    # Keep the mock for environments without a DB
    return [
        {
            "segment_id": "A",
            "name": "High-Value Loyalists",
            "size": 0.18,
            "avg_order_value": 185.4,
            "purchase_freq_per_month": 2.3,
            "churn_risk": 0.08,
            "traits": ["subscribed", "multi-channel", "high_roas"],
        },
        {
            "segment_id": "B",
            "name": "Bargain Hunters",
            "size": 0.27,
            "avg_order_value": 48.2,
            "purchase_freq_per_month": 1.1,
            "churn_risk": 0.22,
            "traits": ["price_sensitive", "coupon_users"],
        },
    ]
