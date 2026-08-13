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

### Embedding Client Adapter
Unified infrastructure component that converts text input sequences into dense floating-point vector representations across multiple provider APIs.

### text-embedding-3-small
OpenAI highly efficient vector embedding model producing 1536-dimensional representations optimized for retrieval and semantic search tasks.

### Deterministic Mock Embedding
Offline pseudo-embedding generator using cryptographic hashing to produce unit-normalized float vectors for reproducible unit tests.

### Batch Chunking
Partitioning large sequences of document chunks into fixed-size request sub-batches to adhere to remote API payload limits.

---

## 🔍 10. Sparse Retrieval & BM25 Indexing

### BM25Okapi
Okapi Best Matching 25 ranking function from the `rank-bm25` library; scores documents by term frequency, inverse document frequency, and document length normalization.

### Sparse Retrieval
Lexical retrieval using exact term matching (BM25) as opposed to dense vector similarity; captures keyword precision and complements semantic search.

### Tokenized Corpus
List of token lists where each inner list is the tokenized representation of one chunk document; the input format required by `BM25Okapi`.

### Index Persistence
Serialization of the tokenized corpus and chunk metadata to JSON so the BM25 index can be rebuilt without re-ingesting source documents.

### k1 / b / epsilon
BM25 hyperparameters: `k1` controls term frequency saturation, `b` controls document length normalization (0-1), and `epsilon` prevents zero IDF for terms appearing in all documents.

---

## 🔀 11. Indexing Orchestration & Dual Indexing

### IndexingOrchestrator
Coordination service that embeds document chunks, upserts dense vectors into a vector store, and builds a sparse BM25 index in a single typed, fail-fast operation.

### IndexingResult
Immutable dataclass summarizing an indexing run: chunk count, vector count, BM25 count, target collection name, and optional persisted BM25 path.

### Dual Indexing
The workflow of populating both a dense vector index (Qdrant) and a sparse lexical index (BM25) for the same chunk corpus, enabling hybrid retrieval in later phases.

### Embedding Dimension Mismatch
Boundary validation error raised when an embedding vector length differs from the vector store's configured dimension, preventing corrupt Qdrant writes.

### Embedding Count Mismatch
Boundary validation error raised when the number of returned embeddings differs from the number of input chunks, indicating a provider failure.

### Fail-Fast Boundary Validation
Validating embedding count and dimension before any I/O so provider misconfiguration surfaces as a typed `RetrievalError` instead of partial or corrupt index writes.

---

## 🔍 12. Dense Vector Search & Hybrid Retrieval

### DenseSearchService
Query-time service that embeds a user query and retrieves top-k nearest vectors from Qdrant using cosine similarity, producing ranked `RetrievalResult` candidates for downstream RRF fusion.

### DENSE_TOP_K_DEFAULT
Constant default of 50 candidate hits fetched from dense vector search for downstream Reciprocal Rank Fusion (RRF).

### Query Embedding Dimension Mismatch
Error raised when the query embedding vector length differs from the vector store's configured dimension (e.g. 1536), preventing invalid Qdrant queries.

### Dense Retrieval
Semantic vector similarity search using dense embeddings and cosine distance, capturing meaning beyond exact keyword matches.

---

## 🔍 13. Sparse BM25 Search Service

### SparseSearchService
Query-time service that runs a lexical BM25 query over the in-memory tokenized corpus and retrieves top-k ranked hits, producing `RetrievalResult` candidates for downstream RRF fusion.

### SPARSE_TOP_K_DEFAULT
Constant default of 50 candidate hits fetched from sparse BM25 search for downstream Reciprocal Rank Fusion (RRF), matching the dense retrieval default for balanced fusion.

### Sparse BM25 Search
Lexical retrieval stage that scores query tokens against the tokenized corpus using the Okapi BM25 ranking function, capturing exact keyword precision to complement dense semantic search.

---

## 🔀 14. Reciprocal Rank Fusion (RRF) & Hybrid Fusion

### RRF (Reciprocal Rank Fusion)
Fusion algorithm that merges multiple ranked result lists by summing `1/(k + rank)` per item; items present in more lists rank higher regardless of raw score magnitudes or scales.

### Rank constant k
Smoothing constant in the RRF formula that dampens rank dominance; `k=60` is the standard value from the original RRF paper (Cormack et al.), used as the default in `RRF_K_DEFAULT`.

### Fused score
Sum of reciprocal-rank contributions across all input lists for a given `chunk_id`; used as the final `relevance_score` on fused `RetrievalResult` instances.

### retrieval_method='rrf'
Marker stamped on fused `RetrievalResult` instances to distinguish them from `'dense'` and `'sparse'` hits in retrieval debug payloads.

### RRFusionService
Hybrid fusion service that composes the dense top-50 hits and sparse top-50 hits into a single fused ranking using the Reciprocal Rank Fusion formula, with deterministic tie-breaking by `chunk_id` and dense payload preference on duplicates.

### RRF_K_DEFAULT
Constant default of 60 for the rank-smoothing constant `k` used in the RRF formula `1/(k + rank)`.

### RRF_TOP_K_DEFAULT
Constant default of 50 fused output hits produced by RRF fusion, matching the dense and sparse candidate pool sizes.

---

## 🔍 15. Retrieval Debug Data Structure & Observability

### DebugRetrievalHit
Compact per-stage retrieval hit exposing `chunk_id`, raw `score`, 1-indexed `rank`, and stage `method` (dense/sparse/rrf). Used in `DebugRetrievalResponse` for observability.

### DebugRetrievalBuilder
Service that orchestrates dense search, sparse search, and RRF fusion to assemble a `DebugRetrievalResponse` payload for the `/api/v1/debug/retrieval` endpoint.

### Stage-wise top_k
Per-pipeline-stage candidate limits (`dense_top_k`, `sparse_top_k`, `rrf_top_k`) allowing the debug endpoint to inspect different candidate counts per retrieval stage.

### DebugRetrievalResponse
Structured diagnostic schema capturing candidate search hits at each pipeline stage: dense, sparse, RRF fusion, and final re-ranking. `dense_hits`, `sparse_hits`, and `rrf_fused` use `DebugRetrievalHit`; `final_reranked` uses `RetrievalResult`.

---

## 🎯 16. Cross-Encoder Re-Ranking & FlashRank Engine

### Cross-Encoder Re-Ranking
A two-stage retrieval technique where a joint-attention neural model evaluates query-passage pairs directly, providing high-precision relevance scores to refine candidate rankings from bi-encoder/lexical first-stage search.

### FlashRank Adapter
A lightweight CPU-optimized local cross-encoder inference adapter utilizing quantized ONNX runtime models for fast reranking without external API latency or costs.

### Candidate Truncation Window
The technique of slicing candidate search hits (e.g. top 30) from initial hybrid retrieval stages before cross-encoder inference to balance retrieval precision with inference latency.

---

## 🎯 17. Cohere Rerank API & Managed Reranking

### Cohere Rerank API
Managed cloud cross-encoder reranking service providing high-precision relevance scores for query-passage pairs via external API endpoints.

### Remote Cross-Encoder Adapter
Adapter translating domain `RetrievalResult` models into external API payloads and returning ranked domain models with updated relevance scores.

### Candidate Top-N Slicing
Truncating retrieved candidate hits (`candidate_k=30`) before API invocation to optimize network payload size and API execution cost.



