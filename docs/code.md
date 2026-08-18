# Technical Code Walkthrough & Function Reference

> **Module:** Core Infrastructure & Environment Constraints (Phase 1.1)

---

## 🏛️ Module Overview

This document provides a detailed breakdown of core modules, function signatures, data flows, and architectural implementations established during Phase 1.1.

---

## 1. Environment & Constraint Validation (`src/core/environment.py`)

### Overview
Validates runtime Python version constraints against `MIN_PYTHON_VERSION` (3, 11) and verifies `pyproject.toml` Poetry declaration integrity.

### Functions

#### `get_python_version_tuple() -> tuple[int, int, int]`
- **Purpose:** Extracts the active Python runtime major, minor, and micro version integers from `sys.version_info`.
- **Return Value:** 3-element tuple `(major, minor, micro)`.

#### `check_python_version(min_version: tuple[int, int] = MIN_PYTHON_VERSION) -> bool`
- **Purpose:** Compares active runtime version against minimum constraint tuple.
- **Parameters:** `min_version` (default `(3, 11)`).
- **Return Value:** `True` if active Python version meets or exceeds `min_version`, `False` otherwise.

#### `locate_pyproject_toml(search_start: Path | None = None) -> Path | None`
- **Purpose:** Traverses directory hierarchy upward to locate `pyproject.toml`.
- **Parameters:** `search_start` starting path (defaults to file location).
- **Return Value:** `Path` to `pyproject.toml` if found, `None` otherwise.

#### `validate_poetry_config(pyproject_path: Path | None = None) -> dict[str, Any]`
- **Purpose:** Inspects `pyproject.toml` to verify Poetry block definitions and `^3.11` version constraints.
- **Return Value:** Dictionary containing `valid` status, `has_poetry`, `has_python_constraint`, and target path.

#### `get_environment_info() -> dict[str, Any]`
- **Purpose:** Aggregates runtime Python version, constraint compliance, and Poetry file location into a summary payload.
- **Return Value:** Structured dictionary summarizing environment readiness.

---

## 2. Dashboard Test Runner (`tests/runner.py`)

### Overview
Provides programmatic test suite execution for integration into developer dashboards and automated QA pipelines.

### Functions

#### `run_project_tests(test_path: str = "tests", extra_args: list[str] | None = None) -> dict[str, Any]`
- **Purpose:** Programmatically launches `pytest.main()` against specified directory paths with optional parameters.
- **Parameters:** `test_path` relative path to tests, `extra_args` additional CLI flags.
- **Return Value:** Structured execution payload:
  ```python
  {
      "status": "PASSED" | "FAILED",
      "exit_code": int,
      "target": str,
  }
  ```

---

## 3. Unit Test Verification Suite (`tests/unit/`)

### Test Modules
- `test_environment.py`: Verifies runtime version detection, tuple parsing, version mocking, `pyproject.toml` discovery, and validation routines.
- `test_pyproject.py`: Asserts `pyproject.toml` existence, Poetry package declarations, Python `^3.11` dependencies, Ruff `py311` target version, and Mypy strict mode flags.
- `test_quality_config.py`: Validates presence and structural rules of `ruff.toml`, `.pre-commit-config.yaml`, `.secrets.baseline`, and `validate_quality_configs()`.
- `test_makefile.py`: Asserts `Makefile` existence, target parsing, missing target detection, and `.PHONY` declaration validity.
- `test_runner.py`: Validates programmatic execution of `run_project_tests()`.


---

## 4. Quality Configuration Auditor (`src/core/quality.py`)

### Overview
Audits static code quality infrastructure configuration files (`ruff.toml`, `.pre-commit-config.yaml`, `.secrets.baseline`) and provides programmatic health checks.

### Functions

#### `validate_ruff_config(base_dir: Path | None = None) -> dict[str, Any]`
- **Purpose:** Audits presence and rule definitions (`select`, `lint.isort`, `py311` target) in `ruff.toml`.
- **Return Value:** Audit result payload dictionary.

#### `validate_pre_commit_config(base_dir: Path | None = None) -> dict[str, Any]`
- **Purpose:** Verifies presence and required hooks (`ruff`, `mypy`, `detect-secrets`) in `.pre-commit-config.yaml`.
- **Return Value:** Hook audit status dictionary.

#### `validate_detect_secrets_baseline(base_dir: Path | None = None) -> dict[str, Any]`
- **Purpose:** Checks existence and JSON structure (`version`, `plugins_used`, `results`) of `.secrets.baseline`.
- **Return Value:** Baseline audit outcome payload dictionary.

#### `validate_quality_configs(base_dir: Path | None = None) -> dict[str, Any]`
- **Purpose:** Aggregates audit checks across all quality tool configurations (`pyproject.toml`, `ruff.toml`, `.pre-commit-config.yaml`, `.secrets.baseline`).
- **Return Value:** Combined validation summary payload dictionary.

---

## 5. Configuration Management (`src/core/config.py`)

### Overview
Manages type-safe application parameters, environment variables, vector store endpoints, retrieval defaults, model definitions, and API keys via Pydantic V2 `BaseSettings`.

### Classes & Functions

#### `Settings(BaseSettings)`
- **Purpose:** Central Pydantic model defining environment properties, server configuration, vector store parameters, retrieval thresholds, model names, and API credentials.
- **Methods:**
  - `is_production() -> bool`: Returns `True` if `environment` is set to production.
  - `is_openai_configured() -> bool`: Returns `True` if `openai_api_key` is non-empty.
  - `is_cohere_configured() -> bool`: Returns `True` if `cohere_api_key` is non-empty.
  - `get_api_key_status() -> dict[str, bool]`: Returns dictionary map of API key availability.

#### `get_settings() -> Settings`
- **Purpose:** Returns cached singleton instance of `Settings` via `@lru_cache`.
- **Return Value:** `Settings` model instance.

#### `clear_settings_cache() -> None`
- **Purpose:** Resets LRU cache for `get_settings()`, enabling environment variable overrides in unit tests.

---

## 6. Modular Package Layout & Auditor (`src/core/layout.py`)

### Overview
Audits and verifies the existence, completeness, and package initialization of the modular domain package architecture (`api`, `retrieval`, `generation`, `ingestion`, `clients`, `models`, `core`, `cache`) and top-level directories (`src`, `frontend`, `tests`).

### Constants & Functions

#### `REQUIRED_PACKAGES: tuple[str, ...]`
- **Purpose:** Immutable tuple defining mandatory Python domain packages under `src/`.

#### `REQUIRED_DIRECTORIES: tuple[str, ...]`
- **Purpose:** Immutable tuple defining mandatory root project directories.

#### `get_project_root() -> Path`
- **Purpose:** Resolves absolute `Path` to project root directory.

#### `validate_package_layout(base_dir: Path | None = None) -> dict[str, Any]`
- **Purpose:** Programmatically audits presence of required packages, `__init__.py` entry points, and root directories.
- **Return Value:** Structured audit dictionary containing `status`, `is_complete`, `packages`, `directories`, `missing_packages`, `missing_directories`, and `root_path`.

---

## 7. Makefile & Developer Shortcut Auditor (`src/core/makefile.py`)

### Overview
Parses and audits project `Makefile` targets (`help`, `install`, `clean`, `lint`, `format`, `typecheck`, `test`, `dev`, `run`, `docker-build`, `docker-run`) and verifies `.PHONY` declaration compliance.

### Constants & Functions

#### `REQUIRED_MAKEFILE_TARGETS: list[str]`
- **Purpose:** List of mandatory target names required in project Makefile.

#### `parse_makefile_targets(project_root: Path | None = None) -> list[str]`
- **Purpose:** Parses target rule names from `Makefile` via multiline regular expression matching.
- **Parameters:** `project_root` optional root directory path.
- **Return Value:** List of string target names defined in Makefile.

#### `validate_makefile(project_root: Path | None = None) -> dict[str, Any]`
- **Purpose:** Programmatically audits existence of Makefile, target completeness against `REQUIRED_MAKEFILE_TARGETS`, and `.PHONY:` header presence.
- **Return Value:** Audit dictionary containing `valid`, `targets`, `missing_targets`, and `has_phony`.

---

## 8. Docker Infrastructure & Compose Skeleton Auditor (`src/core/docker.py`)

### Overview
Parses and audits `docker-compose.yml` declarations, service configurations (`api`, `qdrant`, `frontend`), port bindings, dependency definitions, volume persistent storage (`qdrant_data`), and associated `Dockerfile` specifications.

### Constants & Functions

#### `REQUIRED_DOCKER_SERVICES: list[str]`
- **Purpose:** List of mandatory container service keys (`api`, `qdrant`, `frontend`) expected in `docker-compose.yml`.

#### `REQUIRED_DOCKER_FILES: list[str]`
- **Purpose:** List of mandatory Docker infrastructure configuration file paths (`Dockerfile`, `docker-compose.yml`, `frontend/Dockerfile`).

#### `REQUIRED_PORT_MAPPINGS: dict[str, list[str]]`
- **Purpose:** Map of required host-to-container port mappings for API (`8000:8000`), Qdrant (`6333:6333`, `6334:6334`), and Frontend (`5173:5173`).

#### `REQUIRED_VOLUMES: list[str]`
- **Purpose:** List of mandatory top-level volume mounts (`qdrant_data`).

#### `parse_docker_compose(project_root: Path | None = None) -> dict[str, Any]`
- **Purpose:** Parses `docker-compose.yml` into a structured Python dictionary using `PyYAML`.
- **Parameters:** `project_root` optional root directory path.
- **Return Value:** Parsed dictionary content of docker-compose file.

#### `validate_docker_setup(project_root: Path | None = None) -> dict[str, Any]`
- **Purpose:** Programmatically audits repository for required Docker files, services, ports, dependencies, and persistent volumes.
- **Return Value:** Structured audit dictionary containing `valid`, `missing_files`, `missing_services`, `missing_volumes`, `services`, and `volumes`.

---

## 9. Base Domain Model & Schema Infrastructure (`src/models/base.py`)

### Overview
Defines `BaseDomainModel`, the foundational immutable base class for all domain DTOs and request/response payloads in the corporate document assistant using Pydantic V2 configuration (`frozen=True`, `extra="forbid"`).

### Classes & Functions

#### `BaseDomainModel(BaseModel)`
- **Purpose:** Abstract base domain schema enforcing immutability, extra field forbidding, enum value extraction, and strict assignment validation.
- **Model Configuration:**
  - `frozen = True`: Enforces model immutability after initialization.
  - `extra = "forbid"`: Rejects undeclared input fields.
  - `use_enum_values = True`: Converts enum members to raw values during serialization.
  - `validate_assignment = True`: Enforces assignment validation.
  - `arbitrary_types_allowed = False`: Requires strict, registered types.

#### `BaseDomainModel.to_dict(self, **kwargs: Any) -> dict[str, Any]`
- **Purpose:** Converts model instance to a standard Python dictionary via Pydantic V2 `model_dump()`.
- **Return Value:** Dictionary representation of model fields.

#### `BaseDomainModel.to_json(self, **kwargs: Any) -> str`
- **Purpose:** Serializes model instance into a JSON string via Pydantic V2 `model_dump_json()`.
- **Return Value:** JSON formatted string payload.

#### `BaseDomainModel.from_dict(cls: type[T], data: dict[str, Any]) -> T`
- **Purpose:** Class method that validates a dictionary payload and returns a typed model instance via Pydantic V2 `model_validate()`.
- **Parameters:** `data` dictionary containing field keys and values.
- **Return Value:** Strongly-typed model instance inheriting from `BaseDomainModel`.

---

## 10. Chunk, Retrieval, and Chat Domain Schemas (`src/models/chunk.py`, `src/models/retrieval.py`, `src/models/chat.py`)

### Overview
Implements concrete domain schemas extending `BaseDomainModel` for document chunk representation, vector/sparse search hit tracking, user query requests, assistant completions with grounded citations, and FinOps telemetry.

### Classes & Submodules

#### `ChunkMetadata(BaseDomainModel)` (`src/models/chunk.py`)
- **Purpose:** Represents metadata metrics for document chunks during parsing and indexing.
- **Fields:** `source_format` (str), `chunk_index` (int, ge=0), `total_chunks` (int, gt=0), `char_count` (int, ge=0), `token_count` (int, ge=0).

#### `ChunkDocument(BaseDomainModel)` (`src/models/chunk.py`)
- **Purpose:** Standardized document chunk schema containing text content and structural metadata.
- **Fields:** `chunk_id` (str), `text` (str), `file_name` (str), `page_number` (int, ge=1), `metadata` (`ChunkMetadata`).

#### `RetrievalResult(BaseDomainModel)` (`src/models/retrieval.py`)
- **Purpose:** Represents retrieved search hit candidates from hybrid vector/sparse indices.
- **Fields:** `chunk_id` (str), `text` (str), `file_name` (str), `page_number` (int, ge=1), `relevance_score` (float), `retrieval_method` (str).

#### `DebugRetrievalHit(BaseDomainModel)` (`src/models/retrieval.py`)
- **Purpose:** Compact per-stage retrieval hit exposing raw score and 1-indexed rank for debug observability.
- **Fields:** `chunk_id` (str), `score` (float), `rank` (int, ge=1), `method` (str: dense/sparse/rrf).

#### `DebugRetrievalResponse(BaseDomainModel)` (`src/models/retrieval.py`)
- **Purpose:** Detailed retrieval debugging payload exposing hits across dense, sparse, RRF fusion, and re-ranking stages.
- **Fields:** `query` (str), `dense_hits` (list[DebugRetrievalHit]), `sparse_hits` (list[DebugRetrievalHit]), `rrf_fused` (list[DebugRetrievalHit]), `final_reranked` (list[RetrievalResult]).

#### `ChatRequest(BaseDomainModel)` (`src/models/chat.py`)
- **Purpose:** User request schema for interaction endpoints.
- **Fields:** `query` (str, min_length=1), `conversation_id` (str, min_length=1), `top_k` (int, default=5, ge=1).

#### `Citation(BaseDomainModel)` (`src/models/chat.py`)
- **Purpose:** Supporting source citation referencing document chunks and pages.
- **Fields:** `file_name` (str), `page_number` (int, ge=1), `chunk_id` (str), `excerpt` (str), `relevance_score` (float).

#### `FinOpsMetadata(BaseDomainModel)` (`src/models/chat.py`)
- **Purpose:** Telemetry tracking token usage, estimated costs, latency, and cache hits.
- **Fields:** `prompt_tokens` (int, ge=0), `completion_tokens` (int, ge=0), `total_tokens` (int, ge=0), `estimated_cost_usd` (float, ge=0.0), `execution_time_seconds` (float, ge=0.0), `is_cached` (bool, default=False).

