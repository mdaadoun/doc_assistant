"""Unit tests for Pydantic settings loading and config helper methods."""

import pytest

from core.config import Settings, clear_settings_cache, get_settings


def test_default_settings_instantiation() -> None:
    """Verify default Settings values match expected baseline configuration."""
    settings = Settings(_env_file=None)
    assert settings.environment == "development"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.log_level == "INFO"
    assert settings.default_top_k == 5
    assert settings.confidence_threshold == 0.35
    assert settings.default_chunk_size == 512
    assert settings.default_overlap_ratio == 0.10
    assert settings.default_model == "gpt-4o-mini"
    assert settings.embedding_model == "text-embedding-3-small"
    assert settings.temperature == 0.0
    assert settings.max_tokens == 2048


def test_production_environment_check() -> None:
    """Verify is_production evaluates true only for production environment strings."""
    dev_settings = Settings(environment="development", _env_file=None)
    assert dev_settings.is_production() is False

    prod_settings = Settings(environment="production", _env_file=None)
    assert prod_settings.is_production() is True

    prod_caps_settings = Settings(environment="PRODUCTION", _env_file=None)
    assert prod_caps_settings.is_production() is True


def test_api_key_configuration_helpers() -> None:
    """Verify key configuration checks and status dict generation."""
    empty_keys = Settings(openai_api_key="", cohere_api_key="   ", _env_file=None)
    assert empty_keys.is_openai_configured() is False
    assert empty_keys.is_cohere_configured() is False
    assert empty_keys.get_api_key_status() == {"openai": False, "cohere": False}

    valid_keys = Settings(
        openai_api_key="sk-test-openai-key",
        cohere_api_key="coh-test-cohere-key",
        _env_file=None,
    )
    assert valid_keys.is_openai_configured() is True
    assert valid_keys.is_cohere_configured() is True
    assert valid_keys.get_api_key_status() == {"openai": True, "cohere": True}


def test_environment_variable_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify system environment variables override default settings values."""
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("PORT", "9090")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env-override")

    settings = Settings(_env_file=None)
    assert settings.environment == "staging"
    assert settings.port == 9090
    assert settings.openai_api_key == "sk-env-override"


def test_get_settings_singleton_caching(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify get_settings caches singleton and clear_settings_cache resets it."""
    clear_settings_cache()
    monkeypatch.setenv("PORT", "8000")
    s1 = get_settings()

    monkeypatch.setenv("PORT", "8888")
    s2 = get_settings()
    assert s1 is s2
    assert s2.port == 8000

    clear_settings_cache()
    s3 = get_settings()
    assert s3 is not s1
    assert s3.port == 8888
    clear_settings_cache()
