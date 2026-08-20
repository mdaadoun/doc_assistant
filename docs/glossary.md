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

---

## 🎯 18. Reranker Service & Primary/Fallback Strategy

### Primary/Fallback Reranking Strategy
A resilient behavioral design pattern where a local high-performance cross-encoder engine (primary) is attempted first, and an external cloud API or alternative model (fallback) is invoked automatically if the primary engine fails.

### RerankerService
Domain service orchestrating candidate passage scoring and ordering across primary and fallback cross-encoder adapters.

### Auto Fallback Flag
A configurable boolean switch (`auto_fallback`) determining whether execution errors in the primary reranking adapter should trigger fallback execution or immediately raise a domain exception.

---

## 🛡️ 19. Confidence Guard & Anti-Hallucination Gating

### Confidence Guard
A domain gating component in the retrieval pipeline that evaluates candidate cross-encoder relevance scores against a minimum confidence threshold before LLM generation.

### Minimum Confidence Threshold (S_min)
Calibrated score cutoff (default 0.35) below which context is deemed insufficient for grounded response generation.

### Refusal Response Bypass
Execution path that short-circuits LLM text generation when retrieval confidence is insufficient, returning a standardized refusal message instantly (`"I cannot answer this question based on the available documentation."`).

### ConfidenceDecision
Pydantic domain schema encapsulating confidence evaluation status (`passed`), top score, threshold, filtered hits, and refusal text.

---

## 🤖 20. Grounded LLM Generation & Contextual Answering

### Grounded LLM Generation
A generation pattern where the language model is constrained strictly to retrieved context blocks, preventing hallucination or usage of prior training knowledge.

### Context Block
A formatted text snippet containing source document metadata (file name, page number) and chunk text passed into the LLM system/user prompt context.

### Zero Temperature (T=0.0)
A sampling setting (`temperature=0.0`) that minimizes generation variance and ensures deterministic output based strictly on prompt context.

### Context Refusal
A fallback response string (`"I cannot answer this question based on the available documentation."`) emitted when no relevant context chunks are provided or retrieved.

---

## 📡 21. Server-Sent Events (SSE) & Response Streaming

### Server-Sent Events (SSE)
A W3C standard protocol enabling servers to push real-time text event streams to clients over a persistent HTTP connection using `text/event-stream`.

### Async Generator Stream Handler
An asynchronous generator construct (`SSEResponseHandler`) that consumes raw token streams from LLM generation and yields formatted SSE protocol frames.

### SSE Event Frame
A text block structured with `event`, `id`, `retry`, and `data` fields separated by single newlines and terminated by a double newline sequence (`\n\n`).

---

## 🔖 22. Citation Extraction & Grounding Validation

### RawCitation
Parsed intermediate domain model representing raw file name and 1-indexed page number extracted from inline completion text.

### CitationValidationResult
Report schema detailing citation grounding status, accuracy score ratio, matched valid citations, and unmatched invalid citations.

### CitationExtractor
Domain component responsible for parsing inline citation syntax from answer text and mapping matches to context chunk metadata.

### CitationValidator
Auditing engine verifying whether extracted completion citations correspond to verified retrieved context blocks.

### verify_document_presence
Method checking whether a specific document file name and 1-indexed page number exist within retrieved context blocks.

### verify_grounding
High-level boolean verification method auditing whether all inline completion citations exist in retrieved context.

### filter_invalid_citations
Utility method sanitizing completion text by removing ungrounded inline citation tags and returning valid Citation objects.

### Strict Validation Mode
Enforcement setting (`strict=True`) in `CitationValidator.validate` that raises `GenerationError` when citation validation accuracy falls below 1.0.

### FinOpsCollector
A dedicated service in generation domain responsible for calculating prompt and completion token counts, estimating USD cost per interaction, and tracking execution latency.

### Token Cost Model Table
A dictionary mapping LLM model identifiers (e.g. gpt-4o-mini, gpt-4o) to input prompt and output completion USD pricing per thousand tokens.

### generate_with_finops
A GroundedGenerator method that executes grounded generation while measuring execution time and constructing a complete FinOpsMetadata telemetry payload alongside the response string.

---

## 🌐 23. API Layer & SSE Streaming Endpoints

### Server-Sent Events (SSE)
A unidirectional lightweight web streaming protocol using `text/event-stream` over HTTP to push real-time event frames from server to client.

### ChatService
Orchestration service connecting hybrid retrieval, confidence gating, grounded LLM token streaming, and SSE event formatting.