#### `ChatResponse(BaseDomainModel)` (`src/models/chat.py`)
- **Purpose:** Assistant response schema containing answer text, grounded citations, confidence metrics, and FinOps telemetry.
- **Fields:** `answer` (str), `citations` (list[Citation]), `confidence_score` (float, 0.0..1.0), `grounded` (bool), `latency_ms` (int, ge=0), `finops` (`FinOpsMetadata`).

---

## 11. Domain Exception Hierarchy (`src/core/exceptions.py`)

### Overview
Defines `AppBaseError`, the root exception for all application errors, and its specialized domain subclasses (`ConfigurationError`, `IngestionError`, `RetrievalError`, `GenerationError`) to provide structured error codes, diagnostic metadata payload dictionaries, serialization, and exception shielding across layer boundaries.

### Classes & Functions

#### `AppBaseError(Exception)` (`src/core/exceptions.py`)
- **Purpose:** Root exception for all application domain errors, enabling unified exception handling and structured error payload serialization.
- **Parameters:**
  - `message: str`: Human-readable error message explaining the failure cause.
  - `code: str = "INTERNAL_ERROR"`: Standardized string error code.
  - `details: dict[str, Any] | None = None`: Contextual diagnostic metadata dictionary.
- **Methods:**
  - `to_dict() -> dict[str, Any]`: Serializes error message, code, and details dictionary into a standard representation.
  - `__repr__() -> str`: Returns class name, code, and error message formatting string.

#### `ConfigurationError(AppBaseError)` (`src/core/exceptions.py`)
- **Purpose:** Raised on invalid, missing, or corrupted system configuration parameters.
- **Default Code:** `"CONFIG_ERROR"`.

#### `IngestionError(AppBaseError)` (`src/core/exceptions.py`)
- **Purpose:** Raised during document parsing, text extraction, structural chunking, or ingestion dispatch failures.
- **Default Code:** `"INGESTION_ERROR"`.

#### `RetrievalError(AppBaseError)` (`src/core/exceptions.py`)
- **Purpose:** Raised on vector store search failures, BM25 sparse indexing errors, or RRF candidate fusion failures.
- **Default Code:** `"RETRIEVAL_ERROR"`.

#### `GenerationError(AppBaseError)` (`src/core/exceptions.py`)
- **Purpose:** Raised on LLM generation errors, stream interruptions, or citation extraction and validation failures.
- **Default Code:** `"GENERATION_ERROR"`.

---

## 12. Parsed Document Schemas & PDF Parser (`src/models/document.py`, `src/ingestion/`)

### Overview
Defines structured document domain models (`PageMetadata`, `ParsedPage`, `DocumentMetadata`, `ParsedDocument`) and document parser interfaces (`BaseDocumentParser`, `PDFParser`) supporting PyMuPDF and pdfplumber engines with page-level metadata extraction and exception shielding.

### Classes & Functions

#### `PageMetadata(BaseDomainModel)` (`src/models/document.py`)
- **Purpose:** Represents per-page dimensions, orientation, and content metrics.
- **Fields:** `page_number` (int, ge=1), `width` (float, ge=0.0), `height` (float, ge=0.0), `rotation` (int), `char_count` (int, ge=0), `word_count` (int, ge=0), `image_count` (int, ge=0), `table_count` (int, ge=0).

#### `ParsedPage(BaseDomainModel)` (`src/models/document.py`)
- **Purpose:** Represents an extracted page containing text payload and metadata.
- **Fields:** `page_number` (int, ge=1), `text` (str), `metadata` (`PageMetadata`).

#### `DocumentMetadata(BaseDomainModel)` (`src/models/document.py`)
- **Purpose:** Global document-level metadata header.
- **Fields:** `title` (str | None), `author` (str | None), `subject` (str | None), `keywords` (str | None), `creator` (str | None), `producer` (str | None), `creation_date` (str | None), `mod_date` (str | None), `total_pages` (int, ge=0), `file_size_bytes` (int, ge=0).

#### `ParsedDocument(BaseDomainModel)` (`src/models/document.py`)
- **Purpose:** Canonical structured document representation produced by all document parsers.
- **Fields:** `file_name` (str), `file_path` (str), `source_format` (str), `doc_metadata` (`DocumentMetadata`), `pages` (list[`ParsedPage`]).

#### `BaseDocumentParser(ABC)` (`src/ingestion/base.py`)
- **Purpose:** Abstract interface contract for format-specific document parsers.
- **Methods:**
  - `parse(file_path: str | Path) -> ParsedDocument`: Abstract method that parses a document file into a `ParsedDocument`.

#### `PDFParser(BaseDocumentParser)` (`src/ingestion/pdf_parser.py`)
- **Purpose:** PDF document parser supporting PyMuPDF (`pymupdf`, default) and `pdfplumber` engines with file validation and exception shielding.
- **Parameters:** `engine: str = "pymupdf"` (valid values: `"pymupdf"`, `"pdfplumber"`).
- **Methods:**
  - `parse(file_path: str | Path) -> ParsedDocument`: Validates file existence and size, dispatches to engine-specific parser helper, and returns `ParsedDocument`.
  - `_parse_pymupdf(path: Path) -> ParsedDocument`: Parses PDF via PyMuPDF (fitz), extracting text, dimensions, and image/table metrics.
  - `_parse_pdfplumber(path: Path) -> ParsedDocument`: Parses PDF via pdfplumber, extracting text, layout bounds, and table metrics.

#### `DOCXParser(BaseDocumentParser)` (`src/ingestion/docx_parser.py`)
- **Purpose:** DOCX document parser using `python-docx` with structural element extraction (headings, tables, image counts, page breaks) and exception shielding.
- **Methods:**
  - `parse(file_path: str | Path) -> ParsedDocument`: Validates file path and non-zero size, opens DOCX via python-docx, delegates payload extraction to `_extract_parsed_document`, and wraps exceptions in `IngestionError`.
  - `_extract_parsed_document(path: Path, doc: DocxDocument) -> ParsedDocument`: Extracts document-level metadata, iterates `doc.element.body` OpenXML nodes sequentially, accumulates page content across break boundaries, and returns `ParsedDocument`.
  - `_has_page_break_before(p: Paragraph) -> bool`: Evaluates if paragraph format defines a page break before flag.
  - `_has_page_break_after(p: Paragraph) -> bool`: Evaluates if paragraph contains explicit XML page break elements (`w:type="page"` or `w:lastRenderedPageBreak`).
  - `_format_paragraph(p: Paragraph) -> str`: Normalizes paragraph text and prepends Markdown header levels (`#` to `######`) for heading styles.
  - `_format_table(table: Table) -> str`: Formats table rows into pipe-separated (`|`) plain text representation.

#### `MarkdownParser(BaseDocumentParser)` (`src/ingestion/markdown_parser.py`)
- **Purpose:** Markdown (.md) parser with YAML frontmatter extraction, header title fallback, page-break marker segmentation, image/table metrics calculation, and exception shielding.
- **Methods:**
  - `parse(file_path: str | Path) -> ParsedDocument`: Validates file existence and non-zero size, reads text content, parses frontmatter and body, and returns structured `ParsedDocument`.
  - `_extract_frontmatter(content: str, path: Path) -> tuple[dict[str, Any], str]`: Extracts top-level YAML frontmatter between `---` delimiters using `yaml.safe_load`.
  - `_build_parsed_document(path: Path, fm: dict[str, Any], body: str) -> ParsedDocument`: Constructs `DocumentMetadata` (with header fallback for missing title) and `ParsedPage` sequence.
  - `_count_tables(text: str) -> int`: Counts contiguous Markdown formatted table blocks (`| ... |`).
  - `_get_str(fm: dict[str, Any], key: str) -> str | None`: Safely extracts string values from frontmatter dictionary.

---

## 13. Recursive Structural Chunker (`src/ingestion/recursive_chunker.py`)

### Overview
Implements `RecursiveStructuralChunker` for document ingestion, dividing `ParsedDocument` instances into standardized `ChunkDocument` models (max 512 tokens, 10% overlap) using hierarchical structural splitting (`["\n\n", "\n", ". ", " ", ""]`) while strictly preserving page boundaries.

### Classes & Functions

#### `RecursiveStructuralChunker` (`src/ingestion/recursive_chunker.py`)
- **Purpose:** Hierarchical text chunker enforcing token bounds, overlap ratios, page boundary isolation, and domain exception shielding.
- **Parameters:**
  - `max_tokens: int = 512`: Maximum token capacity per chunk.
  - `overlap_percentage: float = 0.10`: Ratio of chunk capacity prepended from preceding split (default 10% = 51 tokens).
  - `separators: Sequence[str] | None`: Custom sequence of structural delimiters (defaults to `["\n\n", "\n", ". ", " ", ""]`).
- **Methods:**
  - `count_tokens(text: str) -> int`: Calculates BPE token count via `tiktoken` (`cl100k_base`) with an offline density fallback formula `max(word_est, char_est)`.
  - `chunk_document(document: ParsedDocument) -> list[ChunkDocument]`: Processes document page by page, constructs `ChunkDocument` schemas with global 0-indexed positions and metadata metrics.
  - `chunk_page_text(text: str) -> list[str]`: Splits single page text payload using `_recursive_split` and applies boundary overlap via `_apply_overlap`.
  - `_recursive_split(text: str, sep_idx: int) -> list[str]`: Recursively evaluates separator cascade to group text into segments $\le \text{max\_tokens}$.
  - `_hard_split(text: str) -> list[str]`: Fallback slice for unbroken text blocks lacking structural delimiters.
  - `_apply_overlap(splits: list[str]) -> list[str]`: Prepends trailing words from previous split to current split up to `overlap_tokens` capacity.

---

## 14. Ingestion Facade & Format Dispatcher (`src/ingestion/facade.py`)

### Overview
Implements `IngestionFacade` orchestrating document validation, format-specific parser dispatching (`PDFParser`, `DOCXParser`, `MarkdownParser`), parsing into `ParsedDocument`, and chunking into `ChunkDocument` models.

### Classes & Functions

#### `IngestionFacade` (`src/ingestion/facade.py`)
- **Purpose:** Central entry point for document ingestion, enforcing fail-fast file validation, extension-based format dispatching, and single/batch document chunking.
- **Parameters:**
  - `parsers: dict[str, BaseDocumentParser] | None = None`: Optional initial map of file extensions to parser instances (defaults to registering PDF, DOCX, and Markdown parsers).
  - `chunker: RecursiveStructuralChunker | None = None`: Optional chunker instance (defaults to standard `RecursiveStructuralChunker()`).
  - `max_file_size_bytes: int | None = None`: Optional byte limit threshold for input file validation.
- **Methods:**
  - `register_parser(extension: str, parser: BaseDocumentParser) -> None`: Registers a `BaseDocumentParser` instance for a normalized file extension string.
  - `unregister_parser(extension: str) -> None`: Unregisters a parser mapping for the given file extension.
  - `supported_formats() -> list[str]`: Returns a sorted list of registered format extension strings.
  - `get_parser(extension: str) -> BaseDocumentParser`: Retrieves the registered parser for an extension or raises an `UNSUPPORTED_FORMAT` `IngestionError`.
  - `validate_file(file_path: str | Path, format_override: str | None = None) -> Path`: Executes fail-fast checks (existence, file path check, non-zero size, size limit, and supported extension) returning resolved `Path`.
  - `parse_document(file_path: str | Path, format_override: str | None = None) -> ParsedDocument`: Validates document file and parses it into structured `ParsedDocument`.
  - `ingest_document(file_path: str | Path, format_override: str | None = None) -> list[ChunkDocument]`: Validates, parses, and chunks document into a `ChunkDocument` list.
  - `ingest_batch(file_paths: Sequence[str | Path], format_override: str | None = None) -> list[ChunkDocument]`: Validates, parses, and chunks a sequence of files into a flattened `ChunkDocument` list.
  - `ingest_differential(target_paths: Sequence[str | Path] | str | Path, format_override: str | None = None) -> DifferentialResult`: Executes differential scan against manifest, purges deleted file tracking, ingests only new/modified files, updates state manifest, and returns `DifferentialResult`.

---

## 15. Differential Update Handling & State Tracker (`src/ingestion/tracker.py`, `src/models/differential.py`)

### Overview
Provides incremental ingestion functionality by tracking file content hashes and state snapshots in a persistent manifest. Automatically categorizes corpus files into `new_files`, `changed_files`, `deleted_files`, and `unchanged_files`, bypassing redundant document parsing and chunking computations.

### Classes & Schemas

#### `FileState` (`src/models/differential.py`)
- **Purpose:** Immutable state record capturing metadata and content hash for a single ingested document file.
- **Fields:**
  - `file_path: str`: Normalized document file path.
  - `content_hash: str`: SHA-256 binary hash of file contents.
  - `file_size_bytes: int`: File size in bytes.
  - `last_modified: float`: File modification epoch timestamp.
  - `processed_at: str`: ISO 8601 UTC timestamp string when file was processed.
  - `chunk_ids: list[str]`: List of chunk identifiers generated from file.

#### `StateManifest` (`src/models/differential.py`)
- **Purpose:** Repository container persisting a dictionary map of file paths to `FileState` instances.
- **Fields:**
  - `version: str`: Schema version string (default `"1.0.0"`).
  - `last_synced_at: str | None`: ISO 8601 UTC timestamp of last manifest sync.
  - `files: dict[str, FileState]`: Map of normalized file path keys to `FileState` models.

#### `DifferentialDelta` (`src/models/differential.py`)
- **Purpose:** Categorized diff payload summary returned during corpus scanning.
- **Fields:** `new_files: list[str]`, `changed_files: list[str]`, `deleted_files: list[str]`, `unchanged_files: list[str]`.
- **Properties:**
  - `has_changes: bool`: Returns `True` if any new, changed, or deleted files are detected.
  - `files_to_process: list[str]`: Returns concatenated list of `new_files` and `changed_files`.

#### `DifferentialTracker` (`src/ingestion/tracker.py`)
- **Purpose:** Service orchestrating file state hashing, scanning target paths, delta generation, and manifest JSON persistence.
- **Parameters:**
  - `manifest_path: str | Path | None = None`: Optional file path for persisting state manifest JSON.
- **Methods:**
  - `compute_file_hash(file_path: str | Path, chunk_size: int = 65536) -> str`: Computes SHA-256 hash using 64KB chunked binary reads.
  - `scan(target_paths: Sequence[str | Path] | str | Path) -> DifferentialDelta`: Scans target files or directories against stored state manifest to produce categorized `DifferentialDelta`.
  - `update_file_state(file_path: str | Path, chunk_ids: list[str] | None = None) -> FileState`: Computes current file hash/metadata and updates manifest state record.
  - `remove_file_state(file_path: str | Path) -> FileState | None`: Removes tracked file entry from manifest state map.
  - `sync_delta(delta: DifferentialDelta) -> None`: Purges all deleted file entries in `delta.deleted_files` from manifest state.
  - `load_manifest(path: str | Path) -> StateManifest`: Parses manifest JSON file into structured `StateManifest` schema.
  - `save_manifest(path: str | Path | None = None) -> Path`: Serializes current state manifest to formatted JSON file.

