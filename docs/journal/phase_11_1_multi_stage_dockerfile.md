# Session 11.1: Multi-Stage Non-Root Dockerfile (< 250MB, UID 10001)

**Date:** 2026-08-24

*Builds and hardens the production multi-stage Docker container specification for the Corporate Document Assistant. Eliminates build-time dependencies from runtime, establishes non-root user execution (UID/GID 10001), optimizes layer caching, configures healthcheck probes, and enforces image size minimization (< 250MB).*

---

### 1. 🎓 Concepts Introduced
- **Multi-Stage Container Build:** Decoupling the dependency installation and build toolchain (Poetry, compiler headers) in a `builder` stage from the minimal `runtime` container image.
- **Least-Privilege Non-Root Execution:** Provisioning a dedicated unprivileged user (`appuser`, UID 10001) and group (`appgroup`, GID 10001) with `/bin/false` login shell to prevent container breakout vulnerabilities.
- **Layer Caching Optimization:** Structuring Docker instructions from least to most volatile (base image -> pyproject.toml -> dependency install -> application source) to maximize build cache reuse across CI/CD pipelines.
- **Automated Dockerfile Contract Auditing:** Programmatically inspecting Dockerfile instructions (`parse_dockerfile_stages`, `validate_dockerfile`) within the test harness to verify security and operational standards without requiring a live Docker daemon.

---

### 2. 🧠 Architecture Decisions (ADR)

#### Decision A: Multi-Stage Build (Builder -> Runtime)
- **Option 1 (Single-Stage Container):** Installing build tools and runtime dependencies together results in heavy image sizes (> 600MB) and leaves unnecessary compilation tools in production.
- **Option 2 (Selected — Multi-Stage Build):** A `builder` stage installs production dependencies via Poetry into system site-packages, and a lightweight `runtime` stage copies only the required site-packages and application files, achieving a final image size < 250MB.

#### Decision B: Base Image Selection (`python:3.11-slim` vs `alpine`)
- **Option 1 (`alpine` Base Image):** Smaller initial base image (~50MB) but requires compiling wheels from source due to musl libc incompatibilities with PyMuPDF and ONNX runtime, drastically increasing build times.
- **Option 2 (Selected — `python:3.11-slim`):** Standard glibc-based Debian slim image provides binary wheel compatibility while keeping total compressed runtime size well under the 250MB threshold.

#### Decision C: Explicit Numeric UID/GID 10001
- **Option 1 (Default Root User or Named User Only):** Running as root creates severe container escape vulnerabilities; named users without explicit numeric IDs can complicate Kubernetes `securityContext` policy enforcement.
- **Option 2 (Selected — Explicit Numeric UID/GID 10001):** Creates dedicated `appuser` (UID 10001) and `appgroup` (GID 10001) and sets `USER 10001`, complying directly with Kubernetes non-root container standards.

---

### 3. 🛠️ Implementation & Code

**Created & Updated Files:**
- `Dockerfile`: Multi-stage Dockerfile with `builder` and `runtime` stages, UID 10001 non-root execution, healthchecks, and Uvicorn ASGI entrypoint.
- `.dockerignore`: Excluded git histories, caches, virtual environments, test fixtures, and documentation from build context.
- `src/main.py`: Created top-level entrypoint module exposing `app` and `create_app` factory with `uvicorn.run` bootstrap.
- `src/core/docker.py`: Added `parse_dockerfile_stages()`, `validate_dockerfile()`, and composite `validate_docker_setup()` enhancements.
- `tests/unit/test_docker.py`: Comprehensive test suite verifying multi-stage definitions, UID/GID 10001 validation, and stage parsing.
- `tests/unit/test_main.py`: Unit tests verifying `src.main` entrypoint exports and factory behavior.
- `tests/unit/test_runner.py`: Registered `test_main.py` in test runner suites.
- `docs/roadmap.md`: Updated Phase 11 - Task 11.1 to completed `[x]`.

---

### 4. 📌 Session Checklist & Deliverables
1. [x] **Multi-stage Dockerfile implemented** (`Dockerfile` with `builder` and `runtime` stages)
2. [x] **Non-root security hardening established** (`appuser:appgroup` with UID/GID 10001, `USER 10001`)
3. [x] **Build context filtered** (`.dockerignore` excluding caches and development files)
4. [x] **Application entrypoint created** (`src/main.py`)
5. [x] **Dockerfile audit engine implemented** (`src/core/docker.py`)
6. [x] **Unit test coverage verified** (`tests/unit/test_docker.py` and `tests/unit/test_main.py` passing, total suite 432 passed)
7. [x] **Static type checking & linting passing** (`make lint`, `make typecheck` strict mode with 0 errors)
8. [x] **Roadmap updated** (Phase 11 - Task 11.1 marked `[x]`)
