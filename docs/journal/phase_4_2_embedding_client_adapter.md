# Architectural Journal — Phase 4.2: Embedding Client Adapter Implementation

> **Phase:** 4.2 | **Date:** 2026-08-11 | **Status:** Completed

---

## 🎯 Objective
Implement a production-ready, modular embedding client adapter supporting OpenAI (`text-embedding-3-small` default with 1536-dimensional output vectors), Google Gemini (`text-embedding-004`), and a deterministic offline `MockEmbeddingAdapter`. Unify provider instantiation through `EmbeddingClientAdapter` with strategy pattern dispatcher and automatic sub-batching, payload order preservation, and domain exception shielding.

---

## 💡 Architectural Choices

### 1. Strategy Pattern & Facade Architecture (`BaseEmbeddingAdapter` & `EmbeddingClientAdapter`)
- **Context:** The application requires vector embedding generation across multiple provider endpoints (OpenAI `text-embedding-3-small`, Google Gemini `text-embedding-004`, and deterministic offline mock vectors) with uniform API contracts.
- **Decision:** Implemented `BaseEmbeddingAdapter` interface with concrete implementations (`OpenAIEmbeddingAdapter`, `GeminiEmbeddingAdapter`, `MockEmbeddingAdapter`) unified through `EmbeddingClientAdapter` facade.
- **Rationale:** Enforces strict layer isolation, decoupling document ingestion pipelines and vector storage indexing from specific third-party provider SDK details.

### 2. Standardized 1536-Dimensional Vector Target & Model Mapping
- **Context:** Qdrant vector collection default configuration expects 1536-dimensional dense vectors for semantic similarity index alignment.
- **Decision:** Configured OpenAI `text-embedding-3-small` as the default primary provider with default 1536 output dimensions, while supporting explicit dimension overrides.
- **Rationale:** Matches production requirements for high-accuracy text representation and aligns perfectly with Qdrant collection geometry.

### 3. Sub-Batching & Fail-Safe Response Order Preserving
- **Context:** Provider embedding endpoints impose maximum item count limits per request payload (e.g. 100 items per batch).
- **Decision:** Implemented automatic chunking in `BaseEmbeddingAdapter._chunk_batch` and sorted OpenAI response arrays by `index` field.
- **Rationale:** Prevents HTTP 400 payload errors on large document ingestion tasks and guarantees 1-to-1 ordering alignment between chunk sequences and generated embedding vectors.

### 4. Domain Exception Shielding & Auto Fallback
- **Context:** Raw third-party SDK errors (e.g., `openai.OpenAIError` or network failures) must not leak unshielded into application API routes.
- **Decision:** Wrapped all SDK calls inside try/except blocks raising `RetrievalError` with detailed structured metadata. Added auto fallback mode to `MockEmbeddingAdapter` when API keys are omitted.
- **Rationale:** Maintains system reliability, simplifies error diagnosis in structured logs, and allows unit testing without external API key dependencies.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Injected Client Dependency Pattern** | Requires dependency injection parameters in adapter constructors. | Defaults to automatic environment loading via `get_settings()` while permitting explicit client injection in pytest suites. |
| **Batch Payload Chunking** | Multiple sequential API calls for very large document batches. | Minimizes request failure risk while logging `structlog` telemetry per sub-batch. |
