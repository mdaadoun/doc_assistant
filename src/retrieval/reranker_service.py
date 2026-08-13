"""Reranker domain service implementing primary/fallback strategy pattern."""

from collections.abc import Sequence
from typing import Any

import structlog

from clients.base_reranker import BaseRerankerAdapter
from clients.reranker import create_reranker_adapter
from core.config import get_settings
from core.exceptions import ConfigurationError, RetrievalError
from models.retrieval import RetrievalResult

logger = structlog.get_logger(__name__)


class RerankerService:
    """Service orchestrating cross-encoder reranking via primary and fallback adapters."""

    def __init__(
        self,
        primary_adapter: BaseRerankerAdapter | None = None,
        fallback_adapter: BaseRerankerAdapter | None = None,
        candidate_k: int | None = None,
        top_k: int | None = None,
        auto_fallback: bool = True,
    ) -> None:
        """Initialize reranker service with primary/fallback adapters or settings defaults."""
        settings = get_settings()
        self.candidate_k = candidate_k or settings.reranker_candidate_k
        self.top_k = top_k or settings.reranker_top_k
        self.auto_fallback = auto_fallback

        if primary_adapter is not None:
            self.primary_adapter: BaseRerankerAdapter | None = primary_adapter
        else:
            primary_prov = settings.reranker_provider or "flashrank"
            self.primary_adapter = self._safe_create_adapter(
                provider=primary_prov,
                model_name=settings.reranker_model,
                candidate_k=self.candidate_k,
                top_k=self.top_k,
            )

        if fallback_adapter is not None:
            self.fallback_adapter: BaseRerankerAdapter | None = fallback_adapter
        else:
            fallback_prov = "cohere" if settings.is_cohere_configured() else "mock"
            self.fallback_adapter = self._safe_create_adapter(
                provider=fallback_prov,
                candidate_k=self.candidate_k,
                top_k=self.top_k,
            )

    def _safe_create_adapter(
        self, provider: str, **kwargs: Any
    ) -> BaseRerankerAdapter | None:
        """Safely instantiate reranker adapter, returning None on error."""
        try:
            return create_reranker_adapter(provider=provider, **kwargs)
        except (ConfigurationError, Exception) as err:
            logger.warning(
                "reranker_adapter_init_failed", provider=provider, error=str(err)
            )
            return None

    def rerank(
        self,
        query: str,
        hits: Sequence[RetrievalResult],
        candidate_k: int | None = None,
        top_k: int | None = None,
    ) -> list[RetrievalResult]:
        """Rerank search candidates using primary adapter with fallback strategy handling."""
        if not query or not query.strip() or not hits:
            return []

        cand_k = candidate_k or self.candidate_k
        out_k = top_k or self.top_k

        if self.primary_adapter is not None:
            try:
                results = self.primary_adapter.rerank(
                    query=query, hits=hits, candidate_k=cand_k, top_k=out_k
                )
                logger.info(
                    "rerank_primary_success",
                    provider=self.primary_adapter.provider_name,
                    count=len(results),
                )
                return results
            except Exception as err:
                logger.warning(
                    "rerank_primary_failed_attempting_fallback",
                    provider=self.primary_adapter.provider_name,
                    error=str(err),
                )
                if not self.auto_fallback:
                    raise RetrievalError(
                        f"Primary reranker ({self.primary_adapter.provider_name}) failed: {err}",
                        code="RERANK_PRIMARY_FAILED",
                        details={"error": str(err)},
                    ) from err

        if self.auto_fallback and self.fallback_adapter is not None:
            try:
                results = self.fallback_adapter.rerank(
                    query=query, hits=hits, candidate_k=cand_k, top_k=out_k
                )
                logger.info(
                    "rerank_fallback_success",
                    provider=self.fallback_adapter.provider_name,
                    count=len(results),
                )
                return results
            except Exception as fallback_err:
                logger.error(
                    "rerank_fallback_failed",
                    provider=self.fallback_adapter.provider_name,
                    error=str(fallback_err),
                )
                raise RetrievalError(
                    f"Both primary and fallback rerankers failed. Fallback error: {fallback_err}",
                    code="RERANK_ALL_FAILED",
                    details={"error": str(fallback_err)},
                ) from fallback_err

        raise RetrievalError(
            "No functional reranker adapter available for execution.",
            code="RERANK_UNAVAILABLE",
        )
