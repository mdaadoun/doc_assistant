# Architectural Journal — Phase 1.6: Docker Compose Skeleton Setup

> **Phase:** 1.6 | **Date:** 2026-08-10 | **Status:** Completed

---

## 🎯 Objective
Initialize the `docker-compose.yml` multi-container infrastructure skeleton orchestrating FastAPI backend, Qdrant vector database, and React frontend services with volume persistence, service dependency mapping, and multi-stage container build definitions.

---

## 💡 Architectural Choices

### 1. Multi-Service Decoupled Container Orchestration (`docker-compose.yml`)
- **Context:** Corporate RAG platforms require vector index storage, backend REST/SSE API services, and dynamic frontend UI clients operating in tandem.
- **Decision:** Define isolated container services (`api`, `qdrant`, `frontend`) in `docker-compose.yml` with explicit dependency ordering (`api` depends on `qdrant`, `frontend` depends on `api`).
- **Rationale:** Ensures clean service boundary separation, independent container scalability, and exact environment parity between development and production deployments.

### 2. Multi-Stage Non-Root Frontend & API Dockerfiles
- **Context:** Container security and image size optimization are critical for production deployment standards.
- **Decision:** Implement multi-stage builds (`builder` -> `runtime`) for both FastAPI backend (`Dockerfile`) and React frontend (`frontend/Dockerfile`), using slim/alpine base images and non-root users/Nginx static servers.
- **Rationale:** Minimizes container footprint (<100MB static frontend, optimized Python runtime) while eliminating security vulnerabilities associated with running containers as root.

### 3. Volume Persistence for Vector Index Storage (`qdrant_data`)
- **Context:** Qdrant vector database instances lose indexed collections if storage is ephemeral inside container layers.
- **Decision:** Configure named volume `qdrant_data` bound to `/qdrant/storage` inside the Qdrant container.
- **Rationale:** Prevents vector index data loss across container rebuilds, upgrades, or restarts.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Multi-Service Local Setup** | Requires Docker engine and higher local memory overhead during development. | Developer options to run individual services natively or lightweight Qdrant containers during rapid iteration. |
| **Multi-Stage Node/Nginx Frontend Build** | Requires frontend Node dependency installation stage during container builds. | Docker build caching layers avoid re-running `npm install` unless package manifests change. |
| **Automated Docker Auditor (`src/core/docker.py`)** | Requires updating validation schemas if service names or ports change. | Clear constants (`REQUIRED_DOCKER_SERVICES`, `REQUIRED_PORT_MAPPINGS`) exported in `core.docker` enforce alignment. |
