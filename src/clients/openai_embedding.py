"""OpenAI text-embedding-3-small adapter implementation."""

from collections.abc import Sequence
from typing import Any, ClassVar

import structlog
from openai import OpenAI

from clients.base_embedding import BaseEmbeddingAdapter
from core.config import get_settings
from core.exceptions import ConfigurationError, RetrievalError

logger = structlog.get_logger(__name__)


class OpenAIEmbeddingAdapter(BaseEmbeddingAdapter):
    """OpenAI vector embedding adapter supporting text-embedding-3-small."""

    MODEL_DIMENSIONS: ClassVar[dict[str, int]] = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(
        self,
        model_name: str | None = None,
        api_key: str | None = None,
        dimension: int | None = None,
        client: OpenAI | Any | None = None,
    ) -> None:
        """Initialize OpenAI client credentials and model settings."""
        settings = get_settings()
        self._model_name = model_name or settings.embedding_model
        resolved_key = api_key or settings.openai_api_key

        if client is not None:
            self.client = client
        else:
            if not resolved_key or not resolved_key.strip():
                raise ConfigurationError("OpenAI API key is missing or unconfigured")
            self.client = OpenAI(api_key=resolved_key)

        default_dim = self.MODEL_DIMENSIONS.get(self._model_name, 1536)
        self._dimension = dimension or default_dim

    @property
    def dimension(self) -> int:
        """Return vector dimension size."""
        return self._dimension

    @property
    def model_name(self) -> str:
        """Return OpenAI model identifier."""
        return self._model_name

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding vector for a single text string."""
        results = self.embed_batch([text])
        return results[0]

    def embed_batch(
        self, texts: Sequence[str], batch_size: int = 100
    ) -> list[list[float]]:
        """Batch generate OpenAI embeddings for sequence of text items."""
        if not texts:
            return []

        sanitized_texts = [self._validate_text(t) for t in texts]
        batches = self._chunk_batch(sanitized_texts, batch_size)
        all_embeddings: list[list[float]] = []

        try:
            for batch in batches:
                processed_batch = [t if t else " " for t in batch]
                response = self.client.embeddings.create(
                    model=self._model_name,
                    input=processed_batch,
                )
                sorted_data = sorted(response.data, key=lambda item: item.index)
                for item in sorted_data:
                    all_embeddings.append(list(item.embedding))

            logger.info(
                "openai_embedding_batch_completed",
                model=self._model_name,
                count=len(all_embeddings),
            )
            return all_embeddings
        except ConfigurationError:
            raise
        except Exception as exc:
            logger.error(
                "openai_embedding_failed", model=self._model_name, error=str(exc)
            )
            raise RetrievalError(
                message=f"OpenAI embedding generation failed: {exc}",
                details={"model": self._model_name, "error": str(exc)},
            ) from exc
