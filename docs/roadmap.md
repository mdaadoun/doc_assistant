# Step-by-Step Implementation Roadmap: Corporate Document Assistant

> **Goal:** Incremental delivery from baseline setup to production-grade RAG platform.
> **Status:** Draft | **Version:** 0.1.0

## Phase Overview

```text
[Phase 1] Base & Infra -> [Phase 2] Domain Schemas -> [Phase 3] Ingestion Pipeline
                                                             |
[Phase 6] Cross-Encoder Re-rank <- [Phase 5] Hybrid RRF <- [Phase 4] Dual Indexing
       |
       v
[Phase 7] Grounded Gen & Citations -> [Phase 8] API Layer -> [Phase 9] React UI
                                                                     |
[Phase 11] Prod Hardening & Docker <- [Phase 10] Eval & QA <----------
```

## Phase 1: Technical Baseline & Infrastructure
**Entry Criteria:** Empty repository.
**Dependencies:** None.
**Tasks:**
- [x] 1.1: Initialize Poetry project with Python 3.11+ constraints
- [x] 1.2: Configure Ruff linter + Mypy strict + pre-commit hooks (detect-secrets)
- [x] 1.3: Set up pydantic-settings config loading (.env, API keys via BaseSettings)
- [x] 1.4: Create modular package layout (src/api, src/retrieval, src/generation, src/ingestion, src/clients, src/models, src/core, src/cache, frontend/)
- [x] 1.5: Create Makefile with dev shortcuts (lint, typecheck, test, format)
- [x] 1.6: Initialize docker-compose.yml skeleton (FastAPI, Qdrant, React)
**Deliverables:** Clean project skeleton, passing linter + typecheck, running docker skeleton.
**Verification:** `make lint && make typecheck` passes with 0 errors.

## Phase 2: Domain Schemas, Contracts & Exception Hierarchy
**Entry Criteria:** Project skeleton and core dependencies installed.
**Dependencies:** Phase 1.
**Tasks:**
- [x] 2.1: Define base domain model (BaseDomainModel with frozen=True)
- [x] 2.2: Create ChunkDocument, RetrievalResult, ChatRequest, ChatResponse, Citation schemas
- [x] 2.3: Create DebugRetrievalResponse and FinOpsMetadata schemas
- [x] 2.4: Define AppBaseError and domain exception hierarchy (IngestionError, RetrievalError, GenerationError, ConfigurationError)
**Deliverables:** Complete Pydantic V2 schema set, exception hierarchy.
**Verification:** All models pass Mypy strict, instantiation tests pass.

## Phase 3: Document Ingestion & Chunking Pipeline
**Entry Criteria:** Schemas and models are defined.
**Dependencies:** Phase 2.
**Tasks:**
- [x] 3.1: Implement PDF parser (PyMuPDF/pdfplumber) with page-level metadata extraction
- [x] 3.2: Implement DOCX parser (python-docx) with structural metadata
- [x] 3.3: Implement Markdown parser with frontmatter extraction
- [x] 3.4: Build recursive structural chunker (512 tokens max, 10% overlap, preserving page boundaries)
- [x] 3.5: Create ingestion facade with format dispatcher and fail-fast validation
- [x] 3.6: Add differential update handling (detect changed/new/deleted files)
**Deliverables:** Working ingestion pipeline consuming PDF/DOCX/MD → ChunkDocument list.
**Verification:** Unit tests on sample documents, chunk size assertions ≤ 512 tokens.

## Phase 4: Dual Indexing (Dense Vectors + Sparse BM25)
**Entry Criteria:** Ingestion pipeline produces valid chunks.
**Dependencies:** Phase 3.
**Tasks:**
- [x] 4.1: Implement vector store adapter (Qdrant client, collection creation, COSINE distance, dim=1536)
- [x] 4.2: Implement embedding client adapter (OpenAI text-embedding-3-small or equivalent, gemini/mistral)
- [x] 4.3: Build BM25 index manager (rank-bm25, tokenized corpus, persistence)
- [x] 4.4: Create indexing orchestrator (embed chunks → upsert vectors + build BM25 index)
**Deliverables:** Fully indexed corpus in Qdrant + BM25 in-memory index.
**Verification:** Qdrant collection point count matches chunk count, BM25 returns results for sample queries.

## Phase 5: Hybrid Retrieval Engine & RRF Fusion
**Entry Criteria:** Indexed data exists in Qdrant and BM25.
**Dependencies:** Phase 4.
**Tasks:**
- [x] 5.1: Implement dense vector search (Qdrant, top 50)
- [x] 5.2: Implement sparse BM25 search (top 50)
- [x] 5.3: Build Reciprocal Rank Fusion (RRF, k=60) merging dense + sparse hits
- [x] 5.4: Expose retrieval debug data structure (dense scores, sparse scores, fused ranks)
**Deliverables:** Working hybrid retrieval returning fused ranked candidates.
**Verification:** Unit tests asserting RRF produces correct rankings, debug payload populated.

