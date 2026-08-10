"""Shared pytest fixtures for Doc Assistant test suite."""

import pytest
from core.config import Settings


@pytest.fixture()
def test_settings() -> Settings:
    """Provide isolated test settings with safe defaults."""
    return Settings(
        environment="testing",
        openai_api_key="test-key-not-real",
        qdrant_host="localhost",
        qdrant_port=6333,
        confidence_threshold=0.35,
    )
