#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Optional: echo each command (for debugging)
# set -x

echo "🔍 Waiting for PostgreSQL to be available..."

# Wait until PostgreSQL is ready
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
  echo "⏳ Still waiting for database at $DB_HOST:$DB_PORT..."
done

echo "✅ PostgreSQL is up at $DB_HOST:$DB_PORT!"

# Optional: Run DB migrations here if using Alembic
# alembic upgrade head

echo "🚀 Starting FastAPI with Gunicorn..."
exec gunicorn app.main:app \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 60
