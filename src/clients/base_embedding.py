"""Abstract base embedding adapter interface and batching utilities."""

from abc import ABC, abstractmethod
from collections.abc import Sequence


class BaseEmbeddingAdapter(ABC):
    """Abstract interface for embedding model providers."""

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate vector embedding for a single text string."""

    @abstractmethod
    def embed_batch(
        self, texts: Sequence[str], batch_size: int = 100
    ) -> list[list[float]]:
        """Generate vector embeddings for a list of text strings in batches."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return vector dimension capacity (e.g. 1536)."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return target embedding model identifier."""

    def _validate_text(self, text: str) -> str:
        """Sanitize text input and ensure valid string structure."""
        if not isinstance(text, str):
            text = str(text)
        return text.strip()

    def _chunk_batch(
        self, texts: Sequence[str], batch_size: int
    ) -> list[list[str]]:
        """Divide sequence of text strings into sub-batches."""
        size = max(1, batch_size)
        return [list(texts[i : i + size]) for i in range(0, len(texts), size)]
