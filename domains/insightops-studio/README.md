# InsightOps Studio (OIIQ Domain)

InsightOps Studio is a commercial performance and engagement intelligence domain injected into the OmniInsight IQ platform. It is treated as a first-class bounded context with isolated schemas, analytics, dashboards, AI contracts, and data assets.

## Scope and Intent
- Focus on commercial performance, KPIs, and engagement intelligence.
- Operates without introducing auth, voice, RAG, vector retrieval, or production infra.
- Uses the platform’s existing FastAPI backend, PostgreSQL, and Next.js frontend.

## Directory Overview
- `docs/` — domain architecture and roadmap references.
- `schemas/` — domain-specific database schema definitions and models.
- `analytics/` — analytics design notes; runtime helpers live under `backend/src/app/services/insightops_analytics/`.
- `dashboards/` — dashboard-facing view models and configuration.
- `ai/` — AI prompt contracts and adapters (no vector/RAG yet).
- `data/` — seed or mock datasets for commercial metrics and engagement signals.

## Domain Boundaries
- Domain documentation and data assets live under `domains/insightops-studio/`.
- Backend runtime code for InsightOps Studio lives only under `backend/src/app/` (models/services/routers).
- Shared platform utilities are consumed via stable interfaces; no cross-domain coupling.
- Analytics remain deterministic until later AI phases introduce summarization.

## Current Phase
Currently tracking Core Development 3 (CD3) analytics foundations after CD2 established the SQL schema and seeds. Subsequent CD phases will layer dashboards and AI narratives incrementally.