---

## 16. Qdrant Vector Store Adapter (`src/retrieval/vector_store.py`)

### Overview
Provides `VectorStoreAdapter` encapsulating Qdrant vector database client operations, including collection lifecycle management, COSINE distance similarity search, 1536-dimensional dense embedding upserts, point metadata filtering, and deletion operations with domain exception shielding.

### Helper Functions & Classes

#### `_to_valid_uuid(id_str: str) -> str` (`src/retrieval/vector_store.py`)
- **Purpose:** Converts arbitrary string chunk keys into valid Qdrant UUID strings via deterministic UUIDv5 namespace mapping.

#### `VectorStoreAdapter` (`src/retrieval/vector_store.py`)
- **Purpose:** Infrastructure adapter wrapping Qdrant database interactions with standardized domain exception handling (`RetrievalError`).
- **Parameters:**
  - `client: QdrantClient | None = None`: Optional pre-configured Qdrant client instance for dependency injection or in-memory testing (`:memory:`).
  - `host: str | None = None`: Hostname for Qdrant server connection (defaults to `Settings.qdrant_host`).
  - `port: int | None = None`: Port number for Qdrant connection (defaults to `Settings.qdrant_port`).
  - `collection_name: str | None = None`: Target vector collection name (defaults to `Settings.qdrant_collection`).
  - `vector_dim: int = 1536`: Dimension capacity for vector embeddings (defaults to 1536).
  - `distance: Distance = Distance.COSINE`: Vector similarity distance metric (defaults to `Distance.COSINE`).
- **Methods:**
  - `collection_exists(collection_name: str | None = None) -> bool`: Evaluates whether the target collection exists in Qdrant.
  - `ensure_collection(collection_name: str | None = None, vector_dim: int | None = None, distance: Distance | None = None, recreate: bool = False) -> bool`: Verifies collection presence and creates configured Qdrant collection if missing or when `recreate=True`.
  - `upsert_chunks(chunks: Sequence[ChunkDocument], embeddings: Sequence[list[float]], collection_name: str | None = None) -> int`: Maps `ChunkDocument` schemas and dense vector embeddings into Qdrant `PointStruct` objects using UUIDv5 keys and upserts them into the collection.
  - `search(query_vector: list[float], top_k: int = 5, collection_name: str | None = None, filter_criteria: dict[str, Any] | None = None) -> list[RetrievalResult]`: Executes similarity search using `query_points`, applies metadata match filters if provided, and maps hits to `RetrievalResult` domain schemas.
  - `get_count(collection_name: str | None = None) -> int`: Returns the total point count contained within the target collection.
  - `delete_points(point_ids: Sequence[str], collection_name: str | None = None) -> bool`: Deletes points by their string chunk keys using UUIDv5 conversion and `PointIdsList` selector.
  - `delete_collection(collection_name: str | None = None) -> bool`: Removes target vector collection from Qdrant if present.

---

## 17. Embedding Client Adapters (`src/clients/`)

### Overview
Provides production-ready vector embedding adapters for multi-provider generation (OpenAI `text-embedding-3-small`, Google Gemini `text-embedding-004`, and deterministic offline `MockEmbeddingAdapter`) with strategy pattern dispatcher `EmbeddingClientAdapter`, automatic payload sub-batching, response index ordering preservation, and domain exception shielding (`RetrievalError`, `ConfigurationError`).

### Infrastructure Classes & Interfaces

#### `BaseEmbeddingAdapter` (`src/clients/base_embedding.py`)
- **Purpose:** Abstract base class defining uniform embedding generation interface and batch partitioning helpers.
- **Abstract Properties & Methods:**
  - `dimension: int`: Vector dimension output capacity.
  - `model_name: str`: Embedding model string identifier.
  - `embed_text(text: str) -> list[float]`: Generates vector embedding for single string input.
  - `embed_batch(texts: Sequence[str], batch_size: int = 100) -> list[list[float]]`: Generates vector embeddings for a sequence of text inputs in sub-batches.
- **Helper Methods:**
  - `_validate_text(text: str) -> str`: Strips whitespace and normalizes text string inputs.
  - `_chunk_batch(texts: Sequence[str], batch_size: int) -> list[list[str]]`: Divides sequence of texts into chunks of `batch_size`.

#### `OpenAIEmbeddingAdapter` (`src/clients/openai_embedding.py`)
- **Purpose:** Adapter encapsulating OpenAI Embeddings API, defaulting to `text-embedding-3-small` with 1536-dimensional vectors.
- **Parameters:**
  - `model_name: str | None = None`: Target OpenAI embedding model (defaults to `Settings.embedding_model`).
  - `api_key: str | None = None`: OpenAI API key (defaults to `Settings.openai_api_key`).
  - `dimension: int | None = None`: Optional output vector dimension.
  - `client: OpenAI | Any | None = None`: Injected client instance for testing.
- **Methods:**
  - `embed_text(text: str) -> list[float]`: Single string vector embedding.
  - `embed_batch(texts: Sequence[str], batch_size: int = 100) -> list[list[float]]`: Batched vector generation with sorting by response `index` field.

#### `GeminiEmbeddingAdapter` (`src/clients/gemini_embedding.py`)
- **Purpose:** Adapter encapsulating Google Gemini Embeddings API (`text-embedding-004`).
- **Parameters:**
  - `model_name: str = "text-embedding-004"`: Target Gemini embedding model identifier.
  - `api_key: str | None = None`: Gemini API key (defaults to `Settings.gemini_api_key`).
  - `dimension: int = 768`: Gemini vector dimension.
  - `client: Any | None = None`: Injected client instance for testing.

#### `MockEmbeddingAdapter` (`src/clients/mock_embedding.py`)
- **Purpose:** Deterministic pseudo-embedding generator using cryptographic hashing for unit testing and offline development.
- **Parameters:**
  - `model_name: str = "mock-embedding-v1"`: Mock model identifier.
  - `dimension: int = 1536`: Target vector dimension size.

#### `EmbeddingClientAdapter` (`src/clients/embedding.py`)
- **Purpose:** Facade dispatcher unifying provider strategy resolution (`openai`, `gemini`, `mock`, `auto`).
- **Parameters:**
  - `provider: str = "openai"`: Target provider strategy name (`openai`, `gemini`, `mock`, `auto`).
  - `model_name: str | None = None`: Target model string identifier.
  - `api_key: str | None = None`: Optional API key override.
  - `dimension: int | None = None`: Vector dimension capacity override.
  - `client: Any | None = None`: Optional pre-configured client object for dependency injection.

---

## 18. BM25 Sparse Index Manager (`src/retrieval/bm25_index.py`, `src/retrieval/bm25_tokenizer.py`)

### Overview
Implements `BM25IndexManager` providing a full sparse retrieval lifecycle (`build`, `search`, `save`, `load`, `clear`) over `rank-bm25`'s `BM25Okapi`. Tokenization is isolated in a pure utility module (`bm25_tokenizer.py`) producing lowercase alphanumeric word tokens. Persistence uses versioned JSON storing the tokenized corpus and `ChunkDocument` metadata, enabling index rebuilds without re-ingesting source documents. Search results are mapped to the existing `RetrievalResult` domain schema with `retrieval_method="sparse"` for downstream RRF fusion.

### Tokenization Utilities (`src/retrieval/bm25_tokenizer.py`)

#### `tokenize(text: str) -> list[str]`
- **Purpose:** Lowercases input text and extracts alphanumeric word tokens via regex `[a-z0-9]+`, stripping punctuation and whitespace.
- **Return Value:** List of lowercase word token strings.

#### `tokenize_corpus(texts: Sequence[str]) -> list[list[str]]`
- **Purpose:** Maps `tokenize` over a sequence of texts to produce the tokenized corpus required by `BM25Okapi`.
- **Return Value:** List of token lists, one per input text.

### BM25 Index Manager (`src/retrieval/bm25_index.py`)

#### `BM25IndexManager` (`src/retrieval/bm25_index.py`)
- **Purpose:** Manages `BM25Okapi` sparse index over a chunk corpus with JSON persistence and domain exception shielding.
- **Parameters:**
  - `k1: float = 1.5`: BM25 term frequency saturation parameter.
  - `b: float = 0.75`: BM25 document length normalization parameter (0-1).
  - `epsilon: float = 0.25`: BM25 IDF epsilon preventing zero IDF for terms in all documents.
- **Properties:**
  - `is_built -> bool`: Returns `True` when `BM25Okapi` exists and the chunk list is non-empty.
  - `size -> int`: Returns the number of indexed chunks.
- **Methods:**
  - `build(chunks: Sequence[ChunkDocument]) -> int`: Stores chunks, tokenizes the corpus, instantiates `BM25Okapi` with configured hyperparameters, and returns the chunk count. Empty corpus leaves the index unbuilt.
  - `search(query: str, top_k: int = 5) -> list[RetrievalResult]`: Raises `RetrievalError` (`BM25_EMPTY_INDEX`) if unbuilt or `RetrievalError` (`INVALID_TOP_K`) if `top_k <= 0`; tokenizes the query; returns `[]` for empty queries; scores via `BM25Okapi.get_scores`; ranks descending; filters zero/negative scores; caps at `top_k`; builds `RetrievalResult` with `retrieval_method="sparse"`.
  - `save(path: str | Path) -> Path`: Serializes `{version, k1, b, epsilon, chunks: [{chunk: model_dump, tokens}]}` to JSON; creates parent directories; wraps `OSError` in `RetrievalError`.
  - `load(path: str | Path) -> int`: Reads JSON; validates version (`_INDEX_VERSION = 1`); restores hyperparameters; Pydantic-validates chunks via `ChunkDocument.model_validate()`; rebuilds `BM25Okapi`; returns chunk count. Wraps `OSError`/`JSONDecodeError` in `RetrievalError`; raises `BM25_INVALID_VERSION` for unsupported versions.
  - `clear() -> None`: Resets chunks, tokenized corpus, and `BM25Okapi` to empty state.

### Package Exports (`src/retrieval/__init__.py`)
- **Purpose:** Exposes `BM25IndexManager`, `VectorStoreAdapter`, `tokenize`, and `tokenize_corpus` as the public retrieval package API.

### Unit Test Verification Suite (`tests/unit/test_bm25_index.py`)
- **Test Modules:**
  - `test_tokenize_lowercase_alphanumeric`: Verifies lowercasing and punctuation stripping.
  - `test_tokenize_corpus`: Verifies corpus tokenization output shape.
  - `test_build_index_and_size`: Verifies build sets `size` and `is_built`.
  - `test_build_empty_corpus`: Verifies empty corpus leaves index unbuilt.
  - `test_search_returns_sparse_hits`: Verifies ranked sparse `RetrievalResult` hits.
  - `test_search_top_k_limit`: Verifies `top_k` caps returned hits.
  - `test_search_empty_query`: Verifies empty queries return `[]`.
  - `test_search_before_build_raises`: Verifies `BM25_EMPTY_INDEX` error.
  - `test_search_invalid_top_k`: Verifies `INVALID_TOP_K` error.
  - `test_save_and_load_roundtrip`: Verifies save/load preserves corpus and search behavior.
  - `test_save_empty_index`: Verifies empty index persistence roundtrip.
  - `test_load_missing_file_raises`: Verifies missing-file `RetrievalError`.
  - `test_load_invalid_version_raises`: Verifies `BM25_INVALID_VERSION` error.
  - `test_clear_resets_state`: Verifies clear resets index state.
- **Runner Registration:** `test_run_project_tests_bm25_index_suite` in `tests/unit/test_runner.py`.

---

## 19. Indexing Orchestrator (`src/retrieval/indexing_orchestrator.py`)

### Overview
Implements `IndexingOrchestrator`, the coordination layer for the dual-indexing workflow (Phase 4.4). It composes the existing single-responsibility components — `BaseEmbeddingAdapter` (batch embedding), `VectorStoreAdapter` (Qdrant upsert), and `BM25IndexManager` (sparse index) — into one typed, fail-fast operation. It returns an immutable `IndexingResult` summary and enforces boundary validation (embedding count and dimension) before any I/O.

### Result Model

#### `IndexingResult` (frozen dataclass)
- **Purpose:** Immutable summary of a completed indexing operation.
- **Fields:**
  - `chunk_count: int`: Number of input chunks processed.
  - `vector_count: int`: Number of vectors upserted into Qdrant.
  - `bm25_count: int`: Number of chunks indexed in the BM25 index.
  - `collection_name: str`: Target Qdrant collection name.
  - `bm25_path: Path | None = None`: Optional persisted BM25 index path.

### Orchestrator Class

#### `IndexingOrchestrator` (`src/retrieval/indexing_orchestrator.py`)
- **Purpose:** Coordinates embedding, vector upsert, and BM25 index build for a chunk corpus.
- **Parameters:**
  - `embedding_adapter: BaseEmbeddingAdapter`: Embedding provider adapter.
  - `vector_store: VectorStoreAdapter`: Qdrant vector store adapter.
  - `bm25_index: BM25IndexManager | None = None`: Sparse index manager (defaults to a new `BM25IndexManager()`).
  - `batch_size: int = 100`: Embedding sub-batch size (clamped to a minimum of 1).
- **Methods:**
  - `index_chunks(chunks: Sequence[ChunkDocument], collection_name: str | None = None, bm25_path: str | Path | None = None) -> IndexingResult`: Coerces chunks to a list, resolves the target collection, returns a zeroed `IndexingResult` for empty input, batch-embeds chunk texts, validates embedding count (`EMBEDDING_COUNT_MISMATCH`) and dimension (`EMBEDDING_DIM_MISMATCH`), ensures the collection, upserts vectors, builds the BM25 index, optionally persists it, and returns the summary.
  - `_validate_dimension(embeddings: Sequence[Sequence[float]]) -> None`: Iterates embeddings and raises `RetrievalError` on the first dimension mismatch with index/expected/actual details.

### Package Exports (`src/retrieval/__init__.py`)
- **Purpose:** Exposes `IndexingOrchestrator` and `IndexingResult` alongside `BM25IndexManager`, `VectorStoreAdapter`, `tokenize`, and `tokenize_corpus`.

### Unit Test Verification Suite (`tests/unit/test_indexing_orchestrator.py`)
- **Test Modules:**
  - `test_index_empty_chunks_returns_empty_result`: Verifies empty input is a no-op returning zeroed counts.
  - `test_index_chunks_embeds_upserts_and_builds_bm25`: Verifies full flow populates vectors and BM25 index.
  - `test_index_chunks_saves_bm25_path`: Verifies BM25 persistence roundtrip and search parity.
  - `test_index_chunks_collection_override`: Verifies custom collection name is honored.
  - `test_index_chunks_embedding_count_mismatch_raises`: Verifies `EMBEDDING_COUNT_MISMATCH` error.
  - `test_index_chunks_dimension_mismatch_raises`: Verifies `EMBEDDING_DIM_MISMATCH` error.
