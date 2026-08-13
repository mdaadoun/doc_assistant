"""FlashRank local cross-encoder model adapter using ONNX runtime."""

from collections.abc import Sequence
from typing import Any

import structlog

from clients.base_reranker import BaseRerankerAdapter
from core.exceptions import ConfigurationError, RetrievalError
from models.retrieval import RetrievalResult

logger = structlog.get_logger(__name__)

FLASHRANK_DEFAULT_MODEL = "ms-marco-MiniLM-L-6-v2"
FLASHRANK_FALLBACK_MODEL = "ms-marco-MiniLM-L-12-v2"
FLASHRANK_PROVIDER_NAME = "flashrank"
DEFAULT_CANDIDATE_K = 30
DEFAULT_TOP_K = 5


class FlashRankRerankerAdapter(BaseRerankerAdapter):
    """FlashRank cross-encoder adapter for re-ranking hybrid search candidates."""

    def __init__(
        self,
        model_name: str = FLASHRANK_DEFAULT_MODEL,
        candidate_k: int = DEFAULT_CANDIDATE_K,
        top_k: int = DEFAULT_TOP_K,
        cache_dir: str | None = None,
        ranker_instance: Any | None = None,
    ) -> None:
        """Initialize FlashRank cross-encoder with model parameters or prebuilt ranker."""
        self._requested_model_name = model_name
        self.candidate_k = max(1, candidate_k)
        self.top_k = max(1, top_k)
        self.cache_dir = cache_dir

        if ranker_instance is not None:
            self._ranker = ranker_instance
            self._effective_model_name = model_name
        else:
            self._effective_model_name, self._ranker = self._initialize_ranker(
                model_name, cache_dir
            )

    def _initialize_ranker(
        self, model_name: str, cache_dir: str | None
    ) -> tuple[str, Any]:
        """Instantiate FlashRank Ranker with graceful model mapping and error wrapping."""
        try:
            import flashrank.Config as config
            from flashrank import Ranker
        except ImportError as err:
            raise ConfigurationError(
                "flashrank package is not installed",
                code="DEPENDENCY_ERROR",
                details={"package": "flashrank"},
            ) from err

        target_model = model_name
        if target_model not in config.model_file_map:
            logger.info(
                "flashrank_model_unmapped_using_fallback",
                requested=model_name,
                fallback=FLASHRANK_FALLBACK_MODEL,
            )
            target_model = FLASHRANK_FALLBACK_MODEL

        kwargs: dict[str, Any] = {"model_name": target_model}
        if cache_dir:
            kwargs["cache_dir"] = cache_dir

        try:
            ranker = Ranker(**kwargs)
            logger.info(
                "flashrank_ranker_initialized",
                requested_model=model_name,
                effective_model=target_model,
            )
            return target_model, ranker
        except Exception as err:
            logger.error(
                "flashrank_init_failed",
                model=target_model,
                error=str(err),
            )
            raise RetrievalError(
                f"Failed to initialize FlashRank model {target_model}: {err}",
                code="RERANKER_INIT_ERROR",
                details={"model_name": target_model, "error": str(err)},
            ) from err

    def rerank(
        self,
        query: str,
        hits: Sequence[RetrievalResult],
        candidate_k: int | None = None,
        top_k: int | None = None,
    ) -> list[RetrievalResult]:
        """Rerank candidates top candidate_k (30) to top_k (5) using cross-encoder."""
        if not hits:
            logger.info("flashrank_rerank_empty_hits")
            return []

        clean_query = query.strip()
        if not clean_query:
            logger.warning("flashrank_rerank_empty_query")
            return []

        eff_candidate_k = candidate_k if candidate_k is not None else self.candidate_k
        eff_top_k = top_k if top_k is not None else self.top_k
        c_k = max(1, eff_candidate_k)
        t_k = max(1, eff_top_k)

        candidate_hits = list(hits[:c_k])
        payload_map = {hit.chunk_id: hit for hit in candidate_hits}

        passages: list[dict[str, Any]] = [
            {
                "id": hit.chunk_id,
                "text": hit.text,
                "meta": {
                    "file_name": hit.file_name,
                    "page_number": hit.page_number,
                },
            }
            for hit in candidate_hits
        ]

        try:
            from flashrank import RerankRequest

            request = RerankRequest(query=clean_query, passages=passages)
            raw_results: list[dict[str, Any]] = self._ranker.rerank(request)
        except Exception as err:
            logger.error(
                "flashrank_inference_failed",
                query=clean_query,
                candidates_count=len(candidate_hits),
                error=str(err),
            )
            raise RetrievalError(
                f"FlashRank cross-encoder inference failed: {err}",
                code="RERANKER_INFERENCE_ERROR",
                details={"query": clean_query, "error": str(err)},
            ) from err

        reranked_results: list[RetrievalResult] = []
        for item in raw_results[:t_k]:
            cid = str(item["id"])
            score = float(item.get("score", 0.0))
            source_hit = payload_map.get(cid)
            if not source_hit:
                continue

            reranked_results.append(
                RetrievalResult(
                    chunk_id=cid,
                    text=source_hit.text,
                    file_name=source_hit.file_name,
                    page_number=source_hit.page_number,
                    relevance_score=score,
                    retrieval_method=FLASHRANK_PROVIDER_NAME,
                )
            )

        reranked_results.sort(key=lambda r: (-r.relevance_score, r.chunk_id))

        logger.info(
            "flashrank_rerank_completed",
            input_candidates=len(candidate_hits),
            output_reranked=len(reranked_results),
            top_score=reranked_results[0].relevance_score if reranked_results else 0.0,
        )

        return reranked_results

    @property
    def model_name(self) -> str:
        """Return model identifier."""
        return self._effective_model_name

    @property
    def provider_name(self) -> str:
        """Return provider identifier."""
        return FLASHRANK_PROVIDER_NAME
