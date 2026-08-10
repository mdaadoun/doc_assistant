# Architectural Journal — Phase 1.3: Pydantic Settings Configuration Setup (.env & BaseSettings)

> **Phase:** 1.3 | **Date:** 2026-08-10 | **Status:** Completed

---

## 🎯 Objective
Set up type-safe, environment-driven configuration management using Pydantic V2 `BaseSettings` and `SettingsConfigDict`. This includes loading application settings from `.env` files and host environment variables, providing default parameters for retrieval and model generation, implementing API key status helpers, and exposing a cached singleton accessor for runtime performance and unit test isolation.

---

## 💡 Architectural Choices

### 1. Type-Safe Configuration with Pydantic V2 `BaseSettings` (`src/core/config.py`)
- **Context:** Applications requiring multi-environment deployment (development, staging, production) often suffer from missing environment variables or type mismatches when using raw `os.getenv()`.
- **Decision:** Implement `Settings` extending `pydantic_settings.BaseSettings` with `SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")`.
- **Rationale:** Ensures strict type casting, default fallbacks, and parameter descriptions across server, vector store, retrieval, and LLM model configurations while silently ignoring unhandled host environment variables.

### 2. Thread-Safe Cached Singleton Pattern (`get_settings()`)
- **Context:** Instantiating configuration objects repeatedly on every request introduces unnecessary file reading and validation overhead.
- **Decision:** Wrap `get_settings()` with `@functools.lru_cache` to return a cached singleton instance of `Settings`.
- **Rationale:** Guarantees zero-cost configuration retrieval during high-throughput execution while maintaining immutability across request lifecycles.

### 3. Deterministic Test Isolation Helper (`clear_settings_cache()`)
- **Context:** Unit tests frequently monkeypatch environment variables to test edge cases, which is blocked by an immutable cached singleton.
- **Decision:** Provide `clear_settings_cache()` to clear the LRU cache on demand.
- **Rationale:** Enables clean, isolated environment variable testing without state leakage across test cases.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **LRU Cache Singleton** | Prevents automatic dynamic settings reload without process restart. | Exposed `clear_settings_cache()` helper for testing and explicit application re-initialization scenarios. |
| **String API Key Storage** | Storing API keys as strings could expose keys in unformatted string representations. | Provided `is_openai_configured()` and `is_cohere_configured()` helpers to validate key presence without printing raw secrets. |
| **`extra="ignore"` Flag** | Ignores unexpected system environment variables rather than failing strict validation. | Guarantees system stability across varied host environments while ensuring defined fields undergo strict type validation. |