- **Runner Registration:** Auto-registered via `tests/runner.py` (pytest on `tests/`).

---

## 20. Dense Vector Search Service (`src/retrieval/dense_search.py`)

### Overview
Implements `DenseSearchService`, the query-time dense retrieval stage of the hybrid engine (Phase 5.1). It embeds a user query via `BaseEmbeddingAdapter`, validates the query and embedding dimension, verifies the target Qdrant collection exists, and delegates the top-k cosine search to `VectorStoreAdapter.search()`. The default candidate pool is 50 (`DENSE_TOP_K_DEFAULT`), satisfying the roadmap requirement for dense retrieval before RRF fusion.

### Module Constant

#### `DENSE_TOP_K_DEFAULT = 50`
- **Purpose:** Default number of dense candidate hits fetched from Qdrant for downstream RRF fusion.

### Service Class

#### `DenseSearchService` (`src/retrieval/dense_search.py`)
- **Purpose:** Encapsulates dense retrieval: query embedding + top-k Qdrant cosine search with fail-fast validation.
- **Parameters:**
  - `embedding_adapter: BaseEmbeddingAdapter`: Embedding provider adapter used to vectorize the query.
  - `vector_store: VectorStoreAdapter`: Qdrant vector store adapter for similarity search.
  - `top_k: int = DENSE_TOP_K_DEFAULT`: Default candidate limit (clamped to a minimum of 1).
- **Methods:**
  - `search(query: str, top_k: int | None = None, collection_name: str | None = None, filter_criteria: dict[str, str] | None = None) -> list[RetrievalResult]`: Validates the query is non-empty (`EMPTY_QUERY`), resolves `target_top_k = max(1, top_k or self.top_k)`, embeds the query text (wrapping provider failures in `RetrievalError`), validates the embedding dimension matches the vector store (`QUERY_DIM_MISMATCH`), verifies the collection exists (`COLLECTION_NOT_FOUND`), delegates to `vector_store.search()`, and returns ranked `RetrievalResult` hits with `retrieval_method="dense"`.

### Package Exports (`src/retrieval/__init__.py`)
- **Purpose:** Exposes `DenseSearchService` and `DENSE_TOP_K_DEFAULT` alongside `BM25IndexManager`, `IndexingOrchestrator`, `IndexingResult`, `VectorStoreAdapter`, `tokenize`, and `tokenize_corpus`.

### Unit Test Verification Suite (`tests/unit/test_dense_search.py`)
- **Test Modules:**
  - `test_default_top_k_constant`: Verifies `DENSE_TOP_K_DEFAULT == 50`.
  - `test_init_defaults_and_clamping`: Verifies default top_k and clamping of non-positive values to 1.
  - `test_search_returns_dense_hits_top_k`: Verifies dense hits with `retrieval_method="dense"`.
  - `test_search_returns_up_to_top_50`: Verifies search caps at 50 hits.
  - `test_search_empty_query_raises`: Verifies `EMPTY_QUERY` error.
  - `test_search_collection_missing_raises`: Verifies `COLLECTION_NOT_FOUND` error.
  - `test_search_dimension_mismatch_raises`: Verifies `QUERY_DIM_MISMATCH` error.
  - `test_search_embedding_failure_wrapped`: Verifies embedding provider failures are wrapped as `RetrievalError`.
  - `test_search_passes_filter_criteria`: Verifies filter criteria are forwarded to the vector store.
  - `test_search_returns_custom_collection_hits`: Verifies custom collection name is honored.
- **Runner Registration:** Auto-registered via `tests/runner.py` (pytest on `tests/`).

---

## 21. Sparse BM25 Search Service (`src/retrieval/sparse_search.py`)

### Overview
Implements `SparseSearchService`, the query-time sparse retrieval stage of the hybrid engine (Phase 5.2). It validates the user query, resolves the top-k limit, verifies the BM25 index is built, and delegates scoring to `BM25IndexManager.search()`. The default candidate pool is 50 (`SPARSE_TOP_K_DEFAULT`), satisfying the roadmap requirement for sparse retrieval before RRF fusion.

### Module Constant

#### `SPARSE_TOP_K_DEFAULT = 50`
- **Purpose:** Default number of sparse candidate hits fetched from the BM25 index for downstream RRF fusion.

### Service Class

#### `SparseSearchService` (`src/retrieval/sparse_search.py`)
- **Purpose:** Encapsulates sparse retrieval: BM25 scoring over the tokenized corpus with fail-fast validation.
- **Parameters:**
  - `bm25_index: BM25IndexManager`: Sparse index manager owning the tokenized corpus and BM25Okapi scoring.
  - `top_k: int = SPARSE_TOP_K_DEFAULT`: Default candidate limit (clamped to a minimum of 1).
- **Methods:**
  - `search(query: str, top_k: int | None = None) -> list[RetrievalResult]`: Validates the query is non-empty (`EMPTY_QUERY`), resolves `target_top_k = max(1, top_k or self.top_k)`, verifies the index is built (`BM25_EMPTY_INDEX`), delegates to `bm25_index.search(query, top_k=target_top_k)`, logs `sparse_search_completed`, and returns ranked `RetrievalResult` hits with `retrieval_method="sparse"`.

### Package Exports (`src/retrieval/__init__.py`)
- **Purpose:** Exposes `SparseSearchService` and `SPARSE_TOP_K_DEFAULT` alongside `BM25IndexManager`, `DenseSearchService`, `DENSE_TOP_K_DEFAULT`, `IndexingOrchestrator`, `IndexingResult`, `VectorStoreAdapter`, `tokenize`, and `tokenize_corpus`.

### Unit Test Verification Suite (`tests/unit/test_sparse_search.py`)
- **Test Modules:**
  - `test_default_top_k_constant`: Verifies `SPARSE_TOP_K_DEFAULT == 50`.
  - `test_init_defaults_and_clamping`: Verifies default top_k and clamping of non-positive values to 1.
  - `test_search_returns_sparse_hits_top_k`: Verifies sparse hits with `retrieval_method="sparse"`.
  - `test_search_returns_up_to_top_50`: Verifies search caps at 50 hits.
  - `test_search_empty_query_raises`: Verifies `EMPTY_QUERY` error.
  - `test_search_unbuilt_index_raises`: Verifies `BM25_EMPTY_INDEX` error.
  - `test_search_custom_top_k_overrides_default`: Verifies per-call `top_k` overrides configured default.
  - `test_search_returns_custom_top_k_hits`: Verifies custom `top_k` returns exactly that many hits when available.
- **Runner Registration:** `test_run_project_tests_sparse_search_suite` in `tests/unit/test_runner.py`.

---

## 22. Reciprocal Rank Fusion Service (`src/retrieval/rrf_fusion.py`)

### Overview
Implements `RRFusionService`, the hybrid fusion stage of Phase 5.3. It merges the top-50 dense vector hits (`DenseSearchService`) and top-50 sparse BM25 hits (`SparseSearchService`) into a single fused ranking using the Reciprocal Rank Fusion formula `score = Σ 1/(k + rank)` with default rank constant `k=60`. Output is a `RetrievalResult` list marked with `retrieval_method="rrf"`, ready for the Phase 5.4 debug payload and the Phase 6 re-ranker.

### Module Constants

#### `RRF_K_DEFAULT = 60`
- **Purpose:** Default rank-smoothing constant in the RRF formula `1/(k + rank)`, dampening the dominance of top-ranked hits.

#### `RRF_TOP_K_DEFAULT = 50`
- **Purpose:** Default fused output limit, matching dense and sparse candidate pool sizes for balanced fusion.

#### `RRF_METHOD = "rrf"`
- **Purpose:** `retrieval_method` marker stamped on fused `RetrievalResult` instances to distinguish them from dense/sparse hits in debug payloads.

### Service Class

#### `RRFusionService` (`src/retrieval/rrf_fusion.py`)
- **Purpose:** Fuses multiple ranked result lists via reciprocal rank scores, deterministically and score-calibration-agnostically.
- **Parameters:**
  - `k: int = RRF_K_DEFAULT`: Rank constant in the reciprocal-rank formula (clamped to a minimum of 1).
  - `top_k: int = RRF_TOP_K_DEFAULT`: Default fused output limit (clamped to a minimum of 1).
- **Methods:**
  - `fuse(dense_hits: list[RetrievalResult], sparse_hits: list[RetrievalResult], top_k: int | None = None) -> list[RetrievalResult]`: Resolves `target_top_k = max(1, top_k or self.top_k)`; fast-paths empty inputs (both lists empty -> `[]`); iterates `(dense_hits, "dense")` then `(sparse_hits, "sparse")`, accumulating `score[chunk_id] += 1/(k + rank)` for each 1-based rank; stores first-seen payload per `chunk_id` with dense payload overwriting sparse on duplicates; sorts chunk IDs by `(-score, chunk_id)`, slices to `target_top_k`, builds fused `RetrievalResult` items with `relevance_score = score` and `retrieval_method = "rrf"`, logs `rrf_fusion_completed`, and returns the fused list.

### Fuse Flow
```text
fuse(dense_hits, sparse_hits, top_k=None)
  -> target_top_k = max(1, top_k or self.top_k)
  -> if not dense_hits and not sparse_hits: log rrf_no_hits; return []
  -> for (hits, method) in ((dense_hits, "dense"), (sparse_hits, "sparse")):
       for rank, hit in enumerate(hits, start=1):
         scores[hit.chunk_id] += 1.0 / (k + rank)
         payloads[hit.chunk_id] = hit  # dense overwrites sparse on duplicate
  -> ranked_ids = sorted(scores.keys(), key=lambda cid: (-scores[cid], cid))[:target_top_k]
  -> fused = [RetrievalResult(chunk_id, text, file_name, page_number, scores[cid], "rrf") for cid in ranked_ids]
  -> log rrf_fusion_completed(dense_hits, sparse_hits, len(fused)); return fused
```

### Package Exports (`src/retrieval/__init__.py`)
- **Purpose:** Exposes `RRFusionService`, `RRF_K_DEFAULT`, `RRF_TOP_K_DEFAULT`, and `RRF_METHOD` alongside `BM25IndexManager`, `DenseSearchService`, `SparseSearchService`, `IndexingOrchestrator`, `IndexingResult`, `VectorStoreAdapter`, `tokenize`, and `tokenize_corpus`.

### Unit Test Verification Suite (`tests/unit/test_rrf_fusion.py`)
- **Test Modules:**
  - `test_default_constants`: Verifies `RRF_K_DEFAULT == 60`, `RRF_TOP_K_DEFAULT == 50`, `RRF_METHOD == "rrf"`.
  - `test_init_defaults_and_clamping`: Verifies default `k`/`top_k` and clamping of non-positive values to 1.
  - `test_fuse_merges_and_ranks_by_rrf_score`: Verifies shared hits rank higher and unique hits are preserved.
  - `test_fuse_uses_reciprocal_rank_formula`: Verifies fused score equals `1/(k+rank)` summed across lists.
  - `test_fuse_returns_top_k`: Verifies fused output is limited to configured `top_k`.
  - `test_fuse_custom_top_k_overrides_default`: Verifies per-call `top_k` overrides configured default.
  - `test_fuse_empty_lists_returns_empty`: Verifies two empty lists return `[]`.
  - `test_fuse_single_list_only`: Verifies fusion works with a single non-empty list.
  - `test_fuse_dense_payload_preferred_on_duplicate`: Verifies dense payload is used when a chunk appears in both lists.
- **Runner Registration:** `test_run_project_tests_rrf_fusion_suite` in `tests/unit/test_runner.py`.

---

## 23. Retrieval Debug Data Structure & Builder (`src/models/retrieval.py`, `src/retrieval/debug_retrieval.py`)

### Overview
Implements the Phase 5.4 retrieval debug data structure (specification FR-09). A compact `DebugRetrievalHit` model exposes raw dense scores, sparse BM25 scores, and fused RRF ranks per stage. A `DebugRetrievalBuilder` service orchestrates the existing `DenseSearchService`, `SparseSearchService`, and `RRFusionService` into a `DebugRetrievalResponse` payload for the `/api/v1/debug/retrieval` endpoint.

### Debug Models (`src/models/retrieval.py`)

#### `DebugRetrievalHit(BaseDomainModel)`
- **Purpose:** Compact per-stage retrieval hit exposing raw score and 1-indexed rank for observability.
- **Fields:** `chunk_id` (str), `score` (float), `rank` (int, ge=1), `method` (str: dense/sparse/rrf).

#### `DebugRetrievalResponse(BaseDomainModel)`
- **Purpose:** Debug payload exposing dense scores, sparse scores, and fused RRF ranks.
- **Fields:**
  - `query` (str): Original user search query.
  - `dense_hits` (list[DebugRetrievalHit]): Dense vector hits with raw scores.
  - `sparse_hits` (list[DebugRetrievalHit]): Sparse BM25 hits with raw scores.
  - `rrf_fused` (list[DebugRetrievalHit]): RRF fused hits with fused ranks.
  - `final_reranked` (list[RetrievalResult]): Final reranked hits (empty until Phase 6).

### Debug Builder Service (`src/retrieval/debug_retrieval.py`)

#### `_to_debug_hits(hits: list[RetrievalResult], method: str) -> list[DebugRetrievalHit]`
- **Purpose:** Pure helper converting ranked `RetrievalResult` lists into compact `DebugRetrievalHit` lists with 1-indexed ranks.
- **Return Value:** List of `DebugRetrievalHit` instances.

#### `DebugRetrievalBuilder` (`src/retrieval/debug_retrieval.py`)
- **Purpose:** Orchestrates dense search, sparse search, and RRF fusion to assemble a `DebugRetrievalResponse`.
- **Parameters:**
  - `dense_search: DenseSearchService`: Dense retrieval service.
  - `sparse_search: SparseSearchService`: Sparse BM25 retrieval service.
  - `rrf_fusion: RRFusionService`: RRF fusion service.
- **Methods:**
  - `build(query: str, dense_top_k: int | None = None, sparse_top_k: int | None = None, rrf_top_k: int | None = None) -> DebugRetrievalResponse`: Runs dense search, sparse search, RRF fusion, converts each stage to `DebugRetrievalHit` lists, and returns a `DebugRetrievalResponse`. `final_reranked` is left empty until Phase 6.

### Build Flow
```text
DebugRetrievalBuilder.build(query, dense_top_k=None, sparse_top_k=None, rrf_top_k=None)
  -> dense_hits = dense_search.search(query, top_k=dense_top_k)
  -> sparse_hits = sparse_search.search(query, top_k=sparse_top_k)
  -> fused_hits = rrf_fusion.fuse(dense_hits, sparse_hits, top_k=rrf_top_k)
  -> response = DebugRetrievalResponse(
       query=query,
       dense_hits=_to_debug_hits(dense_hits, "dense"),
       sparse_hits=_to_debug_hits(sparse_hits, "sparse"),
       rrf_fused=_to_debug_hits(fused_hits, "rrf"),
     )
  -> log debug_retrieval_built; return response
```

