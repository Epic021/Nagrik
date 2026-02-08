#!/bin/bash

# Nagrik Backend Startup Script

cd "$(dirname "$0")"

# Activate virtual environment
source ../.venv/bin/activate

# Start uvicorn
echo "Starting Nagrik Backend on http://localhost:8000..."
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
