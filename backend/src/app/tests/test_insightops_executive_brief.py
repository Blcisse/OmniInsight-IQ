from datetime import date

import pytest
from fastapi.testclient import TestClient

from src.app.core.database import get_db
from src.app.main import app
from src.app.schemas.insightops_analytics import Anomaly, AnomalyResponse, DeltaSummary, EngagementSummary

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


@pytest.fixture
def mock_brief_services(monkeypatch):
    today = date.today()

    async def fake_kpi_summary(**kwargs):
        return DeltaSummary(
            latest_value=120.0,
            previous_value=100.0,
            absolute_delta=20.0,
            percent_delta=20.0,
            rolling_avg_7d_latest=110.0,
        )

    async def fake_engagement_summary(**kwargs):
        return EngagementSummary(
            total=100.0,
            average_per_day=10.0,
            last_day_value=12.0,
            health_score=85.0,
        )

    async def fake_anomalies(**kwargs):
        return AnomalyResponse(
            org_id=kwargs.get("org_id", "demo_org"),
            anomalies=[
                Anomaly(
                    type="kpi_spike",
                    severity="warning",
                    description="Test anomaly",
                    date=today,
                )
            ],
        )

    monkeypatch.setattr("src.app.services.insightops_executive_brief.get_kpi_summary", fake_kpi_summary)
    monkeypatch.setattr("src.app.services.insightops_executive_brief.get_engagement_summary", fake_engagement_summary)
    monkeypatch.setattr("src.app.services.insightops_executive_brief.get_anomalies", fake_anomalies)
    yield


def test_executive_brief_endpoint_returns_payload(mock_brief_services):
    resp = client.get("/insightops/executive-brief", params={"org_id": "demo_org", "window_days": 14})
    assert resp.status_code == 200
    body = resp.json()

    assert "priority_score" in body
    assert isinstance(body["insights"], list) and body["insights"]
    assert isinstance(body["risks"], list) and body["risks"]
    assert isinstance(body["opportunities"], list)

    # Deterministic rules: improving KPI + healthy engagement should create an opportunity
    assert any("Growth momentum" in opp["title"] for opp in body["opportunities"])
    # Anomalies present yields a risk
    assert any(risk["title"] == "Anomalies detected" for risk in body["risks"])


def test_executive_brief_handles_missing_data(monkeypatch):
    async def empty_kpi_summary(**kwargs):
        return DeltaSummary(
            latest_value=None,
            previous_value=None,
            absolute_delta=None,
            percent_delta=None,
            rolling_avg_7d_latest=None,
        )

    async def minimal_engagement_summary(**kwargs):
        return EngagementSummary(
            total=0.0,
            average_per_day=0.0,
            last_day_value=None,
            health_score=30.0,
        )

    async def no_anomalies(**kwargs):
        return AnomalyResponse(org_id=kwargs.get("org_id", "demo_org"), anomalies=[])

    monkeypatch.setattr("src.app.services.insightops_executive_brief.get_kpi_summary", empty_kpi_summary)
    monkeypatch.setattr("src.app.services.insightops_executive_brief.get_engagement_summary", minimal_engagement_summary)
    monkeypatch.setattr("src.app.services.insightops_executive_brief.get_anomalies", no_anomalies)

    resp = client.get("/insightops/executive-brief", params={"org_id": "demo_org", "window_days": 7})
    assert resp.status_code == 200
    body = resp.json()

    assert isinstance(body["notes"], list)
    assert any("No KPI data available for revenue" in note for note in body["notes"])
    # No anomalies + limited signals should still return a payload
    assert body["risks"] == []
    assert body["opportunities"] == []
