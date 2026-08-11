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

#### `DebugRetrievalResponse(BaseDomainModel)` (`src/models/retrieval.py`)
- **Purpose:** Detailed retrieval debugging payload exposing hits across dense, sparse, RRF fusion, and re-ranking stages.
- **Fields:** `query` (str), `dense_hits` (list[RetrievalResult]), `sparse_hits` (list[RetrievalResult]), `rrf_fused` (list[RetrievalResult]), `final_reranked` (list[RetrievalResult]).

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
