"""Presentation layer: FastAPI routes, SSE streaming, authentication middleware."""

from api.app import app, create_app

__all__: list[str] = ["app", "create_app"]