### Package Exports
- **`src/models/__init__.py`:** Exposes `DebugRetrievalHit` alongside `DebugRetrievalResponse` and `RetrievalResult`.
- **`src/retrieval/__init__.py`:** Exposes `DebugRetrievalBuilder` alongside `DenseSearchService`, `SparseSearchService`, `RRFusionService`, and other retrieval components.

### Unit Test Verification Suite
- **`tests/unit/test_debug_retrieval_and_finops.py`:** Validates `DebugRetrievalHit` rank constraint (ge=1) and immutability; `DebugRetrievalResponse` defaults, serialization roundtrip, and immutability; `FinOpsMetadata` boundaries.
- **`tests/unit/test_debug_retrieval_builder.py`:** Validates builder populates all stage hits, forwards per-stage `top_k` parameters, and handles empty pipeline.
- **`tests/unit/test_domain_schemas.py`:** Updated to use `DebugRetrievalHit` for dense/rrf fields in `DebugRetrievalResponse`.
- **Runner Registration:** `test_run_project_tests_debug_retrieval_builder_suite` in `tests/unit/test_runner.py`.

---

## 24. FlashRank Cross-Encoder Reranker Adapters (`src/clients/base_reranker.py`, `src/clients/flashrank_reranker.py`, `src/clients/mock_reranker.py`, `src/clients/reranker.py`)

### Overview
Implements Phase 6.1 cross-encoder reranking adapters. An abstract base interface (`BaseRerankerAdapter`) defines the reranking contract. `FlashRankRerankerAdapter` provides CPU-optimized local ONNX cross-encoder scoring, reducing the top 30 hybrid RRF fused candidates down to top 5 high-relevance chunks for context injection. `MockRerankerAdapter` enables deterministic offline testing. `create_reranker_adapter` provides factory instantiation based on configuration settings.

### Base Interface (`src/clients/base_reranker.py`)

#### `BaseRerankerAdapter(ABC)`
- **Purpose:** Abstract interface for cross-encoder reranking providers.
- **Abstract Methods & Properties:**
  - `rerank(query: str, hits: Sequence[RetrievalResult], candidate_k: int | None = None, top_k: int | None = None) -> list[RetrievalResult]`: Reranks candidate hits using cross-encoder scoring.
  - `model_name -> str`: Returns cross-encoder model identifier.
  - `provider_name -> str`: Returns provider identifier.

### Concrete Adapters (`src/clients/flashrank_reranker.py`, `src/clients/mock_reranker.py`)

#### `FlashRankRerankerAdapter(BaseRerankerAdapter)`
- **Purpose:** Local ONNX cross-encoder adapter for re-ranking hybrid search candidates.
- **Parameters:**
  - `model_name: str = "ms-marco-MiniLM-L-6-v2"`: Requested cross-encoder model name.
  - `candidate_k: int = 30`: Default candidate truncation window size.
  - `top_k: int = 5`: Default output count returned by adapter.
  - `cache_dir: str | None = None`: Optional model cache directory.
  - `ranker_instance: Any | None = None`: Optional pre-instantiated FlashRank `Ranker` object.
- **Methods:**
  - `rerank(query: str, hits: Sequence[RetrievalResult], candidate_k: int | None = None, top_k: int | None = None) -> list[RetrievalResult]`: Truncates hits to candidate_k (30), formats passage payloads, executes FlashRank pairwise ONNX cross-encoder scoring, and returns top_k (5) reranked `RetrievalResult` objects sorted in descending score order.

#### `MockRerankerAdapter(BaseRerankerAdapter)`
- **Purpose:** Mock reranker adapter returning deterministic relevance scores for fast offline unit testing.
- **Methods:**
  - `rerank(query: str, hits: Sequence[RetrievalResult], candidate_k: int | None = None, top_k: int | None = None) -> list[RetrievalResult]`: Computes deterministic word-overlap scores over candidates and returns top_k results.

#### `CohereRerankerAdapter(BaseRerankerAdapter)`
- **Purpose:** Cohere Rerank API adapter supporting cloud-based cross-encoder candidate reranking (`src/clients/cohere_reranker.py`).
- **Parameters:**
  - `model_name: str = "rerank-v3.5"`: Cohere rerank model identifier.
  - `api_key: str | None = None`: Optional Cohere API key (falls back to `Settings.cohere_api_key`).
  - `candidate_k: int = 30`: Default candidate truncation window size.
  - `top_k: int = 5`: Default output reranked hit count.
  - `client: Any | None = None`: Optional pre-instantiated SDK client or mock client.
  - `httpx_client: httpx.Client | None = None`: Optional pre-configured HTTP client for direct API requests.
- **Methods:**
  - `rerank(query: str, hits: Sequence[RetrievalResult], candidate_k: int | None = None, top_k: int | None = None) -> list[RetrievalResult]`: Truncates hits to top candidate_k (30), passes document text payload to Cohere Rerank API (`v2/rerank`), maps returned relevance scores back to `RetrievalResult` objects with `retrieval_method="cohere"`, and returns top_k (5) results sorted descending.

### Adapter Factory (`src/clients/reranker.py`)

#### `create_reranker_adapter(provider: str = "flashrank", model_name: str | None = None, candidate_k: int = 30, top_k: int = 5, **kwargs: Any) -> BaseRerankerAdapter`
- **Purpose:** Factory function instantiating the requested reranker adapter ("flashrank", "cohere", or "mock").

### Reranking Flow
```text
FlashRankRerankerAdapter.rerank(query, hits, candidate_k=30, top_k=5)
  -> candidate_hits = hits[:candidate_k] (top 30)
  -> passages = [{"id": hit.chunk_id, "text": hit.text, "meta": {...}} for hit in candidate_hits]
  -> raw_results = self._ranker.rerank(RerankRequest(query=clean_query, passages=passages))
  -> reranked_results = [RetrievalResult(chunk_id=item["id"], score=item["score"], retrieval_method="flashrank") for item in raw_results[:top_k]]
  -> return sorted reranked_results[:top_k]

CohereRerankerAdapter.rerank(query, hits, candidate_k=30, top_k=5)
  -> candidate_hits = hits[:candidate_k] (top 30)
  -> documents = [hit.text for hit in candidate_hits]
  -> raw_results = self._call_cohere_api(clean_query, documents, top_n=top_k)
  -> reranked_results = [RetrievalResult(chunk_id=candidate_hits[idx].chunk_id, score=item["relevance_score"], retrieval_method="cohere") for item in raw_results[:top_k]]
  -> return sorted reranked_results[:top_k]
```

### Package Exports & Registration
- **`src/clients/__init__.py`:** Exports `BaseRerankerAdapter`, `FlashRankRerankerAdapter`, `CohereRerankerAdapter`, `MockRerankerAdapter`, and `create_reranker_adapter`.
- **Runner Registration:** `test_run_project_tests_flashrank_reranker_suite` and `test_run_project_tests_cohere_reranker_suite` in `tests/unit/test_runner.py`.

---

## 25. Reranker Domain Service (`src/retrieval/reranker_service.py`)

### Overview
Implements Phase 6.3 cross-encoder re-ranking service utilizing a primary/fallback strategy pattern. Encapsulates primary (local CPU FlashRank ONNX) and secondary (cloud Cohere Rerank API or offline Mock) adapters. Seamlessly degrades on inference failures or missing credentials while shielding upstream caller code from provider-specific exceptions. Integrated with `DebugRetrievalBuilder` to populate the `final_reranked` search stage.

### `RerankerService`

#### `RerankerService(primary_adapter: BaseRerankerAdapter | None = None, fallback_adapter: BaseRerankerAdapter | None = None, candidate_k: int | None = None, top_k: int | None = None, auto_fallback: bool = True)`
- **Purpose:** Service orchestrating candidate passage re-ranking across primary and fallback strategy adapters.
- **Parameters:**
  - `primary_adapter`: Primary cross-encoder adapter instance (defaults to Settings reranker provider).
  - `fallback_adapter`: Fallback cross-encoder adapter instance (defaults to Cohere or Mock).
  - `candidate_k`: Candidate truncation window limit (defaults to `settings.reranker_candidate_k`).
  - `top_k`: Top re-ranked candidate output limit (defaults to `settings.reranker_top_k`).
  - `auto_fallback`: Boolean flag enabling automatic fallback strategy invocation when primary fails.
- **Methods:**
  - `_safe_create_adapter(provider: str, **kwargs: Any) -> BaseRerankerAdapter | None`: Safely instantiates reranker adapter, returning `None` on configuration or dependency error.
  - `rerank(query: str, hits: Sequence[RetrievalResult], candidate_k: int | None = None, top_k: int | None = None) -> list[RetrievalResult]`: Executes re-ranking attempt on primary adapter. If primary raises an exception and `auto_fallback` is enabled, catches error and dispatches to fallback adapter. Raises `RetrievalError` if all adapters fail.

### Execution Flow
```text
RerankerService.rerank(query, hits)
  ├── 1. Validate inputs (empty/blank query or empty hits -> return [])
  ├── 2. Attempt primary_adapter.rerank()
  │     ├── Success -> return primary reranked results
  │     └── Exception -> log warning ("rerank_primary_failed_attempting_fallback")
  ├── 3. If auto_fallback is True and fallback_adapter is available:
  │     ├── Attempt fallback_adapter.rerank()
  │     ├── Success -> return fallback reranked results
  │     └── Exception -> raise RetrievalError(code="RERANK_ALL_FAILED")
  └── 4. If fallback disabled or unavailable -> raise RetrievalError
```

### Package Exports & Registration
- **`src/retrieval/__init__.py`:** Exports `RerankerService`.
- **Runner Registration:** `test_run_project_tests_reranker_service_suite` in `tests/unit/test_runner.py`.

---

## 26. Confidence Guard Service & Domain Schemas (`src/retrieval/confidence_guard.py`)

### Overview
Implements Phase 6.4 confidence guard gating layer. Intercepts cross-encoder reranked search hits prior to generative LLM execution, evaluating top candidate relevance against a calibrated minimum score cutoff ($S_{\text{min}} \ge 0.35$). Short-circuits low-confidence or out-of-corpus queries with an ungrounded refusal response payload (`"I cannot answer this question based on the available documentation."`), bypassing generative LLM token consumption and eliminating hallucination risk.

### Domain Schema (`src/models/retrieval.py`)

#### `ConfidenceDecision`
- **Purpose:** Pydantic schema representing the outcome of confidence threshold evaluation.
- **Fields:**
  - `passed: bool`: `True` if highest candidate hit score meets or exceeds $S_{\text{min}}$ cutoff threshold.
  - `top_score: float`: Highest relevance score among retrieved search hit candidates.
  - `threshold: float`: Calibrated confidence cutoff threshold applied during evaluation.
  - `filtered_hits: list[RetrievalResult]`: List of candidate search hits meeting or exceeding threshold.
  - `refusal_message: str`: Standardized corporate refusal disclaimer string.

### Confidence Guard Service (`src/retrieval/confidence_guard.py`)

#### `ConfidenceGuard`
- **Purpose:** Service orchestrating confidence gating, hit filtering, and refusal response payload construction.
- **Constants:**
  - `DEFAULT_REFUSAL_RESPONSE: str = "I cannot answer this question based on the available documentation."`
  - `DEFAULT_CONFIDENCE_THRESHOLD: float = 0.35`
- **Methods:**
  - `__init__(threshold: float | None = None, refusal_message: str | None = None)`: Initializes guard with configured threshold (clamped to $[0.0, 1.0]$) and refusal message disclaimer.
  - `is_confident(hits: Sequence[RetrievalResult]) -> bool`: Evaluates whether candidate hits list is non-empty and contains at least one hit with `relevance_score >= threshold`.
  - `filter_hits(hits: Sequence[RetrievalResult]) -> list[RetrievalResult]`: Filters candidate hits to return only those with `relevance_score >= threshold`.
  - `evaluate(hits: Sequence[RetrievalResult]) -> ConfidenceDecision`: Computes top relevance score, evaluates gating condition, filters valid candidate hits, logs telemetry, and returns structured `ConfidenceDecision`.
  - `create_refusal_response(top_score: float = 0.0, latency_ms: int = 0) -> ChatResponse`: Constructs standard refusal `ChatResponse` payload (`grounded=False`, `citations=[]`, clamped `confidence_score`, zero-token `FinOpsMetadata`).

### Execution & Gating Flow
```text
ConfidenceGuard.evaluate(hits)
  ├── 1. Extract top_score = max(hit.relevance_score) or 0.0
  ├── 2. Check passed = is_confident(hits) -> (top_score >= threshold)
  ├── 3. If passed:
  │     └── filtered_hits = filter_hits(hits)  (relevance_score >= S_min)
  ├── 4. If failed:
  │     └── filtered_hits = []
  ├── 5. Log structlog event "confidence_guard_evaluated"
  └── 6. Return ConfidenceDecision(passed, top_score, threshold, filtered_hits, refusal_message)

ConfidenceGuard.create_refusal_response(top_score, latency_ms)
  ├── 1. Clamp score to [0.0, 1.0]
  ├── 2. Convert latency_ms to execution_time_seconds
  └── 3. Return ChatResponse(
           answer=refusal_message,
           citations=[],
           confidence_score=clamped_score,
           grounded=False,
           latency_ms=latency_ms,
           finops=FinOpsMetadata(tokens=0, cost=0.0, is_cached=False)
         )
```

### Package Exports & Registration
- **`src/retrieval/__init__.py`:** Exports `ConfidenceGuard`, `DEFAULT_CONFIDENCE_THRESHOLD`, and `DEFAULT_REFUSAL_RESPONSE`.
- **Runner Registration:** `test_run_project_tests_confidence_guard_suite` in `tests/unit/test_runner.py`.

---

## 27. Grounded LLM Generation Service (`src/generation/engine.py`)

### Overview
Implements Phase 7.1 grounded LLM generation service. Enforces context-only grounding via a strict corporate assistant system prompt, zero sampling temperature ($T=0.0$), and `AsyncGenerator` streaming token completion. Short-circuits empty context inputs with an immediate refusal response string (`"I cannot answer this question based on the available documentation."`), preventing unnecessary LLM API calls and eliminating hallucination leakage.

### Constants & Configuration
- `SYSTEM_PROMPT: str`: System prompt instructing the model to answer strictly from provided context blocks, state refusal if facts are missing, and append inline citations `[Doc: <file_name> | Page: <page_number>]`.
- `NO_CONTEXT_REFUSAL: str = "I cannot answer this question based on the available documentation."`: Standard refusal disclaimer string.

### Grounded Generation Service (`src/generation/engine.py`)

