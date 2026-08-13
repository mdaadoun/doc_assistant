"""Unit tests for API key authentication middleware and dependency providers."""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.app import create_app
from api.dependencies import get_chat_service, verify_api_key
from api.services.chat_service import ChatService
from core.config import Settings, clear_settings_cache


def test_verify_api_key_unconfigured_bypasses_check() -> None:
    """Verify verify_api_key allows requests when app_api_key is empty."""
    settings = Settings(app_api_key="", _env_file=None)
    result_none = verify_api_key(api_key=None, settings=settings)
    assert result_none == ""

    result_provided = verify_api_key(api_key="any-key", settings=settings)
    assert result_provided == "any-key"


def test_verify_api_key_configured_missing_key_raises_401() -> None:
    """Verify missing X-API-Key header raises HTTP 401 when app_api_key is set."""
    settings = Settings(app_api_key="secret-key-123", _env_file=None)
    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(api_key=None, settings=settings)

    assert exc_info.value.status_code == 401
    assert "Invalid or missing API key" in exc_info.value.detail
    assert exc_info.value.headers.get("WWW-Authenticate") == "ApiKey"


def test_verify_api_key_configured_invalid_key_raises_401() -> None:
    """Verify invalid X-API-Key header raises HTTP 401 when app_api_key is set."""
    settings = Settings(app_api_key="secret-key-123", _env_file=None)
    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(api_key="wrong-key", settings=settings)

    assert exc_info.value.status_code == 401
    assert "Invalid or missing API key" in exc_info.value.detail


def test_verify_api_key_configured_valid_key_succeeds() -> None:
    """Verify matching X-API-Key header passes validation and returns key."""
    settings = Settings(app_api_key="secret-key-123", _env_file=None)
    key = verify_api_key(api_key="secret-key-123", settings=settings)
    assert key == "secret-key-123"


def test_api_endpoint_auth_enforcement_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify FastAPI routes reject unauthorized requests when app_api_key is enforced."""
    clear_settings_cache()
    monkeypatch.setenv("APP_API_KEY", "prod-secret-999")

    app = create_app()

    class DummyChatService(ChatService):
        async def stream_chat(self, request):  # type: ignore[no-untyped-def]
            yield "event: done\ndata: {}\n\n"

    app.dependency_overrides[get_chat_service] = lambda: DummyChatService()
    client = TestClient(app)

    # 1. Unauthenticated request -> 401
    resp_unauth = client.post(
        "/api/v1/chat",
        json={"query": "Test question?", "conversation_id": "c1"},
    )
    assert resp_unauth.status_code == 401
    assert "Invalid or missing API key" in resp_unauth.json()["detail"]

    # 2. Wrong API key -> 401
    resp_wrong = client.post(
        "/api/v1/chat",
        json={"query": "Test question?", "conversation_id": "c1"},
        headers={"X-API-Key": "wrong-secret"},
    )
    assert resp_wrong.status_code == 401

    # 3. Valid API key -> 200
    resp_valid = client.post(
        "/api/v1/chat",
        json={"query": "Test question?", "conversation_id": "c1"},
        headers={"X-API-Key": "prod-secret-999"},
    )
    assert resp_valid.status_code == 200

    clear_settings_cache()
