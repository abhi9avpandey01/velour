#!/bin/bash
# Start Celery background worker
celery -A app.worker.celery_app worker --loglevel=info &

# Start Uvicorn FastAPI web server
uvicorn app.main:app --host 0.0.0.0 --port $PORT
