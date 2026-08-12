# Architectural Journal — Phase 5.3: Reciprocal Rank Fusion (RRF) Implementation

> **Phase:** 5.3 | **Date:** 2026-08-12 | **Status:** Completed

---

## 🎯 Objective
Implement the Reciprocal Rank Fusion (RRF) stage of the hybrid retrieval engine (Phase 5). The feature merges the top-50 dense vector hits and top-50 sparse BM25 hits into a single fused ranking using the RRF formula `score = Σ 1/(k + rank)` with `k=60`, producing `RetrievalResult` candidates for downstream re-ranking (Phase 6) and debug payloads (Phase 5.4).

---

## 💡 Architectural Choices

### 1. Dedicated Fusion Service Layer (`RRFusionService`)
- **Context:** Phase 5.1 and 5.2 delivered symmetric `DenseSearchService` and `SparseSearchService` query-time services each producing `RetrievalResult` lists of up to 50 hits. Feature 5.3 requires a fusion stage that combines these heterogeneous ranked lists.
- **Decision:** Implemented `RRFusionService` as a standalone, dependency-free module. `fuse(dense_hits, sparse_hits, top_k=None)` accepts the two ranked lists directly and returns a fused `RetrievalResult` list.
- **Rationale:** Decoupling fusion from the individual search services keeps each component single-responsibility and independently testable. The pure function-style interface can be composed by either the future phase 5.4 debug service or the phase 6 re-ranker without circular dependencies. Inputs are already uniform `RetrievalResult` models, so no new adapter types are required.

### 2. Rank-Based Scoring with k=60 (`RRF_K_DEFAULT = 60`)
- **Context:** Dense cosine scores and BM25 lexical scores live on different scales and distributions, making direct score averaging or weighting unreliable across query drift and index changes.
- **Decision:** Applied the canonical RRF formula: for each hit at 1-based rank `r` in a list, accumulate `1 / (k + r)`. The default rank constant is `k = 60`, the standard value from the original RRF paper (Cormack et al.).
- **Rationale:** RRF is score-calibration-agnostic: it converts absolute scores into rank contributions, so a well-calibrated dense score cannot dominate an uncalibrated BM25 score. Hits present in both lists receive summed contributions and are naturally ranked above hits present in only one list, rewarding cross-retriever agreement.

### 3. Deterministic Tie-Breaking by `chunk_id`
- **Context:** Without a stable tie-breaker, items with equal fused scores would be ordered by Python dict insertion order, which depends on input list ordering (dense processed first) and is not reproducible across calls.
- **Decision:** Sorted fused chunk IDs by `(-score, chunk_id)` before slicing to `target_top_k`.
- **Rationale:** Deterministic output ordering is critical for caching, evaluation benchmarks (Phase 10), and debugging reproducibility. Sorting by `chunk_id` as the secondary key is simple, hashable, and stable across runs and environments.

### 4. Dense Payload Preference on Duplicate `chunk_id`
- **Context:** A chunk may appear in both dense and sparse lists. RRF must output a single `RetrievalResult` per chunk.
- **Decision:** The first-seen payload is stored per `chunk_id`; when a duplicate is encountered, the dense-list payload overwrites the sparse one (`method == "dense"` branch).
- **Rationale:** Dense hits carry the canonical display payload for the hybrid pipeline; sparse hits are primarily rank contributors. This preserves text, file name, and page metadata from the dense branch while still accumulating both rank contributions into the fused score.

### 5. Empty-Input Fast Path & Parameter Clamping
- **Context:** Fusion can be invoked with zero hits from either or both branches (e.g. empty corpus or empty query result).
- **Decision:** If both input lists are empty, `fuse` logs `rrf_no_hits` and returns `[]` immediately. Both `k` and `top_k` are clamped to a minimum of 1 in the constructor.
- **Rationale:** The empty fast path avoids unnecessary dictionary allocations and keeps no-hit behavior silent and cheap. Clamping prevents division-by-zero (`k=0`) and invalid output limits while preserving the configured defaults (`k=60`, `top_k=50`).

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Rank-Based RRF vs Weighted Score Fusion** | RRF ignores relevance score magnitudes entirely; a hit ranked #1 in one list cannot dominate a hit ranked #2 in both lists. | Rank-based fusion is robust to score calibration drift across dense and sparse branches; weighted convex-combination fusion is more precise but requires brittle score normalization. RRF is the standard, well-tested choice for hybrid retrieval. |
| **In-Memory Score Aggregation** | `fuse` builds `O(n)` dictionaries for scores and payloads where `n = dense_hits + sparse_hits` (up to 100). Sorting is `O(n log n)`. | Cost is bounded and acceptable for top-50 + top-50 fusion; a heap-based partial sort could be introduced if candidate lists scale beyond ~1k. |
| **Dense Payload Heuristic** | Preferring the dense payload assumes dense result text is canonical; sparse-only chunks fall back to sparse payload. | Consistent with the hybrid design where dense semantic retrieval is the primary branch; sparse supplements recall. |
| **Per-Instance `k`/`top_k` State** | Service instances store fusion parameters, but callers can still override `top_k` per call. | Mirrors `DenseSearchService`/`SparseSearchService` conventions and keeps the interface symmetric across the retrieval pipeline. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
RRFusionService.fuse(dense_hits, sparse_hits, top_k=None)
  -> resolve target_top_k = max(1, top_k or self.top_k)
  -> fast-path: if both lists empty, log rrf_no_hits, return []
  -> for each (list, method) in [(dense, "dense"), (sparse, "sparse")]:
       for each hit at rank r (1-based):
         score[chunk_id] += 1 / (k + r)
         payloads[chunk_id] = hit (dense payload overwrites sparse on duplicate)
  -> ranked_ids = sorted(score keys by (-score, chunk_id))[:target_top_k]
  -> build fused RetrievalResult list with relevance_score = score, retrieval_method = 'rrf'
  -> log rrf_fusion_completed; return fused list
```

### Validation Commands
```bash
# Unit tests (9 RRF fusion tests)
.venv/bin/pytest tests/unit/test_rrf_fusion.py -v

# Related retrieval suite
.venv/bin/pytest tests/unit/test_rrf_fusion.py tests/unit/test_sparse_search.py tests/unit/test_dense_search.py

# Typecheck
mypy src/retrieval/rrf_fusion.py src/retrieval/__init__.py
```

---

## 📌 Session Checklist & Deliverables
1. [x] **RRF fusion service** (`src/retrieval/rrf_fusion.py`) — `RRFusionService` + `RRF_K_DEFAULT = 60`, `RRF_TOP_K_DEFAULT = 50`, `RRF_METHOD = "rrf"`.
2. [x] **Package exports** (`src/retrieval/__init__.py`) — `RRFusionService`, `RRF_K_DEFAULT`, `RRF_TOP_K_DEFAULT`, `RRF_METHOD`.
3. [x] **Unit tests** (`tests/unit/test_rrf_fusion.py`) — 9 tests covering constants, clamping, merge ranking, RRF formula precision, top_k limit/custom override, empty lists, single-list-only, and dense payload preference.
4. [x] **Test runner registration** (`tests/unit/test_runner.py`) — `test_run_project_tests_rrf_fusion_suite`.
5. [x] **Verification** — 9/9 RRF fusion tests pass; 19/19 runner tests pass; ruff check + format pass; mypy strict passes.