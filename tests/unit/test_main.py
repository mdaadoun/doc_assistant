"""Unit tests for src.main application entrypoint."""

from fastapi import FastAPI

import src.main as main_module
from src.main import app, create_app


def test_main_exports() -> None:
    """Verify src.main exports app instance and create_app factory."""
    assert isinstance(app, FastAPI)
    assert callable(create_app)
    assert app.title == "Corporate Document Assistant API"


def test_main_create_app_invocation() -> None:
    """Verify create_app callable produces a configured FastAPI instance."""
    new_app = create_app()
    assert isinstance(new_app, FastAPI)
    assert new_app.title == "Corporate Document Assistant API"


def test_main_all_declaration() -> None:
    """Verify __all__ exposed symbols."""
    assert "app" in main_module.__all__
    assert "create_app" in main_module.__all__
