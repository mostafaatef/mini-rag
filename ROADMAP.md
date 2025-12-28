# Enterprise Technical Roadmap: From MVP to Ministry-Grade RAG

This document outlines the strategic technical steps required to evolve the current "Mini RAG" Proof-of-Concept into a production-ready, enterprise-grade solution suitable for government or ministry deployment.

## Phase 1: Security & Compliance (Highest Priority)

*Objective: Secure access and ensure data integrity.*

- [ ] **Authentication & Authorization**
  - Implement **OAuth2 / OIDC** (Integrate with Keycloak, Azure AD, or Auth0).
  - Enforce **JWT Validation** on all API endpoints (`Dependencies`).
  - Implement **RBAC (Role-Based Access Control)**:
    - `Admin`: Manage users, view system logs, re-index data.
    - `Editor`: Upload/Delete documents.
    - `Viewer`: Query only.

- [ ] **Input/Output Guardrails**
  - Integrate **Guardrails AI** or **NeMo Guardrails**.
  - **Input**: Block Prompt Injection attacks, PII leaks, and malicious content.
  - **Output**: Detect and block hallucinations or toxic/inappropriate language before responding.

- [ ] **Audit Logging**
  - Create a persistent audit trail (separate from app logs).
  - Log: `User ID`, `Query Timestamp`, `Access Type`, `Document Accessed`.
  - Ensure logs are immutable or strictly controlled (Compliance Requirement).

## Phase 2: Advanced RAG Architecture (Accuracy)

*Objective: Improve retrieval precision and answer quality.*

- [ ] **Hybrid Search**
  - Combine **Sparse Vectors (BM25)** (Keyword match) with **Dense Vectors** (Semantic match).
  - *Why*: User searches often contain specific IDs, Law Numbers, or Proper Nouns that semantic search might miss.
  - *Tech*: Qdrant Hybrid or switching to Elasticsearch/OpenSearch.

- [ ] **The "Reranker" Layer**
  - Introduce a **Cross-Encoder Reranker** (e.g., Cohere Rerank, BGE-Reranker).
  - *Process*: Retrieve Top-50 via Hybrid Search -> Rerank Top-50 -> Pass Top-5 to LLM.
  - *Impact*: Drastically improves relevance.

- [ ] **Advanced Ingestion Pipeline**
  - Improve PDF Parsing: Use **Unstructured IO** or **Azure Document Intelligence** (OCR).
  - Handle **Tables** specifically (markdown preservation).
  - Add **Parent-Child Chunking**: Retrieve small chunks for accuracy, but feed the surrounding "Parent" context to the LLM.

- [ ] **Query Expansion/Transformation**
  - Implement "HyDE" (Hypothetical Document Embeddings) or Query Rewriting to improve Arabic search terms before retrieval.

## Phase 3: Scalability & Reliability

*Objective: Handle high concurrency and large workloads.*

- [ ] **Async Worker Queue**
  - Decouple file processing from the main Web API.
  - Implementation: **Celery** + **Redis** or **RabbitMQ**.
  - *Why*: Preventing server timeouts when uploading large (100MB+) PDF Law books.

- [ ] **Caching Layer**
  - **Semantic Caching**: Use **Redis** to store query embeddings.
  - If a user asks a similar question to a previous one, return the cached answer instantly.

- [ ] **Infrastructure**
  - Docker Compose -> **Kubernetes (Helm Charts)**.
  - Horizontal Pod Autoscaling (HPA) based on CPU/Memory/Request Count.
  - Database High Availability (Replica sets for Mongo/Postgres).

## Phase 4: Observability & Evaluation

*Objective: Trust, monitor, and improve.*

- [ ] **End-to-End Tracing**
  - Implement **OpenTelemetry**.
  - Trace request lifecycle: API -> DB -> VectorDB -> LLM.
  - Visualize latency bottlenecks (e.g., with Jaeger or Datadog).

- [ ] **Evaluation Pipeline (CI/CD for AI)**
  - Integrate **Ragas** or **DeepEval**.
  - Create a "Golden Dataset" of 100 Q&A pairs verified by domain experts.
  - Auto-run evaluation on every code/prompt change to measure `Faithfulness` and `Answer Relevance`.

- [ ] **Feedback Loop**
  - Add API endpoint for users to vote (👍/👎) on answers.
  - Store feedback to retrain/fine-tune future models.

## Phase 5: Deployment Strategy

*Objective: Data Sovereignty and Performance.*

- [ ] **Local LLM Hosting** (Optional but likely for Ministry)
  - Replace Cloud Models (Google/OpenAI) with high-performance Local Models (e.g., **Llama 3 70B**, **Qwen 2.5 72B**).
  - Host using **vLLM** or **TGI** on GPU servers within Ministry premise (Air-gapped).

- [ ] **Secrets Management**
  - Move `.env` to a secure Vault (e.g., HashiCorp Vault).
