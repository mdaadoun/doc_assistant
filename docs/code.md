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

---

## 33. Citation Drawer & Source Excerpt Inspector (`frontend/src/components/CitationDrawer.tsx`)

### Overview
Renders the complementary sidebar panel displaying retrieved grounded document citations, provenance metadata, search filtering, and an active source excerpt inspector.

### Component Interface (`CitationDrawerProps`)
```typescript
export interface CitationDrawerProps {
  citations: Citation[];
  activeCitation: Citation | null;
  onSelectCitation: (citation: Citation | null) => void;
  onClose?: () => void;
  title?: string;
}
```

### Core Sub-structures & Features
- `drawer-header`: Displays drawer title, dynamic citation count badge (`#citations-count-badge`), and optional drawer close action.
- `citation-search-box`: Input field (`#citation-search-input`) with in-memory substring filtering over document names, excerpts, and chunk IDs via `useMemo`.
- `active-citation-inspector`: Dedicated container (`#active-citation-inspector`) rendering the full text excerpt (`#active-excerpt-text`), provenance metadata (file name, page number, relevance score), chunk ID tag, and clipboard copy action (`#copy-excerpt-btn`).
- `empty-citations-card`: Informative placeholder (`#empty-citations-state` / `#empty-citations-prompt`) displayed when no citations have been retrieved or when search filter produces zero matches.
- `citations-list`: Accessible list (`#citations-list`, `role="list"`) containing interactive citation cards (`role="listitem"`, `tabIndex={0}`, `aria-selected`).

### Data Flow
```text
SSE stream delivers citations: Citation[] to App state
  │
  ▼
App supplies citations & activeCitation to CitationDrawer
  │
  ▼
User interacts via search input ──► useMemo dynamically filters card list
  │
  ▼
User clicks Citation Card or inline Citation Pill in ResponseView
  │
  ▼
onSelectCitation(citation) updates activeCitation in App state
  │
  ▼
CitationDrawer opens active-citation-inspector with full source excerpt
  │
  ▼
User clicks "Copy Excerpt" ──► navigator.clipboard writes text with "Copied!" feedback
```

### Python Audit & Validation (`src/core/frontend_validators.py`)

#### `validate_citation_drawer_component(project_root: Path | None = None) -> dict[str, Any]`
- **Purpose:** Audits `CitationDrawer.tsx` component source code for contract compliance, search filtering, inspector structure, and accessibility attributes.
- **Audited Rules:**
  - File existence at `frontend/src/components/CitationDrawer.tsx`.
  - Required props present (`citations`, `activeCitation`, `onSelectCitation`).
  - Semantic DOM IDs present (`citation-drawer`, `citations-count-badge`, `empty-citations-state`, `citations-list`).
  - Active inspector structure present (`activeCitation`, `active-citation-inspector`).
  - Clipboard copy action present (`handleCopyExcerpt`, `clipboard` / `Copy`).
  - Search filter mechanism present (`filter`, `searchTerm`).
  - Metadata display present (`page_number`, `relevance_score`, `file_name`).
- **Return Value:** Structured dictionary containing `valid: bool`, `missing_props: list[str]`, `missing_ids: list[str]`, and feature booleans.

### Unit Test Suite (`tests/unit/test_citation_drawer.py`)
- `test_citation_drawer_component_exists_and_valid`: Asserts component satisfies all contract, prop, and inspection requirements.
- `test_citation_drawer_props_interface`: Verifies `CitationDrawerProps` TypeScript interface definitions.
- `test_citation_drawer_active_inspector_and_copy`: Asserts active source excerpt inspector and clipboard copy handlers.
- `test_citation_drawer_empty_and_filter_states`: Asserts empty state and search filter fallback rendering.
- `test_citation_drawer_search_filter_logic`: Verifies in-memory search filtering by filename or excerpt text.
- `test_citation_drawer_page_and_score_formatting`: Asserts page number, relevance score, and chunk ID formatting.
- `test_citation_drawer_accessibility_and_semantic_ids`: Asserts presence of required ARIA attributes, semantic roles, and DOM IDs.
- `test_citation_drawer_missing_file`: Asserts validator failure when component file is missing.
- `test_citation_drawer_incomplete_component`: Asserts validator failure when component has missing props/IDs.

---

## 32. Loading States, Error Handling & Confidence Indicators (`frontend/src/components/ConfidenceIndicator.tsx`, `frontend/src/components/ErrorBanner.tsx`, `frontend/src/components/LoadingIndicator.tsx`, `src/core/resilience_validators.py`)

### Overview
Provides full resilience, continuous feedback, and visual confidence calibration for the Corporate Document Assistant frontend. Introduces a 3-tier confidence classification model with an accessible progress bar meter and minimum confidence threshold indicator ($S_{\min} = 0.35$), multi-phase pipeline lifecycle state tracking (`retrieving` $\to$ `reranking` $\to$ `generating` $\to$ `complete`) with skeleton shimmer animation, and non-blocking inline error recovery with automated query replay.

### Confidence Indicator Component (`frontend/src/components/ConfidenceIndicator.tsx`)

#### `getConfidenceTier(score: number) -> { tier, label, badgeClass }`
- **Purpose:** Classifies continuous relevance scores into discrete confidence tiers:
  - High ($\ge 0.70$): `tier="high"`, `label="High Confidence"`, `badgeClass="badge-confidence-high"`.
  - Moderate ($0.35 \le score < 0.70$): `tier="medium"`, `label="Moderate Confidence"`, `badgeClass="badge-confidence-medium"`.
  - Low / Refusal ($< 0.35$): `tier="low"`, `label="Low Confidence / Refusal"`, `badgeClass="badge-confidence-low"`.
- **Return Value:** Structured tier descriptor object.

#### `ConfidenceIndicator` Component
- **Props Interface (`ConfidenceIndicatorProps`):**
  - `confidenceScore: number`: Normalized relevance score $[0.0, 1.0]$.
  - `grounded?: boolean`: Boolean flag indicating whether the response satisfies factual grounding constraints.
  - `showMeter?: boolean`: Whether to display the visual progress meter bar.
  - `compact?: boolean`: Compact display mode for inline badges.
  - `className?: string`: Optional CSS class name override.
- **Key Rendered Elements:**
  - `#confidence-indicator`: Container element with ARIA semantics.
  - `#confidence-score-badge`: Badge displaying formatted percentage (`(score * 100).toFixed(1)%`).
  - `#confidence-tier-badge`: Categorical tier badge (`data-tier` attribute).
  - `#confidence-meter-bar`: Accessible progressbar container (`role="progressbar"`, `aria-valuenow`, `aria-valuemin="0"`, `aria-valuemax="100"`).
  - `#confidence-threshold-marker`: Visual indicator anchored at $35\%$ representing the $S_{\min} = 0.35$ confidence gate.
  - `#grounded-status-badge`: Verification badge showing `✓ Verified Grounded` or `⚠ Grounding Warning`.

### Error Banner Component (`frontend/src/components/ErrorBanner.tsx`)

#### `ErrorBanner` Component
- **Props Interface (`ErrorBannerProps`):**
  - `error: ErrorInfo | string | null`: Structured error metadata or error message string.
  - `onRetry?: () => void`: Asynchronous callback invoking query replay.
  - `onDismiss?: () => void`: Callback clearing the active error state.
  - `title?: string`: Header title string (defaults to `"Query Execution Failed"`).
  - `className?: string`: Optional CSS class name override.
- **Key Rendered Elements:**
  - `#error-banner`: Alert container (`role="alert"`, `aria-live="assertive"`, `aria-atomic="true"`).
  - `#error-title`: Header title element.
  - `#error-code-badge`: Error code tag (e.g., `NETWORK_ERROR`, `STREAM_ERROR`, `HTTP_ERROR`).
  - `#error-message-text`: Diagnostic error detail text.
  - `#retry-button`: Interactive button invoking `onRetry()` to replay the failed query.
  - `#dismiss-error-btn`: Button invoking `onDismiss()` to clear the error banner.

