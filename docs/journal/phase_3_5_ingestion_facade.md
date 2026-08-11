# Architectural Journal — Phase 3.5: Ingestion Facade with Format Dispatcher and Fail-Fast Validation

> **Phase:** 3.5 | **Date:** 2026-08-11 | **Status:** Completed

---

## 🎯 Objective
Implement `IngestionFacade` to unify document ingestion operations behind a single entry point, orchestrating dynamic format-specific parser dispatching, fail-fast file validation, document parsing, and single/batch structural chunking.

---

## 💡 Architectural Choices

### 1. Facade Pattern for Ingestion Orchestration
- **Context:** Downstream API endpoints and indexing services require a simple, unified contract to parse and chunk diverse file types without needing to interact directly with individual parser or chunker classes.
- **Decision:** Create `IngestionFacade` as an orchestrator encapsulating format selection (`BaseDocumentParser`), file validation (`validate_file`), parsing (`parse_document`), and structural chunking (`ingest_document`, `ingest_batch`).
- **Rationale:** Decouples pipeline callers from concrete parser implementations and provides a centralized location for pipeline policies like file size limits and extension mapping.

### 2. Extensible Format Dispatcher Mapping
- **Context:** Corporate RAG systems ingest multiple document formats (PDF, DOCX, Markdown) and may require runtime extension for additional formats or custom parsers.
- **Decision:** Build a dynamic format dispatcher inside `IngestionFacade` that maps normalized file extension strings (`.pdf`, `.docx`, `.md`, `.markdown`) to registered `BaseDocumentParser` instances, supporting runtime registration via `register_parser()` and `unregister_parser()`.
- **Rationale:** Enables open-closed extensibility—new format parsers can be registered dynamically without modifying facade core code or existing parsers.

### 3. Fail-Fast Validation Policy
- **Context:** Invoking heavy document parsing libraries (e.g. PyMuPDF, python-docx) on missing, empty, oversized, or unsupported files wastes compute resources and generates unhandled parser crashes.
- **Decision:** Implement `validate_file()` to verify file existence, file path type, non-zero file size, maximum file size threshold (`max_file_size_bytes`), and extension registration prior to executing parser or chunker routines.
- **Rationale:** Immediately intercepts invalid requests and raises structured `IngestionError` domain exceptions with specific diagnostic error codes (`FILE_NOT_FOUND`, `INVALID_FILE`, `EMPTY_FILE`, `FILE_TOO_LARGE`, `UNSUPPORTED_FORMAT`).

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Extension-Based Dispatching** | Relying on file extensions does not detect mislabeled file formats (e.g., PDF renamed to .docx). | Provided `format_override` parameter in facade methods to allow explicit parser selection regardless of file extension. |
| **Synchronous Batch Ingestion** | Ingesting large file lists sequentially in `ingest_batch()` holds thread execution. | Provides immediate in-memory chunk aggregation for small to medium batches, serving as a clean target for future background queue worker delegation. |
| **Centralized File Size Limit** | Global `max_file_size_bytes` applies to all formats uniformly. | Optional configuration parameter that can be customized or overridden per facade instance when instantiated. |
