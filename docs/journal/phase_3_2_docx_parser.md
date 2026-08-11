# Architectural Journal — Phase 3.2: DOCX Parser & Structural Metadata Extraction

> **Phase:** 3.2 | **Date:** 2026-08-11 | **Status:** Completed

---

## 🎯 Objective
Implement `DOCXParser` using `python-docx` conforming to `BaseDocumentParser`, extracting structural metadata (headings, tables, page breaks, image counts, core properties), and enforcing exception shielding.

---

## 💡 Architectural Choices

### 1. OpenXML Body Element Traversal (`CT_P` & `CT_Tbl`)
- **Context:** DOCX documents contain paragraphs and tables mixed sequentially. Processing `doc.paragraphs` and `doc.tables` independently destroys document element flow order.
- **Decision:** Iterate over raw OpenXML child nodes in `doc.element.body`, dispatching `CT_P` nodes to paragraph formatters and `CT_Tbl` nodes to table formatters in exact document sequence.
- **Rationale:** Preserves natural document flow and context continuity for downstream chunking engines.

### 2. Flow-Based Pagination & Structural Break Detection
- **Context:** DOCX files are flow-based documents without fixed physical page boundaries.
- **Decision:** Detect explicit page breaks (`page_break_before` flags, `w:br type=page` XML tags, `w:lastRenderedPageBreak`) to flush page buffers into `ParsedPage` instances, while providing a single-page fallback for unpaginated documents.
- **Rationale:** Enables page-like pagination provenance for citation mapping even in flow-formatted documents.

### 3. Structural Heading Normalization to Markdown
- **Context:** Downstream recursive chunkers require clear hierarchy signals to split content along logical boundaries.
- **Decision:** Convert DOCX paragraph heading styles (`Heading 1-6`, `Title`, `Subtitle`) into standardized Markdown headers (`#` to `######`).
- **Rationale:** Retains document hierarchy in extracted plain text while standardizing inputs across PDF, DOCX, and Markdown formats.

### 4. Exception Shielding & Boundary Validation
- **Context:** Low-level zip archive corruption or missing files in third-party libraries leak internal implementation details.
- **Decision:** Validate file existence and non-zero size before parsing, and intercept `python-docx` driver errors to raise structured domain `IngestionError` exceptions (`FILE_NOT_FOUND`, `EMPTY_FILE`, `DOCX_PARSING_ERROR`).
- **Rationale:** Ensures consistent error contracts across all ingestion parsers.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **OpenXML Body Traversal** | Relies on python-docx XML internals (`CT_P`, `CT_Tbl`). | Encapsulate traversal logic within `DOCXParser` helper methods to isolate engine specifics. |
| **Flow-Based Pagination** | Unpaginated DOCX files merge content into a single page. | Explicit page breaks create page splits; single-page output remains fully chunkable by downstream recursive splitters. |
| **Markdown Heading Normalization** | Strips custom docx typography styling. | Preserves semantic heading hierarchy necessary for RAG chunking while discarding non-essential visual formatting. |
