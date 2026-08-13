"""API routes subpackage for chat and diagnostic endpoints."""

from api.routes.chat import router as chat_router

__all__: list[str] = ["chat_router"]
