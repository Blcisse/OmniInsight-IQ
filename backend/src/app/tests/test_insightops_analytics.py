from datetime import date

import pytest
from fastapi.testclient import TestClient

from src.app.main import app
from src.app.core.database import get_db
from src.app.schemas.insightops_analytics import (
    Anomaly,
    AnomalyResponse,
    SeriesPoint,
    SeriesResponse,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_db_dependency():
    async def _dummy_db():
        class _DummySession:
            pass

        yield _DummySession()

    app.dependency_overrides[get_db] = _dummy_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(autouse=True)
def mock_insightops_services(monkeypatch):
    today = date.today()

    async def fake_kpi_series(**kwargs):
        return SeriesResponse(
            org_id=kwargs.get("org_id", "demo_org"),
            key=kwargs.get("metric_key", "revenue"),
            start_date=today,
            end_date=today,
            points=[SeriesPoint(date=today, value=123.0)],
        )

    async def fake_signal_series(**kwargs):
        return SeriesResponse(
            org_id=kwargs.get("org_id", "demo_org"),
            key=kwargs.get("signal_key", "touches"),
            start_date=today,
            end_date=today,
            points=[SeriesPoint(date=today, value=45.0)],
        )

    async def fake_anomalies(**kwargs):
        return AnomalyResponse(
            org_id=kwargs.get("org_id", "demo_org"),
            anomalies=[
                Anomaly(type="kpi_spike", severity="warning", description="Test anomaly", date=today)
            ],
        )

    monkeypatch.setattr("src.app.services.insightops_analytics.get_kpi_series", fake_kpi_series)
    monkeypatch.setattr("src.app.services.insightops_engagement.get_signal_series", fake_signal_series)
    monkeypatch.setattr("src.app.services.insightops_anomalies.get_anomalies", fake_anomalies)
    yield


def test_insightops_health():
    resp = client.get("/insightops/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("domain") == "insightops-studio"
    assert body.get("status") == "ok"


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