### Loading Indicator Component (`frontend/src/components/LoadingIndicator.tsx`)

#### `LoadingIndicator` Component
- **Props Interface (`LoadingIndicatorProps`):**
  - `phase?: RetrievalPhase`: Active pipeline lifecycle phase (`idle`, `retrieving`, `reranking`, `generating`, `complete`, `error`).
  - `message?: string`: Optional custom status message override.
  - `elapsedSeconds?: number`: Elapsed time in seconds.
  - `className?: string`: Optional CSS class name override.
- **Key Rendered Elements:**
  - `#loading-indicator`: Live region container (`role="status"`, `aria-live="polite"`, `aria-busy="true"`).
  - `#loading-spinner`: Animated CSS spinner.
  - `#retrieval-phase-label`: Human-readable phase description.
  - `#loading-step-list`: Visual pipeline progression track (`Dual Search` $\to$ `Re-Rank & Guard` $\to$ `Grounded Stream`).
  - `#loading-skeleton-pulse`: Multi-line CSS shimmer animation simulating incoming content layout before first-token arrival.

### Data Flow Architecture

```text
User submits query via QueryInput
  │
  ▼
App sets retrievalPhase = 'retrieving' & clears previous errors
  │
  ▼
ResponseView renders in-flight LoadingIndicator with step progression & skeleton pulse
  │
  ▼
streamChat initiates SSE connection to /api/v1/chat
  │
  ├─► onMetadata: updates confidenceScore, grounded status, and citations
  │               retrievalPhase transitions to 'generating'
  │               ResponseView renders ConfidenceIndicator with visual meter & S_min marker
  │
  ├─► onToken: appends streaming tokens to message content in real time
  │
  ├─► onDone: retrievalPhase transitions to 'complete' & finalizes FinOps metadata
  │
  └─► onError / Catch: captures structured ErrorInfo (code, message, query, topK)
                       retrievalPhase transitions to 'error'
                       App renders ErrorBanner & ResponseView renders inline message error card
                       User clicks "Retry Query" ──► handleRetry replays execution idempotently
```

### Python Audit & Validation (`src/core/resilience_validators.py`)

#### `validate_confidence_indicator_component(project_root: Path | None = None) -> dict[str, Any]`
- **Purpose:** Audits `ConfidenceIndicator.tsx` for tier calculation logic ($0.70$, $0.35$), progressbar ARIA semantics, meter width, and threshold marker.

#### `validate_error_banner_component(project_root: Path | None = None) -> dict[str, Any]`
- **Purpose:** Audits `ErrorBanner.tsx` for alert role, error code badge, dismiss action, and retry handler.

#### `validate_loading_indicator_component(project_root: Path | None = None) -> dict[str, Any]`
- **Purpose:** Audits `LoadingIndicator.tsx` for pipeline step tracks, skeleton shimmer animation, and live region status role.

#### `validate_resilience_and_confidence_components(project_root: Path | None = None) -> dict[str, Any]`
- **Purpose:** Consolidated facade validating all phase 9.5 resilience and confidence components.

### Unit Test Suite (`tests/unit/test_loading_and_confidence.py`)
- `test_resilience_and_confidence_components_exist_and_valid`: Validates that all phase 9.5 components pass structural and accessibility audits.
- `test_confidence_indicator_component_contract`: Asserts presence of required props, IDs, tier thresholds, and progressbar attributes.
- `test_error_banner_component_contract`: Asserts presence of alert role, error code badge, and retry/dismiss handlers.
- `test_loading_indicator_component_contract`: Asserts presence of status role, pipeline step tracks, spinner, and skeleton pulse.
- `test_response_view_integration_with_confidence_and_errors`: Asserts integration of `ConfidenceIndicator`, `LoadingIndicator`, and inline error retry cards.
- `test_app_integration_with_error_banner_and_retry`: Asserts `ErrorBanner` rendering and `handleRetry` query replay in `App.tsx`.
- `test_resilience_validators_missing_files`: Asserts validator failure on missing component files.
- `test_resilience_validators_incomplete_components`: Asserts validator failure on incomplete component stubs.

---

## 33. Evaluation Dataset Schemas & Quality Audit (`src/models/evaluation.py`, `src/core/eval_dataset.py`)

### Overview
Defines immutable domain models and robust I/O utilities for loading, validating, and persisting ground-truth benchmark datasets used by evaluation frameworks.

### Architecture & Data Flow

```text
  data/eval_dataset.jsonl
            │
            ▼ (line-by-line streaming)
  load_eval_dataset_from_jsonl()
            │
            ├─► Pydantic Model Validation (EvalDatasetItem, EvalGroundTruthCitation)
            │      └─► IngestionError wrapping on JSON syntax / schema corruption
            │
            ▼
       EvalDataset (frozen container)
            │
            ├─► validate_eval_dataset_quality()
            │      ├─► Total queries >= 50
            │      ├─► Out-of-corpus queries >= 10
            │      ├─► Query ID uniqueness
            │      └─► Citation attribution integrity
            ▼
     RetrievalMonitor Benchmarking Suite
```

### Domain Models (`src/models/evaluation.py`)

#### `EvalGroundTruthCitation(BaseDomainModel)`
- `file_name: str`: Source document file name.
- `page_number: int`: 1-indexed source page number (default 1).
- `chunk_id: str`: Target ground-truth chunk ID.
- `excerpt: str`: Optional reference text excerpt.

#### `EvalDatasetItem(BaseDomainModel)`
- `query_id: str`: Unique query identifier (e.g. `eval-001`).
- `query: str`: User question or evaluation query string.
- `ground_truth_answer: str`: Expected grounded answer or standard refusal response.
- `ground_truth_citations: list[EvalGroundTruthCitation]`: List of expected supporting citations.
- `is_out_of_corpus: bool`: Flag indicating whether query is out-of-corpus expecting refusal.
- `category: str`: Domain policy category (e.g., `sla`, `security`, `hr_policy`, `out_of_corpus`).

#### `EvalDataset(BaseDomainModel)`
- `items: list[EvalDatasetItem]`: Collection of validated evaluation items.
- `version: str`: Dataset schema version (default `1.0.0`).
- Properties: `total_queries`, `out_of_corpus_count`, `in_corpus_count`.

### Functions (`src/core/eval_dataset.py`)

#### `get_default_eval_dataset_path(base_dir: Path | None = None) -> Path`
- **Purpose:** Resolves standard path to `data/eval_dataset.jsonl`.
- **Return Value:** Absolute `Path` to dataset file.

#### `load_eval_dataset_from_jsonl(file_path: Path | str | None = None) -> EvalDataset`
- **Purpose:** Streams JSONL file line-by-line, parses each line into `EvalDatasetItem`, catches I/O or JSON formatting exceptions, and wraps them in `IngestionError`.
- **Return Value:** Populated `EvalDataset` instance.

#### `save_eval_dataset_to_jsonl(dataset: EvalDataset, file_path: Path | str) -> int`
- **Purpose:** Serializes `EvalDataset` items into JSON Lines format at the target path, creating parent folders if necessary.
- **Return Value:** Integer count of written records.

#### `validate_eval_dataset_quality(dataset: EvalDataset, min_total: int = 50, min_out_of_corpus: int = 10) -> dict[str, Any]`
- **Purpose:** Validates minimum cardinality thresholds, uniqueness of `query_id`, empty citations for out-of-corpus records, and valid citations for in-corpus records.
- **Return Value:** Audit result dictionary with `valid: bool`, counts, and error list.

