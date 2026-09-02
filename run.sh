#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND="$ROOT/frontend"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required."
  exit 1
fi

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "OPENAI_API_KEY is not set."
  echo 'Run: export OPENAI_API_KEY="your-key"'
  exit 1
fi

if [ ! -d "$ROOT/.venv" ]; then
  echo "Expected Python venv at $ROOT/.venv was not found."
  echo "Use your existing Python environment or adjust this script."
fi

cd "$FRONTEND"
if [ ! -d node_modules ]; then
  npm install
fi

cd "$ROOT/backend"
uvicorn api:app --reload --port 8000 &
BACKEND_PID=$!

cleanup() {
  kill "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cd "$FRONTEND"
npm run dev
