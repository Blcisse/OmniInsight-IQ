# InsightOps Studio Analytics

This folder documents analytics stubs focused on commercial performance and engagement intelligence. Runtime helpers live under
`backend/src/app/services/insightops_analytics/`. Early analytic themes include:

- **Trends**: trajectory and momentum of KPIs over time.
- **Deltas**: period-over-period changes that highlight gains or regressions.
- **Anomalies**: simple detection of unusual movements that warrant a closer look.

These are descriptive placeholders; implementation logic will be added in later Core Dev phases.
Use this directory for deterministic analytics logic that transforms domain data into insights before any AI summarization.

Scope for future steps:
- Aggregations, trends, and time-based comparisons.
- Delta calculations and simple anomaly indicators.
- Domain-scoped analytics services callable by APIs and dashboards.
