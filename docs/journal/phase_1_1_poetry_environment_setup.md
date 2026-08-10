# Architectural Journal — Phase 1.1: Poetry Environment Setup & Python 3.11+ Constraints

> **Phase:** 1.1 | **Date:** 2026-08-10 | **Status:** Completed

---

## 🎯 Objective
Initialize the Poetry project for `doc_assistant` with strict Python 3.11+ language constraints, comprehensive static analysis tooling (Ruff & Mypy strict mode), environment version assertion utilities, and app dashboard test runner integration.

---

## 💡 Architectural Choices

### 1. Enforcing Python >= 3.11 Runtime & Compiler Constraints
- **Context:** Corporate RAG platforms require high-throughput text chunking, embedding serialization, vector operations, and SSE response streaming.
- **Decision:** Constrain language runtime to Python `^3.11` in `pyproject.toml`, target `py311` in Ruff, and specify `python_version = "3.11"` in Mypy strict mode.
- **Rationale:** Python 3.11 delivers significant performance improvements (up to 60% CPython execution speedups via specialized interpreter frames and adaptive bytecode), native `ExceptionGroup` handling for concurrent task execution, and refined typing features.

### 2. Runtime Version Validation (`src/core/environment.py`)
- **Context:** Environment misconfigurations or deployment on legacy Python runtimes (e.g., 3.9/3.10) can cause silent failures or type assertion breakdowns.
- **Decision:** Built programmatic version validation routines (`check_python_version`, `validate_poetry_config`, `get_environment_info`).
- **Rationale:** Early startup checks fail fast with structured diagnostics if the host runtime fails minimum language constraints.

### 3. Programmatic Dashboard Test Runner (`tests/runner.py`)
- **Context:** Integration with developer dashboards requires a clean, structured Python API for executing test suites without shell subprocess dependence.
- **Decision:** Implemented `run_project_tests()` wrapping `pytest.main()`, returning structured outcome dictionaries (`status`, `exit_code`, `target`).
- **Rationale:** Enables direct programmatic invocation from frontend dashboards, CLI launchers, and automated QA gates.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Python >= 3.11 Constraint** | Incompatibility with legacy Python runtimes (3.9 / 3.10). | Enforce version bounds in `pyproject.toml` and Docker base image (`python:3.11-slim`). |
| **In-Code Runtime Validation** | Adds minimal startup overhead (< 1ms). | Cache validation results and run check only during lifecycle startup. |
