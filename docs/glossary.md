# Technical Glossary

> **Scope:** Domain terms, architectural definitions, and infrastructure concepts for the Corporate Document Assistant.

---

## 🛠️ 1. Infrastructure & Build System

### Poetry Constraint
A version specification rule defined in `pyproject.toml` (e.g. `python = "^3.11"`) enforcing minimum language, package, and dependency constraints across developer and container runtimes.

### Runtime Version Validation
The programmatic inspection of system runtime properties (`sys.version_info`) against mandatory minimum requirements during application startup.

### Dashboard Test Runner
A module wrapper around test frameworks (`pytest.main()`) programmatically launching test suites and returning structured status outputs for developer dashboards and CI/CD pipelines.

### Static Type Guarding
Compile-time static analysis using Mypy strict mode to enforce explicit type signatures across all packages, preventing implicit untyped escapes.

---

## 🧹 2. Code Quality & Static Analysis

### Ruff
Fast Python linter and formatter written in Rust, replacing Flake8, Black, and isort.

### Mypy Strict Mode
Static type checker configuration mode enforcing explicit return/argument annotations, disallowing untyped defs, and prohibiting implicit optional types.

### Pre-commit Hooks
Automated git hook framework executing static checks, formatters, and security scanners prior to committing code.

### detect-secrets
Enterprise secret scanner that analyzes codebases using heuristics and high-entropy string detection to prevent credential leakage.

### Secrets Baseline
A JSON-formatted snapshot file (`.secrets.baseline`) recording known/audited secret findings to bypass false positives.

---

## ⚙️ 3. Configuration & Runtime Settings

### BaseSettings
Pydantic class extension (`pydantic_settings.BaseSettings`) for parsing, type-casting, and validating application configuration from system environment variables and `.env` files.

### SettingsConfigDict
Pydantic V2 metadata configuration dictionary defining model settings such as `env_file`, `env_file_encoding`, and `extra="ignore"`.

### lru_cache Singleton
Functional caching pattern leveraging Python's `functools.lru_cache` decorator to cache and reuse initialized immutable `Settings` instances across application lifecycles.

---

## 📦 4. Modular Package Architecture

### Modular Layout
Architectural organization separating distinct system domains (API, ingestion, retrieval, generation, clients, models, core, cache) into isolated Python packages.

### Package Layout Auditor
Programmatic validator verifying the existence and completeness of required core Python packages and directory structures.

---

## 🛠️ 5. Makefile & Developer Shortcuts

### Makefile
A build automation tool specification file defining rules, dependencies, and shell commands for target creation and development tasks.

### .PHONY
A Makefile directive indicating that target names represent explicit commands rather than output file names on disk.

### Dev Shortcuts
Convenience Makefile targets encapsulating multi-step static analysis, type checking, testing, and formatting routines.

---

## 🐳 6. Docker Containerization & Infrastructure

### Docker Compose
Multi-container Docker orchestration tool defining services, networks, and volumes in a unified YAML specification file (`docker-compose.yml`).

### Container Skeleton
Base infrastructure container configuration establishing service dependencies, health ordering, and port/volume bindings before detailed application code completion.

---

## 🏛️ 7. Domain Schemas & Base Models

### BaseDomainModel
The foundational base model for all domain schemas in the corporate document assistant, enforcing immutability and strict field validation.

### Frozen Schema
A Pydantic V2 model configuration (`frozen=True`) where instances are immutable and hashable after creation.

### Forbid Extra
A Pydantic V2 validation setting (`extra="forbid"`) that raises a `ValidationError` if undeclared fields are passed during instantiation.

### ChunkDocument
Normalized text chunk with structural metadata and source file attributes used during document ingestion and vector storage.

### RetrievalResult
Standardized search hit model representing retrieved context chunks enriched with relevance scoring and strategy attributes.

### Citation
Verifiable source text reference linking generated assistant responses directly to source document pages and chunk IDs.

### FinOpsMetadata
Telemetry payload tracking token counts, estimated USD costs, execution latency, and caching status per request.

### DebugRetrievalResponse
Structured diagnostic schema capturing candidate search hits at each pipeline stage: dense, sparse, RRF fusion, and final re-ranking.

---

## ⚠️ 8. Domain Exceptions & Error Handling

### AppBaseError
The root base exception class for all domain errors within the Doc Assistant application, encapsulating error code, message, and diagnostic metadata payload dictionary.

