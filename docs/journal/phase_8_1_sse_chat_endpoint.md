# Architectural Journal — Phase 8.1: POST /api/v1/chat with SSE Streaming

> **Phase:** 8.1 | **Date:** 2026-08-13 | **Status:** Completed

---

## 🎯 Objective
Implement feature 8.1: `POST /api/v1/chat` endpoint with Server-Sent Events (SSE) streaming. Encapsulate the RAG pipeline orchestration inside a dedicated `ChatService` (`src/api/services/chat_service.py`), configure dependency injection via `get_chat_service` (`src/api/dependencies.py`), establish the presentation layer endpoint (`src/api/routes/chat.py`), and provide a FastAPI application factory (`src/api/app.py`).

---

## 💡 Architectural Choices

### 1. Presentation & Service Layer Isolation
- **Context:** The presentation layer router must handle HTTP protocol concerns without embedding direct database, retrieval, or LLM execution logic.
- **Decision:** Created `ChatService` (`src/api/services/chat_service.py`) to manage hybrid candidate retrieval, confidence evaluation, grounded LLM streaming, and SSE event packaging. Route handler `chat_endpoint` in `src/api/routes/chat.py` delegates execution directly to `ChatService`.
- **Rationale:** Strict layer isolation ensures presentation logic remains decoupled from underlying domain services, respecting the Single Responsibility Principle.

### 2. Dependency Injection Pattern (`FastAPI Depends`)
- **Context:** API routes require access to orchestration services while supporting isolated unit testing and mock substitution.
- **Decision:** Defined `get_chat_service` in `src/api/dependencies.py` and passed `ChatService` via `Depends(get_chat_service)` in `chat_endpoint`.
- **Rationale:** Enables seamless dependency overrides (`app.dependency_overrides`) in unit tests without changing route handler signatures.

### 3. Early Confidence Guard Refusal Short-Circuit
- **Context:** Queries lacking relevant retrieved context should not invoke downstream LLM streaming endpoints.
- **Decision:** In `ChatService.stream_chat`, candidate hits are passed to `ConfidenceGuard.evaluate`. If confidence check fails (`passed == False`), an ungrounded refusal stream is yielded immediately alongside metadata.
- **Rationale:** Prevents unnecessary LLM token costs and reduces API response latency for unanswerable or out-of-domain queries.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **SSE Streaming vs WebSockets** | SSE is unidirectional (server to client only). | Unidirectional SSE matches LLM token generation flow while avoiding WebSocket connection handshake overhead. |
| **Initial Metadata Frame Emitting** | Candidate citations are emitted in the initial `metadata` event before token generation finishes. | UI receives immediate citation metadata for zero layout shift while answer deltas stream in real-time. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
POST /api/v1/chat (ChatRequest)
  ├── 1. FastAPI router validates ChatRequest schema
  ├── 2. Injects ChatService via Depends(get_chat_service)
  ├── 3. ChatService.stream_chat(request)
  │      ├── Execute hybrid search (dense + sparse + RRF + reranker)
  │      ├── Evaluate candidates with ConfidenceGuard
  │      ├── If unconfident: yield refusal stream via SSEResponseHandler
  │      └── If confident: yield metadata frame + GroundedGenerator token deltas + done frame
  └── 4. Return StreamingResponse(media_type="text/event-stream")
```

### Module Breakdown
- **`src/api/routes/chat.py`:** FastAPI APIRouter exposing `POST /chat`.
- **`src/api/services/chat_service.py`:** Orchestration service managing retrieval, confidence check, generation, and SSE stream formatting.
- **`src/api/dependencies.py`:** Dependency injection provider for `ChatService`.
- **`src/api/app.py`:** FastAPI application factory (`create_app`).

---

## 🧪 Verification & Results
- **Unit Tests:** Created `tests/unit/test_chat_endpoint.py` and registered `test_run_project_tests_chat_endpoint_suite` in `tests/unit/test_runner.py`.
- **Suite Execution:** All 275 tests passed cleanly in `11.52s`.
- **Type Safety:** `mypy src` passed with 0 errors across 60 source files.
