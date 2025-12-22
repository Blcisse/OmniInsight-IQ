import json
import os
import types

import pytest
from fastapi.testclient import TestClient


# Import the FastAPI app
from src.app.main import app

pytestmark = pytest.mark.integration

client = TestClient(app)


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_sales_endpoints_list_and_create():
    # List should return a list
    resp = client.get("/api/sales/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)

    # Create a new sale
    payload = {"item": "Test Widget", "amount": 12.5, "customer": "QA"}
    resp2 = client.post("/api/sales/", json=payload)
    assert resp2.status_code == 201
    created = resp2.json()
    assert created["item"] == payload["item"]
    assert created["amount"] == payload["amount"]
    assert "id" in created


def test_analytics_routes():
    resp = client.get("/api/analytics/")
    assert resp.status_code == 200
    body = resp.json()
    assert "total_sales" in body and "by_day" in body
    assert isinstance(body["by_day"], list)

    # Predict endpoint
    resp2 = client.get("/api/analytics/predict?horizon_days=5")
    assert resp2.status_code == 200
    pred = resp2.json()
    assert "forecast" in pred
    assert len(pred["forecast"]) == 5


def test_marketing_routes():
    resp = client.get("/api/marketing/campaign-metrics")
    assert resp.status_code == 200
    metrics = resp.json()
    assert isinstance(metrics, list)
    if metrics:
        m = metrics[0]
        assert "campaign_id" in m and "impressions" in m

    resp2 = client.get("/api/marketing/conversions")
    assert resp2.status_code == 200
    conversions = resp2.json()
    assert isinstance(conversions, list)


def test_insights_route():
    resp = client.get("/api/insights/")
    assert resp.status_code == 200
    insights = resp.json()
    assert isinstance(insights, list)
    if insights:
        assert "recommendation" in insights[0]


def test_load_mock_data_files_exist():
    # Ensure mock JSON files are present and valid JSON
    base = os.path.join("src", "app", "data")
    for fname in ("sales.json", "marketing.json", "analytics.json"):
        path = os.path.join(base, fname)
        assert os.path.exists(path), f"Missing {fname}"
        with open(path, "r", encoding="utf-8") as f:
            json.load(f)
