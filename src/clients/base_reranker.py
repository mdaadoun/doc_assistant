"""Abstract base adapter interface for cross-encoder reranking providers."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from models.retrieval import RetrievalResult


class BaseRerankerAdapter(ABC):
    """Abstract base class for cross-encoder reranking adapters."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        hits: Sequence[RetrievalResult],
        candidate_k: int | None = None,
        top_k: int | None = None,
    ) -> list[RetrievalResult]:
        """Rerank retrieved candidates for a query using cross-encoder scoring."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return cross-encoder model identifier."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return reranker provider name e.g. flashrank, cohere, mock."""