### Metadata Frame
Initial SSE event frame transmitting conversation ID, confidence score, grounding status, and retrieved citations before answer token deltas.

---

## 🔍 24. Retrieval Diagnostic Endpoint & Observability

### RetrievalDiagnosticEndpoint
REST API diagnostic endpoint (`GET /api/v1/debug/retrieval`) exposing internal multi-stage retrieval hits (dense vector, sparse BM25, RRF fused, and reranked) for observability and system auditability.

### DebugRetrievalResponse
Pydantic DTO encapsulating intermediate and final retrieval scores, ranks, and metadata per retrieval stage.

---

## 🔒 25. API Key Authentication Middleware & Security

### APIKeyHeader
FastAPI security utility that extracts API keys from request HTTP headers (e.g. `X-API-Key`) without throwing unhandled exceptions when `auto_error` is disabled.

### Header Authentication
A lightweight security protocol passing secret tokens in custom request HTTP headers for client authorization.

### Dependency Security Scheme
FastAPI authorization dependency pattern that validates caller credentials before invoking endpoint route handlers.

---

## 🌐 26. CORS, Request Validation & Error Handling Middleware

### CORS (Cross-Origin Resource Sharing)
HTTP mechanism allowing restricted resources to be requested from different domains. Configured via `CORSMiddleware` with origin allowlists, credentials, methods, and headers.

### Preflight Request
OPTIONS request sent by browser before actual cross-origin request to check server permissions. Cached via `max_age=600` to reduce overhead.

### Security Headers
HTTP response headers that instruct browsers to enforce security policies: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `X-XSS-Protection: 1; mode=block`.

### Error Envelope
Standardized JSON structure wrapping error responses with `code`, `message`, and `details` fields, ensuring consistent client-side error handling.

### X-Request-ID
Tracing header used to correlate requests across distributed systems. Injected or preserved by `RequestValidationMiddleware` on all responses.

### Production CORS Guard
Validation rule rejecting wildcard origin `*` combined with `allow_credentials=True` in production environments to prevent credential leakage.

---

## 🧩 27. Service Dependency Injection & Lifespan Context

### ServiceContainer
Lifespan-scoped composition root holding application service singletons (`ChatService`, `DebugRetrievalBuilder`) for the duration of the FastAPI app lifecycle.

### Lifespan Context
FastAPI `asynccontextmanager` executed on application startup/shutdown, used here to bootstrap and dispose the service container.

### Composition Root
Central wiring point where service dependencies are instantiated and injected, avoiding scattered global singletons.

### Lazy Fallback Container
Behavior in `_get_container` that creates and caches a default `ServiceContainer` on `app.state` when the lifespan has not run (e.g. direct `TestClient` usage), preserving backward compatibility with existing tests.

### app.state.container
FastAPI application state attribute holding the lifespan-scoped `ServiceContainer` instance, enabling dependency providers to resolve services per app lifecycle.

---

## ⚛️ 28. React & Vite Presentation Layer

### Server-Sent Events (SSE) (Frontend Stream Consumer)
Unidirectional HTTP-based streaming protocol used to stream token deltas, citation metadata, and stream lifecycle events from FastAPI to React in real time via `fetch` and `ReadableStream`.

### Vite Dev Server Proxy
Development-time HTTP proxy configured in `vite.config.ts` forwarding API requests from frontend development port 5173 to the backend ASGI server at port 8000.

### Citation Drawer
A presentation component displaying interactive source document citations, page numbers, relevance scores, and text excerpts.

### FinOps Telemetry
Execution metrics tracking token usage (prompt, completion, total), estimated USD costs, execution latency, and cache hit status per interaction.

---

## ⌨️ 29. Query Input & Submission Handling

### QueryInputComponent
The presentation layer React component responsible for capturing user queries, validating length and format, configuring top_k retrieval depth, and dispatching search payloads to the chat streaming handler.

### KeyboardSubmissionGuard
Event handling mechanism that distinguishes between multiline text expansion (`Shift+Enter`) and atomic query submission (`Enter`), preventing accidental whitespace submissions while maintaining seamless typing ergonomics.

### TopKSelector
Input control allowing users to adjust the number of context chunks retrieved from the dual vector/lexical index before RRF fusion and re-ranking.

### SuggestedQueriesPills
Pre-configured interactive suggestion chips representing standard corporate document inquiries (obligations, compliance, termination clauses) to accelerate onboarding and benchmark retrieval.

---

## 🌊 30. SSE Streaming Answer Display & Real-Time Rendering

