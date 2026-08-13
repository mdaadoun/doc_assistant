# Architectural Journal — Phase 8.3: Set Up API Key Authentication Middleware (`dependencies.py`)

> **Phase:** 8.3 | **Date:** 2026-08-13 | **Status:** Completed

---

## 🎯 Objective
Implement feature 8.3: Set up API key authentication middleware (`src/api/dependencies.py`). Configure security dependency providers that validate incoming client `X-API-Key` headers against application settings (`src/core/config.py`), protecting presentation layer endpoints while supporting zero-boilerplate unauthenticated local development.

---

## 💡 Architectural Choices

### 1. Security Dependency Provider Scheme (`verify_api_key`)
- **Context:** API endpoints require a lightweight authorization check to restrict access while staying modular and testable without tightly coupling middleware logic directly inside app routing setup.
- **Decision:** Utilized FastAPI's `APIKeyHeader(name="X-API-Key", auto_error=False)` combined with `verify_api_key` dependency provider in `src/api/dependencies.py`.
- **Rationale:** Disabling `auto_error` on `APIKeyHeader` allows custom error handling in `verify_api_key`, returning standardized `HTTP 401 Unauthorized` responses with `WWW-Authenticate: ApiKey` headers instead of generic 403 Forbidden errors.

### 2. Configurable Dev-Bypass Fallback (`app_api_key`)
- **Context:** Developers and automated test suites need unhindered local access without hardcoding authorization tokens for every HTTP call when running in development environments.
- **Decision:** Added `app_api_key: str` setting to `Settings` (`src/core/config.py`). When `app_api_key` is empty or unconfigured, `verify_api_key` bypasses key verification automatically.
- **Rationale:** Delivers zero-config developer ergonomics in local development while guaranteeing strict 401 authentication enforcement when deployed to staging or production with `APP_API_KEY` configured.

### 3. Router-Level Security Injection (`dependencies=[Depends(verify_api_key)]`)
- **Context:** Multiple route modules (`/api/v1/chat` and `/api/v1/debug/retrieval`) require authorization enforcement without duplicating dependency signatures on individual handler functions.
- **Decision:** Injected `dependencies=[Depends(verify_api_key)]` into `APIRouter` initializations in `src/api/routes/chat.py` and `src/api/routes/debug.py`.
- **Rationale:** Guarantees all sub-routes inherit API key validation automatically while leaving route function signatures focused on request payload parameters.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Router-Level Dependency Injection** | Requires explicitly overriding dependency bindings or settings in unit tests. | Standard FastAPI `app.dependency_overrides` or setting `APP_API_KEY=""` in test fixtures allows effortless test execution. |
| **Header-Based Secret Verification** | Lacks fine-grained user scopes or token expiration compared to OAuth2 / JWT. | Lightweight API key authentication matches requirement constraints for corporate assistant service-to-service communication. |

---

## 🛠️ Implementation & Code

### Security Verification Flow
```text
Client HTTP Request (e.g. POST /api/v1/chat or GET /api/v1/debug/retrieval)
  ├── 1. FastAPI extracts X-API-Key header via APIKeyHeader scheme
  ├── 2. Depends(verify_api_key) invokes verify_api_key(api_key, settings)
  ├── 3. Check settings.app_api_key:
  │      ├── If app_api_key is empty -> Allow request (bypasses check for dev mode)
  │      ├── If app_api_key is set & header is missing/invalid -> Raise HTTP 401 Unauthorized
  │      └── If app_api_key matches header -> Validation succeeds
  └── 4. Execute route handler function
```

### Module Breakdown
- **`src/core/config.py`:** Added `app_api_key` field, `is_app_api_key_configured()` helper, and updated `get_api_key_status()` dictionary map.
- **`src/api/dependencies.py`:** Exported `api_key_header`, `verify_api_key`, and `ApiKeyDep` annotated dependency provider.
- **`src/api/routes/chat.py` & `src/api/routes/debug.py`:** Applied `dependencies=[Depends(verify_api_key)]` to router definitions.
- **`tests/unit/test_api_key_auth.py`:** Full unit test suite covering unconfigured bypass, missing key, invalid key, valid key, and end-to-end FastAPI client authentication enforcement.

---

## 🧪 Verification & Results
- **Unit Tests:** Implemented `tests/unit/test_api_key_auth.py` and registered `test_run_project_tests_api_key_auth_suite` in `tests/runner.py` / `tests/unit/test_runner.py`.
- **Suite Execution:** All 286 unit tests passed cleanly in `12.89s`.
- **Code Quality:** Type safe under `mypy` and compliant with `ruff` linting guidelines.
