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
# InsightOps Studio Domain (INJ-1 Scaffolding)

InsightOps Studio is a first-class commercial performance and engagement intelligence domain within OmniInsight IQ. This scaffolding reserves isolated space for upcoming schemas, analytics, dashboards, and AI contracts without introducing feature logic.

## Goals
- Keep InsightOps Studio isolated from other domains while allowing shared platform utilities where appropriate.
- Provide clear locations for future data models, analytics computations, dashboard routes, and AI prompt contracts.
- Maintain PwC-aligned recruiter-grade demonstration quality with domain-driven structure.

## Structure
- `schemas/` — Domain-owned database schema definitions and related migration/model artifacts (INJ-2 scope).
- `analytics/` — Deterministic computation layer for commercial metrics and engagement signals (INJ-3 scope).
- `dashboards/` — Frontend dashboard views and supporting assets for InsightOps Studio (INJ-4 scope).
- `ai_contracts/` — Prompt and response schemas plus contracts for LLM-based narratives (INJ-5 scope).

## Boundaries
- No authentication, RAG, vector retrieval, voice, or production infra changes are included in this domain scaffold.
- InsightOps Studio should integrate via explicit APIs/contracts rather than implicit coupling to other domains.
- Shared utilities should remain in existing shared modules; domain-specific logic lives under `insightops-studio/`.

## Next Steps
Follow the INJ series to progressively fill each folder with domain artifacts while keeping commits atomic per QSC guidance.