#### `GroundedGenerator`
- **Purpose:** Core generative LLM service for contextual question answering.
- **Methods:**
  - `__init__(api_key: str | None = None, model: str | None = None, temperature: float | None = None, client: AsyncOpenAI | None = None)`: Initializes generator with API key validation or custom `AsyncOpenAI` client injection, model defaults (`gpt-4o-mini`), and zero temperature ($0.0$).
  - `_format_context(contexts: Sequence[dict[str, Any] | Any]) -> str`: Internal helper formatting context dictionaries or domain objects into structured text blocks (`Source File`, `Page Number`, `Content`).
  - `generate_stream(query: str, contexts: Sequence[dict[str, Any] | Any]) -> AsyncGenerator[str, None]`: Streams completion token deltas asynchronously using OpenAI chat completions, yielding refusal if contexts list is empty and raising `GenerationError` on API failure.
  - `generate(query: str, contexts: Sequence[dict[str, Any] | Any]) -> str`: Non-streaming convenience method aggregating streaming tokens into a complete answer string.

### Execution & Streaming Flow
```text
GroundedGenerator.generate_stream(query, contexts)
  ├── 1. Check if not contexts -> Yield NO_CONTEXT_REFUSAL -> Return
  ├── 2. Format context list into text blocks via _format_context()
  ├── 3. Construct prompt: "CONTEXT INFORMATION:\n{context_str}\n\nUSER QUESTION: {query}"
  ├── 4. Invoke client.chat.completions.create(
  │        model=self.model,
  │        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
  │        temperature=0.0,
  │        stream=True
  │      )
  ├── 5. Iterate stream -> Extract chunk.choices[0].delta.content -> Yield delta
  └── 6. Catch Exception -> Log structlog error -> Raise GenerationError
```

### Package Exports & Registration
- **`src/generation/__init__.py`:** Exports `GroundedGenerator`, `SYSTEM_PROMPT`, and `NO_CONTEXT_REFUSAL`.
- **Runner Registration:** `test_run_project_tests_grounded_generator_suite` in `tests/unit/test_runner.py`.

---

## 28. Server-Sent Events (SSE) Streaming Response Handler (`src/generation/sse.py`, `src/models/chat.py`)

### Overview
Implements Phase 7.2 SSE response streaming infrastructure. Formats raw tokens, JSON payloads, and Pydantic domain models into W3C-compliant Server-Sent Events stream frames (`text/event-stream`). Provides `SSEResponseHandler` to wrap `AsyncGenerator` token streams from `GroundedGenerator` into a structured event lifecycle sequence (`metadata` -> `token` deltas -> `done` completion) with mid-stream exception catching and error framing.

### Domain Schemas (`src/models/chat.py`)

#### `SSEMetaDataPayload`
- **Purpose:** Initial metadata event payload emitted over SSE prior to token delta generation.
- **Fields:** `conversation_id` (str), `confidence_score` (float, 0.0..1.0), `grounded` (bool), `citations` (list[`Citation`]).

#### `SSETokenPayload`
- **Purpose:** Streaming token delta payload emitted for each generated text token.
- **Fields:** `delta` (str).

#### `SSEDonePayload`
- **Purpose:** Completion payload emitted upon successful stream termination.
- **Fields:** `status` (str, default `"completed"`), `finish_reason` (str, default `"stop"`).

#### `SSEErrorPayload`
- **Purpose:** Diagnostic payload emitted when an exception occurs during streaming token generation.
- **Fields:** `error` (str), `code` (str, default `"GENERATION_ERROR"`).

### Helper Function & Handler Class (`src/generation/sse.py`)

#### `format_sse_event(event: str | None = None, data: str | BaseModel | dict[str, Any] | list[Any] | None = None, event_id: str | None = None, retry: int | None = None) -> str`
- **Purpose:** Formats data primitives, dictionaries, or Pydantic models into a W3C-compliant SSE frame string.
- **Parameters:** `event` frame name, `data` frame payload, `event_id` frame sequence ID, `retry` reconnection delay ms.
- **Return Value:** SSE frame string terminated by `\n\n`.

#### `SSEResponseHandler`
- **Purpose:** Handler converting raw token stream generators into formatted SSE event streams.
- **Methods:**
  - `__init__(media_type: str = "text/event-stream")`: Initializes handler with media type header.
  - `format_frame(...) -> str`: Static delegate to `format_sse_event`.
  - `stream_generator(token_stream: AsyncGenerator[str, None], conversation_id: str, confidence_score: float = 1.0, grounded: bool = True, citations: Sequence[Citation | dict[str, Any]] | None = None) -> AsyncGenerator[str, None]`: Asynchronous generator yielding `metadata`, `token` deltas, `error` (if raised), and `done` SSE frames.
  - `stream_raw_tokens(token_stream: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]`: Asynchronous generator streaming raw data-only token deltas.

### Streaming Flow
```text
SSEResponseHandler.stream_generator(token_stream, conversation_id, confidence_score, grounded, citations)
  ├── 1. Format citations -> Construct SSEMetaDataPayload
  ├── 2. Yield format_frame(event="metadata", data=meta_payload)
  ├── 3. Iterate async for token in token_stream:
  │        ├── Construct SSETokenPayload(delta=token)
  │        └── Yield format_frame(event="token", data=token_payload)
  ├── 4. On Exception -> Catch error -> Construct SSEErrorPayload -> Yield format_frame(event="error", data=err_payload)
  └── 5. Construct SSEDonePayload(status="completed", finish_reason="stop") -> Yield format_frame(event="done", data=done_payload)
```

### Package Exports & Registration
- **`src/generation/__init__.py`:** Exports `SSEResponseHandler` and `format_sse_event`.
- **`src/models/__init__.py`:** Exports `SSEMetaDataPayload`, `SSETokenPayload`, `SSEDonePayload`, and `SSEErrorPayload`.
- **Runner Registration:** `test_run_project_tests_sse_handler_suite` in `tests/unit/test_runner.py`.

---

## 29. Citation Extraction & Validation Engine (`src/generation/citations.py`)

### Overview
Implements Phase 7.3 inline citation extraction and grounding validation engine. Parses inline document references formatted as `[Doc: <file_name> | Page: <page_number>]` from generative completion strings via regular expressions (`CITATION_REGEX`). Resolves raw tags against retrieved context blocks (`ChunkDocument`, `RetrievalResult`, dynamic dicts) to produce fully populated `Citation` domain objects. Validates citation integrity and computes zero-tolerance citation accuracy metrics (`citation_accuracy`).

### Domain Schemas & Constants (`src/generation/citations.py`)

#### `CITATION_REGEX`
- **Purpose:** Compiled regular expression pattern matching inline document and page tags.
- **Pattern:** `r"\[Doc:\s*([^|\]]+?)\s*\|\s*Page:\s*(\d+)\s*\]"` (case-insensitive).

#### `RawCitation(BaseDomainModel)`
- **Purpose:** Parsed intermediate domain schema representing an extracted document citation reference prior to context matching.
- **Fields:** `file_name` (str), `page_number` (int, ge=1).

#### `CitationValidationResult(BaseDomainModel)`
- **Purpose:** Validation report payload summarizing grounding status and citation metrics.
- **Fields:** `is_valid` (bool), `citation_accuracy` (float, 0.0..1.0), `valid_citations` (list[`Citation`]), `invalid_citations` (list[`RawCitation`]).

### Engine Classes (`src/generation/citations.py`)

#### `CitationExtractor`
- **Purpose:** Extracts raw inline citation tags from completion text and resolves metadata against retrieved context objects.
- **Methods:**
  - `extract_raw(text: str) -> list[RawCitation]`: Extracts, cleans, and deduplicates raw document citation targets from text.
  - `_extract_context_meta(ctx: Any) -> tuple[str, int, str, str, float]`: Helper extracting normalized `file_name`, `page_number`, `chunk_id`, `excerpt`, and `relevance_score` from dynamic context objects or dicts.
  - `extract_citations(text: str, contexts: Sequence[Any]) -> list[Citation]`: Parses raw tags and matches them against context blocks to construct fully populated `Citation` instances.

#### `CitationValidator`
- **Purpose:** Audits extracted inline citations against retrieved context blocks to detect ungrounded or hallucinated document tags. Enforces strict-mode validation policies, document presence checks, and non-destructive tag filtering.
- **Methods:**
  - `verify_document_presence(file_name: str, page_number: int, contexts: Sequence[Any]) -> bool`: Direct case-insensitive context lookup checking if a target document filename and 1-indexed page number exist in retrieved context.
  - `verify_grounding(text: str, contexts: Sequence[Any]) -> bool`: Boolean convenience helper evaluating whether all inline citations extracted from completion text match retrieved context blocks.
  - `filter_invalid_citations(text: str, contexts: Sequence[Any]) -> tuple[str, list[Citation]]`: Non-destructive sanitizer that strips ungrounded `[Doc: ... | Page: ...]` tags from completion text while returning valid matched `Citation` models.
  - `validate(text_or_citations: str | Sequence[Citation], contexts: Sequence[Any], strict: bool = False) -> CitationValidationResult`: Core validation method auditing tags against context metadata. Calculates `citation_accuracy`, constructs `CitationValidationResult`, and raises `GenerationError` (`code="CITATION_VALIDATION_ERROR"`) when `strict=True` and `is_valid=False`.

### Extraction & Validation Flow
```text
CitationValidator.validate(text_or_citations, contexts, strict=False)
  ├── 1. Parse raw citations via CitationExtractor.extract_raw(text) OR map Citation list to RawCitation instances
  ├── 2. Extract normalized context metadata via CitationExtractor._extract_context_meta(ctx)
  ├── 3. Match each raw citation against context metadata (case-insensitive filename, exact page number)
  │        ├── If matched -> Construct valid Citation -> Append to valid_citations
  │        └── If unmatched -> Append to invalid_citations
  ├── 4. Calculate accuracy = len(valid) / total -> Set is_valid = (len(invalid) == 0)
  └── 5. If strict and not is_valid -> Log structlog warning -> Raise GenerationError(code="CITATION_VALIDATION_ERROR")
```

### Package Exports & Registration
- **`src/generation/__init__.py`:** Exports `CITATION_REGEX`, `RawCitation`, `CitationValidationResult`, `CitationExtractor`, and `CitationValidator`.
- **Runner Registration:** `test_run_project_tests_citations_suite` in `tests/unit/test_runner.py`.

---

## 30. FinOps Telemetry & Metadata Collection Engine (`src/generation/finops.py`, `src/generation/engine.py`)

### Overview
Implements Phase 7.5 FinOps metadata collection and telemetry engine. Provides `FinOpsCollector` service (`src/generation/finops.py`) to count prompt/completion tokens using `tiktoken` with offline fallback heuristics, calculate estimated USD costs via a per-model pricing table (`MODEL_PRICING`), measure execution latency via `track_latency` context manager, and build structured `FinOpsMetadata` domain objects (`src/models/chat.py`). Integrates telemetry generation directly into `GroundedGenerator` via `generate_with_finops(query, contexts)`.

### Configuration & Utilities (`src/generation/finops.py`)

#### `MODEL_PRICING`
- **Purpose:** Dictionary mapping model identifier strings to USD cost rates per 1,000 tokens: `(prompt_rate_per_1k, completion_rate_per_1k)`.
- **Supported Models:** `gpt-4o-mini` ($0.00015 / $0.0006), `gpt-4o` ($0.0025 / $0.01), `gpt-4-turbo` ($0.01 / $0.03), `gpt-3.5-turbo` ($0.0005 / $0.0015), `text-embedding-3-small` ($0.00002 / $0.0).
- **Default Fallback:** `DEFAULT_MODEL_PRICING = (0.00015, 0.0006)`.

#### `count_tokens(text: str, model: str = "gpt-4o-mini") -> int`
- **Purpose:** Counts tokens for a text string using `tiktoken` with multi-tier offline fallback.
- **Resolution Strategy:** Tries `tiktoken.encoding_for_model(model)`, falls back to `tiktoken.get_encoding("cl100k_base")`, and falls back to word-ratio heuristic (`len(words) * 1.3`) if tokenizer loading fails.

#### `calculate_cost(prompt_tokens: int, completion_tokens: int, model: str = "gpt-4o-mini", is_cached: bool = False) -> float`
- **Purpose:** Calculates estimated USD cost based on token counts and model pricing matrix.
- **Caching Handling:** Instantly returns `0.0` USD when `is_cached=True`.

### Telemetry Collector Service (`src/generation/finops.py`)

#### `FinOpsCollector`
- **Purpose:** Centralized collector for token counts, USD cost calculation, and latency tracking.
- **Methods:**
  - `__init__(default_model: str = "gpt-4o-mini")`: Initializes collector with default model name.
  - `count_tokens(text: str, model: str | None = None) -> int`: Delegate counting tokens for input text.
  - `calculate_cost(prompt_tokens: int, completion_tokens: int, model: str | None = None, is_cached: bool = False) -> float`: Delegate calculating cost in USD.
  - `collect(prompt_text: str = "", completion_text: str = "", execution_time_seconds: float = 0.0, model: str | None = None, is_cached: bool = False, prompt_tokens: int | None = None, completion_tokens: int | None = None) -> FinOpsMetadata`: Constructs fully populated `FinOpsMetadata` schema model.
  - `track_latency() -> Generator[dict[str, Any], None, None]`: Context manager measuring execution block duration in seconds (`elapsed_seconds`).

### Grounded Generator Integration (`src/generation/engine.py`)

#### `GroundedGenerator.generate_with_finops(query: str, contexts: Sequence[dict[str, Any] | Any]) -> tuple[str, FinOpsMetadata]`
- **Purpose:** Executes grounded completion generation, measures total wall-clock execution time, and returns the generated answer string paired with populated `FinOpsMetadata`.

### Telemetry Collection Flow
```text
FinOpsCollector.collect(prompt_text, completion_text, execution_time_seconds, model, is_cached)
  ├── 1. Resolve target model (model or default_model)
  ├── 2. Calculate prompt_tokens via count_tokens(prompt_text, target_model) [or use explicit override]
  ├── 3. Calculate completion_tokens via count_tokens(completion_text, target_model) [or use explicit override]
  ├── 4. Total tokens = prompt_tokens + completion_tokens
  ├── 5. Calculate cost via calculate_cost(prompt_tokens, completion_tokens, target_model, is_cached)
  └── 6. Construct & return FinOpsMetadata(
           prompt_tokens=p_tokens,
           completion_tokens=c_tokens,
           total_tokens=total,
           estimated_cost_usd=cost,
           execution_time_seconds=round(exec_time, 4),
           is_cached=is_cached
         )
```

### Package Exports & Registration
- **`src/generation/__init__.py`:** Exports `FinOpsCollector`, `count_tokens`, `calculate_cost`, and `MODEL_PRICING`.
- **Runner Registration:** `test_run_project_tests_finops_collector_suite` in `tests/unit/test_runner.py`.

