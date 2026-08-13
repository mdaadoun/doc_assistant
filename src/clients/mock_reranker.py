"""Mock cross-encoder reranker adapter for fast unit testing and offline fallbacks."""

from collections.abc import Sequence

from clients.base_reranker import BaseRerankerAdapter
from models.retrieval import RetrievalResult

MOCK_RERANKER_PROVIDER = "mock"


class MockRerankerAdapter(BaseRerankerAdapter):
    """Mock reranker adapter returning deterministic relevance scores."""

    def __init__(
        self,
        model_name: str = "mock-miniLM-L6-v2",
        default_candidate_k: int = 30,
        default_top_k: int = 5,
    ) -> None:
        """Initialize mock reranker adapter."""
        self._model_name = model_name
        self.default_candidate_k = max(1, default_candidate_k)
        self.default_top_k = max(1, default_top_k)

    def rerank(
        self,
        query: str,
        hits: Sequence[RetrievalResult],
        candidate_k: int | None = None,
        top_k: int | None = None,
    ) -> list[RetrievalResult]:
        """Simulate cross-encoder reranking by calculating mock scores."""
        if not hits or not query.strip():
            return []

        c_k = candidate_k if candidate_k is not None else self.default_candidate_k
        t_k = top_k if top_k is not None else self.default_top_k
        candidates = list(hits[: max(1, c_k)])

        scored_results: list[RetrievalResult] = []
        query_words = set(query.lower().split())
        for idx, hit in enumerate(candidates):
            hit_words = set(hit.text.lower().split())
            overlap = len(query_words & hit_words)
            mock_score = 0.5 + (0.4 * (overlap / max(1, len(query_words)))) - (idx * 0.01)
            mock_score = max(0.0, min(1.0, mock_score))

            scored_results.append(
                RetrievalResult(
                    chunk_id=hit.chunk_id,
                    text=hit.text,
                    file_name=hit.file_name,
                    page_number=hit.page_number,
                    relevance_score=round(mock_score, 4),
                    retrieval_method="mock_flashrank",
                )
            )

        scored_results.sort(key=lambda r: (-r.relevance_score, r.chunk_id))
        return scored_results[: max(1, t_k)]

    @property
    def model_name(self) -> str:
        """Return model identifier."""
        return self._model_name

    @property
    def provider_name(self) -> str:
        """Return provider identifier."""
        return MOCK_RERANKER_PROVIDER
