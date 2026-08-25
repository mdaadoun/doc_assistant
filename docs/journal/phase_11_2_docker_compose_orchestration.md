# Session 11.2: Complete Docker Compose Orchestration (FastAPI + Qdrant + React + Volumes)

**Date:** 2026-08-25

*Establishes the production-ready multi-container orchestration architecture for the Corporate Document Assistant. Connects the FastAPI backend ASGI server, Qdrant vector database, and React Vite frontend through a dedicated bridge network, configures named persistent storage volumes, embeds non-root healthcheck probes, and implements an automated static compose validation suite.*

---

### 1. 🎓 Concepts Introduced
- **Multi-Service Container Orchestration:** Coordinating the lifecycle, startup dependencies, and isolated network communication for decoupled backend (`api`), vector database (`qdrant`), and static client (`frontend`) services via `docker-compose.yml`.
- **Persistent Named Volumes:** Provisioning engine-managed storage abstractions (`qdrant_data`, `cache_data`) that persist embeddings, indexes, and cache entries independently of container lifetimes while isolating non-root container permissions.
- **In-Container Healthcheck Probes:** Configuring proactive periodic diagnostic probes across all stack services (`python urllib` probe for API, TCP socket probe for Qdrant, HTTP spider for Frontend) to support deterministic readiness gating.
- **Nginx Reverse Proxy & Unbuffered SSE Streaming:** Serving the React SPA with SPA routing fallback (`try_files $uri $uri/ /index.html`) while proxying `/api/` traffic with disabled buffering (`proxy_buffering off`) and extended read timeouts for real-time SSE token delivery.
- **Static Compose Contract Auditing:** Programmatically inspecting `docker-compose.yml` schemas, port mappings, volume definitions, network topologies, and healthchecks in Python (`validate_docker_compose`) without requiring a live Docker daemon.

---

### 2. 🧠 Architecture Decisions (ADR)

#### Decision A: Dedicated User-Defined Bridge Network (`doc_network`)
- **Option 1 (Default Docker Bridge Network):** Containers use the default bridge network, which requires manual IP tracking and lacks automatic container-name DNS resolution.
- **Option 2 (Selected — User-Defined Bridge Network `doc_network`):** Containers communicate securely using service names (`http://qdrant:6333`, `http://api:8000`), restricting internal container ports from unneeded external network exposure.

#### Decision B: Hybrid Storage Architecture (Named Volumes + Bind Mount)
- **Option 1 (Pure Host Bind Mounts):** Mounting all directories from the host leads to filesystem permission conflicts with non-root containers (UID 10001) and degrades I/O performance on non-Linux hosts.
- **Option 2 (Selected — Named Volumes with Selective Ingestion Bind Mount):** High-throughput data stores (`qdrant_data`, `cache_data`) utilize Docker named volumes for optimal I/O throughput and permission safety, while `./data:/app/data` is mounted as a host bind mount for user document ingestion.

#### Decision C: Nginx Reverse Proxy with Disabled Buffering for SSE
- **Option 1 (Direct Frontend-to-Backend CORS):** Browser directly addresses `http://localhost:8000`, requiring complex CORS allowlist management and exposing multiple service ports to public ingress.
- **Option 2 (Selected — Nginx Reverse Proxy on Port 5173):** Nginx exposes a single origin, routes `/api/` with `proxy_buffering off` and `proxy_read_timeout 300s` for streaming SSE, and falls back all other routes to `index.html`.

---

### 3. 🛠️ Implementation & Code

**Created & Updated Files:**
- `docker-compose.yml`: Complete production compose specification defining `api`, `qdrant`, and `frontend` services with environment variables, healthchecks, `doc_network`, and named volumes (`qdrant_data`, `cache_data`).
- `frontend/nginx.conf`: Nginx configuration supporting SPA routing and unbuffered `/api/` reverse proxy pass with extended SSE timeouts.
- `frontend/Dockerfile`: Multi-stage Dockerfile updated to copy `nginx.conf` into Nginx default configuration.
- `src/core/docker.py`: Enhanced with `validate_docker_compose()`, `REQUIRED_NETWORKS`, updated `REQUIRED_VOLUMES`, and comprehensive compose auditing.
- `src/core/__init__.py`: Exported `validate_docker_compose`, `validate_dockerfile`, `parse_dockerfile_stages`, and `REQUIRED_NETWORKS`.
- `tests/unit/test_docker.py`: Added unit tests verifying compose structure, healthcheck definitions, network attachments, and error scenarios.
- `docs/roadmap.md`: Updated Phase 11 - Task 11.2 to completed `[x]`.

---

### 4. 📌 Session Checklist & Deliverables
1. [x] **Complete `docker-compose.yml` implemented** (`api`, `qdrant`, `frontend`, networks, volumes)
2. [x] **Named volumes configured** (`qdrant_data`, `cache_data` alongside `./data` bind mount)
3. [x] **Service healthcheck probes configured** across all three container services
4. [x] **Frontend Nginx reverse proxy configured** (`frontend/nginx.conf` with unbuffered SSE proxy)
5. [x] **Docker Compose audit engine implemented** (`src/core/docker.py` with `validate_docker_compose()`)
6. [x] **Unit test coverage verified** (`tests/unit/test_docker.py` passing, 434 tests in total suite)
7. [x] **Static type checking & linting passing** (`make lint`, `make typecheck` strict mode with 0 errors)
8. [x] **Roadmap updated** (Phase 11 - Task 11.2 marked `[x]`)
