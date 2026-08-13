# Session 8.5: Service Dependency Injection (Lifespan Context)

**Date:** 2026-08-13

*Implements lifespan-scoped service dependency injection for the FastAPI API layer. Introduces a `ServiceContainer` composition root bootstrapped and disposed by the FastAPI lifespan context, replacing module-level global singletons with deterministic, per-app-lifecycle service resolution.*

---

### 1. 🎓 Concepts Introduced
- **ServiceContainer:** Lifespan-scoped composition root holding application service singletons (`ChatService`, `DebugRetrievalBuilder`) for the duration of the FastAPI app lifecycle.
- **Lifespan context:** FastAPI `asynccontextmanager` executed on application startup/shutdown, used here to bootstrap and dispose the service container.
- **Composition root:** Central wiring point where service dependencies are instantiated and injected, avoiding scattered global singletons.

---

### 2. 🧠 Architecture Decisions (ADR)

#### Decision A: Lifespan-scoped container vs module-level global singletons
- **Option 1 (Global singletons):** Simple, but leaks state across requests and tests, hard to reset, and prevents deterministic teardown.
- **Option 2 (Selected — Lifespan container):** Scopes service lifetime to the app lifecycle, enabling clean startup bootstrap and shutdown disposal, plus per-app isolation in tests.

#### Decision B: Lazy fallback container
- **Option 1 (Strict container requirement):** Providers raise if lifespan has not run; breaks direct `TestClient` usage in existing tests.
- **Option 2 (Selected — Lazy fallback):** `_get_container` creates and caches a default container on `app.state` when absent, preserving backward compatibility. Mitigated by lifespan always bootstrapping in `create_app()`.

#### Decision C: Provider signature accepting `Request`
- **Option 1 (No-arg providers):** Cannot access `app.state`; requires global state.
- **Option 2 (Selected — `request: Request`):** Providers read `request.app.state.container`, enabling per-app service resolution and typed FastAPI override functions in tests.

---

### 3. 🛠️ Implementation & Code

**New file: `src/api/services/container.py`**
```python
class ServiceContainer:
    def __init__(self, chat_service=None, debug_builder=None):
        self.chat_service = chat_service or ChatService()
        self.debug_builder = debug_builder or DebugRetrievalBuilder()

    @classmethod
    def create_default(cls):
        return cls()

    def dispose(self):
        logger.info("service_container_disposed")
```

**Updated: `src/api/dependencies.py`**
```python
def _get_container(request: Request) -> ServiceContainer:
    container = getattr(request.app.state, "container", None)
    if container is None:
        container = ServiceContainer.create_default()
        request.app.state.container = container
    return container

def get_chat_service(request: Request) -> ChatService:
    return _get_container(request).chat_service

def get_debug_retrieval_builder(request: Request) -> DebugRetrievalBuilder:
    return _get_container(request).debug_builder
```

**Updated: `src/api/app.py`**
```python
def _build_lifespan() -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        container = ServiceContainer.create_default()
        app.state.container = container
        try:
            yield
        finally:
            container.dispose()
            app.state.container = None
    return lifespan
```

**Updated: `ruff.toml`**
```toml
[lint.flake8-bugbear]
extend-immutable-calls = ["fastapi.Depends", "fastapi.Security"]
```

**Validation commands**
```bash
.venv/bin/pytest tests/unit -p no:cacheprovider   # 304 passed
.venv/bin/pytest tests/unit/test_runner.py -p no:cacheprovider  # 34 passed
.venv/bin/mypy src/api/services/container.py src/api/dependencies.py src/api/app.py  # Success
.venv/bin/ruff check src/api  # All checks passed
```

---

### 4. 📌 Session Checklist & Deliverables
1. [x] **ServiceContainer composition root** (`src/api/services/container.py`)
2. [x] **Lifespan-scoped DI providers** (`src/api/dependencies.py`)
3. [x] **Lifespan bootstrap/dispose wiring** (`src/api/app.py`)
4. [x] **Unit tests** (`test_service_container.py`, `test_lifespan_di.py`)
5. [x] **Test runner registration** (`test_runner.py`)
6. [x] **Existing test overrides updated** to typed `Request` functions
7. [x] **Full unit suite passing** (304 tests)