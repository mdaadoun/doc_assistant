"""CORS middleware setup with production safety guards."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import Settings, get_settings


def _validate_cors_config(settings: Settings) -> None:
    """Reject insecure wildcard origin with credentials in production."""
    is_insecure = (
        settings.is_production()
        and "*" in settings.cors_origins
        and settings.cors_allow_credentials
    )
    if is_insecure:
        raise ValueError(
            "CORS wildcard origin '*' cannot be combined with allow_credentials=True in production"
        )


def setup_cors(app: FastAPI, settings: Settings | None = None) -> None:
    """Attach CORSMiddleware with validated origin, method, and header policies."""
    cfg = settings or get_settings()
    _validate_cors_config(cfg)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=cfg.cors_allow_credentials,
        allow_methods=cfg.cors_allow_methods,
        allow_headers=cfg.cors_allow_headers,
        max_age=600,
    )
