import pytest
from fastapi.testclient import TestClient

from src.app.main import app
from src.app.routers.insightops_router import get_db_optional


pytestmark = pytest.mark.unit
client = TestClient(app)


@pytest.fixture(autouse=True)
def override_db_optional():
    async def _no_db():
        yield None

    app.dependency_overrides[get_db_optional] = _no_db
    yield
    app.dependency_overrides.pop(get_db_optional, None)


@pytest.fixture
def fail_if_db(monkeypatch):
    def _raise(*args, **kwargs):
        raise AssertionError("DB access should be bypassed in demo mode")

    monkeypatch.setattr("src.app.services.insightops_executive_brief.get_kpi_summary", _raise)
    monkeypatch.setattr("src.app.services.insightops_executive_brief.get_engagement_summary", _raise)
    monkeypatch.setattr("src.app.services.insightops_executive_brief.get_anomalies", _raise)
    yield


def test_demo_mode_returns_driver_and_narrative_without_db(fail_if_db):
    resp = client.get(
        "/insightops/executive-brief",
        params={"org_id": "demo_org", "window_days": 14, "demo_mode": True, "demo_profile": "EXEC_REVENUE_RISK"},
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["driver_attribution"] is not None
    assert body["prioritized_insights"]
    assert body["executive_narrative"] is not None
    assert body["top_drivers"] is not None
    assert body["priority_focus"] is not None


def test_invalid_demo_profile_returns_400():
    resp = client.get(
        "/insightops/executive-brief",
        params={"org_id": "demo_org", "window_days": 14, "demo_mode": True, "demo_profile": "UNKNOWN_PROFILE"},
    )
    assert resp.status_code == 400
    assert "demo_profile" in resp.json().get("detail", "")


def test_demo_mode_defaults_to_revenue_risk_profile(fail_if_db):
    resp = client.get("/insightops/executive-brief", params={"org_id": "demo_org", "window_days": 7, "demo_mode": True})
    assert resp.status_code == 200
    body = resp.json()

    assert body["driver_attribution"] is not None
    assert body["executive_narrative"] is not None
    assert body["prioritized_insights"]
