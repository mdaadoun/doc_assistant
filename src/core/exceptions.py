"""Domain exception hierarchy for structured error handling."""

from typing import Any


class AppBaseError(Exception):
    """Root exception for all application domain errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Serialize exception details to structured dictionary."""
        return {
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}, message={self.message!r})"


class ConfigurationError(AppBaseError):
    """Raised on invalid or missing system configuration."""

    def __init__(
        self,
        message: str,
        code: str = "CONFIG_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)


class IngestionError(AppBaseError):
    """Raised during document parsing, extraction, or chunking failures."""

    def __init__(
        self,
        message: str,
        code: str = "INGESTION_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)


class RetrievalError(AppBaseError):
    """Raised on vector store, BM25 search, or fusion strategy failures."""

    def __init__(
        self,
        message: str,
        code: str = "RETRIEVAL_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)


class GenerationError(AppBaseError):
    """Raised on LLM generation, streaming, or citation extraction failures."""

    def __init__(
        self,
        message: str,
        code: str = "GENERATION_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)

