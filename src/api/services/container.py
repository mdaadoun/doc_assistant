"""Lifespan-scoped service container for application dependency injection."""

import structlog

from api.services.chat_service import ChatService
from cache.service import ResponseCacheService
from retrieval.debug_retrieval import DebugRetrievalBuilder

logger = structlog.get_logger(__name__)


class ServiceContainer:
    """Holds application services for the current app lifespan."""

    def __init__(
        self,
        chat_service: ChatService | None = None,
        debug_builder: DebugRetrievalBuilder | None = None,
        cache_service: ResponseCacheService | None = None,
    ) -> None:
        """Initialize container with provided services or default implementations."""
        self.cache_service = cache_service or ResponseCacheService()
        self.chat_service = chat_service or ChatService()
        self.debug_builder = debug_builder or DebugRetrievalBuilder()

    @classmethod
    def create_default(cls) -> "ServiceContainer":
        """Build a container with default service implementations."""
        return cls()

    def dispose(self) -> None:
        """Release external resources held by container services."""
        logger.info("service_container_disposed")