### Unit Test Suite (`tests/unit/test_eval_dataset.py`)
- `test_load_default_eval_dataset_and_validate_thresholds`: Asserts default dataset contains $\ge 50$ total and $\ge 10$ out-of-corpus records, and passes quality audit.
- `test_eval_dataset_item_immutability`: Verifies immutable Pydantic `frozen=True` constraint on evaluation models.
- `test_validate_eval_dataset_quality_error_branches`: Tests quality audit detection of duplicate IDs and misconfigured out-of-corpus citations.
- `test_load_eval_dataset_missing_file_raises_ingestion_error`: Tests `IngestionError` (`EVAL_DATASET_NOT_FOUND`) on missing file.
- `test_load_eval_dataset_corrupted_json_raises_ingestion_error`: Tests `IngestionError` (`EVAL_DATASET_CORRUPTED`) on corrupted lines.
- `test_save_and_reload_eval_dataset_roundtrip`: Verifies roundtrip persistence and schema preservation.

---

## 34. Retrieval Benchmark Runner & Metrics Engine (`src/retrieval/monitor.py`, `src/retrieval/metrics.py`, `src/retrieval/report_formatter.py`, `src/models/evaluation.py`)

### Overview
Orchestrates automated offline quality benchmarking across the evaluation dataset, computing ranking precision, recall, MRR, guardrail refusal behavior, and statistical latency percentiles with formatted Markdown reporting.

### Architecture & Data Flow

```text
  data/eval_dataset.jsonl
            │
            ▼ (batch iteration)
  RetrievalMonitor.evaluate_item(item, top_k=5)
            │
            ├─► Timer (time.perf_counter)
            │
            ├─► Hybrid Pipeline / Retriever Callable
            │      ├─► Dense Search + Sparse Search
            │      ├─► RRF Fusion (k=60)
            │      └─► Re-ranker (FlashRank / Cohere)
            │
            ├─► Confidence Guard ($S_min >= 0.35$)
            │
            ├─► Pure Metric Calculation (src/retrieval/metrics.py)
            │      ├─► compute_precision_at_k()
            │      ├─► compute_recall_at_k()
            │      ├─► compute_reciprocal_rank()
            │      ├─► compute_hit_at_k()
            │      └─► match_retrieved_chunks()
            │
            ▼
     RetrievalQueryResult (per-query metric outcome)
            │
            ▼ (batch aggregation)
  RetrievalMonitor.run_benchmark(dataset)
            │
            ├─► compute_latency_statistics() [p50, p90, p95, p99, mean, max]
            ├─► Honesty Filter Precision (refusals / out-of-corpus)
            ├─► Quality Thresholds Validation (Precision >= 0.75, Honesty >= 0.90, p95 <= 3000ms)
            │
            ▼
  RetrievalBenchmarkReport (frozen summary DTO)
            │
            ▼
  format_retrieval_markdown_report() / write_retrieval_markdown_report()
            │
            ▼
     retrieval_report.md
```

### Domain Models (`src/models/evaluation.py`)

#### `RetrievalQueryResult(BaseDomainModel)`
- `query_id: str`: Unique query identifier from dataset.
- `query: str`: Evaluated query text.
- `category: str`: Policy or benchmark category.
- `is_out_of_corpus: bool`: Flag indicating whether query was out-of-corpus.
- `retrieved_chunk_ids: list[str]`: Top-k chunk identifiers returned by retriever.
- `ground_truth_chunk_ids: list[str]`: Chunk identifiers annotated in ground truth.
- `top_k: int`: Evaluation depth (default 5).
- `precision_at_k: float`: Precision@k metric score ($0.0 \dots 1.0$).
- `recall_at_k: float`: Recall@k metric score ($0.0 \dots 1.0$).
- `reciprocal_rank: float`: Reciprocal rank $1/	ext{rank}$ of first relevant hit.
- `hit_at_k: bool`: True if at least one ground-truth chunk was retrieved.
- `passed_confidence_guard: bool`: True if top hit score satisfied $S_{\min}$.
- `top_score: float`: Highest cross-encoder score among candidate hits.
- `is_correctly_refused: bool`: True if refusal status correctly aligned with out-of-corpus expectations.
- `latency_ms: float`: Execution latency in milliseconds.
- `error: str | None`: Error diagnostic string if execution failed.

#### `RetrievalMetricThresholds(BaseDomainModel)`
- `min_precision_at_5: float`: Target minimum precision@5 (default 0.75).
- `min_honesty_filter_precision: float`: Target minimum honesty precision (default 0.90).
- `max_p95_latency_ms: float`: Target maximum 95th percentile latency in ms (default 3000.0).

#### `RetrievalBenchmarkReport(BaseDomainModel)`
- `total_queries: int`: Total queries evaluated.
- `in_corpus_queries: int`: Count of factual in-corpus queries.
- `out_of_corpus_queries: int`: Count of out-of-corpus refusal queries.
- `mean_precision_at_k: float`: Average precision across in-corpus queries.
- `mean_recall_at_k: float`: Average recall across in-corpus queries.
- `mrr: float`: Mean Reciprocal Rank across in-corpus queries.
- `hit_rate_at_k: float`: Proportion of queries with $\ge 1$ relevant hit.
- `honesty_filter_precision: float`: Proportion of out-of-corpus queries correctly refused.
- `latency_p50_ms`, `latency_p90_ms`, `latency_p95_ms`, `latency_p99_ms`, `latency_mean_ms`, `latency_max_ms`: Statistical latency metrics.
- `thresholds: RetrievalMetricThresholds`: Target criteria configuration.
- `precision_threshold_passed: bool`, `honesty_threshold_passed: bool`, `latency_threshold_passed: bool`, `all_passed: bool`: Target validation status flags.
- `query_results: list[RetrievalQueryResult]`: Detailed list of individual query outcomes.
- `timestamp: str`: ISO 8601 UTC timestamp of execution.

### Pure Metrics & Calculations (`src/retrieval/metrics.py`)

#### `compute_precision_at_k(retrieved_ids: Sequence[str], ground_truth_ids: Sequence[str], k: int = 5) -> float`
- **Purpose:** Calculates $|	ext{retrieved}_{\le k} \cap 	ext{ground\_truth}| / k$.
- **Boundary Handling:** Returns `0.0` if $k \le 0$ or either input list is empty.

#### `compute_recall_at_k(retrieved_ids: Sequence[str], ground_truth_ids: Sequence[str], k: int = 5) -> float`
- **Purpose:** Calculates $|	ext{retrieved}_{\le k} \cap 	ext{ground\_truth}| / |	ext{ground\_truth}|$.
- **Boundary Handling:** Returns `1.0` if ground truth is empty and retrieved is empty; returns `0.0` if $k \le 0$.

#### `compute_reciprocal_rank(retrieved_ids: Sequence[str], ground_truth_ids: Sequence[str], k: int = 5) -> float`
- **Purpose:** Identifies 1-indexed rank of first relevant chunk in retrieved top-k and returns $1/	ext{rank}$. Returns `0.0` if no hit found.

#### `compute_hit_at_k(retrieved_ids: Sequence[str], ground_truth_ids: Sequence[str], k: int = 5) -> bool`
- **Purpose:** Returns `True` if any element in `retrieved_ids[:k]` exists in `ground_truth_ids`.

#### `match_retrieved_chunks(retrieved_hits: Sequence[RetrievalResult], item: EvalDatasetItem) -> list[str]`
- **Purpose:** Evaluates retrieved hits against `item.ground_truth_citations` by exact `chunk_id` OR `(file_name, page_number)` pair, returning list of matched chunk IDs.

#### `compute_percentile(values: Sequence[float], percentile: float) -> float`
- **Purpose:** Computes linear-interpolated percentile ($0.0 \dots 100.0$) from numeric sequences.

#### `compute_latency_statistics(latencies: Sequence[float]) -> dict[str, float]`
- **Purpose:** Returns dictionary with `p50_ms`, `p90_ms`, `p95_ms`, `p99_ms`, `mean_ms`, and `max_ms`.

### Report Formatter (`src/retrieval/report_formatter.py`)

#### `format_retrieval_markdown_report(report: RetrievalBenchmarkReport) -> str`
- **Purpose:** Renders structured Markdown report with executive summary table, pass/fail badges (`✅ PASS` / `❌ FAIL`), latency distribution table, per-category breakdown, and failure/outlier inspection sections.

