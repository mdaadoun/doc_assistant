# Architectural Journal — Phase 6.3: Reranker Service with Primary/Fallback Strategy Pattern

> **Phase:** 6.3 | **Date:** 2026-08-13 | **Status:** Completed

---

## 🎯 Objective
Implement `RerankerService` in `src/retrieval/reranker_service.py` orchestrating cross-encoder candidate re-ranking using a primary adapter (local FlashRank ONNX) and a fallback adapter (Cohere Rerank API or Mock adapter). Integrated with `DebugRetrievalBuilder` to populate stage-wise `final_reranked` search results.

---

## 💡 Architectural Choices

### 1. Primary / Fallback Strategy Pattern Composition
- **Context:** Cross-encoder inference can fail due to local ONNX runtime issues, unmapped models, or external API outages / missing credentials.
- **Decision:** Implemented `RerankerService` in `src/retrieval/reranker_service.py` wrapping primary and fallback `BaseRerankerAdapter` instances.
- **Rationale:** Delegates cross-encoder re-ranking to a primary adapter (e.g. FlashRank CPU ONNX inference) and gracefully catches runtime errors to seamlessly trigger a fallback adapter (e.g. Cohere Rerank API or Mock adapter).

### 2. Safe Adapter Instantiation & Dependency Shielding
- **Context:** External SDKs or API keys may be absent in offline test environments.
- **Decision:** Safely wraps adapter creation inside `_safe_create_adapter`, returning `None` on configuration or import failures rather than crashing the retrieval pipeline on initialization.
- **Rationale:** Requires checking for adapter availability before invocation, but enables offline mock fallbacks and graceful degradation without throwing unhandled startup crashes.

### 3. Debug Retrieval Payload Integration
- **Context:** Diagnosing relevance degradation requires full visibility into search candidates at all pipeline stages.
- **Decision:** Updated `DebugRetrievalBuilder` to accept `RerankerService` as an optional dependency and execute final stage re-ranking over hybrid RRF fused candidate hits.
- **Rationale:** Exposes end-to-end stage-wise observability for dense search, sparse search, RRF fusion, and final cross-encoder re-ranking in `DebugRetrievalResponse.final_reranked`.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Primary / Fallback Strategy Pattern Composition** | Adds slight orchestration complexity in error handling and logging. | Guarantees high availability and zero unhandled exception leakage during critical query execution paths. |
| **Safe Adapter Instantiation & Dependency Shielding** | Requires checking for adapter availability before invocation. | Enables offline mock fallbacks and graceful degradation without unhandled exceptions. |
| **Debug Retrieval Payload Integration** | Incurs additional cross-encoder execution time during debug payload construction. | Reranking only processes top candidate hits (`candidate_k=30`) down to top output hits (`top_k=5`). |

---

## 🛠️ Implementation & Code

### Key Flows
```text
RerankerService.rerank(query, hits, candidate_k=30, top_k=5)
  -> Check query and hits: return [] if empty or blank
  -> Step 1: Attempt primary_adapter.rerank(query, hits, candidate_k, top_k)
       -> If success: return primary reranked results
       -> If exception: catch & log warning ("rerank_primary_failed_attempting_fallback")
  -> Step 2: If auto_fallback is True and fallback_adapter is available:
       -> Attempt fallback_adapter.rerank(query, hits, candidate_k, top_k)
       -> If success: return fallback reranked results
       -> If exception: raise RetrievalError(code="RERANK_ALL_FAILED")
  -> Step 3: If no adapter available or fallback disabled: raise RetrievalError
```

---

## 🔬 Verification Summary
- Executed unit test suite: **30 passed** in 8.69s (including `test_reranker_service.py` and test runner registration).
- Mypy type checking: **0 errors** across source files (`Success: no issues found in 2 source files`).
