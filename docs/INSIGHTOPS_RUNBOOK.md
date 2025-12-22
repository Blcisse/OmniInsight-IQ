# InsightOps Operator Runbook

## A) Quick Start (5 minutes)
- Backend (from repo root):  
  `source .venv/bin/activate && uvicorn backend.src.app.main:app --reload --port 8000`
- Frontend (from repo root):  
  `cd frontend && npm run dev`
- Expected ports: Backend `8000`, Frontend `3000`
- One curl per tier:
  - Backend health: `curl -sf http://localhost:8000/insightops/health`
  - Backend executive brief: `curl -sf "http://localhost:8000/insightops/executive-brief?org_id=demo_org&window_days=14"`
  - Frontend proxy health: `curl -sf http://localhost:3000/api/insightops/health`
  - Frontend proxy executive brief: `curl -sf "http://localhost:3000/api/insightops/executive-brief?org_id=demo_org&window_days=14"`

## B) Verification Gates
- Unit tests (DB-free): `bash scripts/test_unit.sh`
- Integration tests (DB required): `bash scripts/test_integration.sh`
- Runtime smoke script (backend + frontend required): `bash scripts/verify_insightops.sh`
- Expected pass/fail notes: the verify script fails if either server is not running; integration tests fail if Postgres is missing or `DATABASE_URL` is unset.

## C) Common Failure Modes (with exact fixes)
- Symptom: `/insightops/*` returns 404  
  Cause: wrong uvicorn entrypoint  
  Fix: run `uvicorn backend.src.app.main:app --reload --port 8000`
- Symptom: `/api/insightops/*` returns 404/500  
  Cause: proxy route missing or wrong `_proxy` import path  
  Fix: confirm route exists under `frontend/src/app/api/insightops/` and imports the proxy helper correctly.
- Symptom: 500 “Failed to parse URL” in Next route handlers  
  Cause: server route using `fetch("/api/...")` instead of absolute URL / proxy helper  
  Fix: use the proxy helper or absolute URLs.
- Symptom: Duplicate query params (orgId + org_id)  
  Cause: mixed client usage  
  Fix: standardize to `org_id` (guardrails now return 400 on mixed usage).
- Symptom: `psql` errors (command not found / connection refused)  
  Cause: Postgres not installed/running or wrong connection string  
  Fix: install/start Postgres or use docker compose; connect with a valid `postgresql://` URL.

## D) Data Model Reference
- `io_kpi_daily`: KPI metric snapshots (org, metric_key, value, date, dimensions)
- `io_engagement_signal_daily`: Engagement signal snapshots (org, signal_key, value, date, dimensions)
- `io_exec_summary`: Stored executive summaries/briefs (period, org, summary_type, payload JSON)
- Note: SQL-first migrations only; Alembic is not used.

## E) Demo Flow (Recruiter-safe)
- Pages to show: `/insightops` (executive dashboard), `/insightops/analyst`, `/insightops/brief`
- Deterministic only: no LLM involvement; outputs are rule-based and repeatable.
