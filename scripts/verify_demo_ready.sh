#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "❌ $1"
  exit 1
}

echo "Checking backend health..."
curl -sf "http://localhost:8000/insightops/health" >/dev/null || fail "Backend health check failed"

echo "Checking demo profile EXEC_REVENUE_RISK..."
curl -sf "http://localhost:8000/insightops/executive-brief?org_id=demo_org&window_days=14&demo_mode=true&demo_profile=EXEC_REVENUE_RISK" >/dev/null || fail "Demo profile EXEC_REVENUE_RISK failed"

echo "Checking demo profile EXEC_ANOMALY_SPIKE..."
curl -sf "http://localhost:8000/insightops/executive-brief?org_id=demo_org&window_days=14&demo_mode=true&demo_profile=EXEC_ANOMALY_SPIKE" >/dev/null || fail "Demo profile EXEC_ANOMALY_SPIKE failed"

echo "✅ Demo readiness verified"
