# Mini-RAG

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Motor-green.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)

**Mini-RAG** is a streamlined implementations of a Retrieval-Augmented Generation (RAG) system. It provides a robust backend API for uploading documents, processing them into chunks, and storing them for semantic search and LLM context augmentation.

---

## 🏗️ Architecture

The project follows a clean, modular architecture:

- **Framework**: FastAPI for high-performance, async API endpoints.
- **Database**: MongoDB (via Motor) for storing Projects, Assets (Files), and Chunks.
- **Processing**: LangChain for document loading (PDF, TXT) and text splitting.
- **Environment**: Docker support for easy database provisioning.

### Key Concepts

- **Project**: A container for a collection of documents.
- **Asset**: A raw file (e.g., PDF, TXT) uploaded to the system.
- **Chunk**: A processed segment of text from an Asset, ready for embedding/retrieval.

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- Docker & Docker Compose

### 2. Setup Database

Start the MongoDB instance using Docker:

```bash
cd docker
cp .env.example .env
# Edit .env if necessary
docker-compose up -d
```

### 3. Setup Application

```bash
cd src
# Create virtual environment (optional but recommended)
conda create -n mini-rag python=3.10
conda activate mini-rag

# Install dependencies
pip install -r requirements.txt
```

### 4. Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```
Ensure `MONGODB_URL` in `.env` matches your Docker configuration (default: `mongodb://localhost:27017`).

### 5. Run Server

```bash
# From the src directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Server will start at `http://localhost:8000`. API docs available at `http://localhost:8000/docs`.

---

## 📚 API Reference

**Note**: All endpoints are prefixed with `/api/v1`.

### Data Management

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/data/upload/{project_title}` | Upload a file. Returns `asset_id`. |
| `POST` | `/data/process/{project_title}` | Process an asset into chunks. Requires `asset_id`. |

**IMPORTANT**: The API uses `asset_id` to reference uploaded files. Please ensure your client applications use this field instead of `file_id`.

---

## 📂 Project Structure

```
mini-rag/
├── docker/             # Docker configuration
├── src/
│   ├── main.py         # Application entry point
│   ├── controllers/    # Business logic (Data, Processing, Project)
│   ├── models/         # Database models & Schemas
│   ├── routes/         # API Endpoints
│   └── helpers/        # Configuration & Utilities
└── README.md
```

---

## 🎓 Learning Resources

This project is part of an educational series on building RAG applications.

| # | Title | Link | Branch |
|---|---|---|---|
| 1 | About the Course | [Video](https://www.youtube.com/watch?v=Vv6e2Rb1Q6w&list=PLvLvlVqNQGHCUR2p0b8a0QpVjDUg50wQj) | NA |
| 4 | Project Architecture | [Video](https://www.youtube.com/watch?v=Ei_nBwBbFUQ&list=PLvLvlVqNQGHCUR2p0b8a0QpVjDUg50wQj&index=4) | [tut-001](https://github.com/bakrianoo/mini-rag/tree/tut-001) |
| 7 | Uploading a File | [Video](https://www.youtube.com/watch?v=5alMKCbFqWs&list=PLvLvlVqNQGHCUR2p0b8a0QpVjDUg50wQj&index=7) | [tut-004](https://github.com/bakrianoo/mini-rag/tree/tut-004) |
| 8 | File Processing | [Video](https://www.youtube.com/watch?v=gQgr2iwtSBw) | [tut-005](https://github.com/bakrianoo/mini-rag/tree/tut-005) |

*(See full playlist for all videos)*

---

## 📮 Postman Collection

Download the Postman collection to test the API endpoints:
[mini-rag-app.postman_collection.json](/assets/mini-rag-app.postman_collection.json)
