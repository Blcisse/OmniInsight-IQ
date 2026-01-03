import pytest

try:
    from backend.src.app.main import app as backend_app  # type: ignore
except Exception:
    from src.app.main import app as backend_app  # type: ignore

from fastapi.testclient import TestClient


def test_model_inference_api():
    client = TestClient(backend_app)
    # Expect 422 for missing body; endpoint exists
    resp = client.post("/api/model-inference/predict", json={})
    assert resp.status_code in (200, 400, 422)


def test_forecast_endpoint():
    client = TestClient(backend_app)
    payload = {
        "model_name": "dummy",
        "timeframe": 3,
        "history": [{"date": "2025-01-01", "target": 1}, {"date": "2025-01-02", "target": 2}],
        "date_col": "date",
        "target_col": "target",
    }
    resp = client.post("/api/model-inference/forecast", json=payload)
    assert resp.status_code in (200, 400)


def test_recommendation_endpoint():
    client = TestClient(backend_app)
    payload = {
        "algorithm": "popularity",
        "records": [
            {"user": "u1", "item": "i1", "rating": 1},
            {"user": "u2", "item": "i2", "rating": 1},
        ],
        "item_col": "item",
        "rating_col": "rating",
        "top_k": 2,
    }
    resp = client.post("/api/model-inference/recommend", json=payload)
    assert resp.status_code in (200, 400)

