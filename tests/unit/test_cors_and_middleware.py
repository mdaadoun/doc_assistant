"""Unit tests for CORS, request validation middleware, and error handlers."""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from api.app import create_app
from api.middleware import (
    register_exception_handlers,
    setup_validation_middleware,
)
from api.middleware.cors import _validate_cors_config
from core.config import Settings
from core.exceptions import IngestionError, RetrievalError


def test_cors_preflight_and_headers_default() -> None:
    """Verify CORS middleware responds with correct headers for cross-origin requests."""
    app = create_app()
    client = TestClient(app)

    response = client.options(
        "/api/v1/chat",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-API-Key, Content-Type",
        },
    )
    assert response.status_code == 200
    # With allow_credentials=True, Starlette echoes the specific origin
    assert (
        response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    )


def test_cors_custom_origin_configuration() -> None:
    """Verify custom allowed origins configuration restricts CORS headers."""
    settings = Settings(
        cors_origins=["https://dashboard.example.com"],
        cors_allow_credentials=True,
        _env_file=None,
    )
    app = create_app(settings=settings)
    client = TestClient(app)

    # Allowed origin
    resp_allowed = client.options(
        "/api/v1/chat",
        headers={
            "Origin": "https://dashboard.example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp_allowed.status_code == 200
    assert (
        resp_allowed.headers.get("access-control-allow-origin")
        == "https://dashboard.example.com"
    )

    # Disallowed origin
    resp_denied = client.options(
        "/api/v1/chat",
        headers={
            "Origin": "https://malicious-site.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp_denied.headers.get("access-control-allow-origin") is None


def test_request_validation_middleware_trace_id_injection() -> None:
    """Verify middleware injects or preserves X-Request-ID header."""
    app = create_app()
    client = TestClient(app)

    # Auto-generated request ID
    resp1 = client.get("/api/v1/debug/retrieval", params={"query": "test"})
    assert "X-Request-ID" in resp1.headers
    assert len(resp1.headers["X-Request-ID"]) > 0

    # Custom request ID preserved
    custom_id = "trace-uuid-12345"
    resp2 = client.get(
        "/api/v1/debug/retrieval",
        params={"query": "test"},
        headers={"X-Request-ID": custom_id},
    )
    assert resp2.headers.get("X-Request-ID") == custom_id


def test_request_validation_middleware_max_payload_limit() -> None:
    """Verify request validation middleware rejects oversized payloads with 413."""
    app = FastAPI()
    setup_validation_middleware(app, max_body_bytes=50)

    @app.post("/test-upload")
    def upload_endpoint() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(app)

    # Small payload succeeds
    resp_small = client.post("/test-upload", content=b"short message")
    assert resp_small.status_code == 200

    # Large payload rejected
    large_data = b"x" * 100
    resp_large = client.post(
        "/test-upload",
        content=large_data,
        headers={"Content-Length": str(len(large_data))},
    )
    assert resp_large.status_code == 413
    assert resp_large.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"


def test_error_handler_app_base_error_mapping() -> None:
    """Verify custom domain exception hierarchy converts to structured JSON responses."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/trigger-retrieval-error")
    def trigger_retrieval() -> None:
        raise RetrievalError(
            message="Vector store collection disconnected",
            code="VECTOR_STORE_OFFLINE",
            details={"collection": "helvetia_docs"},
        )

    @app.get("/trigger-ingestion-error")
    def trigger_ingestion() -> None:
        raise IngestionError(message="Corrupt PDF payload", code="PDF_PARSE_FAILED")

    client = TestClient(app)

    # Retrieval error -> 500
    r1 = client.get("/trigger-retrieval-error")
    assert r1.status_code == 500
    data1 = r1.json()
    assert data1["error"]["code"] == "VECTOR_STORE_OFFLINE"
    assert data1["error"]["message"] == "Vector store collection disconnected"
    assert data1["error"]["details"]["collection"] == "helvetia_docs"
    assert data1["detail"] == "Vector store collection disconnected"

    # Ingestion error -> 400
    r2 = client.get("/trigger-ingestion-error")
    assert r2.status_code == 400
    data2 = r2.json()
    assert data2["error"]["code"] == "PDF_PARSE_FAILED"


def test_error_handler_request_validation_error() -> None:
    """Verify Pydantic validation errors return HTTP 422 with structured details."""
    app = create_app()
    client = TestClient(app)

    response = client.post("/api/v1/chat", json={})
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(data["error"]["details"], list)


def test_error_handler_http_exception() -> None:
    """Verify standard HTTPException returns structured error format."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/trigger-404")
    def trigger_404() -> None:
        raise HTTPException(status_code=404, detail="Resource not found")

    client = TestClient(app)
    response = client.get("/trigger-404")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "HTTP_ERROR"
    assert data["detail"] == "Resource not found"


def test_error_handler_unhandled_exception() -> None:
    """Verify unexpected internal exception returns 500 with sanitized message."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/trigger-crash")
    def trigger_crash() -> None:
        raise RuntimeError("Database connection string contains password secret")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/trigger-crash")
    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    # Ensure sensitive runtime internal trace string is sanitized
    assert "password secret" not in data["error"]["message"]


def test_cors_production_wildcard_credentials_rejected() -> None:
    """Verify production CORS config rejects wildcard origin with credentials."""
    settings = Settings(
        environment="production",
        cors_origins=["*"],
        cors_allow_credentials=True,
        _env_file=None,
    )
    with pytest.raises(ValueError, match="wildcard origin"):
        _validate_cors_config(settings)


def test_cors_production_explicit_origins_allowed() -> None:
    """Verify production CORS config accepts explicit origins with credentials."""
    settings = Settings(
        environment="production",
        cors_origins=["https://app.example.com"],
        cors_allow_credentials=True,
        _env_file=None,
    )
    _validate_cors_config(settings)  # Should not raise


def test_security_headers_injected_on_response() -> None:
    """Verify middleware injects standard security headers on all responses."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/debug/retrieval", params={"query": "test"})
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"


def test_error_payload_detail_matches_message() -> None:
    """Verify structured error envelope keeps detail field consistent with message."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/trigger-http-error")
    def trigger_http_error() -> None:
        raise HTTPException(status_code=403, detail="Forbidden access")

    client = TestClient(app)
    response = client.get("/trigger-http-error")
    data = response.json()
    assert data["error"]["message"] == "Forbidden access"
    assert data["detail"] == "Forbidden access"
    assert data["error"]["details"] == {}
