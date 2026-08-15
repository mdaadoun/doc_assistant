"""Structured error handling middleware and FastAPI exception handlers."""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.exceptions import (
    AppBaseError,
    ConfigurationError,
    GenerationError,
    IngestionError,
    RetrievalError,
)

logger = logging.getLogger(__name__)


def _build_error_payload(
    code: str, message: str, details: dict[str, Any] | list[Any] | None = None
) -> dict[str, Any]:
    """Construct standardized error response envelope."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "detail": message,
    }


def _map_app_error_status(exc: AppBaseError) -> int:
    """Map domain exception instance to standard HTTP status code."""
    if "status_code" in exc.details and isinstance(exc.details["status_code"], int):
        return exc.details["status_code"]
    if isinstance(exc, IngestionError):
        return status.HTTP_400_BAD_REQUEST
    if isinstance(exc, ConfigurationError):
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    if isinstance(exc, RetrievalError | GenerationError):
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return status.HTTP_500_INTERNAL_SERVER_ERROR


async def app_base_error_handler(request: Request, exc: AppBaseError) -> JSONResponse:
    """Handle custom AppBaseError domain hierarchy and format response."""
    status_code = _map_app_error_status(exc)
    logger.warning("Domain exception caught on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status_code,
        content=_build_error_payload(
            code=exc.code,
            message=exc.message,
            details=exc.details,
        ),
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic/FastAPI request validation errors."""
    logger.warning("Request validation error on %s: %s", request.url.path, exc)
    errors = list(exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_build_error_payload(
            code="VALIDATION_ERROR",
            message="Invalid request payload or parameters",
            details=errors,
        ),
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle standard HTTP exceptions maintaining header compatibility."""
    logger.info("HTTPException %s on %s", exc.status_code, request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_payload(
            code="HTTP_ERROR",
            message=str(exc.detail),
        ),
        headers=exc.headers,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected internal server errors."""
    logger.error(
        "Unhandled error processing %s: %s", request.url.path, exc, exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_build_error_payload(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected internal server error occurred",
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on FastAPI application instance."""
    app.add_exception_handler(AppBaseError, app_base_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
