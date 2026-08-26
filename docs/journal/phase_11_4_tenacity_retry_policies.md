# Session 11.4: Add Tenacity Retry Policies on All External I/O (LLM, Embedding, Reranker APIs)

**Date:** 2026-08-26

*Implements production-grade resilience and fault tolerance across all external I/O boundaries in the Corporate Document Assistant. Introduces a centralized transient exception classifier (`is_retryable_exception`) and Tenacity-powered retry runners (`retry_sync_call`, `retry_async_call`) configured with exponential backoff and randomized jitter. Seamlessly integrates retry policies into OpenAI and Google GenAI embedding adapters, Cohere cross-encoder rerank adapters, and GroundedGenerator streaming generation, guaranteeing automatic recovery from transient HTTP 429 rate limits and 5xx upstream outages while ensuring immediate fail-fast behavior on non-retryable client and configuration errors.*

---

### 1. 🎓 Concepts Introduced
- **Exponential Backoff with Full Randomized Jitter:** An algorithmic retry pacing strategy that exponentially increases wait times between consecutive failed attempts while adding randomized variance (`wait_random_exponential`) to decorrelate concurrent retries and eliminate thundering herd storms against upstream API providers.
- **Transient Fault Discrimination:** A robust classification mechanism (`is_retryable_exception`) inspecting HTTP status codes (429, 500, 502, 503, 504), SDK exception hierarchies (OpenAI rate limit, timeout, connection errors; httpx status and network errors), and stdlib connection dropouts to isolate temporary errors from permanent bugs.
- **Fast-Failing on Non-Retryable Client Faults:** Immediate abort on 4xx client errors (400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found) and domain `ConfigurationError`, preventing wasted backoff latency when requests cannot succeed without user/code intervention.
- **Resilient Stream Connection Handshake:** Protecting asynchronous SSE stream creation (`client.chat.completions.create(stream=True)`) with exponential retries before token emission, preventing broken connection handshakes while avoiding duplicate token artifacts down to the client.
- **Structured Resilience Telemetry:** Emitting detailed warning logs (`tenacity_retry_attempt`) capturing target function name, attempt index, planned sleep duration, and underlying exception details before each retry interval.

---

### 2. 🧠 Architecture Decisions (ADR)

#### Decision A: Dynamic Runner Wrappers (`retry_sync_call`/`retry_async_call`) vs. Static Class Decorators
- **Option 1 (Static Module Decorators `@retry(...)`):** Binds fixed retry parameters at module import time, complicating dynamic configuration overrides from `Settings` and making unit test mocking fragile.
- **Option 2 (Selected — Dynamic Runner Wrappers):** `retry_sync_call` and `retry_async_call` instantiate Tenacity `Retrying` and `AsyncRetrying` contexts dynamically using active `Settings` values, enabling runtime adjustments and clean unit testing.

#### Decision B: Centralized Exception Classifier vs. Per-Adapter Exception Handlers
- **Option 1 (Per-Adapter Try/Except Catch Blocks):** Duplicates error code matching and transient status parsing across multiple provider adapters (OpenAI, Gemini, Cohere, AsyncOpenAI).
- **Option 2 (Selected — Unified `is_retryable_exception` Discriminator):** Centralizes all HTTP, SDK, and network error classification logic within `src/core/retry.py`, ensuring consistent retry behavior across all infrastructure clients.

#### Decision C: Stream Initialization Retry vs. In-Stream Iteration Retry
- **Option 1 (In-Stream Token Retry):** Retrying mid-stream during token iteration requires complex state rollback mechanisms and risks emitting duplicated response text to downstream clients.
- **Option 2 (Selected — Stream Handshake Retry):** Retrying the initial completions stream creation resolves connection failures and rate limits before any data is yielded, ensuring clean SSE delivery.

---

### 3. 🛠️ Implementation & Code

**Created & Updated Files:**
- `src/core/retry.py`: Implemented `is_retryable_exception`, `_log_retry_attempt`, `create_sync_retrying`, `create_async_retrying`, `retry_sync_call`, and `retry_async_call`.
- `src/core/config.py`: Added `retry_max_attempts`, `retry_min_wait_seconds`, and `retry_max_wait_seconds` to `Settings`.
- `src/core/__init__.py`: Exported core retry and resilience functions.
- `src/clients/openai_embedding.py`: Integrated `retry_sync_call` into batch embedding creation.
- `src/clients/gemini_embedding.py`: Integrated `retry_sync_call` into Gemini `models.embed_content` batch calls.
- `src/clients/cohere_reranker.py`: Integrated `retry_sync_call` into Cohere SDK and httpx API rerank calls.
- `src/generation/engine.py`: Integrated `retry_async_call` into `_create_completion_stream` for LLM generation.
- `tests/unit/test_retry_policies.py`: Implemented 13 unit tests covering exception discrimination, sync/async retry execution, exhaustion, fast-failing, and adapter integrations.
- `docs/roadmap.md`: Updated Phase 11 - Task 11.4 to completed `[x]`.

---

### 4. 📌 Session Checklist & Deliverables
1. [x] **Centralized Exception Discriminator Built** (`is_retryable_exception` in `src/core/retry.py`)
2. [x] **Configurable Tenacity Retrying Orchestrators Created** (`create_sync_retrying`, `create_async_retrying`)
3. [x] **Sync and Async Runner Wrappers Implemented** (`retry_sync_call`, `retry_async_call`)
4. [x] **Settings Config Updated** with retry parameters (`retry_max_attempts=4`, `min_wait=0.5s`, `max_wait=8.0s`)
5. [x] **OpenAI Embedding Adapter Retries Added**
6. [x] **Gemini Embedding Adapter Retries Added**
7. [x] **Cohere Reranker Adapter Retries Added**
8. [x] **GroundedGenerator LLM Stream Handshake Retries Added**
9. [x] **Comprehensive Test Suite Passing** (480 passed, 1 skipped)
10. [x] **Static Typing & Linter Clean** (`make lint` and `make typecheck` strict mode passing with 0 errors)
11. [x] **Roadmap Marked Completed** (Phase 11 - Task 11.4 marked `[x]`)
