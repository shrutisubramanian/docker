#!/bin/bash
echo "Starting FastAPI Backend Server..."
source venv/bin/activate
export PYTHONPATH=$(pwd)
uvicorn backend.src.api:app --port 8000 --reload