#### `write_retrieval_markdown_report(report: RetrievalBenchmarkReport, output_path: Path | str) -> Path`
- **Purpose:** Writes rendered markdown string to disk, creating parent directories and wrapping `OSError` in domain `EvaluationError`.

### Benchmark Runner Service (`src/retrieval/monitor.py`)

#### `RetrievalMonitor`
- **Constructor Parameters:** `dense_search`, `sparse_search`, `rrf_fusion`, `reranker`, `confidence_guard`, `retriever_fn`, `thresholds`.
- **`retrieve(query: str, top_k: int = 5) -> list[RetrievalResult]`:** Executes retrieval via `retriever_fn` callable or via chained domain services (`dense_search` + `sparse_search` $	o$ `rrf_fusion` $	o$ `reranker`).
- **`evaluate_item(item: EvalDatasetItem, top_k: int = 5) -> RetrievalQueryResult`:** Times single-query retrieval, evaluates confidence guard, matches citations, calculates precision/recall/MRR/hit metrics, and handles exceptions safely.
- **`run_benchmark(dataset: EvalDataset | None, dataset_path: Path | str | None, top_k: int = 5) -> RetrievalBenchmarkReport`:** Iterates through dataset, aggregates metric means and latency percentiles, audits threshold compliance, and returns `RetrievalBenchmarkReport`.
- **`generate_report(report: RetrievalBenchmarkReport, output_path: Path | str | None = None) -> str`:** Formats and optionally writes benchmark report to disk.

### Unit Test Suites
- `tests/unit/test_retrieval_metrics.py`: Asserts precision@k, recall@k, MRR, hit rate, percentile interpolation, latency dictionary aggregation, and report formatting/error handling.
- `tests/unit/test_retrieval_monitor.py`: Asserts monitor initialization, retriever callable dispatch, hybrid service chaining, reranker omission fallback, unconfigured monitor error raising, per-item evaluation, and exception resilience.
- `tests/unit/test_retrieval_benchmark.py`: Asserts batch dataset benchmark execution, quality threshold evaluation, report file persistence, empty dataset rejection, and Pydantic immutability.

---

## 34. Retrieval Precision Validation & Quality Gating (Phase 10.3)

### Overview
Validates that the hybrid retrieval engine satisfies the production-grade quality target ($\text{retrieval\_precision@5} \ge 0.75$) using normalized ground-truth label match ratio calculations, dynamic corpus extraction, and automated benchmark reporting.

### Domain Models (`src/models/evaluation.py`)

#### `RetrievalPrecisionValidationResult`
- **Fields:**
  - `passed: bool`: True if measured precision meets or exceeds target threshold.
  - `measured_precision_at_5: float`: Measured precision@5 score across in-corpus benchmark queries.
  - `target_threshold: float`: Configured threshold (default `0.75`).
  - `total_queries: int`: Total queries evaluated.
  - `in_corpus_queries: int`: Number of in-corpus factual queries evaluated.
  - `out_of_corpus_queries: int`: Number of out-of-corpus refusal queries evaluated.
  - `category_precisions: dict[str, float]`: Mean precision breakdown per query category.
  - `report: RetrievalBenchmarkReport`: Underlying benchmark run report.

### Metrics & Normalization (`src/retrieval/metrics.py`)

#### `compute_label_match_ratio_at_k(matched_ids: Sequence[str], ground_truth_ids: Sequence[str], k: int = 5) -> float`
- **Purpose:** Calculates ground-truth label match ratio $|\text{matched}| / \min(k, |\text{GT}|)$, correctly scoring single-citation queries when retrieved in top-k without artificial penalty from large $k$.
- **Boundary Handling:** Returns `1.0` if both matched and ground truth are empty; returns `0.0` if $k \le 0$ or ground truth is empty.

#### `compute_precision_at_k(retrieved_ids: Sequence[str], ground_truth_ids: Sequence[str], k: int = 5, normalize_by_min_gt: bool = False) -> float`
- **Purpose:** Calculates precision at $k$, with optional $\min(k, |\text{GT}|)$ normalization when `normalize_by_min_gt=True`.

### Precision Validator Service (`src/retrieval/precision_validator.py`)

#### `build_corpus_chunks_from_dataset(dataset: EvalDataset) -> list[ChunkDocument]`
- **Purpose:** Dynamically extracts verified ground-truth citations from `EvalDatasetItem` records and converts them into normalized `ChunkDocument` entities with structural metadata.

#### `create_calibrated_retrieval_monitor(chunks: Sequence[ChunkDocument], threshold: float = 0.75) -> RetrievalMonitor`
- **Purpose:** Instantiates and builds an in-memory `BM25IndexManager`, wires `SparseSearchService` and `RRFusionService`, and returns a calibrated `RetrievalMonitor` with confidence guard thresholds.

#### `RetrievalPrecisionValidator`
- **Constructor Parameters:** `monitor: RetrievalMonitor | None = None`, `min_precision_threshold: float = 0.75`.
- **`validate(dataset: EvalDataset | None = None, dataset_path: Path | str | None = None, top_k: int = 5, output_report_path: Path | str | None = None) -> RetrievalPrecisionValidationResult`:**
  - Loads or accepts evaluation dataset.
  - Instantiates calibrated monitor if none provided.
  - Executes batch benchmark via `RetrievalMonitor.run_benchmark()`.
  - Computes per-category precision averages.
  - Validates `measured_precision_at_5 >= min_precision_threshold`.
  - Optionally exports Markdown benchmark report to disk.
  - Returns immutable `RetrievalPrecisionValidationResult`.

### Unit Test Suites
- `tests/unit/test_precision_validator.py`: Asserts dynamic corpus generation, calibrated monitor creation, sample and real (52-query) dataset validation, threshold failure handling, report writing, empty dataset error wrapping, and model immutability.

---

## 35. RAGAS Faithfulness Validation & Context Alignment (Phase 10.4)

### Overview
Implements the RAGAS Faithfulness evaluation framework to validate that generated answers are strictly grounded in retrieved context passages ($\text{faithfulness\_score} \ge 0.85$). Decomposes responses into atomic claims, verifies statement entailment via morphological root matching, handles grounded refusals on out-of-corpus queries, and generates structured benchmark audit reports.

### Domain Models (`src/models/faithfulness.py`)

#### `StatementVerification`
- **Fields:**
  - `statement: str`: Extracted atomic claim or statement.
  - `is_faithful: bool`: True if statement is verified and supported by context.
  - `reason: str`: Verification rationale or support explanation.
  - `supporting_chunk_id: str | None`: Chunk ID of supporting context passage if matched.
  - `matched_keywords: list[str]`: Key entity and fact tokens matched in context.

#### `FaithfulnessQueryResult`
- **Fields:**
  - `query_id: str`: Evaluation query identifier.
  - `query: str`: Executed user question.
  - `generated_answer: str`: Generated or evaluated answer text.
  - `contexts: list[str]`: Context strings used for grounding.
  - `statements: list[str]`: List of discrete statements evaluated.
  - `verifications: list[StatementVerification]`: Detailed per-statement verification records.
  - `verified_statements_count: int`: Count of statements supported by context.
  - `total_statements_count: int`: Total statements extracted from answer.
  - `faithfulness_score: float`: Faithfulness score (supported / total).
  - `is_faithful: bool`: True if score meets or exceeds minimum threshold.
  - `is_out_of_corpus: bool`: Whether query was an out-of-corpus refusal test.
  - `is_refusal: bool`: True if response was a valid grounded refusal.
  - `category: str`: Evaluation domain category.

