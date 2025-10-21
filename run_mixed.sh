#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

info() { printf "[hybrid-local] %s\n" "$*"; }
err() { printf "[hybrid-local][error] %s\n" "$*" >&2; }

# Require active virtual environment so backend runs on host Python
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  err "Activate your Python virtual environment before running this script."
  err "Example: source .venv/bin/activate"
  exit 1
fi

# Load backend environment variables
ENV_FILE="$ROOT_DIR/.env"
if [[ -f "$ENV_FILE" ]]; then
  info "Loading environment from .env"
  # shellcheck disable=SC1090
  set -a
  source "$ENV_FILE"
  set +a
else
  err ".env not found; backend may miss required credentials"
fi

# Ensure redis URL points to published container port
export REDIS_URL="${REDIS_URL:-redis://localhost:6379}"

# Frontend should call backend running on host
export VITE_API_URL="${VITE_API_URL:-http://host.docker.internal:8000}"

# Locate docker compose command
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  err "docker compose not found. Install Docker Desktop or docker-compose."
  exit 1
fi

# Start Docker services (redis + frontend)
info "Starting Docker services: redis, frontend"
"${COMPOSE_CMD[@]}" up redis frontend -d

cleanup() {
  info "Stopping backend"
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true

  info "Stopping Docker services"
  "${COMPOSE_CMD[@]}" stop frontend redis >/dev/null 2>&1 || true
}

trap cleanup EXIT INT TERM

# Ensure uvicorn is in path
if ! command -v uvicorn >/dev/null 2>&1; then
  err "uvicorn not found in current environment. pip install uvicorn"
  exit 1
fi

# Launch backend using uvicorn from current venv
info "Starting FastAPI backend on http://127.0.0.1:8000"
(
  cd "$ROOT_DIR"
  uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
) &
BACKEND_PID=$!

info "Frontend available at http://localhost:3000"
info "Press Ctrl+C to stop"

wait "$BACKEND_PID"
