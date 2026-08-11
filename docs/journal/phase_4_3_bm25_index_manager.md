# Architectural Journal — Phase 4.3: BM25 Index Manager Implementation

> **Phase:** 4.3 | **Date:** 2026-08-11 | **Status:** Completed

---

## 🎯 Objective
Implement a production-ready BM25 sparse index manager using `rank-bm25` (`BM25Okapi`), a tokenized corpus pipeline, and versioned JSON persistence. The manager provides a full lifecycle (`build`, `search`, `save`, `load`, `clear`) and returns standardized `RetrievalResult` domain schemas with `retrieval_method="sparse"` for downstream RRF fusion.

---

## 💡 Architectural Choices

### 1. Separate Tokenizer Module (`bm25_tokenizer.py`) from Index Manager (`bm25_index.py`)
- **Context:** BM25 requires a tokenized corpus and tokenized queries; tokenization is a pure, reusable transformation.
- **Decision:** Implemented `tokenize()` and `tokenize_corpus()` as standalone pure functions in `bm25_tokenizer.py`, while `BM25IndexManager` owns the index lifecycle (build/search/save/load/clear).
- **Rationale:** Enforces single-responsibility, keeps files under 250 LOC, enables independent unit testing, and allows future tokenizer swaps (e.g. stemmer, stopword filter) without touching index logic.

### 2. Versioned JSON Persistence of Tokenized Corpus + Chunk Metadata
- **Context:** The BM25 index must survive process restarts without re-ingesting source documents.
- **Decision:** `save()` serializes `{version, k1, b, epsilon, chunks: [{chunk: model_dump, tokens}]}` to JSON; `load()` validates the version field (`_INDEX_VERSION = 1`), restores hyperparameters, Pydantic-validates chunks via `ChunkDocument.model_validate()`, and rebuilds `BM25Okapi`.
- **Rationale:** JSON is human-readable, diffable, and version-controllable. Pickle is opaque, Python-version-sensitive, and a security risk (arbitrary code execution on load). The version field guards against breaking schema drift.

### 3. Configurable BM25Okapi Hyperparameters (`k1`, `b`, `epsilon`)
- **Context:** BM25 scoring behavior depends on term frequency saturation, document length normalization, and IDF epsilon handling.
- **Decision:** Exposed `k1=1.5`, `b=0.75`, `epsilon=0.25` as constructor parameters matching `rank-bm25` library defaults.
- **Rationale:** Allows per-corpus tuning without code changes. Defaults are the standard Okapi BM25 baseline.

### 4. Search Returns `RetrievalResult` with `retrieval_method="sparse"`
- **Context:** Phase 5 requires Reciprocal Rank Fusion (RRF) to merge dense and sparse hits uniformly.
- **Decision:** `search()` maps BM25 hits to the existing `RetrievalResult` domain schema with `retrieval_method="sparse"`.
- **Rationale:** Reuses the Phase 2 domain contract, enabling RRF to operate on a uniform list regardless of retrieval method, avoiding duplicate model types and preserving provenance for debug payloads.

### 5. Domain Exception Shielding & Fail-Fast State Guards
- **Context:** Raw `OSError`, `JSONDecodeError`, or unbuilt-index states must not leak into service layers.
- **Decision:** All I/O and state errors are wrapped in `RetrievalError` with structured details. Searching an unbuilt index raises `BM25_EMPTY_INDEX`; invalid `top_k` raises `INVALID_TOP_K`; unsupported persistence versions raise `BM25_INVALID_VERSION`.
- **Rationale:** Consistent with the existing exception hierarchy (`core/exceptions.py`) and structured logging via `structlog` on build/save/load/search events.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **JSON Persistence** | Larger file size and slower serialization than binary formats (pickle/npz). | Acceptable for corporate doc scale; human-readable and diffable; aligns with zero-dynamic-typing guardrails. |
| **In-Memory BM25Okapi** | No incremental updates — full rebuild required on corpus change. | Phase 4.4 indexing orchestrator rebuilds after ingestion; acceptable for dual-indexing workflow. |
| **RetrievalResult Text Duplication** | Search results carry full chunk text, duplicating memory. | Only top-k results are materialized; acceptable for retrieval pipeline scale. |
| **Exception Wrapping Boilerplate** | Additional try/except blocks per I/O method. | Ensures callers never see raw `OSError`/`JSONDecodeError`; structured diagnostics in logs. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
build(chunks) -> tokenize_corpus -> BM25Okapi(corpus, k1, b, epsilon)
search(query, top_k) -> tokenize(query) -> get_scores -> rank desc -> filter score>0 -> top_k RetrievalResult
save(path) -> JSON {version, k1, b, epsilon, chunks:[{chunk, tokens}]}
load(path) -> validate version -> Pydantic model_validate -> rebuild BM25Okapi
```

### Validation Commands
```bash
# Unit tests (14 BM25 tests)
.venv/bin/pytest tests/unit/test_bm25_index.py -v

# Full suite
.venv/bin/pytest

# Lint & typecheck
ruff check src/retrieval/ tests/unit/test_bm25_index.py tests/unit/test_runner.py
mypy src/retrieval/
```

---

## 📌 Session Checklist & Deliverables
1. [x] **BM25 tokenizer module** (`src/retrieval/bm25_tokenizer.py`) — pure lowercase alphanumeric tokenization.
2. [x] **BM25 index manager** (`src/retrieval/bm25_index.py`) — build/search/save/load/clear lifecycle with `RetrievalError` shielding.
3. [x] **Package exports** (`src/retrieval/__init__.py`) — `BM25IndexManager`, `tokenize`, `tokenize_corpus`.
4. [x] **Unit tests** (`tests/unit/test_bm25_index.py`) — 14 tests covering tokenizer, build, search, persistence, error handling.
5. [x] **Test runner registration** (`tests/unit/test_runner.py`) — `test_run_project_tests_bm25_index_suite`.
6. [x] **Verification** — 146 tests pass, Ruff clean, Mypy strict clean.