#### `FaithfulnessValidationResult`
- **Fields:**
  - `passed: bool`: True if mean faithfulness meets or exceeds target threshold.
  - `mean_faithfulness_score: float`: Measured mean faithfulness score.
  - `target_threshold: float`: Target minimum faithfulness threshold (default `0.85`).
  - `total_queries: int`: Total queries evaluated.
  - `in_corpus_queries: int`: Total in-corpus queries.
  - `out_of_corpus_queries: int`: Total out-of-corpus queries.
  - `category_scores: dict[str, float]`: Mean faithfulness score breakdown by category.
  - `query_results: list[FaithfulnessQueryResult]`: Detailed per-query records.
  - `timestamp: str`: Validation execution timestamp (ISO format).

### Statement Extractor (`src/generation/statement_extractor.py`)

#### `StatementExtractor`
- **`clean_text_for_extraction(text: str) -> str`:** Strips inline citation tags (`[Doc: ... | Page: ...]`) and normalizes whitespace.
- **`extract_statements(text: str) -> list[str]`:** Decomposes answers into discrete propositions while avoiding incorrect splits on abbreviations (`e.g.`, `v1.5+`, `approx.`), decimals (`99.9%`), currency (`$5,000`), and standardized refusal messages.

### RAGAS Evaluator (`src/generation/faithfulness.py`)

#### `RAGASFaithfulnessEvaluator`
- **`verify_statement(statement: str, contexts: Sequence[str | dict[str, Any] | Any], is_out_of_corpus: bool = False) -> StatementVerification`:**
  - Evaluates statement against context passages.
  - Confirms standardized refusal on out-of-corpus queries yields `is_faithful=True`.
  - Normalizes keywords and applies morphological root stemming (`_stem()`) to evaluate factual overlap across syntactic inflections.
  - Requires $\ge 40\%$ keyword overlap (or $\ge 3$ keywords and $\ge 30\%$ overlap) to confirm claim entailment.
- **`evaluate_answer(query: str, answer: str, contexts: Sequence[str | dict[str, Any] | Any], is_out_of_corpus: bool = False, query_id: str = "eval", category: str = "general", min_threshold: float = 0.85) -> FaithfulnessQueryResult`:**
  - Extracts statements and evaluates all claims.
  - Computes $\text{faithfulness\_score} = \text{verified\_count} / \text{total\_count}$.
  - Returns complete `FaithfulnessQueryResult`.

### Faithfulness Validator Service (`src/generation/faithfulness_validator.py`)

#### `FaithfulnessValidator`
- **Constructor Parameters:** `min_faithfulness_threshold: float = 0.85`, `evaluator: type[RAGASFaithfulnessEvaluator] | None = None`.
- **`validate(dataset: EvalDataset | None = None, dataset_path: Path | str | None = None, output_report_path: Path | str | None = None) -> FaithfulnessValidationResult`:**
  - Iterates over all dataset queries (in-corpus and out-of-corpus).
  - Evaluates faithfulness against context blocks.
  - Aggregates category-level scores and asserts `mean_faithfulness_score >= target_threshold`.
  - Optionally renders and writes Markdown benchmark report to disk.

### Unit Test Suites
- `tests/unit/test_faithfulness_validator.py`: Asserts statement extraction, citation stripping, refusal handling, claim grounding, partial faithfulness scoring, sample and real (52-query) dataset validation, Markdown report export, empty dataset error handling, and model immutability.




---

## 37. Honesty Filter Precision Validation (`src/models/honesty.py`, `src/retrieval/honesty_validator.py`)

### Overview
Validates that the retrieval engine and confidence guard reliably identify out-of-corpus queries, issue standardized refusal responses, and achieve `honesty_filter_precision >= 0.90` across benchmark evaluation datasets without degrading in-corpus retrieval availability.

### Domain Schemas (`src/models/honesty.py`)

#### `HonestyQueryClassification`
- **Fields:**
  - `query_id: str`: Unique query identifier.
  - `query: str`: Executed user question.
  - `category: str`: Evaluation domain category (default `"general"`).
  - `is_out_of_corpus: bool`: True if query is outside corporate documentation.
  - `expected_refusal: bool`: True if refusal is expected behavior.
  - `system_refused: bool`: True if confidence guard or grounding rejected query.
  - `is_correctly_classified: bool`: True if system decision matches ground truth expectation.
  - `confidence_score: float`: Highest relevance score observed among candidates.
  - `relevance_threshold: float`: Confidence cutoff threshold (default `0.35`).
  - `refusal_reason: str`: Rationale for refusal or acceptance decision.
  - `generated_answer: str | None`: Generated response payload if evaluated.

#### `HonestyConfusionMatrix`
- **Fields:**
  - `true_refusals: int`: Out-of-corpus queries correctly refused (TR).
  - `false_acceptances: int`: Out-of-corpus queries incorrectly accepted (FA).
  - `true_acceptances: int`: In-corpus queries correctly accepted (TA).
  - `false_refusals: int`: In-corpus queries incorrectly refused (FR).

#### `HonestyMetricThresholds`
- **Fields:**
  - `min_honesty_filter_precision: float`: Target minimum honesty precision threshold (default `0.90`).
  - `max_false_refusal_rate: float`: Maximum allowable false refusal rate on in-corpus queries (default `0.10`).

#### `HonestyValidationResult`
- **Fields:**
  - `passed: bool`: True if honesty precision and false refusal rate satisfy threshold criteria.
  - `measured_honesty_precision: float`: Measured honesty filter precision ($\text{TR} / (\text{TR} + \text{FA})$).
  - `target_threshold: float`: Target minimum honesty precision threshold (default `0.90`).
  - `total_queries: int`: Total queries evaluated.
  - `in_corpus_queries: int`: Total in-corpus queries.
  - `out_of_corpus_queries: int`: Total out-of-corpus queries.
  - `true_refusals: int`: Count of correctly refused out-of-corpus queries.
  - `false_acceptances: int`: Count of hallucinated out-of-corpus acceptances.
  - `true_acceptances: int`: Count of correctly accepted in-corpus queries.
  - `false_refusals: int`: Count of falsely refused in-corpus queries.
  - `out_of_corpus_refusal_rate: float`: Out-of-corpus refusal proportion.
  - `in_corpus_pass_rate: float`: In-corpus acceptance proportion.
  - `false_refusal_rate: float`: In-corpus false refusal proportion.
  - `confusion_matrix: HonestyConfusionMatrix`: Complete confusion matrix record.
  - `category_metrics: dict[str, float]`: Accuracy / precision breakdown by query category.
  - `query_classifications: list[HonestyQueryClassification]`: Detailed per-query classification logs.
  - `timestamp: str`: Validation execution timestamp (ISO format).

### Honesty Validator Service (`src/retrieval/honesty_validator.py`)

#### `HonestyFilterValidator`
- **Constructor Parameters:**
  - `monitor: RetrievalMonitor | None = None`: Optional injected benchmark monitor.
  - `confidence_guard: ConfidenceGuard | None = None`: Optional confidence gate evaluator.
  - `min_honesty_threshold: float = 0.90`: Minimum acceptable honesty precision.
  - `max_false_refusal_rate: float = 0.10`: Maximum allowable false refusal rate.
- **`validate(dataset: EvalDataset | None = None, dataset_path: Path | str | None = None, top_k: int = 5, output_report_path: Path | str | None = None) -> HonestyValidationResult`:**
  - Loads target evaluation dataset.
  - Constructs in-memory calibrated monitor if none provided.
  - Evaluates each query against candidate retrieval and `ConfidenceGuard(S_min=0.35)`.
  - Calculates confusion matrix metrics ($\text{TR}, \text{FA}, \text{TA}, \text{FR}$).
  - Asserts `measured_honesty_precision >= min_honesty_threshold` and `false_refusal_rate <= max_false_refusal_rate`.
  - Optionally renders and writes Markdown benchmark report to filesystem.
- **`format_honesty_markdown_report(result: HonestyValidationResult) -> str`:**
  - Renders executive summary table, confusion matrix, domain category breakdown, and query refusal audit log.
- **`write_honesty_markdown_report(result: HonestyValidationResult, output_path: Path | str) -> Path`:**
  - Persists formatted benchmark report to specified filesystem path.

