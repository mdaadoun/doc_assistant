"""Gemini vector embedding client adapter implementation."""

from collections.abc import Sequence
from typing import Any

import structlog

from clients.base_embedding import BaseEmbeddingAdapter
from core.config import get_settings
from core.exceptions import ConfigurationError, RetrievalError

logger = structlog.get_logger(__name__)


class GeminiEmbeddingAdapter(BaseEmbeddingAdapter):
    """Google Gemini embedding adapter supporting text-embedding-004."""

    def __init__(
        self,
        model_name: str = "text-embedding-004",
        api_key: str | None = None,
        dimension: int = 768,
        client: Any | None = None,
    ) -> None:
        """Initialize Gemini embedding adapter and API connection."""
        settings = get_settings()
        self._model_name = model_name
        self._dimension = dimension
        resolved_key = api_key or getattr(settings, "gemini_api_key", "")

        if client is not None:
            self.client = client
        else:
            if not resolved_key or not resolved_key.strip():
                raise ConfigurationError("Gemini API key is missing or unconfigured")
            try:
                import google.genai as genai

                self.client = genai.Client(api_key=resolved_key)
            except Exception as exc:
                raise ConfigurationError(
                    f"Failed to initialize Gemini genai client: {exc}"
                ) from exc

    @property
    def dimension(self) -> int:
        """Return Gemini vector dimension size."""
        return self._dimension

    @property
    def model_name(self) -> str:
        """Return Gemini model identifier."""
        return self._model_name

    def embed_text(self, text: str) -> list[float]:
        """Generate vector embedding for single text input."""
        results = self.embed_batch([text])
        return results[0]

    def embed_batch(
        self, texts: Sequence[str], batch_size: int = 100
    ) -> list[list[float]]:
        """Generate Gemini vector embeddings in batches."""
        if not texts:
            return []

        sanitized_texts = [self._validate_text(t) if t else " " for t in texts]
        batches = self._chunk_batch(sanitized_texts, batch_size)
        all_embeddings: list[list[float]] = []

        try:
            for batch in batches:
                response = self.client.models.embed_content(
                    model=self._model_name,
                    contents=batch,
                )
                if hasattr(response, "embeddings") and response.embeddings:
                    for emb in response.embeddings:
                        all_embeddings.append(list(emb.values))
                elif hasattr(response, "embedding") and response.embedding:
                    all_embeddings.append(list(response.embedding.values))
                else:
                    raise RetrievalError(
                        "Invalid response format from Gemini embedding API"
                    )

            return all_embeddings
        except (ConfigurationError, RetrievalError):
            raise
        except Exception as exc:
            logger.error(
                "gemini_embedding_failed", model=self._model_name, error=str(exc)
            )
            raise RetrievalError(
                message=f"Gemini embedding generation failed: {exc}",
                details={"model": self._model_name, "error": str(exc)},
            ) from exc
