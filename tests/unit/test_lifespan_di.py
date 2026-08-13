"""Unit tests for lifespan-scoped dependency injection wiring in FastAPI app."""

from fastapi.testclient import TestClient
from starlette.requests import Request

from api.app import create_app
from api.dependencies import get_chat_service, get_debug_retrieval_builder
from api.services.chat_service import ChatService
from api.services.container import ServiceContainer
from retrieval.debug_retrieval import DebugRetrievalBuilder


def _make_request(app) -> Request:
    """Build a minimal Starlette Request bound to the given FastAPI app."""
    scope = {
        "type": "http",
        "app": app,
        "method": "GET",
        "path": "/",
        "headers": [],
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
        "scheme": "http",
        "root_path": "",
    }
    return Request(scope)


def test_lifespan_bootstraps_service_container() -> None:
    """Verify app lifespan creates and attaches ServiceContainer to app.state."""
    app = create_app()

    with TestClient(app) as client:
        container: ServiceContainer | None = getattr(app.state, "container", None)
        assert container is not None
        assert isinstance(container.chat_service, ChatService)
        assert isinstance(container.debug_builder, DebugRetrievalBuilder)
        # Container is shared across requests within the same lifespan
        assert (
            client.get("/api/v1/debug/retrieval", params={"query": "test"}).status_code
            == 200
        )


def test_lifespan_disposes_and_clears_container_on_shutdown() -> None:
    """Verify container is disposed and removed from app.state after lifespan exits."""
    app = create_app()

    with TestClient(app):
        assert getattr(app.state, "container", None) is not None

    assert getattr(app.state, "container", None) is None


def test_dependency_providers_resolve_from_lifespan_container() -> None:
    """Verify get_chat_service and get_debug_retrieval_builder resolve container services."""
    app = create_app()

    with TestClient(app):
        container: ServiceContainer = app.state.container
        request = _make_request(app)

        chat_service = get_chat_service(request)
        debug_builder = get_debug_retrieval_builder(request)

        assert chat_service is container.chat_service
        assert debug_builder is container.debug_builder


def test_dependency_providers_lazy_fallback_without_lifespan() -> None:
    """Verify providers lazily create a container when lifespan has not run."""
    app = create_app()

    # TestClient without context manager does not run lifespan startup
    client = TestClient(app)
    response = client.get("/api/v1/debug/retrieval", params={"query": "test"})
    assert response.status_code == 200
    assert getattr(app.state, "container", None) is not None