### SSE Token Delta Stream
Real-time incremental text delivery over HTTP using Server-Sent Events, where tokens are concatenated in the presentation layer as they arrive from the LLM.

### Blinking Streaming Cursor
Visual affordance indicating active unidirectional text generation from the backend model before the 'done' event frame.

### Grounded Badge Indicator
UI indicator communicating whether the generated response is strictly grounded in retrieved corpus context or is a safe confidence-gate refusal.

---

## 📑 31. Citation Drawer & Source Excerpt Inspection

### Citation Drawer
A complementary presentation sidebar component displaying grounded document references, page numbers, relevance scores, and source context excerpts retrieved during RAG execution.

### Active Source Inspector
An expanded inspection view within the citation drawer displaying full context text, provenance metadata, chunk identifiers, and clipboard copy actions for a selected citation.

### Citation Pill
An interactive, inline document reference badge embedded in assistant messages that highlights and focuses the corresponding citation in the citation drawer.

### Client-Side Substring Filtering
A reactive in-memory search mechanism that dynamically filters the visible citation cards by document name, chunk ID, or excerpt keywords without network overhead.

---

## 📑 32. Loading States, Error Handling & Confidence Indicators

### Confidence Meter
A visual and accessible UI component displaying the cross-encoder relevance score as a percentage bar with explicit indication of the minimum confidence threshold (S_min = 0.35).

### Retrieval Phase Tracking
A multi-state lifecycle indicator representing the progressive execution stages of a RAG query: idle, dual search retrieval, cross-encoder re-ranking, and grounded SSE streaming.

### Inline Error Recovery
A non-blocking error display pattern that renders failure diagnostics within the conversation thread alongside an automated retry action button to re-execute failed operations.

### Skeleton Shimmer Loading
An animated placeholder UI simulating incoming content structure during retrieval latency before the first streaming response token arrives.

### Confidence Tiering
A discrete categorical classification of continuous retrieval relevance scores into High (>= 0.70), Moderate (0.35 - 0.699), and Low / Refusal (< 0.35).

---

## 📊 33. Evaluation Datasets & QA Benchmarking

### EvalDatasetItem
An immutable domain schema representing an annotated evaluation benchmark record, containing the query ID, question prompt, ground-truth answer, expected source citations, and out-of-corpus classification flag.

### EvalGroundTruthCitation
A structured attribution record defining the target source file name, 1-indexed page number, and chunk identifier required for automated retrieval precision calculations.

### Honesty Filter Evaluation
An evaluation testing protocol validating that the retrieval and generation pipeline accurately refuses to hallucinate when prompted with out-of-corpus, adversarial, or low-relevance queries.

### Retrieval Ground Truth Triplet
A standardized benchmark tuple comprising an input query prompt, labeled context citations, and reference ground-truth answer used to evaluate retrieval precision@k and RAGAS faithfulness metrics.

---

## 📈 34. Retrieval Benchmark Metrics & RetrievalMonitor

### RetrievalMonitor
Core evaluation runner that executes automated benchmark batches across annotated evaluation queries, measuring precision@k, recall@k, MRR, guardrail triggers, and latency percentiles.

### Precision@k
The proportion of top-k retrieved chunks that belong to the annotated ground-truth citations for a given query.

### Recall@k
The proportion of all relevant ground-truth chunks that are successfully retrieved within the top-k candidate results.

### Mean Reciprocal Rank (MRR)
The statistical average of reciprocal ranks (1/rank) of the first relevant document retrieved across all evaluation queries.

### Honesty Filter Precision
The ratio of correctly refused out-of-corpus queries to the total number of out-of-corpus queries evaluated, measuring refusal guard reliability.

### RetrievalQueryResult
An immutable Pydantic V2 domain schema recording per-query benchmark metrics including retrieved chunk IDs, ground-truth matches, precision@k, recall@k, MRR, confidence guard decision, and latency in milliseconds.

### RetrievalBenchmarkReport
A comprehensive aggregate report model capturing total query count, in/out-of-corpus breakdowns, mean precision, mean recall, MRR, hit rate, honesty filter precision, latency percentiles ($p_{50}, p_{90}, p_{95}, p_{99}$), and threshold compliance status.

### RetrievalMetricThresholds
A domain schema encapsulating non-negotiable benchmark targets ($	ext{precision@5} \ge 0.75$, $	ext{honesty} \ge 0.90$, $p_{95} \le 3000	ext{ ms}$) used for automated pass/fail gating.

