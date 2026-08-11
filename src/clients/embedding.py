"""Unified embedding client adapter facade with provider selection."""

from collections.abc import Sequence
from typing import Any

import structlog

from clients.base_embedding import BaseEmbeddingAdapter
from clients.gemini_embedding import GeminiEmbeddingAdapter
from clients.mock_embedding import MockEmbeddingAdapter
from clients.openai_embedding import OpenAIEmbeddingAdapter
from core.config import get_settings
from core.exceptions import ConfigurationError

logger = structlog.get_logger(__name__)


class EmbeddingClientAdapter(BaseEmbeddingAdapter):
    """Facade adapter encapsulating embedding providers (OpenAI, Gemini, Mock)."""

    def __init__(
        self,
        provider: str = "openai",
        model_name: str | None = None,
        api_key: str | None = None,
        dimension: int | None = None,
        client: Any | None = None,
    ) -> None:
        """Initialize provider strategy based on selection or environment configuration."""
        settings = get_settings()
        self.provider = provider.lower().strip()
        self._target_model = model_name or settings.embedding_model

        if self.provider == "auto":
            if settings.is_openai_configured() or api_key:
                self.provider = "openai"
            elif settings.is_gemini_configured():
                self.provider = "gemini"
            else:
                logger.warning("no_embedding_api_key_found_using_mock_fallback")
                self.provider = "mock"

        if self.provider == "openai":
            self.adapter: BaseEmbeddingAdapter = OpenAIEmbeddingAdapter(
                model_name=self._target_model,
                api_key=api_key,
                dimension=dimension,
                client=client,
            )
        elif self.provider == "gemini":
            self.adapter = GeminiEmbeddingAdapter(
                model_name=model_name or "text-embedding-004",
                api_key=api_key,
                dimension=dimension or 768,
                client=client,
            )
        elif self.provider == "mock":
            dim = dimension or 1536
            self.adapter = MockEmbeddingAdapter(
                model_name=self._target_model,
                dimension=dim,
            )
        else:
            raise ConfigurationError(
                message=f"Unsupported embedding provider: {provider}",
                details={"supported_providers": ["openai", "gemini", "mock", "auto"]},
            )

    @property
    def dimension(self) -> int:
        """Return vector dimension of underlying active adapter."""
        return self.adapter.dimension

    @property
    def model_name(self) -> str:
        """Return model identifier of underlying active adapter."""
        return self.adapter.model_name

    def embed_text(self, text: str) -> list[float]:
        """Delegate text embedding generation to active provider adapter."""
        return self.adapter.embed_text(text)

    def embed_batch(
        self, texts: Sequence[str], batch_size: int = 100
    ) -> list[list[float]]:
        """Delegate batch embedding generation to active provider adapter."""
        return self.adapter.embed_batch(texts, batch_size=batch_size)
