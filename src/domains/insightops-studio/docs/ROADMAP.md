# InsightOps Studio Roadmap (Core Development)

A staged plan to build commercial performance and engagement intelligence within OmniInsight IQ.

## Phase Outline
- **CD1 – Foundation & Scaffolding**: Establish domain folders, architecture framing, and boundaries (current).
- **CD2 – Data Models & Metrics**: Define PostgreSQL schemas for performance KPIs and engagement signals; add seed/mock data and read-only FastAPI endpoints.
- **CD3 – Analytics Layer**: Implement deterministic aggregations (trends, deltas, anomalies) within domain analytics services.
- **CD4 – Dashboards & Visualization**: Wire InsightOps Studio routes/components with KPI cards, charts, and tables distinct from health dashboards.
- **CD5 – AI Summaries**: Add LLM-based executive summaries over deterministic analytics (no RAG/vector memory yet).
- **CD6 – Cross-Domain Intelligence (Optional)**: Correlate commercial metrics with other domain signals via explicit APIs.

## Principles and Constraints
- Stay within `src/domains/insightops-studio` unless a CD step explicitly authorizes shared-path changes.
- Avoid auth changes, RAG/vector retrieval, voice, or production infra in these phases.
- Keep AI usage pluggable and limited to summarization of known deterministic inputs.

## Near-Term Actions (CD1/early CD2)
- Finalize domain scaffolding docs and placeholders.
- Define initial schema drafts for commercial performance, KPIs, and engagement signals.
- Prepare mock datasets to enable deterministic analytics prototypes.
