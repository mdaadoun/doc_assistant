"""FastAPI application factory for Corporate Document Assistant API."""

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

import structlog
from fastapi import FastAPI

from api.middleware import (
    register_exception_handlers,
    setup_cors,
    setup_validation_middleware,
)
from api.routes.chat import router as chat_router
from api.routes.debug import router as debug_router
from api.services.container import ServiceContainer
from core.config import Settings, get_settings

logger = structlog.get_logger(__name__)


def _build_lifespan() -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    """Create lifespan context bootstrapping and disposing the service container."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        """Bootstrap services on startup and release resources on shutdown."""
        container = ServiceContainer.create_default()
        app.state.container = container
        logger.info(
            "service_container_started",
            chat_service=type(container.chat_service).__name__,
            debug_builder=type(container.debug_builder).__name__,
        )
        try:
            yield
        finally:
            container.dispose()
            app.state.container = None
            logger.info("service_container_stopped")

    return lifespan


def create_app(settings: Settings | None = None) -> FastAPI:
    """Construct and configure the main FastAPI application instance."""
    app_settings = settings or get_settings()
    app = FastAPI(
        title="Corporate Document Assistant API",
        version="0.1.0",
        description="RAG platform API with SSE streaming chat and diagnostic endpoints",
        lifespan=_build_lifespan(),
    )

    setup_cors(app, app_settings)
    setup_validation_middleware(app)
    register_exception_handlers(app)

    app.include_router(chat_router)
    app.include_router(debug_router)
    return app


app = create_app()
