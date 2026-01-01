#!/bin/sh
set -e

echo "Running database migrations..."
cd /app/src/models/schemes/mini_rag_db/sql

python3 -m alembic upgrade head || {
    echo "ERROR: Migrations failed!"
    exit 1
}

cd /app
echo "Migrations successful. Starting application..."
exec "$@"