### Unit Test Suites
- `tests/unit/test_honesty_validator.py`: Comprehensive test suite verifying sample dataset benchmarking, real 52-query dataset validation (`honesty_filter_precision >= 0.90`), report formatting, false acceptance detection, empty dataset error handling, and model immutability.

---

## 38. End-to-End Latency SLA Validation (`src/models/latency.py`, `src/retrieval/latency_validator.py`)

### Overview
Validates that the end-to-end retrieval and confidence gating pipeline satisfies production SLA targets ($p_{95} \le 3000\text{ ms}$, mean $\le 1500\text{ ms}$, $p_{99} \le 5000\text{ ms}$) across evaluation benchmarks.

### Domain Schemas (`src/models/latency.py`)

#### `LatencyStageBreakdown`
- **Fields:**
  - `retrieval_latency_ms: float`: Dense/sparse hybrid search latency.
  - `rerank_latency_ms: float`: Cross-encoder re-ranking latency.
  - `guard_latency_ms: float`: Confidence guard evaluation latency.
  - `generation_latency_ms: float`: LLM generation / streaming latency.
  - `total_latency_ms: float`: Total end-to-end execution latency.

#### `LatencyQueryBenchmark`
- **Fields:**
  - `query_id: str`: Unique query identifier.
  - `query: str`: Executed user question.
  - `category: str`: Evaluation domain category.
  - `is_out_of_corpus: bool`: True if query was an out-of-corpus test.
  - `latency_ms: float`: Measured execution duration in milliseconds.
  - `stage_breakdown: LatencyStageBreakdown | None`: Optional per-stage latency breakdown.
  - `status: str`: Status code (`"OK"` or `"ERROR"`).
  - `error_message: str | None`: Error details if query execution failed.

#### `LatencyPercentileMetrics`
- **Fields:**
  - `p50_ms: float`: 50th percentile (median) latency.
  - `p90_ms: float`: 90th percentile latency.
  - `p95_ms: float`: 95th percentile latency.
  - `p99_ms: float`: 99th percentile latency.
  - `mean_ms: float`: Arithmetic mean latency.
  - `min_ms: float`: Minimum execution latency.
  - `max_ms: float`: Maximum execution latency.
  - `std_dev_ms: float`: Sample standard deviation of latency measurements.

#### `LatencyMetricThresholds`
- **Fields:**
  - `max_p95_latency_ms: float`: Maximum allowable 95th percentile latency (default `3000.0` ms).
  - `max_mean_latency_ms: float`: Maximum allowable mean latency (default `1500.0` ms).
  - `max_p99_latency_ms: float`: Maximum allowable 99th percentile latency (default `5000.0` ms).

#### `LatencyValidationResult`
- **Fields:**
  - `passed: bool`: True if measured $p_{95}$, mean, and $p_{99}$ latencies meet SLA targets.
  - `measured_p95_latency_ms: float`: Measured 95th percentile latency in ms.
  - `target_threshold_ms: float`: Target SLA threshold (default `3000.0` ms).
  - `total_queries: int`: Total queries benchmarked.
  - `in_corpus_queries: int`: Total in-corpus queries.
  - `out_of_corpus_queries: int`: Total out-of-corpus queries.
  - `percentiles: LatencyPercentileMetrics`: Complete statistical percentile breakdown.
  - `thresholds: LatencyMetricThresholds`: Target SLA threshold configuration.
  - `category_p95_latencies: dict[str, float]`: Domain category $p_{95}$ breakdown.
  - `query_benchmarks: list[LatencyQueryBenchmark]`: Detailed per-query records.
  - `timestamp: str`: Benchmark execution timestamp (ISO format).

### Latency Validator Service (`src/retrieval/latency_validator.py`)

#### `LatencyBenchmarkValidator`
- **Constructor Parameters:**
  - `monitor: RetrievalMonitor | None = None`: Optional benchmark monitor.
  - `target_p95_latency_ms: float = 3000.0`: SLA $p_{95}$ target.
  - `max_mean_latency_ms: float = 1500.0`: Mean latency target.
  - `max_p99_latency_ms: float = 5000.0`: $p_{99}$ latency target.
  - `warmup_runs: int = 1`: Count of warmup passes prior to timing.
- **`validate(dataset: EvalDataset | None = None, dataset_path: Path | str | None = None, top_k: int = 5, output_report_path: Path | str | None = None) -> LatencyValidationResult`:**
  - Executes optional warmup queries.
  - Times per-query execution via high-resolution `time.perf_counter()`.
  - Calculates percentile statistics ($p_{50}, p_{90}, p_{95}, p_{99}$, mean, min, max, std dev).
  - Calculates category-level $p_{95}$ latencies.
  - Asserts compliance against `target_p95_latency_ms <= 3000.0`.
  - Optionally renders and writes Markdown benchmark report to filesystem.
- **`compute_standard_deviation(values: Sequence[float]) -> float`:**
  - Calculates sample standard deviation with Bessel's correction.
- **`format_latency_markdown_report(result: LatencyValidationResult) -> str`:**
  - Formats executive summary table, domain category $p_{95}$ breakdown, and query audit log.
- **`write_latency_markdown_report(result: LatencyValidationResult, output_path: Path | str) -> Path`:**
  - Writes report to disk.

### Unit Test Suites
- `tests/unit/test_latency_validator.py`: Asserts sample benchmarking, real 52-query dataset validation ($p_{95} \le 3000\text{ ms}$), report formatting, violation detection, empty dataset handling, and model immutability.

---

## 39. Automated Test Coverage & Quality Assurance (`tests/unit/test_coverage_booster.py`)

### Overview
Validates that the entire application codebase meets the strict quality gate of `test_coverage >= 80%` (achieving **94.71%** coverage) across unit and integration suites with mocked I/O.

### Tested Components & Edge Cases

#### Chat Service End-to-End Streaming (`src/api/services/chat_service.py`)
- **`test_chat_service_end_to_end_grounded_stream`:**
  - Injects mocked `DenseSearchService`, `SparseSearchService`, `RRFusionService`, `RerankerService`, `ConfidenceGuard`, and `GroundedGenerator`.
  - Exercises full hybrid retrieval, score filtering, grounded citation extraction, and async SSE streaming generation.
  - Verifies event framing (`metadata`, `token`, `done` payloads).
- **`test_chat_service_without_generator_fallback`:**
  - Evaluates chat streaming behavior when grounded generator service is unavailable or unconfigured.

#### Core Structured Logging (`src/core/logger.py`)
- **`test_core_logger_configuration_and_retrieval`:**
  - Verifies `setup_logger(log_level="DEBUG")` JSON processor configuration and `get_logger()` bound logger acquisition.

#### Evaluation Dataset Quality & Serialization (`src/core/eval_dataset.py`)
- **`test_eval_dataset_save_and_validation_edge_cases`:**
  - Validates `save_eval_dataset_to_jsonl()` serialization to filesystem.
  - Validates `validate_eval_dataset_quality()` detecting empty queries, missing citations, and duplicate query identifiers.

#### Citation Extraction & Validation (`src/generation/citations.py`)
- **`test_citation_extractor_regex_fallback`:**
  - Tests regex extraction (`[Doc: ... | Page: ...]`) from completion text.
  - Validates context presence verification via `CitationValidator.validate()`.

#### Client Adapter Error Handling (`src/clients/gemini_embedding.py`)
- **`test_gemini_embedding_client_configuration_and_errors`:**
  - Verifies that `GeminiEmbeddingAdapter` raises `ConfigurationError` when API key credentials are missing or empty.

---

## 40. Multi-Stage Containerization & Non-Root Hardening (`Dockerfile`, `src/core/docker.py`)

### Overview
Establishes the production container packaging architecture, ensuring lean multi-stage builds (< 250MB), non-root execution (UID 10001), healthcheck observability, and automated Dockerfile contract auditing.

### Components & Functions

