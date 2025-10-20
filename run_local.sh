#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

info() { printf "[run-local] %s\n" "$*"; }
err() { printf "[run-local][error] %s\n" "$*" >&2; }

# Load environment variables
ENV_FILE="$ROOT_DIR/.env"
if [[ -f "$ENV_FILE" ]]; then
  info "Loading environment from .env"
  # shellcheck disable=SC1090
  set -a
  source "$ENV_FILE"
  set +a
else
  err ".env not found; Neo4j/Qdrant/Gemini credentials must be set manually"
fi

# Ensure logs directory exists
mkdir -p "$ROOT_DIR/logs"

cleanup() {
  info "Shutting down services"
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
  [[ -n "${REDIS_PID:-}" ]] && kill "$REDIS_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

# Optional local Redis
if command -v redis-server >/dev/null 2>&1; then
  info "Starting redis-server (default port 6379)"
  redis-server --port 6379 --daemonize no &
  REDIS_PID=$!
  export REDIS_URL="redis://localhost:6379"
else
  err "redis-server not found; ensure REDIS_URL points to a reachable instance"
fi

command -v uvicorn >/dev/null 2>&1 || {
  err "uvicorn not found in PATH. Activate your Python environment (e.g., 'source venv/bin/activate')."
  exit 1
}

# Start FastAPI backend
info "Starting FastAPI backend on http://127.0.0.1:8000"
(
  cd "$ROOT_DIR"
  uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
) &
BACKEND_PID=$!

# Frontend dev server (Vite)
if [[ -d "$ROOT_DIR/frontend" ]]; then
  if command -v npm >/dev/null 2>&1; then
    info "Starting frontend dev server on http://127.0.0.1:5173"
    (
      cd "$ROOT_DIR/frontend"
      if [[ ! -d node_modules ]]; then
        info "Installing frontend dependencies"
        npm install
      fi
      npm run dev -- --host
    ) &
    FRONTEND_PID=$!
  else
    err "npm not found; skipping frontend startup"
  fi
else
  err "frontend directory not found; skipping UI startup"
fi

info "Services launched. Press Ctrl+C to stop."

wait
