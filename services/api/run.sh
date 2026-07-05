#!/bin/bash
# Run database migrations
alembic upgrade head


# Start Uvicorn FastAPI web server
uvicorn app.main:app --host 0.0.0.0 --port $PORT
