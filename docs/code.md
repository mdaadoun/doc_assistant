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



