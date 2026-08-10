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
