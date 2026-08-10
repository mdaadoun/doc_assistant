# Architectural Journal — Phase 2.1: Base Domain Model Setup

> **Phase:** 2.1 | **Date:** 2026-08-10 | **Status:** Completed

---

## 🎯 Objective
Define the foundational base domain model (`BaseDomainModel`) using Pydantic V2 immutable configuration (`frozen=True`) to enforce immutability, thread-safety, strict boundary validation (`extra="forbid"`), and standardized DTO serialization across all domain schemas.

---

## 💡 Architectural Choices

### 1. Enforce Pydantic V2 `frozen=True` on `BaseDomainModel`
- **Context:** Complex RAG pipelines process data across multiple stages (ingestion, hybrid retrieval, RRF fusion, cross-encoder re-ranking, confidence guarding, grounded generation).
- **Decision:** Configure `model_config = ConfigDict(frozen=True)` across all domain models inheriting from `BaseDomainModel`.
- **Rationale:** Guarantees thread-safety, predictability, and prevents accidental in-memory mutation across architectural layers (Core, Infrastructure, Presentation).

### 2. Set `extra="forbid"` in `ConfigDict`
- **Context:** Inputs originating from external API requests or document parsers may contain unexpected or malicious fields.
- **Decision:** Mandate `extra="forbid"` on `BaseDomainModel`.
- **Rationale:** Prevents silent data leakage and unexpected input fields from corrupting domain entities or bypassing validation rules.

### 3. Standardized Serialization Helper Methods (`to_dict`, `to_json`, `from_dict`)
- **Context:** Domain schemas must interface cleanly with FastAPI endpoints, logging utilities, and vector store adapters.
- **Decision:** Implement `to_dict()`, `to_json()`, and `from_dict()` helper methods wrapping Pydantic V2 native `model_dump()`, `model_dump_json()`, and `model_validate()`.
- **Rationale:** Provides a clean, uniform, and type-safe interface for domain layer DTO serialization and deserialization across the codebase.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Immutable Models (`frozen=True`)** | Requires creating new instances (e.g., via `model_copy(update={...})`) when updating attributes instead of in-place mutation. | Immutability overhead is negligible in Pydantic V2 (Rust core) and guarantees thread-safe, side-effect-free execution. |
| **Strict Boundary Validation (`extra="forbid"`)** | Requires explicit model updates whenever downstream external APIs add fields that domain schemas care about. | Schema modifications are version-controlled, explicit, and audited via typecheck and unit tests. |
| **Serialization Helper Methods** | Adds lightweight wrapper methods over native Pydantic V2 functions. | Methods ensure consistent interface signatures and simplified call sites across service boundaries. |