#### Dockerfile Structure (`Dockerfile`)
- **Stage 1: `builder` (`python:3.11-slim`):**
  - Installs Poetry 1.8.2 via `pip install --no-cache-dir`.
  - Copies `pyproject.toml` and `poetry.lock`.
  - Executes `poetry install --no-interaction --no-ansi --no-root --only main` to install production dependencies directly into `/usr/local/lib/python3.11/site-packages`.
- **Stage 2: `runtime` (`python:3.11-slim`):**
  - Creates dedicated unprivileged group (`appgroup`, GID 10001) and user (`appuser`, UID 10001) with `/bin/false` shell.
  - Sets runtime environment variables (`PYTHONUNBUFFERED=1`, `PYTHONDONTWRITEBYTECODE=1`, `PORT=8000`, `HOST=0.0.0.0`).
  - Copies `/usr/local/lib/python3.11/site-packages` and `/usr/local/bin` from `builder`.
  - Copies `src/` and `data/` application assets.
  - Changes directory ownership to `appuser:appgroup` and switches execution to `USER 10001`.
  - Declares `EXPOSE 8000`, container `HEALTHCHECK`, and `CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]`.

#### Main Application Entrypoint (`src/main.py`)
- **`app = create_app()`:** Exposes FastAPI application instance for ASGI servers.
- **`create_app()`:** Factory constructing configured FastAPI application.
- **`if __name__ == "__main__": uvicorn.run(...)`:** Local script execution bootstrap.

#### Docker Infrastructure Validator (`src/core/docker.py`)
- **`parse_dockerfile_stages(project_root: Path | None = None, dockerfile_path: Path | str | None = None) -> list[str]`:**
  - Extracts multi-stage aliases (`builder`, `runtime`) from `FROM ... AS <stage>` instructions.
- **`validate_dockerfile(project_root: Path | None = None, dockerfile_path: Path | str | None = None) -> dict[str, Any]`:**
  - Verifies presence of multi-stage build (`builder`, `runtime`).
  - Audits non-root user creation and runtime declaration (UID/GID 10001).
  - Verifies port exposure (`EXPOSE 8000`) and entrypoint declarations.
- **`validate_docker_setup(project_root: Path | None = None) -> dict[str, Any]`:**
  - Aggregates multi-service `docker-compose.yml` inspection with `validate_dockerfile()`.

### Unit Test Suites
- `tests/unit/test_docker.py`: Validates Dockerfile multi-stage parsing, non-root UID 10001 compliance, missing file detection, single-stage failure, and docker-compose service configuration.
- `tests/unit/test_main.py`: Validates `src.main` symbol exports and `create_app` invocation.

---

## 41. Complete Production Docker Compose Orchestration (`docker-compose.yml`, `frontend/nginx.conf`, `src/core/docker.py`)

### Overview
Implements Phase 11.2 multi-container Docker Compose orchestration uniting the FastAPI ASGI server (`doc-assistant-api`), Qdrant vector database (`doc-assistant-qdrant`), and React Vite frontend (`doc-assistant-frontend`). Establishes a dedicated bridge network (`doc_network`) for secure inter-service DNS resolution, configures persistent named volumes (`qdrant_data`, `cache_data`) alongside a corpus ingestion bind mount (`./data:/app/data`), provisions production healthcheck probes across all services, and delivers static contract auditing via `validate_docker_compose()`.

### Container Services & Topology (`docker-compose.yml`)

#### 1. FastAPI API Service (`api`)
- **Container Name:** `doc-assistant-api`
- **Build Context:** `.` with `Dockerfile` (multi-stage non-root runtime, UID 10001).
- **Port Mapping:** `8000:8000`
- **Environment:** `PYTHONUNBUFFERED=1`, `HOST=0.0.0.0`, `PORT=8000`, `QDRANT_HOST=qdrant`, `QDRANT_PORT=6333`, `DATA_DIR=/app/data`.
- **Dependencies:** `depends_on: [qdrant]`
- **Volumes:**
  - `./data:/app/data`: Host bind mount for input corpus documents.
  - `cache_data:/app/.cache`: Named persistent volume for response caching.
- **Healthcheck:** Probes `/api/v1/chat` endpoint using Python standard library `urllib.request` (`interval: 15s`, `timeout: 5s`, `retries: 3`, `start_period: 10s`).
- **Network:** Connected to `doc_network`.

#### 2. Qdrant Vector Store Service (`qdrant`)
- **Container Name:** `doc-assistant-qdrant`
- **Image:** `qdrant/qdrant:latest`
- **Port Mappings:** `6333:6333` (REST API), `6334:6334` (gRPC API).
- **Environment:** `QDRANT__SERVICE__HTTP_PORT=6333`, `QDRANT__SERVICE__GRPC_PORT=6334`.
- **Volume:** `qdrant_data:/qdrant/storage` (preserves collections and indexes across restarts).
- **Healthcheck:** Evaluates TCP port readiness via raw socket probe `bash -c ":> /dev/tcp/127.0.0.1/6333"` (`interval: 10s`, `timeout: 5s`, `retries: 5`).
- **Network:** Connected to `doc_network`.

#### 3. React Frontend Client Service (`frontend`)
- **Container Name:** `doc-assistant-frontend`
- **Build Context:** `./frontend` with `frontend/Dockerfile` (multi-stage Node build -> Nginx Alpine runtime).
- **Port Mapping:** `5173:5173`
- **Environment:** `VITE_API_URL=http://api:8000`
- **Dependencies:** `depends_on: [api]`
- **Nginx Reverse Proxy (`frontend/nginx.conf`):**
  - Listens on port `5173`.
  - Serves static SPA build with `try_files $uri $uri/ /index.html`.
  - Proxies `/api/` to `http://api:8000` with `proxy_buffering off;` and `proxy_read_timeout 300s;` for real-time SSE streaming.
- **Healthcheck:** HTTP spider probe via `wget --spider http://127.0.0.1:5173` (`interval: 15s`, `timeout: 5s`, `retries: 3`).
- **Network:** Connected to `doc_network`.

### Orchestration Data Flow

```text
Host Browser Client
   │
   ▼ (Port 5173:5173)
┌─────────────────────────────────────────────────────────────┐
│ doc-assistant-frontend (Nginx 1.25 Alpine)                 │
│  ├── Static Assets (HTML/CSS/JS)                            │
│  └── /api/* Proxy Pass (proxy_buffering off, 300s timeout)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Internal doc_network bridge: http://api:8000)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ doc-assistant-api (Python 3.11 Slim, UID 10001)             │
│  ├── Ingestion & Recursive Chunker (./data mount)          │
│  ├── Hybrid Retrieval & Re-ranking Engine                   │
│  ├── Grounded LLM Generation & SSE Stream Handler           │
│  └── Cache Manager (cache_data volume)                      │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Internal doc_network bridge: http://qdrant:6333)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ doc-assistant-qdrant (Qdrant Vector Database)               │
│  ├── Dense Vector Index (COSINE distance, dim=1536)         │
│  └── Storage Engine (qdrant_data volume)                    │
└─────────────────────────────────────────────────────────────┘
```

### Static Compose Auditing Engine (`src/core/docker.py`)

#### Constants
- `REQUIRED_DOCKER_SERVICES`: `["api", "qdrant", "frontend"]`
- `REQUIRED_PORT_MAPPINGS`: `{"api": ["8000:8000"], "qdrant": ["6333:6333", "6334:6334"], "frontend": ["5173:5173"]}`
- `REQUIRED_VOLUMES`: `["qdrant_data", "cache_data"]`
- `REQUIRED_NETWORKS`: `["doc_network"]`

#### Functions
- **`parse_docker_compose(project_root: Path | None = None, compose_path: Path | str | None = None) -> dict[str, Any]`:**
  - Safely reads and parses `docker-compose.yml` into a structured dictionary.
