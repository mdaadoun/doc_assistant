# Architectural Journal — Phase 1.4: Modular Package Layout Setup (src/* & frontend/)

> **Phase:** 1.4 | **Date:** 2026-08-10 | **Status:** Completed

---

## 🎯 Objective
Establish a production-ready, modular package architecture by scaffolding isolated domain packages within `src/` (`api`, `retrieval`, `generation`, `ingestion`, `clients`, `models`, `core`, `cache`) and a root `frontend/` presentation directory. Implement a package layout auditor (`src/core/layout.py`) to programmatically validate project structural integrity during test suite execution.

---

## 💡 Architectural Choices

### 1. Explicit `src/` Layout Separation with Dedicated Domain Packages
- **Context:** Large-scale RAG systems require strict boundary separation between presentation, core retrieval/generation domain logic, data models, external client adapters, and infrastructure caches.
- **Decision:** Scaffold isolated Python subpackages under `src/` (`api`, `retrieval`, `generation`, `ingestion`, `clients`, `models`, `core`, `cache`) with explicit package includes in `pyproject.toml`.
- **Rationale:** Prevents circular dependencies, isolates presentation logic from data layers, and avoids implicit imports of the editable source directory during testing.

### 2. Standalone `frontend/` Presentation Directory Outside `src/`
- **Context:** Combining web frontend application source code with Python package source directories creates noise for Python linting, typing, and packaging tools.
- **Decision:** Place the `frontend/` directory at the project root outside `src/`, containing a Vite/React application manifest.
- **Rationale:** Decouples Node/React packaging and build pipelines from Python toolchains while preserving a clean mono-repo project layout.

### 3. Programmatic Package Layout Auditor (`src/core/layout.py`)
- **Context:** Submodule scaffold completeness can regress as files or directories are added or moved.
- **Decision:** Implement `validate_package_layout()` in `src/core/layout.py` to audit `REQUIRED_PACKAGES` and `REQUIRED_DIRECTORIES`.
- **Rationale:** Enables unit tests and dashboard test runners to detect missing package scaffolding or missing `__init__.py` entry points automatically.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **`src/` Package Layout** | Requires explicit package declarations in `pyproject.toml` and pythonpath configuration. | Configured Poetry `packages` list and added `pythonpath = [".", "src"]` in `pytest.ini`. |
| **Root `frontend/` Directory** | Mypy or linters might attempt to inspect `frontend/` directory unless excluded. | Added `^frontend/` to `exclude` list in `pyproject.toml` `[tool.mypy]` section. |
| **Automated Layout Auditing** | Adds layout validation checks into unit test suite. | Utilized fast `Path.is_dir()` and `Path.is_file()` filesystem checks executing in under 1ms. |
