import pytest
from fastapi.testclient import TestClient

from src.app.main import app


@pytest.mark.parametrize(
    "path",
    [
        "/health",
        "/api/sales/",
        "/api/marketing/campaign-metrics",
        "/api/analytics/",
        "/api/analytics/predict",
        "/api/insights/",
    ],
)
def test_backend_endpoints_basic(path):
    client = TestClient(app)
    resp = client.get(path)
    # Some endpoints may be empty but should not 500
    assert resp.status_code in (200, 201, 204, 422)


def test_reports_generate_csv():
    client = TestClient(app)
    resp = client.get("/api/reports/generate?fmt=csv")
    # If router is wired, we should get CSV (or 400 if missing libs for PDF)
    assert resp.status_code == 200
    assert resp.headers.get("content-type", "").startswith("text/csv")

