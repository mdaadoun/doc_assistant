# Architectural Journal — Phase 2.2: Domain Schemas Setup

> **Phase:** 2.2 | **Date:** 2026-08-10 | **Status:** Completed

---

## 🎯 Objective
Implement domain schemas for RAG operations, document ingestion, hybrid search hit tracking, user chat requests/responses, citations, and FinOps cost telemetry (`ChunkDocument`, `RetrievalResult`, `ChatRequest`, `ChatResponse`, `Citation`, `FinOpsMetadata`, `DebugRetrievalResponse`).

---

## 💡 Architectural Choices

### 1. Immutable Pydantic V2 Domain Models (`frozen=True`)
- **Context:** RAG pipelines pass document chunks, search candidates, and generated completions across multiple processing stages.
- **Decision:** Extend `BaseDomainModel` across all domain schemas (`ChunkMetadata`, `ChunkDocument`, `RetrievalResult`, `DebugRetrievalResponse`, `ChatRequest`, `Citation`, `FinOpsMetadata`, `ChatResponse`).
- **Rationale:** Enforces side-effect-free data flow, thread safety, and strict runtime field validation across ingestion, retrieval, and generation services.

### 2. Single-Responsibility Schema Modules (250 LOC Limit)
- **Context:** Keeping all domain models in a single monolithic file risks violating modularity guidelines and the hard 250 LOC/file limit.
- **Decision:** Split schemas into cohesive domain submodules (`src/models/chunk.py`, `src/models/retrieval.py`, `src/models/chat.py`) and re-export them cleanly via `src/models/__init__.py`.
- **Rationale:** Maintains modular organization, single responsibility per file, and high maintainability under 200 LOC per file.

### 3. Strict Boundary Validation (`extra="forbid"`) and Range Constraints
- **Context:** User query inputs and retrieved external data payloads could contain unexpected extra parameters or invalid numerical bounds.
- **Decision:** Enforce `extra="forbid"` and apply Pydantic `Field` bounds (e.g. `ge=0`, `ge=1`, `min_length=1`, `confidence_score` between `0.0` and `1.0`).
- **Rationale:** Guarantees data sanitization at API boundaries and prevents payload pollution.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Decoupled Module Structure** | Requires importing from submodules or managing exports in `__init__.py`. | Centralized re-export in `src/models/__init__.py` provides clean top-level imports (`from models import ChatRequest, ChunkDocument`). |
| **Strict Field Validation Bounds** | Raises `ValidationError` if external sources produce out-of-bound metadata. | Upstream parsers and adapters sanitize values before instantiation. |
| **Decoupled Chunk & Retrieval Schemas** | Separates ingestion chunks (`ChunkDocument`) from retrieval hits (`RetrievalResult`). | `ChunkDocument` models static index data while `RetrievalResult` encapsulates query-dynamic scores and strategies. |
