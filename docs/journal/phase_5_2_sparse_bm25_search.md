# Architectural Journal — Phase 5.2: Sparse BM25 Search Implementation

> **Phase:** 5.2 | **Date:** 2026-08-12 | **Status:** Completed

---

## 🎯 Objective
Implement the sparse BM25 search stage of the hybrid retrieval engine (Phase 5). The feature runs a lexical BM25 query over the in-memory tokenized corpus and retrieves the top 50 ranked hits, producing `RetrievalResult` candidates for downstream Reciprocal Rank Fusion (RRF, task 5.3).

---

## 💡 Architectural Choices

### 1. Dedicated Query-Time Service Layer (`SparseSearchService`)
- **Context:** Phase 4 delivered `BM25IndexManager` for low-level sparse index lifecycle (build, search, save, load, clear). Feature 5.2 requires a query-time orchestration that sequences validation + top-k resolution + delegation.
- **Decision:** Implemented `SparseSearchService` that composes `BM25IndexManager` via dependency injection. It owns the query-time flow: validate query → resolve top_k → check index built → delegate to `bm25_index.search()`.
- **Rationale:** Mirrors the `DenseSearchService` pattern from feature 5.1, providing a symmetric interface for the upcoming RRF fusion service (5.3). Keeps `BM25IndexManager` focused on index lifecycle and scoring while centralizing query validation, top_k clamping, and logging in the service layer.

### 2. Default Top-50 Candidate Pool (`SPARSE_TOP_K_DEFAULT = 50`)
- **Context:** The roadmap specifies top 50 for sparse retrieval to provide sufficient recall before RRF fusion merges dense and sparse results.
- **Decision:** Introduced a module-level constant `SPARSE_TOP_K_DEFAULT = 50` used as the service default, while allowing per-call override via the `top_k` parameter.
- **Rationale:** Aligns with `DENSE_TOP_K_DEFAULT = 50` from feature 5.1. Equal candidate counts from both branches ensure balanced Reciprocal Rank Fusion (RRF) in phase 5.3, preventing one branch from dominating the fused ranking.

### 3. Fail-Fast Validation Guards
- **Context:** Query-time retrieval can fail for several reasons: empty queries or unbuilt indexes.
- **Decision:** The service validates the query is non-empty (`EMPTY_QUERY`) and checks the BM25 index is built (`BM25_EMPTY_INDEX`) before delegating to `BM25IndexManager.search()`.
- **Rationale:** Fail-fast guards produce clear `RetrievalError` codes instead of opaque failures, improving debuggability. The service-level `EMPTY_QUERY` guard complements the index-level `BM25_EMPTY_INDEX` guard, keeping single-responsibility separation.

### 4. Reuse of Existing BM25 Index Search
- **Context:** `BM25IndexManager.search()` already implements BM25Okapi scoring, ranking, zero-score filtering, and `RetrievalResult` mapping.
- **Decision:** `SparseSearchService` delegates the actual scoring to `BM25IndexManager.search()`, passing the query and resolved top_k.
- **Rationale:** Avoids duplicating BM25 scoring logic already tested in Phase 4.3, preserving single-responsibility and keeping the service thin and focused on orchestration.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Dedicated Service Layer** | Adds a thin layer over `BM25IndexManager.search()`. | Keeps retrieval pipeline modular for future RRF fusion (5.3) and re-ranking (6.x); each component remains independently testable. |
| **top_k Clamping** | Clamps non-positive top_k to 1 silently. | Consistent with `DenseSearchService`; `BM25IndexManager` still raises on `top_k <= 0` as a defensive lower-layer guard. |
| **In-Memory Sparse Index** | Sparse search remains in-memory (rank-bm25), so large corpora consume RAM. | Acceptable for current scope; JSON persistence available for reload without re-ingesting source documents. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
SparseSearchService.search(query, top_k=None)
  -> validate query non-empty (EMPTY_QUERY)
  -> resolve target_top_k = max(1, top_k or self.top_k)
  -> check bm25_index.is_built (BM25_EMPTY_INDEX)
  -> bm25_index.search(query, top_k=target_top_k)
  -> return list[RetrievalResult] with retrieval_method='sparse'
```

### Validation Commands
```bash
# Unit tests (8 sparse search tests)
.venv/bin/pytest tests/unit/test_sparse_search.py -v

# Related retrieval suite
.venv/bin/pytest tests/unit/test_sparse_search.py tests/unit/test_bm25_index.py tests/unit/test_dense_search.py

# Typecheck
mypy src/retrieval/sparse_search.py src/retrieval/__init__.py
```

---

## 📌 Session Checklist & Deliverables
1. [x] **Sparse search service** (`src/retrieval/sparse_search.py`) — `SparseSearchService` + `SPARSE_TOP_K_DEFAULT = 50`.
2. [x] **Package exports** (`src/retrieval/__init__.py`) — `SparseSearchService`, `SPARSE_TOP_K_DEFAULT`.
3. [x] **Unit tests** (`tests/unit/test_sparse_search.py`) — 8 tests covering default top-50, top_k clamping, sparse hit retrieval, 50-cap, empty query errors, unbuilt index errors, per-call override, and custom top-k.
4. [x] **Test runner registration** (`tests/unit/test_runner.py`) — `test_run_project_tests_sparse_search_suite`.
5. [x] **Verification** — 8/8 sparse search tests pass; 173/173 unit tests pass; mypy strict passes.