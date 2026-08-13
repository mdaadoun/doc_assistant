"""Middleware package containing CORS, validation, and error handling."""

from api.middleware.cors import setup_cors
from api.middleware.error_handler import register_exception_handlers
from api.middleware.validation import setup_validation_middleware

__all__ = [
    "setup_cors",
    "setup_validation_middleware",
    "register_exception_handlers",
]
