"""FastAPI application factory for Corporate Document Assistant API."""

from fastapi import FastAPI

from api.middleware import (
    register_exception_handlers,
    setup_cors,
    setup_validation_middleware,
)
from api.routes.chat import router as chat_router
from api.routes.debug import router as debug_router
from core.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Construct and configure the main FastAPI application instance."""
    app_settings = settings or get_settings()
    app = FastAPI(
        title="Corporate Document Assistant API",
        version="0.1.0",
        description="RAG platform API with SSE streaming chat and diagnostic endpoints",
    )

    setup_cors(app, app_settings)
    setup_validation_middleware(app)
    register_exception_handlers(app)

    app.include_router(chat_router)
    app.include_router(debug_router)
    return app


app = create_app()
