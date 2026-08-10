"""Unit tests for domain exception hierarchy."""

import pytest

from core import (
    AppBaseError,
    ConfigurationError,
    GenerationError,
    IngestionError,
    RetrievalError,
)


def test_app_base_error_defaults_and_serialization() -> None:
    """Verify AppBaseError initialization, serialization, and representation."""
    err = AppBaseError(message="System failure")

    assert isinstance(err, Exception)
    assert err.message == "System failure"
    assert err.code == "INTERNAL_ERROR"
    assert err.details == {}
    assert str(err) == "System failure"
    assert "AppBaseError(code='INTERNAL_ERROR'" in repr(err)

    serialized = err.to_dict()
    assert serialized == {
        "message": "System failure",
        "code": "INTERNAL_ERROR",
        "details": {},
    }


def test_app_base_error_with_custom_code_and_details() -> None:
    """Verify AppBaseError handles explicit code and contextual metadata dictionary."""
    details = {"component": "database", "retries": 3}
    err = AppBaseError(message="Connection failed", code="DB_CONN_ERROR", details=details)

    assert err.code == "DB_CONN_ERROR"
    assert err.details == details
    assert err.to_dict()["details"]["retries"] == 3


def test_configuration_error_instantiation() -> None:
    """Verify ConfigurationError default error code and inheritance."""
    err = ConfigurationError("Invalid key")

    assert isinstance(err, AppBaseError)
    assert err.code == "CONFIG_ERROR"
    assert err.message == "Invalid key"


def test_ingestion_error_instantiation() -> None:
    """Verify IngestionError default error code and metadata context."""
    err = IngestionError("PDF extraction failed", details={"filename": "doc.pdf"})

    assert isinstance(err, AppBaseError)
    assert err.code == "INGESTION_ERROR"
    assert err.details["filename"] == "doc.pdf"


def test_retrieval_error_instantiation() -> None:
    """Verify RetrievalError default error code and exception handling."""
    err = RetrievalError("Qdrant search timeout")

    assert isinstance(err, AppBaseError)
    assert err.code == "RETRIEVAL_ERROR"


def test_generation_error_instantiation() -> None:
    """Verify GenerationError default error code and serialization."""
    err = GenerationError("LLM response corrupted", details={"model": "gpt-4o"})

    assert isinstance(err, AppBaseError)
    assert err.code == "GENERATION_ERROR"
    assert err.to_dict()["details"]["model"] == "gpt-4o"


def test_polymorphic_exception_catching() -> None:
    """Verify all domain errors are caught by AppBaseError block."""
    exceptions = [
        ConfigurationError("Config missing"),
        IngestionError("Parse failed"),
        RetrievalError("Vector search failed"),
        GenerationError("Generation failed"),
    ]

    for exc in exceptions:
        with pytest.raises(AppBaseError) as exc_info:
            raise exc
        assert exc_info.value.code in {
            "CONFIG_ERROR",
            "INGESTION_ERROR",
            "RETRIEVAL_ERROR",
            "GENERATION_ERROR",
        }
