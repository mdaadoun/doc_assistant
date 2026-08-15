"""Request validation middleware with security headers and tracing."""

import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

_SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "X-XSS-Protection": "1; mode=block",
}


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Enforces request boundary validation, tracing, and security headers."""

    def __init__(self, app: FastAPI, max_body_bytes: int = 10_485_760) -> None:
        super().__init__(app)
        self.max_body_bytes = max_body_bytes

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request: validate size, inject trace ID, and add security headers."""
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        content_length = request.headers.get("content-length")
        is_oversized = (
            content_length
            and content_length.isdigit()
            and int(content_length) > self.max_body_bytes
        )
        if is_oversized:
            return Response(
                content='{"error":{"code":"PAYLOAD_TOO_LARGE","message":"Payload size exceeds max limit"}}',
                status_code=413,
                media_type="application/json",
            )

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        for header_name, header_value in _SECURITY_HEADERS.items():
            response.headers.setdefault(header_name, header_value)
        return response


def setup_validation_middleware(app: FastAPI, max_body_bytes: int = 10_485_760) -> None:
    """Register request validation middleware on FastAPI application."""
    app.add_middleware(RequestValidationMiddleware, max_body_bytes=max_body_bytes)
