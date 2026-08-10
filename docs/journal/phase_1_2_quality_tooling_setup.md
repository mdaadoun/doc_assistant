# Architectural Journal — Phase 1.2: Static Quality Tooling Configuration (Ruff, Mypy Strict, Pre-Commit Hooks)

> **Phase:** 1.2 | **Date:** 2026-08-10 | **Status:** Completed

---

## 🎯 Objective
Establish an automated static quality guardrail infrastructure for the Corporate Document Assistant project. This includes configuring Ruff as a unified linter and formatter, setting Mypy to strict typing, integrating pre-commit hooks, generating a detect-secrets baseline, and providing programmatic quality validation utilities.

---

## 💡 Architectural Choices

### 1. Unified Linting & Formatting with Ruff (`ruff.toml` & `pyproject.toml`)
- **Context:** Python codebases traditionally suffer from slow linting cycles and conflicting configurations between Black, Flake8, and isort.
- **Decision:** Adopt Ruff configured targeting Python 3.11 with selected rule sets (`E`, `W`, `F`, `I`, `B`, `UP`, `SIM`, `RUF`).
- **Rationale:** Ruff executes up to 100x faster than legacy Python linters, consolidates formatting and import sorting into a single toolchain, and provides consistent developer tooling across local and CI environments.

### 2. Mandatory Strict Type Guarding (Mypy Strict Mode)
- **Context:** RAG pipelines process complex multi-modal data payloads (documents, vectors, embeddings, and chat responses) where type ambiguity can cause subtle runtime crashes.
- **Decision:** Configure `[tool.mypy]` in `pyproject.toml` with `strict = true`, disallowing untyped defs, incomplete defs, and implicit optional types across all `src/` modules.
- **Rationale:** Guarantees strict boundary type safety and eliminates dynamic `any` escapes across core domain modules.

### 3. Pre-Commit Hooks & Credential Leakage Prevention (`.pre-commit-config.yaml` & `.secrets.baseline`)
- **Context:** Production RAG applications consume sensitive credentials (OpenAI API keys, vector database keys, database passwords).
- **Decision:** Configure pre-commit hooks containing `trailing-whitespace`, `end-of-file-fixer`, `ruff`, `mypy strict`, and `detect-secrets` with an audited `.secrets.baseline` snapshot.
- **Rationale:** Automates commit-level quality verification and prevents credential exposure before code hits source control.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Ruff Consolidation** | Replaces traditional Black/Flake8 setup with single tool dependency. | Ruff implements compatible formatting rules and isort import ordering, matching standard PEP 8 conventions. |
| **Mypy Strict Enforce** | Increases initial code authoring time due to explicit type annotation requirements. | Provides long-term maintainability, self-documenting code, and zero runtime type errors across API boundaries. |
| **detect-secrets Baseline** | Requires baseline maintenance when new false positives occur during development. | Store audited snapshot in `.secrets.baseline` and update via `detect-secrets scan --update` during planned baseline updates. |
