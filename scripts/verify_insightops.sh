#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "❌ $1"
  exit 1
}

echo "Checking backend health..."
curl -sf http://localhost:8000/insightops/health >/dev/null || fail "Backend health check failed"

echo "Checking executive brief..."
curl -sf "http://localhost:8000/insightops/executive-brief?org_id=demo_org&window_days=14" >/dev/null || fail "Executive brief check failed"

echo "Checking frontend proxy health..."
curl -sf http://localhost:3000/api/insightops/health >/dev/null || fail "Frontend proxy health check failed"

echo "✅ InsightOps verification succeeded"
