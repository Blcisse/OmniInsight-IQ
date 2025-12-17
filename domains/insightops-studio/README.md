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
