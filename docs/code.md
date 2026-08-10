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




