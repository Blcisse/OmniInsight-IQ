import pytest
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4
from fastapi.testclient import TestClient

from src.app.core.database import get_db
from src.app.main import app
from src.app.schemas.insightops_executive_brief import ExecutiveBriefResponse

pytestmark = pytest.mark.unit
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


def _fake_brief() -> ExecutiveBriefResponse:
  return ExecutiveBriefResponse(
    org_id="demo_org",
    generated_at=datetime.utcnow(),
    window_days=14,
    priority_score=55,
    priority_level="medium",
    insights=[],
    risks=[],
    opportunities=[],
    notes=[],
  )


def test_executive_brief_persist_false_does_not_write(monkeypatch):
  async def fake_brief_builder(**kwargs):
    return _fake_brief()

  async def should_not_be_called(*args, **kwargs):
    raise AssertionError("save_exec_brief should not be called when persist is False")

  monkeypatch.setattr("src.app.services.insightops_executive_brief.build_executive_brief", fake_brief_builder)
  monkeypatch.setattr("src.app.services.insightops_exec_persistence.save_exec_brief", should_not_be_called)

  resp = client.get("/insightops/executive-brief", params={"persist": False})
  assert resp.status_code == 200
  body = resp.json()
  assert body.get("saved") in (None, False)


def test_executive_brief_persist_true_writes(monkeypatch):
  async def fake_brief_builder(**kwargs):
    return _fake_brief()

  saved_calls = {}

  class StubRecord:
    def __init__(self):
      self.id = uuid4()
      self.org_id = "demo_org"
      self.summary_type = "board"
      self.period_start = date.today() - timedelta(days=14)
      self.period_end = date.today()
      self.summary_text = "stub"
      self.payload_json = {}
      self.model_name = None
      self.created_at = datetime.utcnow()
      self.updated_at = datetime.utcnow()

  async def fake_save_exec_brief(db, org_id, brief, summary_type, **kwargs):
    saved_calls["called"] = True
    return StubRecord()

  monkeypatch.setattr("src.app.services.insightops_executive_brief.build_executive_brief", fake_brief_builder)
  monkeypatch.setattr("src.app.services.insightops_exec_persistence.save_exec_brief", fake_save_exec_brief)

  resp = client.get("/insightops/executive-brief", params={"persist": True, "summary_type": "board"})
  assert resp.status_code == 200
  body = resp.json()
  assert saved_calls.get("called") is True
  assert body.get("saved") is True
  assert body.get("summary_id")


def test_latest_executive_summary_endpoint(monkeypatch):
  class StubRecord:
    def __init__(self):
      self.id = uuid4()
      self.period_start = date.today() - timedelta(days=7)
      self.period_end = date.today()
      self.org_id = "demo_org"
      self.summary_type = "board"
      self.summary_text = "Latest summary"
      self.payload_json = None
      self.model_name = None
      self.created_at = datetime.utcnow()
      self.updated_at = datetime.utcnow()

  async def fake_latest(*args, **kwargs):
    return StubRecord()

  monkeypatch.setattr("src.app.services.insightops_exec_persistence.get_latest_exec_summary", fake_latest)

  resp = client.get("/insightops/executive-summaries/latest", params={"org_id": "demo_org"})
  assert resp.status_code == 200
  body = resp.json()
  assert body["org_id"] == "demo_org"
  assert body["summary_text"] == "Latest summary"
  assert body.get("payload_json") is None


def test_list_executive_summaries_endpoint(monkeypatch):
  def _make_record(label: str):
    ns = SimpleNamespace()
    ns.id = uuid4()
    ns.period_start = date.today() - timedelta(days=14)
    ns.period_end = date.today()
    ns.org_id = "demo_org"
    ns.summary_type = "board"
    ns.summary_text = label
    ns.payload_json = None
    ns.model_name = None
    ns.created_at = datetime.utcnow()
    ns.updated_at = datetime.utcnow()
    return ns

  async def fake_list(*args, **kwargs):
    return [_make_record("Summary A"), _make_record("Summary B")]

  monkeypatch.setattr("src.app.services.insightops_exec_persistence.list_exec_summaries", fake_list)

  resp = client.get("/insightops/executive-summaries", params={"org_id": "demo_org", "limit": 2})
  assert resp.status_code == 200
  body = resp.json()
  assert isinstance(body, list)
  assert len(body) == 2
  assert body[0]["summary_text"] == "Summary A"