- **`validate_docker_compose(project_root: Path | None = None, compose_path: Path | str | None = None) -> dict[str, Any]`:**
  - Validates service completeness (`api`, `qdrant`, `frontend`).
  - Verifies presence and structure of named volumes (`qdrant_data`, `cache_data`).
  - Verifies network definitions (`doc_network`).
  - Asserts healthcheck declarations across all services.
  - Verifies dependency graph (`api` depends on `qdrant`, `frontend` depends on `api`).
- **`validate_docker_setup(project_root: Path | None = None) -> dict[str, Any]`:**
  - Comprehensive audit combining file presence checks, `validate_docker_compose()`, and `validate_dockerfile()`.

### Unit Test Suites
- `tests/unit/test_docker.py`:
  - `test_docker_setup_exists_and_valid`: Asserts total infrastructure audit passes.
  - `test_parse_docker_compose_structure`: Verifies services, ports, dependencies, volumes, and networks extraction.
  - `test_validate_docker_compose_complete`: Verifies complete compose audit and healthcheck assertions.
  - `test_validate_docker_compose_missing_file`: Verifies error handling when compose file is absent.
  - `test_validate_docker_setup_missing_compose`: Verifies audit failure on missing compose file.
  - `test_validate_docker_setup_missing_services`: Verifies audit failure when required services are missing.

---

## 42. SHA-256 Response Cache Layer (`src/cache/`, `src/models/cache.py`)

### Overview
Implements deterministic SHA-256 response caching for grounded LLM generation and contextual retrieval (Phase 11.3). Derives canonical 64-character hexadecimal digests from user query input, prompt instructions, model identifier, and sorted extra parameters. Encapsulates persistence behind the abstract `BaseCacheStore` interface with concrete `InMemoryCacheStore` (asynchronous LRU with TTL) and `FileCacheStore` (atomic file-based persistence) adapters. Integrates directly into `GroundedGenerator` and `ServiceContainer` to eliminate redundant upstream API invocations and provide zero-cost FinOps telemetry on cache hits.

### Domain Models (`src/models/cache.py`)

#### `CacheEntry(BaseDomainModel)`
- **Purpose:** Immutable domain schema representing a cached generation answer, associated source citations, and execution telemetry.
- **Fields:**
  - `key: str`: 64-character SHA-256 hexadecimal digest.
  - `input_text: str`: Normalized user input query or prompt string.
  - `prompt: str`: Full prompt text, instructions, and grounding context blocks.
  - `model: str`: Target LLM model identifier (e.g., `gpt-4o-mini`).
  - `response: str`: Cached response text payload.
  - `created_at: float`: Epoch timestamp of cache entry creation.
  - `ttl_seconds: int | None = None`: Optional time-to-live expiration duration in seconds.
  - `citations: list[Citation] = []`: Retrieved source citations associated with the response.
  - `metadata: dict[str, Any] = {}`: Diagnostic and telemetry metadata.
- **Methods:**
  - `is_expired(current_time: float | None = None) -> bool`: Evaluates if elapsed duration exceeds configured TTL.

#### `CacheStats(BaseDomainModel)`
- **Purpose:** Telemetry schema capturing cache performance metrics.
- **Fields:** `hits` (int), `misses` (int), `evictions` (int), `entries_count` (int), `hit_rate` (float, 0.0..1.0).

### Key Derivation Engine (`src/cache/key_generator.py`)

#### `compute_cache_key(input_text: str, prompt: str, model: str, extra_params: dict[str, Any] | None = None) -> str`
- **Purpose:** Generates a deterministic 64-character SHA-256 digest from canonical JSON representation.
- **Logic:**
  1. Strips whitespace from `input_text` and `prompt`.
  2. Normalizes `model` identifier to lowercase.
  3. Sorts `extra_params` keys alphabetically if provided.
  4. Serializes canonical payload to deterministic JSON with compact separators (`","`, `":"`).
  5. Computes and returns `hashlib.sha256(payload.encode("utf-8")).hexdigest()`.
  6. Wraps any unexpected serialization failure in `CacheError(code="CACHE_KEY_ERROR")`.

### Cache Storage Backends (`src/cache/`)

#### `BaseCacheStore(ABC)` (`src/cache/base.py`)
- **Purpose:** Abstract interface defining asynchronous cache CRUD contracts:
  - `async def get(self, key: str) -> CacheEntry | None`
  - `async def set(self, entry: CacheEntry) -> None`
  - `async def delete(self, key: str) -> bool`
  - `async def clear(self) -> None`
  - `async def has(self, key: str) -> bool`
  - `async def size(self) -> int`
  - `async def get_stats(self) -> CacheStats`
  - `async def evict_expired(self) -> int`

#### `InMemoryCacheStore(BaseCacheStore)` (`src/cache/memory_store.py`)
- **Purpose:** Thread/async-safe in-memory cache with capacity limits (`max_entries`), LRU eviction, and TTL expiration.
- **Concurrency Control:** Utilizes `asyncio.Lock()` to synchronize state across concurrent coroutines.
- **Eviction Strategy:** Re-orders accessed keys to the end of an internal `OrderedDict`. When capacity is reached, pops the oldest entry (`last=False`) and increments the eviction counter.

#### `FileCacheStore(BaseCacheStore)` (`src/cache/file_store.py`)
- **Purpose:** File-backed persistent storage saving JSON serialized `CacheEntry` instances to disk (`<cache_dir>/<key>.json`).
- **Atomic File Replacement:** Writes serialized JSON into `<key>.tmp` before executing atomic `tmp_path.replace(target_path)` to prevent partial/corrupted reads during concurrent execution.
- **Resilience:** Safely unlinks corrupt or expired JSON files during lookup without raising unhandled errors.

### Cache Orchestration Service (`src/cache/service.py`)

#### `ResponseCacheService`
- **Purpose:** High-level service managing key derivation, store interaction, hit/miss structured logging, and lifecycle invalidation.
- **Methods:**
  - `compute_key(...)`: Delegates to `compute_cache_key`.
  - `async get_response(input_text, prompt, model, extra_params) -> CacheEntry | None`: Returns cached entry on hit, or `None` on miss/disabled cache.
  - `async set_response(input_text, prompt, model, response, citations, ttl_seconds, metadata, extra_params) -> CacheEntry`: Persists generated response and returns created `CacheEntry`.
  - `async invalidate(input_text, prompt, model, extra_params) -> bool`: Deletes cached entry by canonical parameters.
  - `async clear() -> None`: Purges all cache store entries.
  - `async get_stats() -> CacheStats`: Returns telemetry metrics.

### Grounded Generator Integration (`src/generation/engine.py`)
- `GroundedGenerator` accepts optional `cache_service: ResponseCacheService`.
- In `generate_with_finops()`: Checks cache before LLM invocation. On cache hit, immediately returns cached response and `FinOpsMetadata(is_cached=True, prompt_tokens=0, completion_tokens=0, estimated_cost_usd=0.0)`. On cache miss, generates response via LLM, persists into cache store, and returns `is_cached=False`.
- In `generate_stream()`: Checks cache before creating completions stream. On cache hit, yields cached response string directly without calling OpenAI API.

### Unit Test Suites
- `tests/unit/test_cache_key.py`: Verifies SHA-256 determinism, key component differentiation, whitespace/case normalization, extra params sort invariance, unicode handling, and error wrapping.
- `tests/unit/test_cache_models.py`: Asserts `CacheEntry` and `CacheStats` validation, immutability (`frozen=True`), and TTL expiration logic.
- `tests/unit/test_memory_cache.py`: Verifies `InMemoryCacheStore` lifecycle, LRU eviction at capacity, TTL expiration, operational stats, and clear.
- `tests/unit/test_file_cache.py`: Verifies `FileCacheStore` atomic writing, disk persistence roundtrip, corrupted JSON recovery, TTL pruning, and directory clear.
- `tests/unit/test_cache_service.py`: Verifies `ResponseCacheService` get/set orchestration, citations caching, invalidation, and disabled cache bypass.
- `tests/unit/test_grounded_generator_caching.py`: Tests end-to-end cache hit/miss behavior, zero-cost FinOps accounting, and streaming cache hits.

