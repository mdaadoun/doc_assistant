"""FastAPI dependency injection providers for API services and infrastructure."""

from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from api.services.chat_service import ChatService
from core.config import Settings, get_settings
from retrieval.debug_retrieval import DebugRetrievalBuilder

_default_chat_service: ChatService | None = None
_default_debug_builder: DebugRetrievalBuilder | None = None

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(
    api_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings),
) -> str:
    """Validate incoming X-API-Key header against configured application API key."""
    expected_key = settings.app_api_key.strip() if settings.app_api_key else ""
    if expected_key:
        if not api_key or api_key.strip() != expected_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )
    return api_key or ""


def get_chat_service() -> ChatService:
    """Dependency provider returning singleton or configured ChatService instance."""
    global _default_chat_service
    if _default_chat_service is None:
        _default_chat_service = ChatService()
    return _default_chat_service


def set_chat_service(service: ChatService | None) -> None:
    """Configure default ChatService provider instance for testing or app bootstrap."""
    global _default_chat_service
    _default_chat_service = service


def get_debug_retrieval_builder() -> DebugRetrievalBuilder:
    """Dependency provider returning singleton or configured DebugRetrievalBuilder instance."""
    global _default_debug_builder
    if _default_debug_builder is None:
        _default_debug_builder = DebugRetrievalBuilder()
    return _default_debug_builder


def set_debug_retrieval_builder(builder: DebugRetrievalBuilder | None) -> None:
    """Configure default DebugRetrievalBuilder provider instance for testing or app bootstrap."""
    global _default_debug_builder
    _default_debug_builder = builder


ApiKeyDep = Annotated[str, Depends(verify_api_key)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
DebugRetrievalBuilderDep = Annotated[
    DebugRetrievalBuilder, Depends(get_debug_retrieval_builder)
]
