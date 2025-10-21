#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
FRONTEND_DIR="${ROOT_DIR}/frontend"
VENV_BIN="${ROOT_DIR}/venv/bin"

BACKEND_CMD=("${VENV_BIN}/uvicorn" "backend.main:app" "--reload" "--host" "0.0.0.0" "--port" "8000")
FRONTEND_CMD=("npm" "run" "dev" "--" "--host")

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

  trap shutdown INT TERM EXIT

  start_backend
  start_frontend

  echo "\n✅ Backend available at http://localhost:8000"
  echo "✅ Frontend available at http://localhost:5173"
  echo "\nPress Ctrl+C to stop both services."

  wait
}

main "$@"