## Phase 6: Cross-Encoder Re-Ranking & Confidence Guard
**Entry Criteria:** Hybrid retrieval outputs ranked candidates.
**Dependencies:** Phase 5.
**Tasks:**
- [x] 6.1: Implement FlashRank cross-encoder adapter (ms-marco-MiniLM-L-6-v2, top 30 → top 5)
- [x] 6.2: Implement Cohere Rerank API fallback adapter
- [x] 6.3: Build re-ranker service with primary/fallback strategy pattern
- [x] 6.4: Implement confidence guard (S_min ≥ 0.35 threshold, refusal response bypass)
**Deliverables:** Complete retrieval pipeline: Hybrid → RRF → Re-rank → Confidence Filter.
**Verification:** Integration tests with threshold edge cases, refusal on low-confidence queries.

## Phase 7: Grounded Generation & Citation Engine
**Entry Criteria:** High-confidence context available from retrieval pipeline.
**Dependencies:** Phase 6.
**Tasks:**
- [x] 7.1: Implement grounded LLM generation service (temperature=0.0, context-only system prompt)
- [x] 7.2: Build SSE streaming response handler (async generator)
- [x] 7.3: Implement citation extraction and validation logic (inline [Doc: <name> | Page: <num>] format)
- [x] 7.4: Build citation validator (verify cited docs exist in retrieved context)
- [x] 7.5: Integrate FinOps metadata collection (token counts, cost, latency)
**Deliverables:** End-to-end query pipeline with cited, grounded answers.
**Verification:** Citation accuracy = 1.00 on test queries, FinOps metadata populated.

## Phase 8: FastAPI Endpoints & API Layer
**Entry Criteria:** Full generation pipeline is functional.
**Dependencies:** Phase 7.
**Tasks:**
- [x] 8.1: Implement POST /api/v1/chat with SSE streaming
- [x] 8.2: Implement GET /api/v1/debug/retrieval diagnostic endpoint
- [x] 8.3: Set up API key authentication middleware (dependencies.py)
- [x] 8.4: Configure CORS, request validation, error handling middleware
- [x] 8.5: Implement service dependency injection (lifespan context)
**Deliverables:** Fully functional API with streaming chat and debug endpoints.
**Verification:** curl/httpie tests against running API, correct SSE event format.

## Phase 9: React Frontend (Presentation Layer)
**Entry Criteria:** Backend API is accessible and stable.
**Dependencies:** Phase 8.
**Tasks:**
- [x] 9.1: Initialize React 18+ / Vite / TypeScript project
- [x] 9.2: Build query input component with submission handling
- [x] 9.3: Implement SSE streaming answer display with real-time rendering
- [x] 9.4: Build citation drawer component (clickable citations showing source excerpts)
- [x] 9.5: Add loading states, error handling, and confidence indicators
**Deliverables:** Working web UI consuming the chat API with streaming and citations.
**Verification:** Manual E2E test: submit query → see streaming answer → click citation drawer.

## Phase 10: Evaluation, Testing & Quality Assurance
**Entry Criteria:** End-to-end system is functional.
**Dependencies:** Phases 1-9.
**Tasks:**
- [x] 10.1: Create eval_dataset.jsonl (≥50 annotated Q&A pairs, 10 out-of-corpus queries)
- [x] 10.2: Build RetrievalMonitor benchmark runner
- [x] 10.3: Validate retrieval_precision@5 ≥ 0.75
- [x] 10.4: Validate faithfulness_score ≥ 0.85 (RAGAS framework)
- [x] 10.5: Validate honesty_filter_precision ≥ 0.90
- [x] 10.6: Validate p95_latency ≤ 3000ms
- [x] 10.7: Achieve ≥80% test coverage with pytest (unit + integration, mocked I/O)
**Deliverables:** Passing benchmark report (retrieval_report.md), test coverage report.
**Verification:** All metric thresholds met, `make test` passes, coverage ≥ 80%.

## Phase 11: Containerization, Caching & Production Hardening
**Entry Criteria:** Tests passing and QA targets achieved.
**Dependencies:** Phase 10.
**Tasks:**
- [x] 11.1: Build multi-stage non-root Dockerfile (< 250MB, UID 10001)
- [ ] 11.2: Complete docker-compose.yml (FastAPI + Qdrant + React + volumes)
- [ ] 11.3: Implement SHA-256 cache layer (keyed on input + prompt + model)
- [ ] 11.4: Add Tenacity retry policies on all external I/O (LLM, embedding, reranker APIs)
- [ ] 11.5: Final Ruff + Mypy strict pass (0 errors)
- [ ] 11.6: Generate final retrieval_report.md and README.md
**Deliverables:** Production-ready containerized deployment, complete documentation.
**Verification:** `docker-compose up` deploys full stack, all health checks pass.

## Quality Targets Summary

| Metric | Threshold |
| :--- | :--- |
| `retrieval_precision@5` | ≥ 0.75 |
| `citation_accuracy` | = 1.00 |
| `hallucination_rate` | ≤ 0.05 |
| `faithfulness_score` | ≥ 0.85 |
| `honesty_filter_precision` | ≥ 0.90 |
| `p95_latency_ms` | ≤ 3000 |
| `test_coverage` | ≥ 80% |
