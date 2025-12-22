# Backend Local Run (InsightOps Studio)

Use this canonical command from the repo root:

```bash
source .venv/bin/activate
uvicorn backend.src.app.main:app --reload --port 8000
```

> **Warning:** Do not start uvicorn with any other module path. InsightOps routes require `backend.src.app.main:app`.
