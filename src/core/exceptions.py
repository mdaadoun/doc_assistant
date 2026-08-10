"""Domain exception hierarchy for structured error handling."""


class AppBaseError(Exception):
    """Root exception for all application errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)


class ConfigurationError(AppBaseError):
    """Raised on invalid or missing configuration."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFIG_ERROR")


class IngestionError(AppBaseError):
    """Raised during document parsing or chunking failures."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="INGESTION_ERROR")


class RetrievalError(AppBaseError):
    """Raised on vector/BM25 search or fusion failures."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="RETRIEVAL_ERROR")


class GenerationError(AppBaseError):
    """Raised on LLM generation or citation extraction failures."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="GENERATION_ERROR")
