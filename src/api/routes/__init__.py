"""API routes subpackage for chat and diagnostic endpoints."""

from api.routes.chat import router as chat_router
from api.routes.debug import router as debug_router

__all__: list[str] = ["chat_router", "debug_router"]
