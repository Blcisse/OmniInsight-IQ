from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def test_insightops_health():
    resp = client.get("/insightops/health")
    assert resp.status_code == 200
    assert resp.json().get("domain") == "insightops-studio"


def test_kpi_summary_includes_latest():
    resp = client.get("/insightops/analytics/kpis/summary", params={"org_id": "demo_org", "metric_key": "revenue"})
    assert resp.status_code == 200
    body = resp.json()
    assert "latest_value" in body


def test_engagement_summary_includes_health():
    resp = client.get(
        "/insightops/analytics/engagement/summary", params={"org_id": "demo_org", "signal_key": "touches"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "health_score" in body


def test_anomalies_returns_list():
    resp = client.get("/insightops/analytics/anomalies", params={"org_id": "demo_org"})
    assert resp.status_code == 200
    body = resp.json()
    assert "anomalies" in body
    assert isinstance(body["anomalies"], list)
