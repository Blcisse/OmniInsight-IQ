from __future__ import annotations

from typing import Dict, Iterable, List, Tuple, Any, Optional

import pandas as pd
import numpy as np


def top_selling_by_category(
    sales_df: pd.DataFrame,
    category_col: str,
    product_col: str,
    value_col: str,
    n: int = 5,
) -> Dict[str, List[Tuple[str, float]]]:
    """Return top-N products per category based on aggregated value_col (e.g., revenue or units)."""
    grouped = sales_df.groupby([category_col, product_col])[value_col].sum().reset_index()
    result: Dict[str, List[Tuple[str, float]]] = {}
    for cat, g in grouped.groupby(category_col):
        top = g.sort_values(value_col, ascending=False).head(n)
        result[str(cat)] = list(zip(top[product_col].astype(str), top[value_col].astype(float)))
    return result


def build_cooccurrence(
    order_items_df: pd.DataFrame,
    order_id_col: str,
    product_col: str,
) -> pd.DataFrame:
    """Build a product co-occurrence matrix from order-item rows."""
    # For each order, mark product presence
    basket = (
        order_items_df.assign(val=1)
        .pivot_table(index=order_id_col, columns=product_col, values="val", fill_value=0, aggfunc="sum")
    )
    # Co-occurrence = item-item dot product across orders
    co = basket.T.dot(basket)
    # Zero diagonal for clarity (self-cooccurrence not useful for cross-sell)
    for i in range(co.shape[0]):
        co.iat[i, i] = 0
    return co


def cross_sell_rules(
    order_items_df: pd.DataFrame,
    order_id_col: str,
    product_col: str,
    min_support: int = 2,
    top_k: int = 5,
) -> Dict[str, List[Tuple[str, int]]]:
    """Generate simple cross-sell suggestions using co-occurrence counts.

    Returns mapping product -> list of (other_product, cooccurrence_count), sorted by count.
    """
    co = build_cooccurrence(order_items_df, order_id_col, product_col)
    rules: Dict[str, List[Tuple[str, int]]] = {}
    items = list(co.index.astype(str))
    for i, item in enumerate(items):
        counts = co.iloc[i]
        recs = (
            counts[counts >= min_support]
            .sort_values(ascending=False)
            .head(top_k)
            .astype(int)
        )
        rules[item] = list(zip(recs.index.astype(str).tolist(), recs.values.tolist()))
    return rules


def define_rec_rules(
    rules: Optional[List[Dict[str, Any]]] = None,
    *,
    top_n: int = 5,
    min_support: int = 2,
    top_k_cross: int = 5,
) -> List[Dict[str, Any]]:
    """Define a list of rule configurations to be applied.

    Each rule config is a dict with keys: {'type': <name>, 'params': {...}}.
    Supported types:
      - 'top_selling_by_category' with params: category_col, product_col, value_col, n
      - 'cross_sell' with params: order_id_col, product_col, min_support, top_k
    """
    if rules is not None:
        return rules
    # Provide sensible defaults; caller can override with explicit rules
    return [
        {"type": "top_selling_by_category", "params": {"n": int(top_n)}},
        {"type": "cross_sell", "params": {"min_support": int(min_support), "top_k": int(top_k_cross)}},
    ]


def apply_rec_rules(
    rules: List[Dict[str, Any]],
    *,
    sales_df: Optional[pd.DataFrame] = None,
    order_items_df: Optional[pd.DataFrame] = None,
    category_col: str = "category",
    product_col: str = "product_id",
    value_col: str = "revenue",
    order_id_col: str = "order_id",
) -> Dict[str, Any]:
    """Apply defined recommendation rules to provided dataframes.

    Returns a dict mapping rule type to its result payload.
    """
    results: Dict[str, Any] = {}
    for rule in rules:
        rtype = rule.get("type")
        params = {**rule.get("params", {})}
        if rtype == "top_selling_by_category":
            if sales_df is None:
                continue
            n = int(params.get("n", 5))
            res = top_selling_by_category(
                sales_df,
                category_col=params.get("category_col", category_col),
                product_col=params.get("product_col", product_col),
                value_col=params.get("value_col", value_col),
                n=n,
            )
            results[rtype] = res
        elif rtype == "cross_sell":
            if order_items_df is None:
                continue
            res = cross_sell_rules(
                order_items_df,
                order_id_col=params.get("order_id_col", order_id_col),
                product_col=params.get("product_col", product_col),
                min_support=int(params.get("min_support", 2)),
                top_k=int(params.get("top_k", 5)),
            )
            results[rtype] = res
        else:
            # Unknown rule; skip
            continue
    return results


def evaluate_rec_performance(
    ground_truth: Dict[Any, Iterable[Any]],
    recommendations: Dict[Any, Iterable[Any]],
    *,
    k: int = 5,
) -> Dict[str, float]:
    """Evaluate recommendation performance with precision@k, recall@k, hit-rate, MAP@k.

    ground_truth: mapping user -> iterable of true items
    recommendations: mapping user -> ordered iterable of recommended items
    """
    users = set(ground_truth.keys()) & set(recommendations.keys())
    if not users:
        return {"precision@k": 0.0, "recall@k": 0.0, "hit_rate": 0.0, "map@k": 0.0}

    precisions: List[float] = []
    recalls: List[float] = []
    hits: List[int] = []
    maps: List[float] = []

    for u in users:
        gt = list(dict.fromkeys(ground_truth.get(u, [])))  # unique preserve order
        rec = list(dict.fromkeys(recommendations.get(u, [])))[:k]
        gt_set = set(gt)
        if not rec:
            precisions.append(0.0)
            recalls.append(0.0)
            hits.append(0)
            maps.append(0.0)
            continue

        hit_flags = [1 if r in gt_set else 0 for r in rec]
        hit_count = int(sum(hit_flags))
        precisions.append(hit_count / max(1, len(rec)))
        recalls.append(hit_count / max(1, len(gt)))
        hits.append(1 if hit_count > 0 else 0)

        # MAP@k
        cum_hits = 0
        prec_sum = 0.0
        for i, flag in enumerate(hit_flags, start=1):
            if flag:
                cum_hits += 1
                prec_sum += cum_hits / i
        denom = min(len(gt), len(rec))
        maps.append(prec_sum / denom if denom > 0 else 0.0)

    return {
        "precision@k": float(np.mean(precisions)),
        "recall@k": float(np.mean(recalls)),
        "hit_rate": float(np.mean(hits)),
        "map@k": float(np.mean(maps)),
    }
