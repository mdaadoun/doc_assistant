# Architectural Journal — Phase 8.2: GET /api/v1/debug/retrieval Diagnostic Endpoint

> **Phase:** 8.2 | **Date:** 2026-08-13 | **Status:** Completed

---

## 🎯 Objective
Implement feature 8.2: `GET /api/v1/debug/retrieval` diagnostic endpoint. Provide a dedicated REST API diagnostic route exposing stage-wise search scores and ranks (dense vector search, sparse BM25 search, RRF fusion, and final cross-encoder reranking) powered by `DebugRetrievalBuilder` (`src/retrieval/debug_retrieval.py`) and wired via FastAPI dependency injection (`src/api/dependencies.py`).

---

## 💡 Architectural Choices

### 1. Read-Only Diagnostic Route & Safe Idempotent Semantics (`GET`)
- **Context:** Observability and debugging workflows require inspecting intermediate retrieval scores without mutating state or triggering generation pipelines.
- **Decision:** Implemented `GET /api/v1/debug/retrieval` (`src/api/routes/debug.py`) returning `DebugRetrievalResponse`.
- **Rationale:** Using HTTP `GET` ensures standard HTTP caching compatibility, safe idempotent invocation, and easy URL sharing with query parameters.

### 2. Dependency Injection Pattern (`DebugRetrievalBuilderDep`)
- **Context:** Route handlers must decouple endpoint routing from retrieval pipeline construction while allowing mock overrides in unit tests.
- **Decision:** Configured `get_debug_retrieval_builder` in `src/api/dependencies.py` and exported `DebugRetrievalBuilderDep = Annotated[DebugRetrievalBuilder, Depends(get_debug_retrieval_builder)]`.
- **Rationale:** Adheres strictly to FastAPI best practices (eliminating B008 lints) and enables fast dependency substitution (`app.dependency_overrides`) during unit testing.

### 3. Defensive Partial Pipeline Handling
- **Context:** Pipeline components (e.g., reranker or sparse search) may be optional or unconfigured in specific deployments.
- **Decision:** Updated `DebugRetrievalBuilder.__init__` and `build()` to handle optional search services gracefully (`dense_search`, `sparse_search`, `rrf_fusion`, `reranker`), falling back to empty hit lists when unconfigured.
- **Rationale:** Guarantees runtime stability and prevents unhandled `AttributeError` exceptions when debugging partially initialized pipelines.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Granular Top-K Parameters** | Exposing per-stage top-k query parameters increases request complexity. | Defaults are set to `None` so standard stage defaults are used unless explicitly overridden. |
| **Compact Debug Hits vs Full Payloads** | Debug hits strip heavy document text to reduce JSON payload size. | Detailed text remains available in `final_reranked` while `dense_hits`, `sparse_hits`, and `rrf_fused` stay compact. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
GET /api/v1/debug/retrieval?query=...&dense_top_k=...
  ├── 1. FastAPI router validates query parameters (query required, top_k >= 1)
  ├── 2. Injects DebugRetrievalBuilder via DebugRetrievalBuilderDep
  ├── 3. DebugRetrievalBuilder.build(query, dense_top_k, sparse_top_k, rrf_top_k, rerank_top_k)
  │      ├── Run dense search -> dense_hits (with raw scores & 1-indexed ranks)
  │      ├── Run sparse search -> sparse_hits (with BM25 scores & 1-indexed ranks)
  │      ├── Fuse candidate hits -> rrf_fused (with RRF fused scores & ranks)
  │      └── Rerank hits via RerankerService -> final_reranked candidate results
  └── 4. Return DebugRetrievalResponse payload
```

### Module Breakdown
- **`src/api/routes/debug.py`:** FastAPI APIRouter exposing `GET /retrieval`.
- **`src/api/dependencies.py`:** Dependency injection providers (`get_debug_retrieval_builder`, `DebugRetrievalBuilderDep`).
- **`src/retrieval/debug_retrieval.py`:** Pipeline builder assembling stage-wise hits into `DebugRetrievalResponse`.
- **`src/api/app.py`:** App factory including `debug_router` under `/api/v1`.

---

## 🧪 Verification & Results
- **Unit Tests:** Created `tests/unit/test_debug_retrieval_endpoint.py` and registered `test_run_project_tests_debug_retrieval_endpoint_suite` in `tests/unit/test_runner.py`.
- **Suite Execution:** All 34 tests passed cleanly in `11.08s`.
- **Type Safety & Linting:** `mypy` and `ruff check` passed with 0 errors across all modified files.
