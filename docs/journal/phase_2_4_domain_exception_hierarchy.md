# Architectural Journal — Phase 2.4: AppBaseError & Domain Exception Hierarchy

> **Phase:** 2.4 | **Date:** 2026-08-10 | **Status:** Completed

---

## 🎯 Objective
Define `AppBaseError` root exception and domain exception hierarchy (`ConfigurationError`, `IngestionError`, `RetrievalError`, `GenerationError`) for structured error handling, diagnostic context tracking, and exception shielding across layer boundaries.

---

## 💡 Architectural Choices

### 1. Root Application Base Exception (`AppBaseError`)
- **Context:** Applications need a single top-level error class to distinguish internal application errors from Python standard library or third-party exceptions.
- **Decision:** Define `AppBaseError` deriving from `Exception`, containing explicit error code, message, and `details` dictionary metadata, along with `to_dict()` serialization.
- **Rationale:** Enables uniform exception handling across presentation and API layers while embedding structured diagnostic metadata for JSON logging.

### 2. Domain-Specific Subclasses (`IngestionError`, `RetrievalError`, `GenerationError`, `ConfigurationError`)
- **Context:** Different subsystems fail for distinct operational reasons (parsing errors vs search timeouts vs LLM rate limits vs bad configuration).
- **Decision:** Create dedicated sub-exceptions mapped to standard string error codes (`INGESTION_ERROR`, `RETRIEVAL_ERROR`, `GENERATION_ERROR`, `CONFIG_ERROR`).
- **Rationale:** Allows callers to selectively catch specific domain errors or handle all application errors polymorphically via `AppBaseError`.

### 3. Contextual Details Metadata Payload & Serialization
- **Context:** Debugging errors in distributed RAG pipelines requires structured context (e.g., document IDs, Qdrant collection names, model names).
- **Decision:** Attach an optional `details: dict[str, Any] | None` parameter to `AppBaseError` and provide a `to_dict()` method.
- **Rationale:** Facilitates structured JSON logging and direct serialization into API HTTP error responses without leaking internal stack traces.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Custom Exception Hierarchy** | Requires wrapping third-party SDK/I/O exceptions (e.g., Qdrant, OpenAI, PyMuPDF) into domain errors. | Enforce Exception Shielding in service and adapter layers to catch raw infrastructure exceptions and wrap them into domain exceptions before bubbling up. |
| **Structured Context Metadata Payload** | Risk of accidentally leaking sensitive information (API keys, raw credentials) into exception details dict. | Sanitize inputs and restrict exception details to operational metadata (IDs, retries, model names) in service wrappers. |