---

## 31. FastAPI SSE Streaming Chat Endpoint & Service Layer (`src/api/routes/chat.py`, `src/api/services/chat_service.py`)

### Overview
Implements Phase 8.1 POST `/api/v1/chat` endpoint with Server-Sent Events (SSE) streaming. Enforces strict layer isolation by delegating pipeline execution to `ChatService` (`src/api/services/chat_service.py`), injects service dependencies via `get_chat_service` (`src/api/dependencies.py`), exposes the route in `src/api/routes/chat.py`, and initializes the FastAPI app via factory `create_app` (`src/api/app.py`).

### Service Layer (`src/api/services/chat_service.py`)

#### `ChatService`
- **Purpose:** Orchestrates candidate retrieval, confidence guard evaluation, grounded LLM streaming generation, and SSE frame formatting.
- **Methods:**
  - `__init__(dense_search, sparse_search, rrf_fusion, reranker, confidence_guard, grounded_generator, sse_handler)`: Initializes pipeline components with sensible defaults or injected mocks.
  - `stream_chat(request: ChatRequest) -> AsyncGenerator[str, None]`: Executes hybrid search, evaluates candidates against `ConfidenceGuard`, streams grounded tokens or refusal text, and formats SSE event frames (`metadata`, `token`, `error`, `done`).

### Presentation Layer & Routing (`src/api/routes/chat.py`, `src/api/app.py`)

#### `chat_endpoint(request: ChatRequest, chat_service: ChatService = Depends(get_chat_service)) -> StreamingResponse`
- **Purpose:** Receives user query and conversation parameters, invokes `ChatService.stream_chat`, and returns a FastAPI `StreamingResponse` with `media_type="text/event-stream"`.
- **Headers:** `Cache-Control: no-cache`, `Connection: keep-alive`, `X-Accel-Buffering: no`.

#### `create_app() -> FastAPI`
- **Purpose:** FastAPI application factory instantiating the application and including `chat_router` under `/api/v1`.

### Execution Flow
```text
POST /api/v1/chat (ChatRequest)
  ├── 1. FastAPI validates ChatRequest schema
  ├── 2. Depends(get_chat_service) injects ChatService instance
  ├── 3. ChatService.stream_chat(request)
  │      ├── Run hybrid vector/sparse retrieval & reranking (if enabled)
  │      ├── ConfidenceGuard.evaluate(candidates)
  │      ├── If unconfident: yield metadata frame + refusal stream + done frame
  │      └── If confident: yield metadata frame + GroundedGenerator token deltas + done frame
  └── 4. StreamingResponse returns text/event-stream
```

### Package Exports & Registration
- **`src/api/__init__.py`:** Exports `app` and `create_app`.
- **`src/api/routes/__init__.py`:** Exports `chat_router` and `debug_router`.
- **`src/api/services/__init__.py`:** Exports `ChatService`.
- **Runner Registration:** `test_run_project_tests_chat_endpoint_suite` in `tests/unit/test_runner.py`.

---

## 32. FastAPI Retrieval Diagnostic Endpoint & Debug Dependency Injection (`src/api/routes/debug.py`, `src/api/dependencies.py`)

### Overview
Implements Phase 8.2 GET `/api/v1/debug/retrieval` diagnostic endpoint. Exposes stage-wise search scores and ranks (dense vector search, sparse BM25 search, RRF fusion, and final cross-encoder reranking) via `DebugRetrievalBuilder` (`src/retrieval/debug_retrieval.py`), configures dependency injection in `src/api/dependencies.py`, and registers the router in `src/api/app.py`.

### Route Handler (`src/api/routes/debug.py`)

#### `debug_retrieval_endpoint`
- **Signature:** `async def debug_retrieval_endpoint(debug_builder: DebugRetrievalBuilderDep, query: str = Query(...), dense_top_k: int | None = Query(default=None, ge=1), sparse_top_k: int | None = Query(default=None, ge=1), rrf_top_k: int | None = Query(default=None, ge=1), rerank_top_k: int | None = Query(default=None, ge=1)) -> DebugRetrievalResponse`
- **Purpose:** Diagnostic endpoint returning intermediate scores and ranks across retrieval stages for a given search query.
- **Parameters:**
  - `query: str`: Search query string (min_length=1).
  - `dense_top_k`, `sparse_top_k`, `rrf_top_k`, `rerank_top_k`: Optional per-stage top-k candidate limits.
  - `debug_builder: DebugRetrievalBuilderDep`: Injected builder instance.

### Dependency Injection Providers (`src/api/dependencies.py`)

#### `get_debug_retrieval_builder() -> DebugRetrievalBuilder`
- **Purpose:** Singleton dependency provider returning standard or configured `DebugRetrievalBuilder` instance.

#### `set_debug_retrieval_builder(builder: DebugRetrievalBuilder | None) -> None`
- **Purpose:** Helper function for configuring or resetting `DebugRetrievalBuilder` dependency instance in test suites.

#### `DebugRetrievalBuilderDep`
- **Purpose:** Type annotation alias for `Annotated[DebugRetrievalBuilder, Depends(get_debug_retrieval_builder)]`.

### Diagnostic Execution Flow
```text
GET /api/v1/debug/retrieval (query="...", dense_top_k=...)
  ├── 1. FastAPI validates Query parameters
  ├── 2. Injects DebugRetrievalBuilder instance via DebugRetrievalBuilderDep
  ├── 3. DebugRetrievalBuilder.build(query, dense_top_k, sparse_top_k, rrf_top_k, rerank_top_k)
  │      ├── Run DenseSearchService.search -> dense_hits (scores & ranks)
  │      ├── Run SparseSearchService.search -> sparse_hits (BM25 scores & ranks)
  │      ├── Run RRFusionService.fuse -> rrf_fused (fused scores & ranks)
  │      └── Run RerankerService.rerank -> final_reranked candidates
  └── 4. Returns DebugRetrievalResponse Pydantic payload
```

### Package Exports & Registration
- **`src/api/routes/__init__.py`:** Exports `chat_router` and `debug_router`.
- **`src/api/dependencies.py`:** Exports `get_debug_retrieval_builder`, `set_debug_retrieval_builder`, `DebugRetrievalBuilderDep`.
- **Runner Registration:** `test_run_project_tests_debug_retrieval_endpoint_suite` in `tests/unit/test_runner.py`.

---

## 33. API Key Authentication Middleware & Security Dependency Injection (`src/api/dependencies.py`, `src/core/config.py`)

### Overview
Implements Phase 8.3 API key authentication middleware. Provides modular client authentication via FastAPI `Security` dependency providers in `src/api/dependencies.py`, backed by Pydantic application settings (`src/core/config.py`). Validates incoming `X-API-Key` headers against `Settings.app_api_key` while automatically bypassing verification in unconfigured local development setups.

### Settings Configuration (`src/core/config.py`)

#### `Settings.app_api_key`
- **Type:** `str` (default: `""`)
- **Purpose:** Application API key credential used for authenticating incoming client HTTP requests.

#### `Settings.is_app_api_key_configured() -> bool`
- **Purpose:** Returns `True` if `app_api_key` is set to a non-empty, non-whitespace string.

#### `Settings.get_api_key_status() -> dict[str, bool]`
- **Purpose:** Returns validation map of external and application API key credentials including `"app": self.is_app_api_key_configured()`.

### Security Dependency Providers (`src/api/dependencies.py`)

#### `api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)`
- **Purpose:** FastAPI security scheme extracting the `X-API-Key` header without raising automatic default HTTP 403 errors.

#### `verify_api_key(api_key: str | None = Security(api_key_header), settings: Settings = Depends(get_settings)) -> str`
- **Signature:** `def verify_api_key(...) -> str`
- **Purpose:** Dependency provider validating request `X-API-Key` against `settings.app_api_key`.
- **Behavior:**
  - If `settings.app_api_key` is empty: Bypasses check and returns key or `""`.
  - If `settings.app_api_key` is configured and `api_key` is missing or mismatched: Raises `HTTPException(status_code=401, detail="Invalid or missing API key", headers={"WWW-Authenticate": "ApiKey"})`.
  - If `api_key` matches: Returns validated API key string.

#### `ApiKeyDep`
- **Purpose:** Type annotation alias for `Annotated[str, Depends(verify_api_key)]`.

### Security Verification Flow
```text
Client Request (e.g. POST /api/v1/chat or GET /api/v1/debug/retrieval)
  ├── 1. FastAPI extracts X-API-Key header via APIKeyHeader scheme
  ├── 2. Depends(verify_api_key) invokes verify_api_key(api_key, settings)
  ├── 3. Evaluate settings.app_api_key:
  │      ├── Unconfigured ("") -> Access granted (dev mode bypass)
  │      ├── Configured & Header missing/invalid -> HTTP 401 Unauthorized
  │      └── Configured & Header matching -> Validation succeeds
  └── 4. Forward execution to route handler
```

### Package Exports & Registration
- **`src/api/dependencies.py`:** Exports `api_key_header`, `verify_api_key`, `ApiKeyDep`.
- **`src/api/routes/chat.py` & `src/api/routes/debug.py`:** Configured with `dependencies=[Depends(verify_api_key)]`.
- **Runner Registration:** `test_run_project_tests_api_key_auth_suite` in `tests/unit/test_runner.py`.

---

## 34. CORS, Request Validation & Error Handling Middleware (`src/api/middleware/`)

### Overview
Implements Phase 8.4 middleware layer providing production-safe CORS configuration, request boundary validation with security headers, and standardized error response envelopes across all exception handlers.

### CORS Middleware (`src/api/middleware/cors.py`)

#### `_validate_cors_config(settings: Settings) -> None`
- **Purpose:** Rejects insecure wildcard origin `*` combined with `allow_credentials=True` in production environments.
- **Behavior:** Raises `ValueError` if `settings.is_production()` and `"*" in settings.cors_origins` and `settings.cors_allow_credentials`.

#### `setup_cors(app: FastAPI, settings: Settings | None = None) -> None`
- **Purpose:** Attaches `CORSMiddleware` with validated origin, method, and header policies.
- **Parameters:** `app` FastAPI instance, `settings` optional `Settings` override.
- **Behavior:** Validates config via `_validate_cors_config`, then adds middleware with `allow_origins`, `allow_credentials`, `allow_methods`, `allow_headers`, and `max_age=600`.

### Request Validation Middleware (`src/api/middleware/validation.py`)

#### `_SECURITY_HEADERS: dict[str, str]`
- **Purpose:** Standard security headers injected on all responses for defense-in-depth.
- **Headers:** `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `X-XSS-Protection: 1; mode=block`.

#### `RequestValidationMiddleware(BaseHTTPMiddleware)`
- **Purpose:** Enforces request boundary validation, tracing, and security headers.
- **Parameters:** `app` FastAPI instance, `max_body_bytes` (default 10,485,760).
- **Methods:**
  - `dispatch(request, call_next) -> Response`: Injects/preserves `X-Request-ID`, validates `Content-Length` against `max_body_bytes` (returns 413 `PAYLOAD_TOO_LARGE` on exceed), calls next handler, then adds security headers to response.

#### `setup_validation_middleware(app: FastAPI, max_body_bytes: int = 10_485_760) -> None`
- **Purpose:** Registers `RequestValidationMiddleware` on FastAPI application.

### Error Handling Middleware (`src/api/middleware/error_handler.py`)

#### `_build_error_payload(code: str, message: str, details: dict[str, Any] | list[Any] | None = None) -> dict[str, Any]`
- **Purpose:** Constructs standardized error response envelope `{error: {code, message, details}, detail}`.

#### `_map_app_error_status(exc: AppBaseError) -> int`
- **Purpose:** Maps domain exception types to HTTP status codes.
- **Mapping:** `IngestionError` -> 400, `ConfigurationError`/`RetrievalError`/`GenerationError` -> 500.

#### `app_base_error_handler(request, exc) -> JSONResponse`
- **Purpose:** Handles `AppBaseError` domain hierarchy, returns structured JSON with domain error code.

#### `validation_error_handler(request, exc) -> JSONResponse`
- **Purpose:** Handles Pydantic `RequestValidationError`, returns 422 with validation details list.

#### `http_exception_handler(request, exc) -> JSONResponse`
- **Purpose:** Handles Starlette `HTTPException`, preserves status code and headers.

#### `unhandled_exception_handler(request, exc) -> JSONResponse`
- **Purpose:** Catch-all for unexpected exceptions, returns sanitized 500 response.

#### `register_exception_handlers(app: FastAPI) -> None`
- **Purpose:** Registers all four exception handlers on FastAPI application.

### Middleware Request Flow
```text
Client HTTP Request
  ├── 1. RequestValidationMiddleware:
  │      ├── Inject/preserve X-Request-ID trace header
  │      ├── Validate Content-Length against max_body_bytes (413 on exceed)
  │      └── Add security headers to response
  ├── 2. CORSMiddleware:
  │      ├── Validate origin against allowlist
  │      └── Handle preflight OPTIONS requests
  ├── 3. Route handler executes
  └── 4. Exception handlers (if error):
         ├── AppBaseError -> domain error envelope
         ├── RequestValidationError -> 422 envelope
         ├── HTTPException -> HTTP error envelope
         └── Exception -> sanitized 500 envelope
