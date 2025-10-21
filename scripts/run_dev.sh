#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
FRONTEND_DIR="${ROOT_DIR}/frontend"
VENV_BIN="${ROOT_DIR}/venv/bin"

BACKEND_CMD=("${VENV_BIN}/uvicorn" "backend.main:app" "--reload" "--host" "0.0.0.0" "--port" "8000")
FRONTEND_CMD=("npm" "run" "dev" "--" "--host")

stop_existing_services() {
  echo "🧹 Stopping any existing dev services..."

  # Helper to terminate listeners on a given port
  stop_port_listener() {
    local port="$1"
    if command -v lsof >/dev/null 2>&1; then
      local pids
      pids=$(lsof -t -i:"${port}" -sTCP:LISTEN 2>/dev/null || true)
      if [[ -n "${pids}" ]]; then
        echo "   • Terminating processes on port ${port}: ${pids}"
        kill ${pids} 2>/dev/null || true
      fi
    fi
  }

  # Backend (uvicorn) cleanup
  stop_port_listener 8000
  pkill -f "uvicorn backend.main:app" 2>/dev/null || true

  # Frontend (Vite) cleanup
  stop_port_listener 5173
  pkill -f "npm run dev" 2>/dev/null || true

  # Allow processes time to exit
  sleep 1
}

print_header() {
  echo "============================================================"
  echo " Hybrid RAG Dev Runner"
  echo "============================================================"
}

check_requirements() {
  if [[ ! -x "${BACKEND_CMD[0]}" ]]; then
    echo "❌ Cannot find uvicorn at ${BACKEND_CMD[0]}"
    echo "   Activate the virtualenv or run: pip install -r requirements.txt"
    exit 1
  fi

  if [[ ! -d "${FRONTEND_DIR}" ]]; then
    echo "❌ Frontend directory not found at ${FRONTEND_DIR}"
    exit 1
  fi

  if [[ ! -d "${FRONTEND_DIR}/node_modules" ]]; then
    echo "📦 Installing frontend dependencies..."
    (cd "${FRONTEND_DIR}" && npm install)
  fi
}

start_backend() {
  echo "🚀 Starting backend (FastAPI on port 8000)"
  (cd "${ROOT_DIR}" && "${BACKEND_CMD[@]}") &
  BACKEND_PID=$!
}

start_frontend() {
  echo "🌐 Starting frontend (Vite on port 5173)"
  (cd "${FRONTEND_DIR}" && "${FRONTEND_CMD[@]}") &
  FRONTEND_PID=$!
}

shutdown() {
  echo "\n🛑 Shutting down services..."
  [[ -n "${BACKEND_PID:-}" ]] && kill "${BACKEND_PID}" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "${FRONTEND_PID}" 2>/dev/null || true
  wait
  echo "✅ Cleanup complete"
}

main() {
  print_header
  check_requirements

  # Ensure no stale instances are running before starting new ones
  stop_existing_services

  trap shutdown INT TERM EXIT

  start_backend
  start_frontend

  echo "\n✅ Backend available at http://localhost:8000"
  echo "✅ Frontend available at http://localhost:5173"
  echo "\nPress Ctrl+C to stop both services."

  wait
}

main "$@"
