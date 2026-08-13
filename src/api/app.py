"""FastAPI application factory for Corporate Document Assistant API."""

from fastapi import FastAPI

from api.routes.chat import router as chat_router
from api.routes.debug import router as debug_router


def create_app() -> FastAPI:
    """Construct and configure the main FastAPI application instance."""
    app = FastAPI(
        title="Corporate Document Assistant API",
        version="0.1.0",
        description="RAG platform API with SSE streaming chat and diagnostic endpoints",
    )
    app.include_router(chat_router)
    app.include_router(debug_router)
    return app


app = create_app()
