#Commands cant or should not run during docker image building

#!/bin/sh
set -e

echo "Running database migrations..."
cd /app/models/schemes/mini_rag_db/sql
alembic upgrade head
cd /app
