"""Unit tests for lifespan-scoped ServiceContainer dependency injection container."""

from api.services.chat_service import ChatService
from api.services.container import ServiceContainer
from cache.service import ResponseCacheService
from retrieval.debug_retrieval import DebugRetrievalBuilder


def test_service_container_default_services() -> None:
    """Verify default container exposes ChatService, DebugRetrievalBuilder, and ResponseCacheService instances."""
    container = ServiceContainer.create_default()

    assert isinstance(container.chat_service, ChatService)
    assert isinstance(container.debug_builder, DebugRetrievalBuilder)
    assert isinstance(container.cache_service, ResponseCacheService)


def test_service_container_injected_services() -> None:
    """Verify container preserves explicitly injected service instances."""
    chat_service = ChatService()
    debug_builder = DebugRetrievalBuilder()
    cache_service = ResponseCacheService()
    container = ServiceContainer(
        chat_service=chat_service,
        debug_builder=debug_builder,
        cache_service=cache_service,
    )

    assert container.chat_service is chat_service
    assert container.debug_builder is debug_builder
    assert container.cache_service is cache_service


def test_service_container_dispose_is_safe() -> None:
    """Verify dispose releases resources without raising."""
    container = ServiceContainer.create_default()
    container.dispose()
