#!/usr/bin/env bash
set -e

source venv/bin/activate

TOKEN=${1:-$TELEGRAM_TOKEN}
API_URL=${2:-${API_URL:-ws://localhost:8000}}
if [ -z "$TOKEN" ]; then
    echo "Usage: TELEGRAM_TOKEN env var or first argument token is required" >&2
    exit 1
fi

python -m src.mcp_server &
SERVER_PID=$!
trap "kill $SERVER_PID" EXIT

export API_URL
python -m src.telegram_bot --token "$TOKEN"
