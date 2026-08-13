# Architectural Journal — Phase 6.2: Cohere Rerank API Fallback Adapter Implementation

> **Phase:** 6.2 | **Date:** 2026-08-13 | **Status:** Completed

---

## 🎯 Objective
Implement the Cohere Rerank API fallback adapter (`CohereRerankerAdapter`) as specified in Phase 6.2 of the roadmap. The adapter enables second-stage cloud-based cross-encoder re-ranking, serving as an external managed fallback/alternative to local FlashRank cross-encoder inference.

---

## 💡 Architectural Choices

### 1. Hybrid Client Execution Path (SDK + `httpx` Fallback)
- **Context:** Applications may run in environments without the external `cohere` SDK installed or may want to pass lightweight custom/mock HTTP clients.
- **Decision:** Implemented `CohereRerankerAdapter` in `src/clients/cohere_reranker.py` supporting both native SDK `.rerank()` dispatch, injected HTTP client dispatch, and direct REST API execution via `httpx.Client()`.
- **Rationale:** Ensures zero mandatory dependency on the heavy SDK while allowing seamless client injection for testing and flexible deployment options.

2. Integration with `BaseRerankerAdapter` Contract
- **Context:** The retrieval layer requires a uniform interface regardless of whether re-ranking runs locally via FlashRank ONNX or remotely via Cohere API.
- **Decision:** `CohereRerankerAdapter` extends `BaseRerankerAdapter` with `provider_name="cohere"` and default model `"rerank-v3.5"`.
- **Rationale:** Preserves layer isolation and simplifies primary/fallback strategy pattern composition in the re-ranking service.

3. Fail-Fast Configuration & Structured Exception Handling
- **Context:** Unconfigured API credentials or external API failures must be reported cleanly without crashing the retrieval pipeline with unhandled generic exceptions.
- **Decision:** Raises `ConfigurationError` (`code="MISSING_API_KEY"`) during initialization if no API key is provided, and wraps API runtime failures into `RetrievalError` (`code="RERANKER_INFERENCE_ERROR"`).
- **Rationale:** Maintains compliance with system error handling policies and domain exception hierarchy.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Managed Cloud API vs Local ONNX Reranking** | Network roundtrips add ~100-200ms latency and incur API costs compared to local CPU ONNX inference. | Candidate truncation window limits external requests to top 30 candidates (`candidate_k=30`) and top 5 output (`top_k=5`). |
| **Direct REST API vs SDK Dependency** | Manual payload construction for REST endpoints requires handling HTTP response schemas. | Adapter normalizes SDK objects, dict responses, and HTTP response JSON into standard domain `RetrievalResult` models. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
CohereRerankerAdapter.rerank(query, hits, candidate_k=30, top_k=5)
  -> Truncate candidate hits to top 30 (candidate_k)
  -> Extract document texts: [hit.text for hit in candidate_hits]
  -> Invoke Cohere API (SDK .rerank() or httpx POST to https://api.cohere.com/v2/rerank)
  -> Map response indices & relevance scores back to RetrievalResult objects (retrieval_method="cohere")
  -> Sort descending by relevance score & return top 5 (top_k)
```

---

## 🔬 Verification Summary
- Executed unit test suite: **210 passed** in 8.29s (including `test_cohere_reranker.py` and test runner registration).
- Mypy type checking: **0 errors** across all source files (`Success: no issues found in 49 source files`).
- Ruff linter: **All checks passed!**
