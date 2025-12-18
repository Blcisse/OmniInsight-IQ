# InsightOps Studio Architecture (CD1)

InsightOps Studio operates as a domain-isolated module within OmniInsight IQ. The architecture emphasizes clear boundaries, deterministic analytics, and staged AI adoption.

## Guiding Principles
- **Isolation first**: Domain assets (schemas, analytics, dashboards, AI contracts) live under `src/domains/insightops-studio`.
- **Deterministic core**: Early phases rely on non-AI analytics; AI summarization arrives later.
- **Shared platform alignment**: Use existing FastAPI, PostgreSQL, and Next.js primitives without altering platform-wide auth or infrastructure.
- **Extensibility**: Design folders to support later data models, analytics services, and dashboard composition.

## Backend Shape
- **Schemas** (`schemas/`): Domain-specific models and migrations for commercial performance and engagement data.
- **Analytics** (`analytics/`): Services for aggregations, trends, deltas, and anomaly indicators (deterministic in CD1-CD3).
- **AI** (`ai/`): Prompt/output contracts and adapters for LLM summarization (introduced in later CD phases; no RAG/vector yet).
- **Data** (`data/`): Seed or mock datasets to support development and demos.

## Frontend Shape
- **Dashboards** (`dashboards/`): View models, composition configs, and UI wiring specific to InsightOps Studio routes. Keeps separation from existing health dashboards.

## Integration Boundaries
- No new auth, voice, RAG, vector retrieval, or production infrastructure.
- Cross-domain interactions occur through explicit APIs or shared utilities—never direct coupling to other domain internals.
- Cloud LLM usage stays pluggable and limited to later CD phases.

## Phase Positioning
- **CD1**: Scaffolding and architecture framing (this document).
- **CD2+**: Introduce schemas, seed data, deterministic analytics, dashboards, and eventually AI summaries in CD5.

## DB & Migrations (CD2 framing)
- **Pattern**: Use SQL-first migrations located in `backend/migrations/sql/` to provision InsightOps tables (no Alembic). ORM models remain aligned with the existing async PostgreSQL setup for app-level access.
- **Naming convention (locked)**: Use the `io_` table prefix for InsightOps tables (e.g., `io_kpi_daily`, `io_engagement_signal`). This preserves isolation without creating a separate Postgres schema and avoids cross-domain name collisions.

### CD2 Core Tables (Minimum Viable Metrics Model)
- `io_kpi_daily`: Daily KPI snapshots keyed by `kpi_date`, `org_id`, `metric_key`, with numeric values, optional units, optional dimensions (region/segment/channel/product), and source tracking.
- `io_engagement_signal_daily`: Daily engagement signals keyed by `signal_date`, `org_id`, `signal_key`, with numeric values, optional dimensions, and source tracking.
- `io_exec_summary`: Stores executive summaries (manager/board) for a period range, with optional `model_name` for later AI provenance. All tables use UUID primary keys and `created_at`/`updated_at` timestamps.
- **Pattern**: Follow the existing platform approach of SQLAlchemy ORM models with Alembic migrations (see `backend/src/app/core/database.py` and `backend/migrations/`). This keeps InsightOps aligned with async PostgreSQL usage already wired in the app.
- **Naming convention (locked)**: Use the `io_` table prefix for InsightOps tables (e.g., `io_kpi_daily`, `io_engagement_signal`). This preserves isolation without creating a separate Postgres schema and avoids cross-domain name collisions.
