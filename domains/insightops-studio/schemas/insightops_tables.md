# InsightOps Core Tables (CD2.1)

This domain uses SQL-first migrations to provision its core tables via `backend/migrations/sql/insightops_tables.sql`. All tables use UUID primary keys and `created_at`/`updated_at` timestamps.

## io_kpi_daily
- **Purpose**: Daily KPI snapshots to track commercial performance.
- **Key columns**: `kpi_date` (indexed), `org_id` (indexed), `metric_key`, `metric_value`, optional `metric_unit`, optional dimensions (`region`, `segment`, `channel`, `product`), optional `source`.
- **Indexes**: `kpi_date`, `org_id`, and composite `(org_id, kpi_date)` for filtering.

## io_engagement_signal_daily
- **Purpose**: Daily engagement signal counts for activity/response tracking.
- **Key columns**: `signal_date` (indexed), `org_id` (indexed), `signal_key`, `signal_value`, optional dimensions, optional `source`.
- **Indexes**: `signal_date`, `org_id`, and composite `(org_id, signal_date)` for filtering.

## io_exec_summary
- **Purpose**: Stores executive summaries over a period for future AI generation.
- **Key columns**: `period_start`, `period_end`, `org_id`, `summary_type`, `summary_text`, optional `model_name`.
- **Indexes**: `org_id` and `(period_start, period_end)` for lookup.
