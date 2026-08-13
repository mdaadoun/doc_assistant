"""FastAPI dependency injection providers for API services and infrastructure."""

from typing import Annotated

from fastapi import Depends

from api.services.chat_service import ChatService

_default_chat_service: ChatService | None = None


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


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