```

### Package Exports & Registration
- **`src/api/middleware/__init__.py`:** Exports `setup_cors`, `setup_validation_middleware`, `register_exception_handlers`.
- **`src/api/app.py`:** Wires all three middleware components in `create_app()`.
- **Runner Registration:** `test_run_project_tests_cors_and_middleware_suite` in `tests/unit/test_runner.py`.

---

## 35. Service Dependency Injection & Lifespan Context (`src/api/services/container.py`, `src/api/dependencies.py`, `src/api/app.py`)

### Overview
Implements Phase 8.5 lifespan-scoped service dependency injection. A `ServiceContainer` composition root holds application service singletons (`ChatService`, `DebugRetrievalBuilder`) for the duration of the FastAPI app lifecycle. The FastAPI lifespan context bootstraps the container on startup (`app.state.container`) and disposes it on shutdown, guaranteeing deterministic resource lifecycle. Dependency providers resolve services from the container via `request.app.state`, replacing module-level global singletons and eliminating cross-request state leakage.

### Service Container (`src/api/services/container.py`)

#### `ServiceContainer`
- **Purpose:** Lifespan-scoped composition root holding application service singletons for the current app lifecycle.
- **Parameters:**
  - `chat_service: ChatService | None = None`: Optional injected `ChatService` (defaults to a new instance).
  - `debug_builder: DebugRetrievalBuilder | None = None`: Optional injected `DebugRetrievalBuilder` (defaults to a new instance).
- **Methods:**
  - `create_default() -> ServiceContainer`: Class factory building a container with default service implementations.
  - `dispose() -> None`: Releases external resources held by container services (extension point for closing HTTP clients, Qdrant connections, async generators).

### Dependency Injection Providers (`src/api/dependencies.py`)

#### `_get_container(request: Request) -> ServiceContainer`
- **Purpose:** Returns the lifespan-scoped container from `request.app.state.container`, lazily creating and caching a default container when the lifespan has not run (e.g. direct `TestClient` usage).

#### `get_chat_service(request: Request) -> ChatService`
- **Purpose:** Dependency provider resolving `ChatService` from the lifespan-scoped container.

#### `get_debug_retrieval_builder(request: Request) -> DebugRetrievalBuilder`
- **Purpose:** Dependency provider resolving `DebugRetrievalBuilder` from the lifespan-scoped container.

### Application Factory & Lifespan (`src/api/app.py`)

#### `_build_lifespan() -> Callable[[FastAPI], AbstractAsyncContextManager[None]]`
- **Purpose:** Creates the FastAPI lifespan asynccontextmanager bootstrapping and disposing the service container.
- **Behavior:**
  - On startup: creates `ServiceContainer.create_default()`, attaches to `app.state.container`, logs service types.
  - On shutdown: calls `container.dispose()` and clears `app.state.container`.

#### `create_app(settings: Settings | None = None) -> FastAPI`
- **Purpose:** FastAPI application factory registering the lifespan context, middleware, and routers.

### Dependency Resolution Flow
```text
create_app() -> FastAPI(lifespan=_build_lifespan())
  ├── Startup: lifespan creates ServiceContainer.create_default()
  │            -> app.state.container = container
  ├── Request: route dependency get_chat_service(request) / get_debug_retrieval_builder(request)
  │            -> _get_container(request) reads app.state.container
  │            -> returns container.chat_service / container.debug_builder
  ├── If lifespan not run (tests): _get_container lazily creates and caches default container
  └── Shutdown: lifespan calls container.dispose(); app.state.container = None
```

### Package Exports & Registration
- **`src/api/services/__init__.py`:** Exports `ChatService` and `ServiceContainer`.
- **`src/api/dependencies.py`:** Exports `get_chat_service`, `get_debug_retrieval_builder`, `ChatServiceDep`, `DebugRetrievalBuilderDep`.
- **`src/api/app.py`:** Wires lifespan context in `create_app()`.
- **Runner Registration:** `test_run_project_tests_service_container_suite` and `test_run_project_tests_lifespan_di_suite` in `tests/unit/test_runner.py`.

---

## Phase 9.1: React 18+ / Vite / TypeScript Project Initialization

### Overview
Initializes the React 18+, Vite, and TypeScript presentation layer skeleton under `frontend/`. Configures strict TypeScript compiler options, Vite dev server proxying to the FastAPI backend, and domain contract synchronization mirroring backend Pydantic models. Implements an SSE streaming client using `fetch` with `ReadableStream` to support POST request bodies, alongside modular UI components (`Header`, `QueryInput`, `ResponseView`, `CitationDrawer`, `App`) styled with custom HSL design system tokens. Core structural validation is provided in `src/core/frontend.py` and tested in `tests/unit/test_frontend.py`.

### Frontend Configuration & Types

#### TypeScript Contracts (`frontend/src/types/index.ts`)
- **Purpose:** Synchronized domain types mirroring Python Pydantic V2 models for strict type safety across the frontend/backend boundary.
- **Key Types:**
  - `Citation`: Source document metadata including `file_name`, `page_number`, `chunk_id`, `excerpt`, and `relevance_score`.
  - `FinOpsMetadata`: Operational metrics (`prompt_tokens`, `completion_tokens`, `total_tokens`, `estimated_cost_usd`, `execution_time_seconds`, `is_cached`).
  - `ChatRequest`: DTO sending `query`, `conversation_id`, and optional `top_k`.
  - `ChatResponse`: Full response payload with answer, citations, confidence, grounding, and finops metadata.
  - `RetrievalResult` & `DebugRetrievalResponse`: Intermediate and multi-stage retrieval hit diagnostic schemas.
  - `SSEEvent`: Discriminated union of SSE frame payloads (`metadata`, `token`, `done`, `error`).
  - `ChatMessage` & `QueryState`: Frontend UI state containers for chat history, streaming states, and selected citations.

### API & SSE Client Service (`frontend/src/services/api.ts`)

#### `streamChat(request: ChatRequest, callbacks: StreamCallbacks) -> Promise<void>`
- **Purpose:** Initiates streaming chat interaction via `POST /api/v1/chat` and processes incoming SSE events in real time.
- **Data Flow:**
  1. Issues `fetch()` POST request with JSON-encoded `ChatRequest` and `Accept: text/event-stream`.
  2. Obtains `ReadableStreamDefaultReader` from response body.
  3. Iteratively reads and decodes binary chunks using `TextDecoder("utf-8")`.
  4. Buffers and parses double-newline separated SSE event frames.
  5. Dispatches typed event callbacks:
     - `metadata`: Triggers `callbacks.onMetadata(meta)` with citations and confidence score.
     - `token`: Triggers `callbacks.onToken(token)` appending text deltas.
     - `done`: Triggers `callbacks.onDone(status)` finalizing response rendering.
     - `error`: Triggers `callbacks.onError(error)` on stream-level failure.

#### `getDebugRetrieval(query: string, topK: number = 5) -> Promise<DebugRetrievalResponse>`
- **Purpose:** Fetches diagnostic multi-stage retrieval hits from `GET /api/v1/debug/retrieval`.

### Python Audit & Validation (`src/core/frontend.py`)

#### `parse_frontend_package_json(project_root: Path | None = None) -> dict[str, Any]`
- **Purpose:** Parses and loads `frontend/package.json` into a dictionary for configuration audits.

#### `parse_frontend_tsconfig(project_root: Path | None = None) -> dict[str, Any]`
- **Purpose:** Parses and loads `frontend/tsconfig.json` to verify strict compiler options.

#### `validate_frontend_setup(project_root: Path | None = None) -> dict[str, Any]`
- **Purpose:** Performs comprehensive validation of the frontend repository structure.
- **Verifications:**
  - Presence of all required files (`package.json`, `tsconfig.json`, `vite.config.ts`, `index.html`, `main.tsx`, `App.tsx`, `index.css`, `types/index.ts`, `services/api.ts`, component files).
  - Validation of npm scripts (`dev`, `build`, `preview`, `typecheck`).
  - Verification of core dependencies (`react`, `react-dom`) and dev dependencies (`@vitejs/plugin-react`, `typescript`, `vite`).
  - Verification of TypeScript domain interface definitions matching required schema contracts.

---

## 31. Query Input Component & Submission Handling (Phase 9.2)

### Overview
Implements a reactive, accessible, and robust user query input component (`frontend/src/components/QueryInput.tsx`) handling input validation, keyboard shortcuts, context depth selection (`top_k`), and asynchronous submission triggering. Includes automated structural and accessibility validation in `src/core/frontend.py` and test suites in `tests/unit/test_query_input.py`.

### React Component Specification (`frontend/src/components/QueryInput.tsx`)

#### `QueryInputProps` Interface
- `onSubmit: (query: string, topK: number) => void`: Callback invoked on valid form submission with trimmed query and selected top_k depth.
- `isLoading: boolean`: Disables interactive inputs and triggers button spinner state during in-flight streaming requests.
- `disabled?: boolean`: General disabling flag (default `false`).
- `placeholder?: string`: Customizable textarea placeholder text.
- `initialTopK?: number`: Initial context chunk retrieval count (default `5`).
- `maxQueryLength?: number`: Upper limit on query character count (default `4000`).
- `suggestedQueries?: string[]`: List of quick-prompt strings displayed as interactive suggestion pills.

#### Component State & Internal Handlers
- `query: string`: Active textarea string state.
- `topK: number`: Context chunk retrieval count.
- `validationError: string | null`: Error message displayed if query length exceeds limits.
- `handleChange(e)`: Updates query state and evaluates length validation constraints.
- `handleSubmit(e)`: Trims whitespace, validates input length, aborts if disabled/empty, executes `onSubmit(trimmed, topK)`, clears the input buffer, and resets errors.
- `handleKeyDown(e)`:
  - `Enter` (without Shift): Prevents default newline insertion and invokes `handleSubmit()`.
  - `Shift+Enter`: Inserts a multiline newline.
  - `Escape`: Resets query buffer and clears validation errors.
- `handleSuggestionClick(item)`: Populates textarea with chosen prompt text and focuses the textarea.
- `handleClear()`: Resets query buffer to empty string and restores focus.

#### Data Flow
```text
User types query / clicks suggested query
  │
  ▼
setQuery updates state ──► handleValidation checks character bounds
  │
  ▼
User presses Enter or clicks "Send Query"
  │
  ▼
handleSubmit executes ──► e.preventDefault()
  │
  ▼
Whitespace trimmed & validated against empty / disabled state
  │
  ▼
onSubmit(trimmed, topK) dispatches to App handler (streamChat)
  │
  ▼
setQuery("") clears input buffer & resets error state
  │
  ▼
UI toggles isLoading / aria-busy state and activates loading spinner
```

### Python Audit & Validation (`src/core/frontend.py`)

#### `validate_query_input_component(project_root: Path | None = None) -> dict[str, Any]`
- **Purpose:** Audits `QueryInput.tsx` component source code for contract compliance, event guards, and accessibility attributes.
- **Audited Rules:**
  - File existence at `frontend/src/components/QueryInput.tsx`.
  - Required props present (`onSubmit`, `isLoading`).
  - Semantic DOM IDs present (`query-form`, `query-input`, `top-k-select`, `submit-query-btn`).
  - Submission guard present (`trim()` check before `onSubmit()`).
  - Keyboard navigation present (`Enter` vs `Shift+Enter` handling).
  - Context selector present (`top_k` / `topK` options).
- **Return Value:** Structured dictionary containing `valid: bool`, `missing_props: list[str]`, `missing_ids: list[str]`, and feature booleans.

### Unit Test Suite (`tests/unit/test_query_input.py`)
- `test_query_input_component_exists_and_valid`: Asserts component satisfies all contract, prop, and a11y requirements.
- `test_query_input_props_interface`: Verifies `QueryInputProps` TypeScript interface definitions.
- `test_query_input_keyboard_shortcuts`: Asserts Enter/Shift+Enter key handling.
- `test_query_input_submission_guards_and_trim`: Verifies whitespace trimming and empty submission guards.
- `test_query_input_accessibility_and_semantic_ids`: Asserts presence of required ARIA attributes, semantic roles, and DOM IDs.
- `test_query_input_top_k_options`: Verifies chunk retrieval options (3, 5, 10, 15).
- `test_query_input_missing_file`: Asserts validator failure when component file is missing.
- `test_query_input_incomplete_component`: Asserts validator failure when component has missing props/IDs.

---

## 30. SSE Streaming Answer Display & Real-Time Rendering (`frontend/src/components/ResponseView.tsx`)

### Overview
Renders real-time conversational exchange between the user and the grounded assistant. Manages incremental token streaming, animated blinking cursor, groundedness status badges, confidence score threshold styling, interactive citation pills, FinOps metrics telemetry, and automatic smooth scroll-to-bottom anchoring.

### React Component Architecture

#### `ResponseViewProps` Interface
```typescript
export interface ResponseViewProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  onSelectCitation?: (citation: Citation) => void;
  autoScroll?: boolean;
}
```

#### Core Component Sub-structures
- `messagesEndRef`: `useRef<HTMLDivElement | null>` anchoring the viewport bottom for smooth auto-scrolling on streaming updates.
- `messages-empty`: Accessible fallback empty state card (`#empty-state-prompt`) guiding first-time users.
- `message-item`: Semantic `<article>` container per turn distinguishing user queries (`.message-user`) and assistant answers (`.message-assistant`).
- `message-header`: Renders sender labels, grounded badge (`Grounded` vs `Ungrounded`), confidence score badge (`Conf: XX.X%` with `S_min >= 0.35` threshold coloring), and timestamp.
- `message-body`: Preserves whitespace, renders real-time token stream deltas, and conditionally displays the animated blinking cursor (`.streaming-cursor`) while `msg.isStreaming` is active.
- `message-citations`: Clickable citation pill buttons (`.citation-pill`) that invoke `onSelectCitation` to highlight source document excerpts in the sidebar drawer.
- `finops-bar`: Execution summary displaying token counts, USD cost estimation, execution time, and cache hit status.

#### Data Flow
```text
User submits query via QueryInput
  │
  ▼
App dispatches streamChat() via api.ts
  │
  ▼
Backend emits SSE "metadata" frame (citations, confidence score, grounded flag)
  │
  ▼
App handler updates assistant message metadata in state
  │
  ▼
Backend emits incremental SSE "token" frames
  │
  ▼
App handler appends token deltas to message content
  │
  ▼
ResponseView re-renders real-time text with animated cursor ▌
  │
  ▼
useEffect triggers messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
  │
  ▼
Backend emits SSE "done" frame ──► App sets isStreaming: false (cursor terminates)
```

### Python Audit & Validation (`src/core/frontend.py`)

#### `validate_response_view_component(project_root: Path | None = None) -> dict[str, Any]`
- **Purpose:** Audits `ResponseView.tsx` component source code for contract compliance, streaming handlers, and accessibility attributes.
- **Audited Rules:**
  - File existence at `frontend/src/components/ResponseView.tsx`.
  - Required props present (`messages`, `isStreaming`).
  - Semantic DOM IDs present (`response-view`, `streaming-cursor`, `empty-state-prompt`).
  - Auto-scroll hook present (`scrollIntoView` / `useRef`).
  - Streaming cursor indicator present (`streaming-cursor` / `isStreaming`).
  - Confidence badge calculation present (`confidenceScore` / `0.35` threshold).
  - Citation chip display present (`citations` / `citation-pill`).
- **Return Value:** Structured dictionary containing `valid: bool`, `missing_props: list[str]`, `missing_ids: list[str]`, and feature booleans.

### Unit Test Suite (`tests/unit/test_streaming_response_view.py`)
- `test_response_view_component_exists_and_valid`: Asserts component satisfies all contract, prop, and streaming requirements.
- `test_response_view_props_interface`: Verifies `ResponseViewProps` TypeScript interface definitions.
- `test_response_view_streaming_cursor_and_deltas`: Asserts conditional rendering of animated cursor during streaming.
- `test_response_view_confidence_and_grounded_badges`: Verifies confidence score badge calculation and grounded status indicators.
- `test_response_view_auto_scrolling_anchor`: Asserts presence of smooth scroll ref and effect hooks.
- `test_response_view_citations_and_finops_telemetry`: Verifies citation pill chips and FinOps telemetry display.
- `test_response_view_accessibility_and_semantic_ids`: Asserts presence of required ARIA attributes, semantic roles, and DOM IDs.
- `test_response_view_missing_file`: Asserts validator failure when component file is missing.
- `test_response_view_incomplete_component`: Asserts validator failure when component has missing props/IDs.
















