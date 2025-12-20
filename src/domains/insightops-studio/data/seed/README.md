# InsightOps Seed Data (CD2.2)

This seed file provides deterministic InsightOps sample data to validate the KPI, engagement, and summary tables during CD2.2. It targets the SQL-first tables created in `backend/migrations/sql/insightops_tables.sql` and assumes the tables already exist.

## Contents
- Inserts ~18 KPI rows across revenue, pipeline, and win_rate metrics
- Inserts ~18 engagement rows across touches, replies, and meetings signals
- Inserts 2 executive summaries
- Uses a single org_id: `demo_org`
- Covers 10 days of daily data with consistent dimensions (region=`NA`, segment=`Enterprise`, channel=`Direct`, product=`Core`)

## How to Apply (local Docker + psql)
1. Ensure Postgres is running (from repo root):
   ```bash
   docker compose up -d postgres
   ```
2. Load the InsightOps tables if you have not already (from repo root):
   ```bash
   PGPASSWORD=postgres psql -h localhost -U postgres -d omniinsightiq -f backend/migrations/sql/insightops_tables.sql
   ```
3. Apply the InsightOps seed data (from repo root):
   ```bash
   PGPASSWORD=postgres psql -h localhost -U postgres -d omniinsightiq -f src/domains/insightops-studio/data/seed/seed_insightops.sql
   ```
4. Verify row counts:
   ```bash
   PGPASSWORD=postgres psql -h localhost -U postgres -d omniinsightiq -c "SELECT COUNT(*) FROM io_kpi_daily;" 
   PGPASSWORD=postgres psql -h localhost -U postgres -d omniinsightiq -c "SELECT COUNT(*) FROM io_engagement_signal_daily;" 
   PGPASSWORD=postgres psql -h localhost -U postgres -d omniinsightiq -c "SELECT COUNT(*) FROM io_exec_summary;"
   ```

These commands assume the default docker-compose Postgres credentials (`postgres` / `postgres`) and database name `omniinsightiq`. Adjust connection details if your environment differs.
