# Architectural Journal — Phase 3.3: Markdown Parser & Frontmatter Extraction

> **Phase:** 3.3 | **Date:** 2026-08-11 | **Status:** Completed

---

## 🎯 Objective
Implement `MarkdownParser` conforming to `BaseDocumentParser` with YAML frontmatter extraction, fallback header title identification, explicit page-break marker segmentation, image/table metric calculation, and exception shielding.

---

## 💡 Architectural Choices

### 1. Polymorphic `BaseDocumentParser` Contract
- **Context:** The document ingestion pipeline must process diverse format inputs (PDF, DOCX, MD) transparently through a unified parser contract.
- **Decision:** Implement `MarkdownParser` extending `BaseDocumentParser`, producing canonical `ParsedDocument` schemas with `source_format="md"`.
- **Rationale:** Guarantees uniform document representations across file types for downstream chunking and vector indexing.

### 2. PyYAML Safe Frontmatter Extraction (`---` Delimiters)
- **Context:** Technical Markdown files often begin with YAML frontmatter blocks containing document metadata headers.
- **Decision:** Extract text enclosed between top-level `---` triple-dash delimiters and deserialize metadata safely using `yaml.safe_load`.
- **Rationale:** Safely extracts structured metadata (title, author, subject, keywords, creation dates) without risking code execution vulnerabilities.

### 3. Regex Fallback for H1 Title Extraction
- **Context:** Not all Markdown files contain YAML frontmatter, but standard documents typically start with a level-1 heading.
- **Decision:** When frontmatter is missing or lacks a `title` key, scan the Markdown body text with regex (`^#\s+(.+)$`) to populate `DocumentMetadata.title`.
- **Rationale:** Ensures key metadata fields remain populated for citation generation even when explicit YAML metadata is omitted.

### 4. Explicit Page Break Marker Segmentation
- **Context:** Markdown documents are continuous text flows lacking native page structures, yet downstream citation systems rely on page provenance.
- **Decision:** Support explicit page break markers (`<!-- pagebreak -->`, `<!-- page_break -->`, `\pagebreak`, `\newpage`) to segment text into separate `ParsedPage` objects, falling back to a single page when unpaginated.
- **Rationale:** Enables precise multi-page citation mapping when document authors configure page breaks.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Regex Metrics Counting** | Regex table and image counting avoids heavy AST parser dependencies (e.g. mistune/marko), but could miscount in complex code block snippets. | Lightweight regex regexes (`!\[.*?\]\(.*?\)` and contiguous `\|` lines) keep runtime footprint minimal; chunking engines operate primarily on plain text blocks. |
| **YAML Frontmatter Parsing** | Requires `PyYAML` library dependency. | `PyYAML` is widely available and stable; wrapping deserialization in `yaml.safe_load` ensures secure execution. |
| **Page Break Markers** | Relies on explicit author tags (`<!-- pagebreak -->`) for multi-page splitting. | Defaulting to single-page processing guarantees zero errors for standard Markdown while rewarding formatted docs with granular page boundaries. |
