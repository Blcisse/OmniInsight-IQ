from fastapi.testclient import TestClient
import pytest

from src.app.main import app
from src.app.core.database import get_db
from src.app.schemas.insightops_executive_brief import ExecutiveBriefResponse


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
def mock_brief(monkeypatch):
    async def fake_brief(**kwargs):
        return ExecutiveBriefResponse(
            org_id=kwargs.get("org_id", "demo_org"),
            generated_at="2024-01-01T00:00:00Z",
            window_days=kwargs.get("window_days", 14),
            priority_score=50,
            priority_level="medium",
            insights=[],
            risks=[],
            opportunities=[],
            notes=[],
        )

    monkeypatch.setattr("src.app.services.insightops_executive_brief.build_executive_brief", fake_brief)
    yield


client = TestClient(app)


def test_health_ok():
    resp = client.get("/insightops/health")
    assert resp.status_code == 200
    assert resp.json().get("status") == "ok"


def test_executive_brief_smoke(mock_brief):
    resp = client.get("/insightops/executive-brief", params={"org_id": "demo_org", "window_days": 14})
    assert resp.status_code == 200
    body = resp.json()
    for key in ["priority_score", "priority_level", "insights", "risks", "opportunities", "notes"]:
        assert key in body