### Exception Shielding
An architectural pattern where lower-level infrastructure or third-party exceptions are caught and wrapped into clean domain-specific exceptions before propagating across layer boundaries.

### ConfigurationError
Domain exception raised when system settings, environment variables, or API keys are missing, invalid, or corrupted.

### IngestionError
Domain exception raised during document parsing, text extraction, structural chunking, or ingestion dispatch failures.

### RetrievalError
Domain exception raised during dense vector search, BM25 sparse search, RRF fusion, or cross-encoder re-ranking failures.

### GenerationError
Domain exception raised during LLM generation, SSE response streaming, or citation extraction and validation failures.

---

## 📄 9. Document Ingestion & Parsers

### BaseDocumentParser
Abstract base class contract requiring a `parse(file_path)` method returning a `ParsedDocument` domain model.

### PDFParser
Ingestion component implementing `BaseDocumentParser` to parse PDF files using PyMuPDF or pdfplumber engines with page-level metadata extraction.

### ParsedDocument
Pydantic V2 domain model representing an entire ingested document with global metadata and ordered `ParsedPage` instances.

### ParsedPage
Pydantic V2 domain schema representing a single extracted document page with text content and `PageMetadata`.

### DOCXParser
Ingestion component implementing `BaseDocumentParser` using `python-docx` to parse DOCX files with structural metadata, heading normalization, and flow-based pagination.

### OpenXML Body Traversal
Iterating sequentially over raw OpenXML child nodes (`CT_P` and `CT_Tbl`) in `doc.element.body` to maintain original document flow order.

### Flow-Based Pagination
Inferring page boundaries in non-paginated XML documents using explicit break elements (`w:br w:type=page` or `page_break_before`) and section dimension properties.

### Structural Heading Normalization
Transforming DOCX paragraph heading styles into standardized Markdown header levels (`#` to `######`) for downstream structural chunking.

### MarkdownParser
Ingestion component implementing `BaseDocumentParser` for Markdown (`.md`) files with YAML frontmatter extraction, header title fallback, and explicit page-break marker segmentation.

### Frontmatter
Metadata block located at the beginning of a Markdown document formatted in YAML between triple-dash (`---`) delimiters.

### PageBreakMarker
Special HTML comment or control keyword in document text (`<!-- pagebreak -->`, `\pagebreak`) used to delimit logical page boundaries for chunking provenance.

### Recursive Structural Chunking
A text segmentation strategy that recursively splits document text using a hierarchy of structural delimiters (paragraphs, lines, sentences, words) to produce chunks constrained within maximum token limits.

### Page Boundary Preservation
An ingestion rule requiring text chunks to remain strictly scoped within individual page boundaries to preserve accurate source page attribution.

### Boundary Overlap Ratio
The percentage (e.g., 10%) of maximum chunk token capacity prepended from the tail of a preceding split to maintain semantic continuity across adjacent chunks.

### Fallback Token Density Estimator
A deterministic token counting algorithm utilizing combined word and character density metrics to estimate token counts when offline or BPE tokenizers are unavailable.

### IngestionFacade
A unified entry-point service class that orchestrates document validation, format-specific parsing, and structural chunking.

### FormatDispatcher
A registry mechanism mapping document file extensions to their corresponding parser instances.

### FailFastValidation
An early verification step that halts processing and raises structured `IngestionError` instances upon encountering invalid files or unsupported formats before resource-intensive operations.

### FormatOverride
An optional parameter allowing explicit specification of the target format parser regardless of file extension.

### Differential Update
Incremental ingestion process that computes deltas between disk state and previously stored manifest to skip unmodified files.

### Content Hash
Cryptographic digest (SHA-256) of raw file bytes used to detect file content modifications uniquely.

### State Manifest
Persisted inventory recording normalized file paths, content hashes, file sizes, modification times, and chunk IDs.

### Differential Delta
Categorized summary payload containing lists of new, changed, deleted, and unchanged file paths.

### Differential Result
Comprehensive execution payload containing the differential delta, newly generated document chunks, and processing statistics.

### Vector Store Adapter
An abstraction layer wrapping external vector database clients (e.g. Qdrant) to manage collections, upsert embeddings, and execute similarity searches.

### COSINE Distance
A similarity metric measuring the cosine of the angle between two normalized dense vector representations.

### Deterministic Point UUID
A UUIDv5 hash derived from an arbitrary string identifier and a namespace UUID, guaranteeing identical UUID outputs for identical input chunk keys.


