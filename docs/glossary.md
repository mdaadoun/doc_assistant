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



