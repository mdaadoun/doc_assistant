# Architectural Journal — Phase 3.1: PDF Parser & Page-Level Metadata Extraction

> **Phase:** 3.1 | **Date:** 2026-08-10 | **Status:** Completed

---

## 🎯 Objective
Implement `PDFParser` supporting PyMuPDF (fitz) and pdfplumber engines, abstracting document extraction under `BaseDocumentParser`, extracting page-level metadata metrics, and enforcing exception shielding.

---

## 💡 Architectural Choices

### 1. Dual-Engine PDF Parsing Architecture (`PyMuPDF` / `pdfplumber`)
- **Context:** Large document corpora require high-throughput text extraction, but complex document layouts and tabular content require specialized layout analysis.
- **Decision:** Implement `PDFParser` conforming to `BaseDocumentParser`, featuring PyMuPDF as the high-speed default engine and `pdfplumber` as an alternate engine for layout analysis.
- **Rationale:** Delivers optimal performance by default while providing flexibility for complex structural documents.

### 2. Page-Level Provenance & Granular Metadata Extraction
- **Context:** Citation-grounded RAG applications must trace LLM responses back to specific source documents and 1-indexed page numbers.
- **Decision:** Extract page dimensions, rotation, word/char counts, image counts, and detected table counts into `PageMetadata` and `ParsedPage` schemas.
- **Rationale:** Ensures complete auditability and page-level citation accuracy during chunking and generation.

### 3. Parser Boundary Exception Shielding
- **Context:** Raw PDF driver exceptions (e.g. `fitz.FileDataError`, `pdfplumber` syntax errors) leak engine implementation details.
- **Decision:** Validate file existence and size before parsing, and intercept underlying driver exceptions to raise domain-specific `IngestionError` with structured error codes (`FILE_NOT_FOUND`, `EMPTY_FILE`, `PDF_PARSING_ERROR`).
- **Rationale:** Prevents raw driver stack traces from leaking across architectural boundaries.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Dual-Engine PDF Parsing** | Increases dependency footprint (`pymupdf` and `pdfplumber`). | Abstract both engines behind `BaseDocumentParser` interface to keep consumers decoupled from specific drivers. |
| **Page-Level Metadata Extraction** | Minor memory overhead storing per-page spatial and metric metadata prior to chunking. | Use frozen Pydantic models with lightweight numerical fields to minimize footprint. |
| **Parser Boundary Exception Shielding** | Requires explicit try/except mapping for each third-party engine. | Standardize error mapping inside `PDFParser` helper methods yielding consistent `IngestionError` instances. |
