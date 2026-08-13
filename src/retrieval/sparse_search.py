"""Sparse BM25 search service: top-50 ranked hits over in-memory index."""

import structlog

from core.exceptions import RetrievalError
from models.retrieval import RetrievalResult
from retrieval.bm25_index import BM25IndexManager

logger = structlog.get_logger(__name__)

SPARSE_TOP_K_DEFAULT = 50


class SparseSearchService:
    """Encapsulate sparse retrieval: BM25 scoring over tokenized corpus."""

    def __init__(
        self,
        bm25_index: BM25IndexManager,
        top_k: int = SPARSE_TOP_K_DEFAULT,
    ) -> None:
        """Configure sparse search service with BM25 index and top-k limit."""
        self.bm25_index = bm25_index
        self.top_k = max(1, top_k)

    def search(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[RetrievalResult]:
        """Run BM25 search over indexed corpus and return ranked sparse hits."""
        if not query or not query.strip():
            raise RetrievalError(
                message="Query must be a non-empty string",
                code="EMPTY_QUERY",
            )

        target_top_k = max(1, top_k or self.top_k)

        if not self.bm25_index.is_built:
            raise RetrievalError(
                message="BM25 index is empty; build it before searching",
                code="BM25_EMPTY_INDEX",
            )

        results = self.bm25_index.search(query=query, top_k=target_top_k)

        logger.info(
            "sparse_search_completed",
            query=query,
            top_k=target_top_k,
            hits=len(results),
        )
        return results
