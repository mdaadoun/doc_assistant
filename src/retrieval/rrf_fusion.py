"""Reciprocal Rank Fusion (RRF) service merging dense + sparse ranked hits."""

import structlog

from models.retrieval import RetrievalResult

logger = structlog.get_logger(__name__)

RRF_K_DEFAULT = 60
RRF_TOP_K_DEFAULT = 50
RRF_METHOD = "rrf"


class RRFusionService:
    """Fuse multiple ranked result lists via reciprocal rank scores."""

    def __init__(
        self,
        k: int = RRF_K_DEFAULT,
        top_k: int = RRF_TOP_K_DEFAULT,
    ) -> None:
        """Configure RRF fusion with rank constant k and output limit."""
        self.k = max(1, k)
        self.top_k = max(1, top_k)

    def fuse(
        self,
        dense_hits: list[RetrievalResult],
        sparse_hits: list[RetrievalResult],
        top_k: int | None = None,
    ) -> list[RetrievalResult]:
        """Merge dense and sparse ranked lists into RRF-ranked hits."""
        target_top_k = max(1, top_k or self.top_k)

        if not dense_hits and not sparse_hits:
            logger.info("rrf_no_hits")
            return []

        scores: dict[str, float] = {}
        payloads: dict[str, RetrievalResult] = {}

        for hits, method in ((dense_hits, "dense"), (sparse_hits, "sparse")):
            for rank, hit in enumerate(hits, start=1):
                scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1.0 / (
                    self.k + rank
                )
                if hit.chunk_id not in payloads or method == "dense":
                    payloads[hit.chunk_id] = hit

        ranked_ids = sorted(
            scores.keys(),
            key=lambda cid: (-scores[cid], cid),
        )[:target_top_k]

        fused: list[RetrievalResult] = []
        for cid in ranked_ids:
            source = payloads[cid]
            fused.append(
                RetrievalResult(
                    chunk_id=cid,
                    text=source.text,
                    file_name=source.file_name,
                    page_number=source.page_number,
                    relevance_score=scores[cid],
                    retrieval_method=RRF_METHOD,
                )
            )

        logger.info(
            "rrf_fusion_completed",
            dense_hits=len(dense_hits),
            sparse_hits=len(sparse_hits),
            fused_hits=len(fused),
        )
        return fused
