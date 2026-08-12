# Architectural Journal — Phase 5.1: Dense Vector Search Implementation

> **Phase:** 5.1 | **Date:** 2026-08-12 | **Status:** Completed

---

## 🎯 Objective
Implement the dense vector search stage of the hybrid retrieval engine (Phase 5). The feature embeds a user query and retrieves the top 50 nearest vectors from Qdrant using cosine similarity, producing a ranked list of `RetrievalResult` candidates for downstream Reciprocal Rank Fusion (RRF, task 5.3).

---

## 💡 Architectural Choices

### 1. Dedicated Query-Time Service Layer (`DenseSearchService`)
- **Context:** Phase 4 delivered `VectorStoreAdapter` for low-level Qdrant CRUD and `BaseEmbeddingAdapter` for text embedding. Feature 5.1 requires a query-time orchestration that sequences embedding + validation + retrieval.
- **Decision:** Implemented `DenseSearchService` that composes `BaseEmbeddingAdapter` and `VectorStoreAdapter` via dependency injection. It owns the query-time flow: validate query → embed → validate dimension → check collection → delegate to `vector_store.search()`.
- **Rationale:** Separates query-time retrieval concerns from indexing-time vector store operations, keeps the retrieval pipeline modular for later RRF fusion (5.3) and re-ranking (6.x), and enables dependency-injected testing with mock embedding adapters.

### 2. Default Top-50 Candidate Pool (`DENSE_TOP_K_DEFAULT = 50`)
- **Context:** The roadmap specifies top 50 for dense retrieval to provide sufficient recall before RRF fusion merges dense and sparse results.
- **Decision:** Introduced a module-level constant `DENSE_TOP_K_DEFAULT = 50` used as the service default, while allowing per-call override via the `top_k` parameter.
- **Rationale:** A larger candidate pool reduces the risk of missing relevant chunks that sparse BM25 might rank differently, while 50 keeps downstream re-ranking cost bounded. The constant makes the default explicit and testable.

### 3. Fail-Fast Validation Guards
- **Context:** Query-time retrieval can fail for several reasons: empty queries, embedding dimension mismatches, or missing collections.
- **Decision:** The service validates the query is non-empty (`EMPTY_QUERY`), verifies the query embedding dimension matches the vector store dimension (`QUERY_DIM_MISMATCH`), and checks the target collection exists (`COLLECTION_NOT_FOUND`) before delegating to Qdrant.
- **Rationale:** Fail-fast guards produce clear `RetrievalError` codes instead of opaque Qdrant failures, improving debuggability and preventing wasted network round-trips.

### 4. Reuse of Existing Vector Store Search
- **Context:** `VectorStoreAdapter.search()` already implements Qdrant `query_points` with COSINE distance, metadata filtering, and `RetrievalResult` mapping.
- **Decision:** `DenseSearchService` delegates the actual Qdrant query to `VectorStoreAdapter.search()`, passing the query vector, top_k, collection name, and optional filter criteria.
- **Rationale:** Avoids duplicating Qdrant client logic already tested in Phase 4.1, preserving single-responsibility and keeping the service thin and focused on orchestration.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Dedicated Service Layer** | Adds a thin layer over `VectorStoreAdapter.search()`. | Keeps retrieval pipeline modular for future RRF fusion (5.3) and re-ranking (6.x); each component remains independently testable. |
| **Collection Existence Check** | Adds one extra Qdrant round-trip per query. | Acceptable for correctness and clear error semantics; prevents opaque failures on missing collections. |
| **top_k Clamping** | Clamps non-positive top_k to 1. | Prevents invalid Qdrant limit values; default 50 balances recall vs latency for hybrid fusion. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
DenseSearchService.search(query, top_k=None, collection_name=None, filter_criteria=None)
  -> validate query non-empty (EMPTY_QUERY)
  -> resolve target_top_k = max(1, top_k or self.top_k)
  -> embed_text(query) -> query_vector
  -> validate len(query_vector) == vector_store.vector_dim (QUERY_DIM_MISMATCH)
  -> validate collection_exists(collection_name) (COLLECTION_NOT_FOUND)
  -> vector_store.search(query_vector, top_k, collection_name, filter_criteria)
  -> return list[RetrievalResult] with retrieval_method='dense'
```

### Validation Commands
```bash
# Unit tests (10 dense search tests)
.venv/bin/pytest tests/unit/test_dense_search.py -v

# Related retrieval suite
.venv/bin/pytest tests/unit/test_dense_search.py tests/unit/test_vector_store.py tests/unit/test_indexing_orchestrator.py tests/unit/test_bm25_index.py

# Typecheck
mypy src/retrieval/dense_search.py src/retrieval/__init__.py
```

---

## 📌 Session Checklist & Deliverables
1. [x] **Dense search service** (`src/retrieval/dense_search.py`) — `DenseSearchService` + `DENSE_TOP_K_DEFAULT = 50`.
2. [x] **Package exports** (`src/retrieval/__init__.py`) — `DenseSearchService`, `DENSE_TOP_K_DEFAULT`.
3. [x] **Unit tests** (`tests/unit/test_dense_search.py`) — 10 tests covering default top-50, top_k clamping, dense hit retrieval, empty query errors, missing collection errors, dimension mismatch, embedding failure wrapping, filter criteria, and custom collection support.
4. [x] **Test runner registration** — auto-registered via `tests/runner.py` (pytest on `tests/`).
5. [x] **Verification** — 10/10 dense search tests pass; 41/41 related retrieval tests pass; mypy strict passes.