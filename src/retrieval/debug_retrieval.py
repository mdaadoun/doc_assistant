"""Retrieval debug builder: assemble stage-wise debug payload for observability."""

import structlog

from models.retrieval import (
    DebugRetrievalHit,
    DebugRetrievalResponse,
    RetrievalResult,
)
from retrieval.dense_search import DenseSearchService
from retrieval.reranker_service import RerankerService
from retrieval.rrf_fusion import RRFusionService
from retrieval.sparse_search import SparseSearchService

logger = structlog.get_logger(__name__)


def _to_debug_hits(hits: list[RetrievalResult], method: str) -> list[DebugRetrievalHit]:
    """Convert ranked retrieval hits into compact debug hits with 1-indexed rank."""
    return [
        DebugRetrievalHit(
            chunk_id=hit.chunk_id,
            score=hit.relevance_score,
            rank=rank,
            method=method,
        )
        for rank, hit in enumerate(hits, start=1)
    ]


class DebugRetrievalBuilder:
    """Run hybrid pipeline and expose dense scores, sparse scores, fused ranks, and reranking."""

    def __init__(
        self,
        dense_search: DenseSearchService,
        sparse_search: SparseSearchService,
        rrf_fusion: RRFusionService,
        reranker: RerankerService | None = None,
    ) -> None:
        """Configure debug builder with dense, sparse, RRF, and optional reranker services."""
        self.dense_search = dense_search
        self.sparse_search = sparse_search
        self.rrf_fusion = rrf_fusion
        self.reranker = reranker

    def build(
        self,
        query: str,
        dense_top_k: int | None = None,
        sparse_top_k: int | None = None,
        rrf_top_k: int | None = None,
        rerank_top_k: int | None = None,
    ) -> DebugRetrievalResponse:
        """Execute dense+sparse search, fuse via RRF, rerank, and return debug payload."""
        dense_hits = self.dense_search.search(query, top_k=dense_top_k)
        sparse_hits = self.sparse_search.search(query, top_k=sparse_top_k)
        fused_hits = self.rrf_fusion.fuse(
            dense_hits=dense_hits, sparse_hits=sparse_hits, top_k=rrf_top_k
        )

        final_reranked = (
            self.reranker.rerank(query, fused_hits, top_k=rerank_top_k)
            if self.reranker is not None
            else []
        )

        response = DebugRetrievalResponse(
            query=query,
            dense_hits=_to_debug_hits(dense_hits, method="dense"),
            sparse_hits=_to_debug_hits(sparse_hits, method="sparse"),
            rrf_fused=_to_debug_hits(fused_hits, method="rrf"),
            final_reranked=final_reranked,
        )

        logger.info(
            "debug_retrieval_built",
            query=query,
            dense_hits=len(dense_hits),
            sparse_hits=len(sparse_hits),
            fused_hits=len(fused_hits),
            final_reranked=len(final_reranked),
        )
        return response
