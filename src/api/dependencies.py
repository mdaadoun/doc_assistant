"""FastAPI dependency injection providers for API services and infrastructure."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader

from api.services.chat_service import ChatService
from api.services.container import ServiceContainer
from core.config import Settings, get_settings
from retrieval.debug_retrieval import DebugRetrievalBuilder

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _get_container(request: Request) -> ServiceContainer:
    """Return lifespan-scoped container, lazily creating one when absent."""
    container: ServiceContainer | None = getattr(request.app.state, "container", None)
    if container is None:
        container = ServiceContainer.create_default()
        request.app.state.container = container
    return container


def verify_api_key(
    api_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings),
) -> str:
    """Validate incoming X-API-Key header against configured application API key."""
    expected_key = settings.app_api_key.strip() if settings.app_api_key else ""
    if expected_key and (not api_key or api_key.strip() != expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key or ""


def get_chat_service(request: Request) -> ChatService:
    """Dependency provider resolving ChatService from lifespan-scoped container."""
    return _get_container(request).chat_service


def get_debug_retrieval_builder(request: Request) -> DebugRetrievalBuilder:
    """Dependency provider resolving DebugRetrievalBuilder from lifespan-scoped container."""
    return _get_container(request).debug_builder


ApiKeyDep = Annotated[str, Depends(verify_api_key)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
DebugRetrievalBuilderDep = Annotated[
    DebugRetrievalBuilder, Depends(get_debug_retrieval_builder)
]
