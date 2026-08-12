# Architectural Journal — Phase 5.4: Retrieval Debug Data Structure Implementation

> **Phase:** 5.4 | **Date:** 2026-08-12 | **Status:** Completed

---

## 🎯 Objective
Expose a retrieval debug data structure capturing dense scores, sparse scores, and fused RRF ranks (roadmap task 5.4, specification FR-09). The feature delivers a `DebugRetrievalBuilder` service that orchestrates the existing dense search, sparse search, and RRF fusion stages into a `DebugRetrievalResponse` payload for the `/api/v1/debug/retrieval` endpoint.

---

## 💡 Architectural Choices

### 1. Compact `DebugRetrievalHit` Model for Debug Stages
- **Context:** Specification FR-09 requires exposing raw dense scores, BM25 scores, and fused RRF ranks. The existing `RetrievalResult` schema carries heavy display fields (`text`, `file_name`, `page_number`) irrelevant to debug observability.
- **Decision:** Introduced `DebugRetrievalHit` (chunk_id, score, rank ge=1, method) and updated `DebugRetrievalResponse.dense_hits`, `sparse_hits`, and `rrf_fused` to use it. `final_reranked` retains `RetrievalResult` for the future cross-encoder stage.
- **Rationale:** A dedicated compact DTO avoids leaking full `RetrievalResult` payloads into the debug endpoint, reducing payload size and keeping debug output focused on observability. The schema matches the spec's JSON contract exactly (`chunk_id`, `score`, `rank`).

### 2. Dedicated `DebugRetrievalBuilder` Orchestration Service
- **Context:** The debug payload requires composing the dense, sparse, and RRF stages into a single response.
- **Decision:** Implemented `DebugRetrievalBuilder` in `src/retrieval/debug_retrieval.py`. It composes existing `DenseSearchService`, `SparseSearchService`, and `RRFusionService` and assembles the `DebugRetrievalResponse`.
- **Rationale:** Encapsulates the hybrid pipeline composition in a single pure-logic service, consistent with the layered architecture (Core Domain Layer). It reuses existing retrieval services rather than duplicating retrieval logic, keeping the builder thin and testable via mocks.

### 3. Per-Stage `top_k` Overrides on `build()`
- **Context:** The debug endpoint may need different candidate counts per stage for granular inspection (e.g., top 10 dense, top 20 sparse, top 5 fused).
- **Decision:** `build()` accepts optional `dense_top_k`, `sparse_top_k`, and `rrf_top_k` parameters, forwarded to the underlying services.
- **Rationale:** Matches the `GET /api/v1/debug/retrieval?limit=10` contract and allows flexible inspection. Defaults fall back to each service's configured `top_k`, preserving backward compatibility.

### 4. Pure `_to_debug_hits` Conversion Helper
- **Context:** Each stage returns `RetrievalResult` lists; the debug payload needs compact `DebugRetrievalHit` lists with 1-indexed ranks.
- **Decision:** Implemented a pure module-level helper `_to_debug_hits(hits, method)` that converts `RetrievalResult` lists into `DebugRetrievalHit` lists with `rank = enumerate(..., start=1)`.
- **Rationale:** Keeps the conversion logic isolated, testable, and reusable. The 1-indexed rank mirrors the RRF formula `1/(k+rank)` and the spec's rank semantics.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Compact DebugRetrievalHit vs Reusing RetrievalResult** | `DebugRetrievalResponse.dense_hits`/`sparse_hits`/`rrf_fused` now use `DebugRetrievalHit` instead of `RetrievalResult`, breaking the previous schema contract. | Aligns with the spec's debug payload shape (FR-09). `final_reranked` retains `RetrievalResult` for the future cross-encoder stage, preserving forward compatibility. |
| **Builder Orchestration vs Direct Service Calls** | The builder adds an abstraction layer over the three retrieval services. | Keeps the builder pure and thin; it performs no I/O itself, delegating to services and only transforming outputs. Testable with mocks. |
| **Synchronous Builder** | The builder is synchronous and assumes services are already configured. | Consistent with the existing synchronous retrieval services (dense, sparse, RRF). Async adaptation can be layered later if needed. |
| **Empty final_reranked Before Phase 6** | `final_reranked` remains empty until the cross-encoder re-ranking stage (Phase 6) is implemented. | The field is already part of the schema to maintain forward compatibility with the spec's debug payload, which includes `final_reranked` with `cross_encoder_score` and `selected` flags. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
DebugRetrievalBuilder.build(query, dense_top_k=None, sparse_top_k=None, rrf_top_k=None)
  -> dense_hits = dense_search.search(query, top_k=dense_top_k)
  -> sparse_hits = sparse_search.search(query, top_k=sparse_top_k)
  -> fused_hits = rrf_fusion.fuse(dense_hits, sparse_hits, top_k=rrf_top_k)
  -> response = DebugRetrievalResponse(
       query=query,
       dense_hits=_to_debug_hits(dense_hits, "dense"),
       sparse_hits=_to_debug_hits(sparse_hits, "sparse"),
       rrf_fused=_to_debug_hits(fused_hits, "rrf"),
     )
  -> log debug_retrieval_built; return response
```

### Validation Commands
```bash
# Unit tests (debug retrieval + builder + runner)
.venv/bin/pytest tests/unit/test_debug_retrieval_and_finops.py tests/unit/test_debug_retrieval_builder.py tests/unit/test_runner.py -v

# Full suite
.venv/bin/pytest -q

# Typecheck
mypy src/models/retrieval.py src/models/__init__.py src/retrieval/debug_retrieval.py src/retrieval/__init__.py
```

---

## 📌 Session Checklist & Deliverables
1. [x] **DebugRetrievalHit model** (`src/models/retrieval.py`) — compact per-stage hit with `chunk_id`, `score`, `rank` (ge=1), `method`.
2. [x] **DebugRetrievalResponse update** (`src/models/retrieval.py`) — `dense_hits`/`sparse_hits`/`rrf_fused` now use `DebugRetrievalHit`; `final_reranked` retains `RetrievalResult`.
3. [x] **DebugRetrievalBuilder service** (`src/retrieval/debug_retrieval.py`) — orchestrates dense + sparse + RRF and assembles the debug payload.
4. [x] **Package exports** (`src/models/__init__.py`, `src/retrieval/__init__.py`) — `DebugRetrievalHit`, `DebugRetrievalBuilder`.
5. [x] **Unit tests** (`tests/unit/test_debug_retrieval_and_finops.py`, `tests/unit/test_debug_retrieval_builder.py`) — hit validation, response serialization, builder stage population, top_k forwarding, empty pipeline.
6. [x] **Test runner registration** (`tests/unit/test_runner.py`) — `test_run_project_tests_debug_retrieval_builder_suite`.
7. [x] **Verification** — 192/192 tests pass; ruff check + format pass on modified files; mypy strict passes.