import pandas as pd
from src.ai.recommendation_engine.rec_core import train_recommendation_model, get_top_predictions


def test_recommendation_popularity():
    df = pd.DataFrame({
        "user": ["u1", "u2", "u1", "u3"],
        "item": ["i1", "i1", "i2", "i3"],
        "rating": [1, 1, 1, 1],
    })
    model, meta = train_recommendation_model(df, algorithm="popularity", item_col="item", rating_col="rating")
    recs = get_top_predictions(model, k=2)
    assert len(recs) >= 1


def test_recommendation_item_knn():
    df = pd.DataFrame({
        "user": ["u1", "u1", "u2", "u2"],
        "item": ["i1", "i2", "i1", "i3"],
        "rating": [5, 4, 5, 3],
    })
    model, meta = train_recommendation_model(df, algorithm="item_knn", user_col="user", item_col="item", rating_col="rating")
    recs = get_top_predictions(model, k=2, user_ratings={"i1": 5})
    assert isinstance(recs, list)

