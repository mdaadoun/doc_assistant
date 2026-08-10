# Interview Questions & Technical Architecture Q&A

> **Scope:** Architecture decisions, design trade-offs, and technical rationale for Corporate Document Assistant.

---

## Phase 1.1: Poetry Project Setup & Environment Constraints

### Q1: Why enforce Python 3.11+ constraints for this Corporate Doc Assistant project?
**Answer:**
Python 3.11 introduces significant runtime performance optimizations (up to 60% faster CPython interpreter execution via specialized interpreter frames), native `ExceptionGroup` support for structured async task error handling, and enhanced typing features (`Self`, `LiteralString`, `TaskGroup`). For a production corporate RAG platform performing high-throughput text parsing, vector serialization, and real-time SSE streaming, Python 3.11+ provides substantial concurrency and memory benefits.

---

### Q2: How does the environment module prevent deployment on incompatible runtimes?
**Answer:**
The `src/core/environment.py` module evaluates `sys.version_info` against `MIN_PYTHON_VERSION` (3, 11) and inspects `pyproject.toml` for valid Poetry declarations and version bounds. By triggering these checks during application lifecycle startup, the application fails fast with diagnostic logs rather than encountering subtle typing or runtime errors mid-execution.

---

### Q3: What is the purpose of registering unit tests into the app dashboard test runner?
**Answer:**
Registering unit tests into `tests/runner.py` via `run_project_tests()` exposes a programmatic Python API for invoking `pytest.main()`. This allows local dashboard applications, management CLIs, and health probes to run test suites programmatically and receive structured JSON status payloads (`PASSED`/`FAILED`, exit code, target path) without spawning raw shell subprocesses.

---

## Phase 1.2: Code Quality Infrastructure Configuration

### Q1: Why use Ruff instead of separate tools like Black, Flake8, and isort?
**Answer:**
Ruff replaces multiple legacy Python linters and formatters with a single high-performance Rust binary, executing checks up to 100x faster while ensuring consistent rule enforcement and simplified configuration.

---

### Q2: How does Mypy strict mode enforce boundary safety in Python services?
**Answer:**
Mypy strict mode disallows untyped function signatures, implicit Optional types, and untyped decorators. This guarantees that internal domain models and external API boundaries maintain explicit contract types, preventing runtime TypeError and AttributeError exceptions.

---

### Q3: What is the purpose of .secrets.baseline when using detect-secrets in pre-commit hooks?
**Answer:**
The `.secrets.baseline` file stores audited high-entropy strings and dummy secrets. Pre-commit hooks compare new changes against this baseline, allowing pre-existing or harmless tokens while immediately flagging new credential additions before git commit.

