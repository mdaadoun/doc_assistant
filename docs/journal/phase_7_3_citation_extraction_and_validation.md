# Architectural Journal — Phase 7.3: Citation Extraction & Validation Logic

> **Phase:** 7.3 | **Date:** 2026-08-13 | **Status:** Completed

---

## 🎯 Objective
Implement `CitationExtractor`, `CitationValidator`, `RawCitation`, and `CitationValidationResult` in `src/generation/citations.py` to parse inline document citations in `[Doc: <file_name> | Page: <page_number>]` format from generative completion responses, verify cited source chunks against retrieved context, and calculate zero-tolerance citation accuracy metrics ($citation\_accuracy = 1.00$).

---

## 💡 Architectural Choices

### 1. Regex-Based Inline Citation Extraction (`CITATION_REGEX`)
- **Context:** Generative answers emit inline citation tags during real-time token streaming. Post-processing tags requires fast, deterministic parsing without calling LLMs again.
- **Decision:** Implemented `CITATION_REGEX` (`\[Doc:\s*([^|\]]+?)\s*\|\s*Page:\s*(\d+)\s*\]`, case-insensitive) and `CitationExtractor.extract_raw(text)` to parse raw document filenames and 1-indexed page numbers.
- **Rationale:** Prevents additional token latency, maintains low processing overhead, and supports real-time tag extraction from completion buffers.

### 2. Decoupled Extraction and Grounding Validation
- **Context:** Parsing inline tags and auditing them against context blocks serve distinct purposes in the RAG pipeline.
- **Decision:** Created `CitationExtractor` to extract raw tags and resolve metadata, and `CitationValidator` to verify citations against retrieved context and produce a structured `CitationValidationResult`.
- **Rationale:** Enables standalone validation on both raw completion strings and structured `Citation` model sequences while keeping parser logic cleanly separated from validation logic.

### 3. Heterogeneous Context Object Normalization
- **Context:** Upstream retrieval results may be passed as dynamic dictionaries or domain model objects (`ChunkDocument`, `RetrievalResult`, custom schemas).
- **Decision:** Built `_extract_context_meta` helper supporting inspectable fallback metadata fields for `file_name`/`source_file`, `page_number`/`page`, `chunk_id`/`id`, `excerpt`/`text`/`content`, and `relevance_score`/`score`.
- **Rationale:** Ensures robust extraction across heterogeneous context sources without requiring strict schema transformations upstream.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Regex-Based Extraction** | Relies on LLM prompt compliance with the exact inline tag format. | Grounded system prompt strictly enforces inline format `[Doc: <file_name> | Page: <page_number>]`. |
| **Two-Pass Citation Processing** | Incurs two passes (raw tag extraction followed by context lookup). | Efficient string normalization and small context lists ($K \le 50$) keep latency negligible ($<1\text{ms}$). |
| **Heterogeneous Context Inspection** | Incurs dynamic attribute and dictionary key checks per item. | Encapsulated in single `_extract_context_meta` helper with type-safe fallback exception handling. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
CitationValidator.validate(text_or_citations, contexts)
  ├── 1. Parse raw citations via CitationExtractor.extract_raw(text) OR map Citation sequence to RawCitation list
  ├── 2. Extract normalized context metadata via CitationExtractor._extract_context_meta(ctx)
  ├── 3. Iterate raw citations:
  │        ├── Match file_name (case-insensitive) and page_number against context metadata
  │        ├── If matched -> Construct valid Citation object -> Append to valid_citations
  │        └── If unmatched -> Append to invalid_citations
  └── 4. Calculate accuracy = len(valid) / total -> Determine is_valid (len(invalid) == 0) -> Return CitationValidationResult
```

---

## 🔬 Verification Summary
- Executed unit test suite: **7 passed** in `test_citations.py` (**258 passed** across entire project suite).
- Registered `test_citations.py` test suite in `tests/unit/test_runner.py`.
- Static type checking: **0 errors** under `mypy src` strict checks.
