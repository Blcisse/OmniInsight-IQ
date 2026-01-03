from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


def prepare_interaction_matrix(
    df: pd.DataFrame,
    user_col: str,
    item_col: str,
    rating_col: str,
) -> Tuple[pd.DataFrame, pd.Index, pd.Index]:
    """Pivot interactions to a user-item matrix (NaN filled with 0).

    Returns (matrix_df, users_index, items_index)
    """
    mat = df.pivot_table(index=user_col, columns=item_col, values=rating_col, aggfunc="sum").fillna(0.0)
    return mat, mat.index, mat.columns


class PopularityRecommender:
    """Very simple popularity-based recommender.

    Ranks items by global average rating or total interactions.
    """

    def __init__(self, item_scores: pd.Series):
        self.item_scores = item_scores.sort_values(ascending=False)

    def recommend(self, seen_items: Optional[List[Any]] = None, k: int = 10) -> List[Tuple[Any, float]]:
        seen = set(seen_items or [])
        recs = [(item, float(score)) for item, score in self.item_scores.items() if item not in seen]
        return recs[:k]


def train_popularity_recommender(
    df: pd.DataFrame,
    item_col: str,
    rating_col: str,
    method: str = "sum",
) -> PopularityRecommender:
    """Train a popularity recommender by summing or averaging ratings per item."""
    if method == "mean":
        scores = df.groupby(item_col)[rating_col].mean()
    else:
        scores = df.groupby(item_col)[rating_col].sum()
    return PopularityRecommender(scores)


class ItemKNNRecommender:
    """Item-based KNN recommender using cosine similarity on item vectors."""

    def __init__(self, model: NearestNeighbors, item_embeddings: np.ndarray, items: List[Any]):
        self.model = model
        self.item_embeddings = item_embeddings
        self.items = items

    def similar_items(self, item_id: Any, top_k: int = 10) -> List[Tuple[Any, float]]:
        if item_id not in self.items:
            return []
        idx = self.items.index(item_id)
        distances, indices = self.model.kneighbors(self.item_embeddings[idx : idx + 1], n_neighbors=min(top_k + 1, len(self.items)))
        # skip self (first result)
        sims = []
        for dist, ind in zip(distances[0], indices[0]):
            if ind == idx:
                continue
            sims.append((self.items[ind], float(1 - dist)))  # cosine distance -> similarity
        return sims[:top_k]

    def recommend_for_user(self, user_ratings: Dict[Any, float], top_k: int = 10) -> List[Tuple[Any, float]]:
        """Score items by weighted sum of similarities to user's rated items."""
        scores: Dict[Any, float] = {}
        seen = set(user_ratings.keys())
        for item_id, weight in user_ratings.items():
            neighbors = self.similar_items(item_id, top_k=top_k * 2)
            for nid, sim in neighbors:
                if nid in seen:
                    continue
                scores[nid] = scores.get(nid, 0.0) + sim * float(weight)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]


def train_item_knn(
    df: pd.DataFrame,
    user_col: str,
    item_col: str,
    rating_col: str,
    *,
    k: int = 20,
) -> ItemKNNRecommender:
    """Train an item-based KNN recommender on item vectors (users as features)."""
    mat, _, items = prepare_interaction_matrix(df, user_col, item_col, rating_col)
    # Items as rows: transpose user-item matrix
    item_mat = mat.T.values  # shape: items x users
    knn = NearestNeighbors(metric="cosine", algorithm="auto")
    knn.fit(item_mat)
    return ItemKNNRecommender(knn, item_mat, list(items))


def train_recommendation_model(
    df: pd.DataFrame,
    *,
    algorithm: str = "popularity",
    user_col: Optional[str] = None,
    item_col: str,
    rating_col: str,
    method: str = "sum",
    k: int = 20,
) -> Tuple[Any, Dict[str, Any]]:
    """Train a recommendation model with a simple unified interface.

    - algorithm="popularity": trains PopularityRecommender (ignores user_col)
    - algorithm="item_knn": trains ItemKNNRecommender (requires user_col)
    Returns (model, meta)
    """
    algo = algorithm.lower()
    if algo == "popularity":
        model = train_popularity_recommender(df, item_col=item_col, rating_col=rating_col, method=method)
        meta = {"algorithm": "popularity", "item_col": item_col, "rating_col": rating_col, "method": method}
        return model, meta
    if algo == "item_knn":
        if not user_col:
            raise ValueError("user_col is required for item_knn algorithm")
        model = train_item_knn(df, user_col=user_col, item_col=item_col, rating_col=rating_col, k=k)
        meta = {"algorithm": "item_knn", "user_col": user_col, "item_col": item_col, "rating_col": rating_col, "k": k}
        return model, meta
    raise ValueError(f"Unsupported algorithm: {algorithm}")


def get_top_predictions(
    model: Any,
    *,
    k: int = 10,
    seen_items: Optional[List[Any]] = None,
    user_ratings: Optional[Dict[Any, float]] = None,
) -> List[Tuple[Any, float]]:
    """Return top-k recommendations from a trained model.

    - PopularityRecommender: ignores user_ratings, filters seen_items
    - ItemKNNRecommender: requires user_ratings mapping {item_id: rating/weight}
    """
    if isinstance(model, PopularityRecommender):
        return model.recommend(seen_items=seen_items, k=k)
    if isinstance(model, ItemKNNRecommender):
        if not user_ratings:
            raise ValueError("user_ratings are required for ItemKNNRecommender predictions")
        return model.recommend_for_user(user_ratings=user_ratings, top_k=k)
    raise ValueError("Unsupported model type for prediction")


def generate_recommendations(context: Dict[str, Any]) -> List[Tuple[Any, float]]:
    """High-level helper to train or use a model and generate recommendations.

    Context keys:
      - model (optional): pre-trained model instance
      - algorithm: 'popularity' | 'item_knn' (used if training)
      - df: pandas DataFrame (used if training)
      - user_col, item_col, rating_col: column names (for training)
      - method (popularity), k (item_knn): training params
      - top_k: number of recommendations
      - seen_items (optional): list of items to exclude
      - user_ratings (optional): dict item->weight for personalized KNN
    """
    model = context.get("model")
    top_k = int(context.get("top_k", 10))
    seen_items = context.get("seen_items")
    user_ratings = context.get("user_ratings")

    if model is None:
        df = context.get("df")
        if df is None or not isinstance(df, pd.DataFrame):
            raise ValueError("Context must include a DataFrame 'df' when 'model' is not provided")
        model, _meta = train_recommendation_model(
            df,
            algorithm=context.get("algorithm", "popularity"),
            user_col=context.get("user_col"),
            item_col=context.get("item_col"),
            rating_col=context.get("rating_col"),
            method=context.get("method", "sum"),
            k=int(context.get("k", 20)),
        )

    return get_top_predictions(model, k=top_k, seen_items=seen_items, user_ratings=user_ratings)
