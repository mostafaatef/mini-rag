FROM ghcr.io/astral-sh/uv:0.6.14-python3.10-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libavif-dev \
    pkg-config \
    libjpeg-dev \
    gcc \
    unzip \
    zip \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from src directory (based on build context '..')
COPY src/requirements.txt /app/requirements.txt

# Install dependencies using uv
RUN uv pip install --no-cache-dir -r requirements.txt --system

# Download NLTK data
RUN python -m nltk.downloader punkt stopwords

# Copy the rest of the application code
COPY src/ .

# Make sure from Alembic
RUN mkdir -p models/schemes/mini_rag_db/sql

# Copy Alembic ini
COPY docker/minirag_app/alembic.ini /app/models/schemes/mini_rag_db/sql/alembic.ini

# Copy entrypoint script
COPY docker/minirag_app/entrypoint.sh /entrypoint.sh

# Make entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set entrypoint to run in the container time not image build time
ENTRYPOINT ["/entrypoint.sh"]

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
