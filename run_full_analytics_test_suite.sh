#!/usr/bin/env bash
set -euo pipefail

echo "==> Running full analytics test suite"

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

if ! command -v pytest >/dev/null 2>&1; then
  echo "pytest is required. Please install it in your environment." >&2
  exit 1
fi

pytest -q tests/ai backend/src/app/tests || {
  echo "Tests failed" >&2
  exit 1
}

echo "All analytics tests passed."
