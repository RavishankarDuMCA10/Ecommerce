#!/usr/bin/env bash
set -euo pipefail

# Starts gateway + two domain services on separate ports for local development.
if [[ -x "../.venv/bin/python" ]]; then
  PYTHON_BIN="../.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

"$PYTHON_BIN" -m uvicorn services.auth_service.main:app --reload --port 8001 &
AUTH_PID=$!

"$PYTHON_BIN" -m uvicorn services.catalog_service.main:app --reload --port 8002 &
CATALOG_PID=$!

"$PYTHON_BIN" -m uvicorn services.gateway.main:app --reload --port 8000 &
GATEWAY_PID=$!

cleanup() {
  kill "$AUTH_PID" "$CATALOG_PID" "$GATEWAY_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM
wait
