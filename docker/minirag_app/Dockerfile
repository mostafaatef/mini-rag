# Use official Python as base
FROM python:3.10-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv
ENV PATH="/uv/bin:$PATH"

WORKDIR /app

# Copy requirements from src directory
COPY src/requirements.txt /app/requirements.txt

# Create venv and install dependencies
RUN uv venv /app/.venv && \
    uv pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN .venv/bin/python -m nltk.downloader punkt stopwords

# Copy the rest of the application code
COPY src/ /app/src/

# Setup Alembic directory structure
RUN mkdir -p /app/src/models/schemes/mini_rag_db/sql

# Copy Alembic ini
COPY docker/minirag_app/alembic.ini /app/src/models/schemes/mini_rag_db/sql/alembic.ini

# Copy entrypoint script
COPY docker/minirag_app/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
