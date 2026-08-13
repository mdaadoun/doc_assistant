# Architectural Journal — Phase 6.1: FlashRank Cross-Encoder Adapter Implementation

> **Phase:** 6.1 | **Date:** 2026-08-13 | **Status:** Completed

---

## 🎯 Objective
Implement the FlashRank cross-encoder adapter (`ms-marco-MiniLM-L-6-v2`, top 30 candidate hits → top 5 reranked hits) as outlined in Phase 6.1 of the roadmap. The adapter provides second-stage neural re-ranking over candidate search hits from the RRF hybrid retrieval stage, improving context precision for downstream LLM generation.

---

## 💡 Architectural Choices

### 1. Abstract Base Reranker Adapter (`BaseRerankerAdapter`)
- **Context:** The retrieval architecture requires supporting multiple reranker providers (local FlashRank ONNX, Cohere Rerank API, mock provider).
- **Decision:** Created `BaseRerankerAdapter` in `src/clients/base_reranker.py` defining standard contracts (`rerank()`, `model_name`, `provider_name`).
- **Rationale:** Enforces strict interface isolation between retrieval orchestration and specific cross-encoder model engines, enabling seamless strategy pattern switching and fallback capabilities.

### 2. Local ONNX FlashRank Cross-Encoder Adapter (`FlashRankRerankerAdapter`)
- **Context:** Cross-encoder inference evaluates joint query-passage attention locally on CPU without external API latency or costs.
- **Decision:** Built `FlashRankRerankerAdapter` in `src/clients/flashrank_reranker.py` wrapping the `flashrank.Ranker` engine with candidate windowing (top 30 → top 5).
- **Rationale:** Uses CPU-optimized ONNX runtime models for fast inference while mapping model requests gracefully (`ms-marco-MiniLM-L-6-v2` / `ms-marco-MiniLM-L-12-v2`).

### 3. Offline Deterministic Mock Reranker (`MockRerankerAdapter`)
- **Context:** Unit test suites require executing deterministically and instantaneously without downloading large ONNX model zips over network.
- **Decision:** Implemented `MockRerankerAdapter` in `src/clients/mock_reranker.py`.
- **Rationale:** Simulates candidate windowing and relevance scoring based on token overlap, enabling unit test runs in isolated sandbox environments.

### 4. Reranker Factory & Configuration Schema Extensions
- **Context:** System settings and client instantiation must remain type-safe and configurable via environment variables.
- **Decision:** Created `create_reranker_adapter` in `src/clients/reranker.py` and added `reranker_provider`, `reranker_model`, `reranker_candidate_k`, `reranker_top_k` to `src/core/config.py`.
- **Rationale:** Centralizes adapter creation and aligns with Pydantic `BaseSettings` practices across the project.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Local ONNX Cross-Encoder vs Vector Search** | Local ONNX execution adds ~30-50ms CPU latency compared to ~5ms for bi-encoder search. | Candidate truncation window limits inference to top 30 candidates, keeping total retrieval latency within acceptable boundaries. |
| **Model Registry Unmapped Names** | `ms-marco-MiniLM-L-6-v2` is not directly listed in FlashRank 0.2.x default map. | Automatic fallback mapping to `ms-marco-MiniLM-L-12-v2` guarantees execution without throwing unhandled exceptions. |
| **Mock Reranker vs Heavy Integration Tests** | Mock adapter does not execute actual neural network weights during unit tests. | Separate integration test suite validates real ONNX model loading when model assets are present. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
FlashRankRerankerAdapter.rerank(query, hits, candidate_k=30, top_k=5)
  -> Truncate input hits to candidate_k (top 30)
  -> Format passages payload: [{"id": cid, "text": text, "meta": {...}}]
  -> Execute Ranker.rerank(RerankRequest(query, passages))
  -> Map raw ONNX scores back to RetrievalResult(relevance_score, retrieval_method="flashrank")
  -> Sort descending by relevance score & return top_k (top 5)
```

---

## 🔬 Verification Summary
- Executed full unit test suite: **202 passed** in 7.84s.
- Verified strict Mypy type checking across all files (`Success: no issues found in 49 source files`).
- Verified Ruff linter rules (`All checks passed!`).
