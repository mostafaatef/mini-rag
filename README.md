# Mini-RAG

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Motor-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Pgvector-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)

**Mini-RAG** is a streamlined implementation of a Retrieval-Augmented Generation (RAG) system. It provides a robust backend API for uploading documents, processing them into chunks, and storing them for semantic search and LLM context augmentation.

---

## 🏗️ Architecture

The project follows a clean, modular architecture:

- **Framework**: FastAPI for high-performance, async API endpoints.
- **Database**:
  - **MongoDB** (via Motor): Stores Projects, Assets (Files), and metadata.
  - **PostgreSQL** (via SQLAlchemy & Alembic): Relational data and vector storage (via `pgvector`).
  - **Vector Store**: Supports Qdrant and Pgvector.
- **Processing**: LangChain for document loading and splitting.
- **LLM Integration**: Supports OpenAI, Cohere, Google Gemini, and Ollama.
- **Environment**: Docker support for easy database provisioning.

### Key Concepts

- **Project**: A container for a collection of documents.
- **Asset**: A raw file (e.g., PDF, TXT) uploaded to the system.
- **Chunk**: A processed segment of text from an Asset, ready for embedding/retrieval.

---

## 🚀 Quick Start

### 1. Prerequisites

- Docker & Docker Compose

### 2. Fast Setup (Docker Only)

The easiest way to run Mini-RAG is via Docker. This will spawn the FastAPI app, Database (Postgres/Mongo), and Monitoring stack (Prometheus/Grafana).

```bash
# Clone and enter the project
cd mini-rag/docker

# Initialize environment files (optional, default examples are provided)
# cp env/.env.example.app env/.env.app

# Start everything
docker compose up -d
```

- **API Server**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`
- **Grafana**: `http://localhost:3000` (Default: admin/admin)
- **Prometheus**: `http://localhost:9090`

### 3. Manual Development Setup

If you prefer to run the application code locally but the databases in Docker:

#### A. Start Databases

```bash
cd docker
docker compose up -d pgvector mongodb qdrant
```

#### B. Setup Python Environment

```bash
cd src
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### C. Database Migrations

```bash
# Run from the project root
alembic -c src/models/schemes/mini_rag_db/sql/alembic.ini upgrade head
```

#### D. Run Server

```bash
# From the src directory
uvicorn main:app --reload
```

---

## 📊 Monitoring & Proxying

The Docker setup includes a pre-configured monitoring stack:

- **Nginx**: Acting as a reverse proxy. Accessible at `http://localhost`.
- **Prometheus**: Collecting metrics from FastAPI, Postgres, and the host system.
- **Grafana**: Visualizing the collected data. Includes data source configurations for Prometheus.

### Why some services were removed?

- **Grafana Agent**: Redundant for local setups; Prometheus handles scraping directly.
- **Pushgateway**: Used for short-lived batch jobs (FastAPI is a long-lived service).
- **Alertmanager**: Used for routing alerts to Slack/Email (unnecessary for local dev).

---

## 🛠️ Cleansing & Maintenance

- **Python environment**: The project now uses `uv` for lightning-fast, reproducible builds in Docker.
- **Single Worker**: Uvicorn is restricted to 1 worker in Docker to prevent local Qdrant database locking.
- **Clean Config**: Example files are updated to use Docker-native hostnames (`pgvector`, `mongodb`).

---

## 📮 Postman Collection

Download the Postman collection to test the API endpoints:
[mini-rag-app.postman_collection.json](/assets/mini-rag-app.postman_collection.json)
