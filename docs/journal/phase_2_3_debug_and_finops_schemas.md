# Architectural Journal — Phase 2.3: DebugRetrievalResponse & FinOpsMetadata Schemas

> **Phase:** 2.3 | **Date:** 2026-08-10 | **Status:** Completed

---

## 🎯 Objective
Implement standardized domain schemas for retrieval stage debugging (`DebugRetrievalResponse`) and FinOps operational cost/token telemetry (`FinOpsMetadata`).

---

## 💡 Architectural Choices

### 1. Multi-Stage Retrieval Debugging Payload (`DebugRetrievalResponse`)
- **Context:** Inspecting search performance across dense vector, sparse BM25, RRF fusion, and cross-encoder re-ranking stages is required during hybrid search evaluation.
- **Decision:** Encapsulate pipeline stage candidate lists inside an immutable `DebugRetrievalResponse` model extending `BaseDomainModel`.
- **Rationale:** Exposes candidate hits (`dense_hits`, `sparse_hits`, `rrf_fused`, `final_reranked`) cleanly, allowing developers and evaluators to diagnose drop-offs and tune fusion weights.

### 2. Operational Cost & Token Telemetry (`FinOpsMetadata`)
- **Context:** Production RAG applications require granular tracking of prompt/completion tokens, USD costs, execution latency, and semantic cache performance.
- **Decision:** Implement `FinOpsMetadata` schema with non-negative field bounds (`ge=0`, `ge=0.0`) and default caching flags (`is_cached=False`).
- **Rationale:** Standardizes cost accounting and latency telemetry across model providers, enabling budget enforcement and cache hit analysis.

### 3. Subclassing BaseDomainModel with Immutability & Boundary Constraints
- **Context:** Telemetry payloads and debug structures pass through API response handlers and loggers across thread boundaries.
- **Decision:** Subclass `BaseDomainModel` (`frozen=True`, `extra="forbid"`) across both schemas.
- **Rationale:** Guarantees payload immutability, thread safety, and strict validation against corrupted provider data or negative metrics.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Multi-Stage Hit Serialization** | Increased JSON response payload size when debug mode is enabled. | Debug payloads are conditionally included only on explicit request flags or dev environments. |
| **Encapsulated FinOps Metrics** | Requires provider wrappers to calculate USD costs per completion request. | Provider adapters map raw usage tokens and cost tables into `FinOpsMetadata` before returning. |
| **Strict Non-Negative Bounds** | Throws `ValidationError` if upstream providers supply negative or corrupted values. | Provider clients validate and clamp raw API metrics prior to schema instantiation. |
