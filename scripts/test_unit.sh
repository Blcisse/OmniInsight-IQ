#!/usr/bin/env bash
set -e
cd backend
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"
pytest -m unit
