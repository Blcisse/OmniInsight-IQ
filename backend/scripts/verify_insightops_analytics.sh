#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"

fail_count=0

check_endpoint() {
  local name="$1"
  local url="$2"
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url" || true)
  if [[ "$status" == "200" ]]; then
    echo "PASS: $name ($url)"
  else
    echo "FAIL: $name ($url) -> HTTP $status"
    fail_count=$((fail_count + 1))
  fi
}

check_endpoint "InsightOps health" "${BASE_URL}/insightops/health"
check_endpoint "KPI summary" "${BASE_URL}/insightops/analytics/kpis/summary?org_id=demo_org&metric_key=revenue"
check_endpoint "Engagement summary" "${BASE_URL}/insightops/analytics/engagement/summary?org_id=demo_org&signal_key=touches"
check_endpoint "Anomalies" "${BASE_URL}/insightops/analytics/anomalies?org_id=demo_org"

if [[ "$fail_count" -gt 0 ]]; then
  exit 1
fi

echo "All InsightOps analytics checks passed."
