#!/bin/bash

set -e

WORKERS=$(( "$(nproc)" * 2 + 1 ))

PYTHONPATH=/app alembic upgrade head
PYTHONPATH=/app python /app/scripts/seed_tables.py
PYTHONPATH=/app python /app/scripts/create_admin.py

exec gunicorn src.main:app \
  --workers "$WORKERS" \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
