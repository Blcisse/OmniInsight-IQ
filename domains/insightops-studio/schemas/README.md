# InsightOps Studio Schemas

This folder hosts domain-isolated schema definitions for InsightOps Studio. CD2 introduces the minimum viable tables:

- **`io_kpi_daily`**: UUID `id`, `kpi_date` (indexed), `org_id` (indexed), `metric_key`, `metric_value` (numeric), optional `metric_unit`, optional dimensions (`region`/`segment`/`channel`/`product`), optional `source`, and `created_at`/`updated_at` timestamps.
- **`io_engagement_signal_daily`**: UUID `id`, `signal_date` (indexed), `org_id` (indexed), `signal_key`, `signal_value` (numeric), optional dimensions, optional `source`, and `created_at`/`updated_at` timestamps.
- **`io_exec_summary`**: UUID `id`, `period_start`, `period_end`, `org_id` (indexed), `summary_type`, `summary_text`, optional `model_name`, and `created_at`/`updated_at` timestamps.

Tables use the locked `io_` prefix and are provisioned via SQL-first migration scripts (see `backend/migrations/sql/insightops_tables.sql`).
