"""FastAPI dependency injection providers for API services and infrastructure."""

from typing import Annotated

from fastapi import Depends

from api.services.chat_service import ChatService
from retrieval.debug_retrieval import DebugRetrievalBuilder

_default_chat_service: ChatService | None = None
_default_debug_builder: DebugRetrievalBuilder | None = None


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


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
DebugRetrievalBuilderDep = Annotated[
    DebugRetrievalBuilder, Depends(get_debug_retrieval_builder)
]
