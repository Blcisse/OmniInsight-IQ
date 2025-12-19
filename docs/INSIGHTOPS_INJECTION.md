# InsightOps Studio Injection

## Why Inject InsightOps Studio into OIIQ
- **Platform extensibility:** Demonstrates OIIQ can host multiple intelligence domains without refactoring the core platform.
- **Commercial focus:** Adds recruiter-grade commercial performance and engagement intelligence alongside existing health modules.
- **Architecture proof:** Validates domain-first patterns (routing, foldering, contracts) that future domains can copy.

## Domain Isolation Rules
- InsightOps Studio lives under `domains/insightops-studio/` with its own docs, schemas, analytics, dashboards, AI contracts, and data stubs.
- InsightOps Studio lives under `src/domains/insightops-studio` with its own docs, schemas, analytics, dashboards, AI contracts, and data stubs.
- Backend exposure is limited to the `/insightops` router namespace (no shared routes, no cross-domain coupling).
- Frontend routes and navigation entries reference the InsightOps path explicitly; no mixing with other domain UIs.
- Shared utilities may be used, but domain logic and data stay isolated unless explicitly promoted to a shared layer.

## Core Development (CD) Roadmap
- **CD1 – Domain Scaffolding & Wiring:** Directory scaffolds, domain docs, health endpoint, frontend entry point.
- **CD2 – Data Models & Metrics Foundation:** Postgres schemas, KPI/engagement entities, seed or mock datasets, read-only API.
- **CD3 – Analytics Layer:** Aggregations, deltas, trends, simple anomalies within the domain analytics service.
- **CD4 – Dashboards & Visualization:** Domain dashboards with KPI cards, charts, and analyst vs executive views.
- **CD5 – LLM Summaries:** Prompt contracts and summaries over deterministic analytics (no RAG yet).
- **CD6 – Cross-Domain Intelligence (optional):** Comparisons with other OIIQ domains where appropriate.
- **CD7 – Vector Memory (planned later):** Chroma-backed retrieval and grounding for InsightOps narratives.
- **CD8 – Voice Interface (planned later):** STT/TTS-driven executive briefings without new analytics logic.
- **CD9 – Hardening & Narrative:** Documentation, diagrams, and recruiter-ready story.

## Explicit Deferrals
- **Auth changes:** No new authentication or authorization work in this injection phase.
- **Vector/RAG:** Chroma integration and retrieval-augmented generation are deferred to CD7.
- **Voice/STT/TTS:** Deferred to CD8.
- **Production infra:** No cloud provisioning or deployment hardening in this phase.
- **Cross-domain coupling:** Only allowed once CD6 explicitly begins.
