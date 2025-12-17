# InsightOps Studio (OIIQ Domain)

InsightOps Studio is a commercial performance and engagement intelligence domain injected into the OmniInsight IQ platform. It is treated as a first-class bounded context with isolated schemas, analytics, dashboards, AI contracts, and data assets.

## Scope and Intent
- Focus on commercial performance, KPIs, and engagement intelligence.
- Operates without introducing auth, voice, RAG, vector retrieval, or production infra.
- Uses the platform’s existing FastAPI backend, PostgreSQL, and Next.js frontend.

## Directory Overview
- `docs/` — domain architecture and roadmap references.
- `schemas/` — domain-specific database schema definitions and models.
- `analytics/` — deterministic analytics services and aggregations.
- `dashboards/` — dashboard-facing view models and configuration.
- `ai/` — AI prompt contracts and adapters (no vector/RAG yet).
- `data/` — seed or mock datasets for commercial metrics and engagement signals.

## Domain Boundaries
- Changes stay within `src/domains/insightops-studio` unless explicitly allowed.
- Shared platform utilities are consumed via stable interfaces; no cross-domain coupling.
- Analytics remain deterministic until later AI phases introduce summarization.

## Current Phase
This directory is initialized under Core Development 1 (CD1): foundational scaffolding for InsightOps Studio. Subsequent CD phases will layer data models, analytics, dashboards, and AI narratives incrementally.
