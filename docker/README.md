# Mini-RAG Docker Infrastructure

This directory contains the complete infrastructure setup for the Mini-RAG application using Docker Compose. It includes the application, vector databases, primary databases, and a full monitoring stack.

## Architecture Overview

The infrastructure consists of the following components:

- **App Layer**: FastAPI application (Minirag) proxied by Nginx.
- **VDB Layer**: Qdrant (Vector DB) and PGVector (Postgres extension for vectors).
- **Data Layer**: MongoDB (NoSQL) and PostgreSQL (SQL).
- **Monitoring Layer**: Prometheus, Grafana, Alertmanager, Pushgateway, and various Exporters (Node, Postgres).

## Directory Structure

```bash
docker/
├── env/                   # Environment variable files for all services
│   ├── .env.app           # FastAPI application settings
│   ├── .env.postgres      # PostgreSQL/PGVector credentials
│   └── ...                # Other service specific envs
├── minirag_app/           # Application-specific Docker setup
│   ├── Dockerfile         # Multi-stage-ready build using 'uv'
│   ├── entrypoint.sh      # Script to run migrations before startup
│   └── alembic.ini        # Alembic configuration for the container
├── docker-compose.yml     # Main service orchestration file
├── nginx.conf             # Nginx configuration (Proxy & Metrics)
└── prometheus.yml         # Prometheus scrape configurations
```

## Getting Started

### 1. Configure Environment Variables

Ensure all `.env` files in `docker/env/` are correctly configured based on the `.env.example` files provided in the same directory.

### 2. Build and Run

From the project root directory, run:

```bash
# Build the application image
docker-compose build

# Start all services in the background
docker-compose up -d

# View and follow logs from all services
docker-compose logs -f

# Follow logs for a specific service (e.g., fastapi)
docker-compose logs -f fastapi
```

## Debugging & Logs

If you encounter issues, use these commands to inspect the state of your infrastructure:

```bash
# Check the status of all containers
docker-compose ps

# Follow logs for all services
docker-compose logs -f

# Follow logs for a specific service
docker-compose logs -f fastapi

# Access a running container's shell (e.g., fastapi)
docker-compose exec fastapi bash

# Access PostgreSQL database directly
docker-compose exec pgvector psql -U minirag -d mini_rag
```

## Accessing Services

| Service | Address | Description |
| :--- | :--- | :--- |
| **App (Nginx)** | `http://localhost:80` | Main API Entry Point |
| **FastAPI** | `http://localhost:8000` | Backend API |
| **Metrics** | `http://localhost:80/metrics` | Prometheus Metrics |
| **Prometheus** | `http://localhost:9090` | Monitoring System |
| **Grafana** | `http://localhost:3000` | Analytics Dashboards |
| **Qdrant UI** | `http://localhost:6333/dashboard` | Vector DB Dashboard |

## Database Migrations

Database migrations are automatically handled by the `entrypoint.sh` script using Alembic whenever the `fastapi` container starts.

## Cleanup & Reset

To stop and remove all resources created by the stack, use the following commands:

```bash
# Stop and remove containers, networks
docker-compose down

# Reset everything (CRITICAL: Removes all volumes and data)
docker-compose down -v

# Full Reset (Removes volumes AND images)
docker-compose down -v --rmi all
```
