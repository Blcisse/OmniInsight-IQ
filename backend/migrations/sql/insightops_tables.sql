-- InsightOps Studio core tables (CD2.1)
-- SQL-first migration to provision KPI, engagement, and summary storage.

-- Ensure UUID generation is available
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS io_kpi_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_date DATE NOT NULL,
    org_id TEXT NOT NULL,
    metric_key TEXT NOT NULL,
    metric_value NUMERIC NOT NULL,
    metric_unit TEXT,
    region TEXT,
    segment TEXT,
    channel TEXT,
    product TEXT,
    source TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS io_engagement_signal_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_date DATE NOT NULL,
    org_id TEXT NOT NULL,
    signal_key TEXT NOT NULL,
    signal_value NUMERIC NOT NULL,
    region TEXT,
    segment TEXT,
    channel TEXT,
    product TEXT,
    source TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS io_exec_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    org_id TEXT NOT NULL,
    summary_type TEXT NOT NULL,
    summary_text TEXT NOT NULL,
    payload_json JSONB,
    model_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Ensure payload_json exists for persisted executive briefs
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'io_exec_summary' AND column_name = 'payload_json'
    ) THEN
        EXECUTE 'ALTER TABLE io_exec_summary ADD COLUMN payload_json JSONB';
    END IF;
END$$;

-- Indexes for date/org filtering and period lookups
CREATE INDEX IF NOT EXISTS idx_io_kpi_daily_kpi_date ON io_kpi_daily (kpi_date);
CREATE INDEX IF NOT EXISTS idx_io_kpi_daily_org_id ON io_kpi_daily (org_id);
CREATE INDEX IF NOT EXISTS idx_io_kpi_daily_org_date ON io_kpi_daily (org_id, kpi_date);

CREATE INDEX IF NOT EXISTS idx_io_eng_signal_daily_signal_date ON io_engagement_signal_daily (signal_date);
CREATE INDEX IF NOT EXISTS idx_io_eng_signal_daily_org_id ON io_engagement_signal_daily (org_id);
CREATE INDEX IF NOT EXISTS idx_io_eng_signal_daily_org_date ON io_engagement_signal_daily (org_id, signal_date);

CREATE INDEX IF NOT EXISTS idx_io_exec_summary_org_id ON io_exec_summary (org_id);
CREATE INDEX IF NOT EXISTS idx_io_exec_summary_period ON io_exec_summary (period_start, period_end);
