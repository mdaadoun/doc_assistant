"""Mock embedding adapter for offline testing and fallback execution."""

import hashlib
import math
from collections.abc import Sequence

from clients.base_embedding import BaseEmbeddingAdapter


class MockEmbeddingAdapter(BaseEmbeddingAdapter):
    """Deterministic mock embedding adapter for isolated unit testing."""

    def __init__(
        self,
        model_name: str = "mock-embedding-v1",
        dimension: int = 1536,
    ) -> None:
        """Initialize mock embedding generator properties."""
        self._model_name = model_name
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        """Return configured mock vector dimension capacity."""
        return self._dimension

    @property
    def model_name(self) -> str:
        """Return mock model name identifier."""
        return self._model_name

    def _generate_vector(self, text: str) -> list[float]:
        """Generate deterministic unit-normalized pseudo-embedding for string."""
        seed_hash = hashlib.sha256(text.encode("utf-8")).digest()
        raw_vals: list[float] = []
        for i in range(self._dimension):
            byte_val = seed_hash[i % len(seed_hash)]
            val = (byte_val / 255.0) * 2.0 - 1.0 + (i * 0.0001)
            raw_vals.append(val)

        norm = math.sqrt(sum(v * v for v in raw_vals)) or 1.0
        return [v / norm for v in raw_vals]

    def embed_text(self, text: str) -> list[float]:
        """Generate deterministic embedding vector for single string."""
        sanitized = self._validate_text(text)
        return self._generate_vector(sanitized)

    def embed_batch(
        self, texts: Sequence[str], batch_size: int = 100
    ) -> list[list[float]]:
        """Generate deterministic embedding vectors for list of strings."""
        if not texts:
            return []
        return [self.embed_text(t) for t in texts]
