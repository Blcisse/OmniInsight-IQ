#!/usr/bin/env bash
set -euo pipefail

echo "==> Running full system optimization test suite"

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

if ! command -v pytest >/dev/null 2>&1; then
  echo "pytest is required. Please install it in your environment." >&2
  exit 1
fi

echo "-- Lint/format check (if pre-commit present)"
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit run --all-files || true
fi

echo "-- Running core analytics tests"
pytest -q tests/ai || { echo "AI tests failed" >&2; exit 1; }

echo "-- Running infra performance/caching/security tests"
pytest -q tests/test_performance.py tests/test_caching.py tests/test_security.py || { echo "Infra tests failed" >&2; exit 1; }

echo "All system optimization tests passed."
