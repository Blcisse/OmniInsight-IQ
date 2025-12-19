# InsightOps Studio Roadmap (Core Development)

A staged plan to build commercial performance and engagement intelligence within OmniInsight IQ.

## Phase Outline
- **CD1 – Foundation & Scaffolding**: Establish domain folders, architecture framing, and boundaries (complete).
- **CD2 – Data Models & Metrics**: Define PostgreSQL schemas for performance KPIs and engagement signals; add seed/mock data and read-only FastAPI endpoints (complete).
- **CD3 – Analytics Layer**: Implement deterministic aggregations (trends, deltas, anomalies) within domain analytics services (current).
- **CD4 – Dashboards & Visualization**: Wire InsightOps Studio routes/components with KPI cards, charts, and tables distinct from health dashboards.
- **CD5 – AI Summaries**: Add LLM-based executive summaries over deterministic analytics (no RAG/vector memory yet).
- **CD6 – Cross-Domain Intelligence (Optional)**: Correlate commercial metrics with other domain signals via explicit APIs.

## Principles and Constraints
- Domain docs and data stay within `domains/insightops-studio/`; backend runtime lives under `backend/src/app/`.
- Avoid auth changes, RAG/vector retrieval, voice, or production infra in these phases.
- Keep AI usage pluggable and limited to summarization of known deterministic inputs.

## Near-Term Actions (CD3)
- Harden analytics helpers for KPI and engagement series queries.
- Align dashboards/consumers to use the read-only InsightOps endpoints.
- Keep seeds and schemas stable while analytics mature.
