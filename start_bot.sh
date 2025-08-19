#!/usr/bin/env bash
set -e

# Load environment variables from .env if present
if [ -f .env ]; then
    set -a
    . ./.env
    set +a
fi

# Activate virtual environment
source venv/bin/activate

TOKEN="${TELEGRAM_TOKEN}"
API_URL="${API_URL:-http://localhost:8000}"

if [ -z "$TOKEN" ]; then
    echo "TELEGRAM_TOKEN must be set in .env" >&2


    exit 1
fi

USE_REAL_FASTAPI=1 uvicorn src.main:app --port 8000 &
SERVER_PID=$!
trap "kill $SERVER_PID" EXIT

export API_URL
python -m src.telegram_bot --token "$TOKEN"
