🌐OmniInsight IQ (OIIQ)
OmniInsight IQ is a hybrid intelligence and analytics ecosystem that merges advanced sales intelligence with health-focused 
data analytics through its partner brand, Thryvion Health. The platform empowers organizations to make data-driven decisions
by providing AI-powered dashboards, predictive analytics, and performance optimization tools for both commerce and healthcare sectors.


🌐Brand Concept: Thryvion Health
Thryvion Health is the wellness and nutrition-focused branch of OIIQ. It transforms raw performance metrics, consumer trends, and product 
analytics in the nutraceutical, supplement, and wellness industries into actionable insights. Its tone is futuristic, clean, and science-driven, 
emphasizing innovation and health intelligence.

🌐System Modules
User & Admin Dashboard
Sales Intelligence Suite (OmniInsight Core)
Health Intelligence Suite (Thryvion Health)
Predictive Analytics Engine
Reports & Visualization Center
Data Ingestion & Processing Layer
API Gateway & Integration Layer
Authentication & Access Control
System Monitoring & Logging
Frontend UI Components Library

📄 Documentation
- [InsightOps Studio Injection](docs/INSIGHTOPS_INJECTION.md)
- [InsightOps Operator Runbook](docs/INSIGHTOPS_RUNBOOK.md)

## Testing
- Unit tests (no DB, no servers): `bash scripts/test_unit.sh`
- Integration tests (requires Postgres + backend): `bash scripts/test_integration.sh`
- Runtime smoke (requires backend + frontend): `bash scripts/verify_insightops.sh`

## CD Phases
- Completed: CD1 (scaffolding), CD2 (data model + endpoints), CD3 (analytics), CD4 (dashboards), CD5 (decision layer), CD6 (hardening in progress)
- Next planned: CD7 (cross-domain intelligence), CD8 (optional LLM augmentation), CD9 (optional voice layer)
