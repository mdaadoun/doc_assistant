"""Cohere Rerank API adapter implementation with SDK and HTTP fallback support."""

from collections.abc import Sequence
from typing import Any

import httpx
import structlog

from clients.base_reranker import BaseRerankerAdapter
from core.config import get_settings
from core.exceptions import ConfigurationError, RetrievalError
from core.retry import retry_sync_call
from models.retrieval import RetrievalResult

logger = structlog.get_logger(__name__)

COHERE_DEFAULT_MODEL = "rerank-v3.5"
COHERE_PROVIDER_NAME = "cohere"
COHERE_API_URL = "https://api.cohere.com/v2/rerank"
DEFAULT_CANDIDATE_K = 30
DEFAULT_TOP_K = 5


class CohereRerankerAdapter(BaseRerankerAdapter):
    """Cohere Rerank API adapter supporting cross-encoder candidate reranking."""

    def __init__(
        self,
        model_name: str | None = None,
        api_key: str | None = None,
        candidate_k: int = DEFAULT_CANDIDATE_K,
        top_k: int = DEFAULT_TOP_K,
        client: Any | None = None,
        httpx_client: httpx.Client | None = None,
    ) -> None:
        """Initialize Cohere reranker with API credentials and parameters."""
        settings = get_settings()
        self._model_name = model_name or COHERE_DEFAULT_MODEL
        self.candidate_k = max(1, candidate_k)
        self.top_k = max(1, top_k)
        self._client = client
        self._httpx_client = httpx_client

        resolved_key = api_key or settings.cohere_api_key
        self._api_key = resolved_key

        if self._client is None and not (resolved_key and resolved_key.strip()):
            raise ConfigurationError(
                "Cohere API key is missing or unconfigured",
                code="MISSING_API_KEY",
                details={"provider": COHERE_PROVIDER_NAME},
            )

    @property
    def model_name(self) -> str:
        """Return Cohere model identifier."""
        return self._model_name

    @property
    def provider_name(self) -> str:
        """Return provider identifier."""
        return COHERE_PROVIDER_NAME

    def rerank(
        self,
        query: str,
        hits: Sequence[RetrievalResult],
        candidate_k: int | None = None,
        top_k: int | None = None,
    ) -> list[RetrievalResult]:
        """Rerank candidates using Cohere Rerank API endpoint."""
        if not hits:
            logger.info("cohere_rerank_empty_hits")
            return []

        clean_query = query.strip()
        if not clean_query:
            logger.warning("cohere_rerank_empty_query")
            return []

        eff_candidate_k = candidate_k if candidate_k is not None else self.candidate_k
        eff_top_k = top_k if top_k is not None else self.top_k
        c_k = max(1, eff_candidate_k)
        t_k = max(1, eff_top_k)

        candidate_hits = list(hits[:c_k])
        documents = [hit.text for hit in candidate_hits]

        try:
            raw_results = self._call_cohere_api(clean_query, documents, t_k)
        except ConfigurationError:
            raise
        except Exception as err:
            logger.error(
                "cohere_rerank_failed",
                model=self._model_name,
                query=clean_query,
                error=str(err),
            )
            raise RetrievalError(
                f"Cohere reranker API error: {err}",
                code="RERANKER_INFERENCE_ERROR",
                details={"model_name": self._model_name, "error": str(err)},
            ) from err

        reranked_results: list[RetrievalResult] = []
        for item in raw_results:
            if isinstance(item, dict):
                idx = item.get("index")
                score = float(item.get("relevance_score", 0.0))
            else:
                idx = getattr(item, "index", None)
                score = float(getattr(item, "relevance_score", 0.0))

            if idx is None or not (0 <= idx < len(candidate_hits)):
                continue

            source_hit = candidate_hits[idx]
            reranked_results.append(
                RetrievalResult(
                    chunk_id=source_hit.chunk_id,
                    text=source_hit.text,
                    file_name=source_hit.file_name,
                    page_number=source_hit.page_number,
                    relevance_score=score,
                    retrieval_method=COHERE_PROVIDER_NAME,
                )
            )

        reranked_results.sort(key=lambda r: (-r.relevance_score, r.chunk_id))
        final_results = reranked_results[:t_k]

        logger.info(
            "cohere_rerank_completed",
            input_candidates=len(candidate_hits),
            output_reranked=len(final_results),
            top_score=final_results[0].relevance_score if final_results else 0.0,
        )

        return final_results

    def _call_cohere_api(
        self, query: str, documents: list[str], top_n: int
    ) -> list[Any]:
        """Invoke Cohere API with Tenacity exponential backoff retry policy."""
        return retry_sync_call(
            self._raw_call_cohere_api,
            query,
            documents,
            top_n,
        )

    def _raw_call_cohere_api(
        self, query: str, documents: list[str], top_n: int
    ) -> list[Any]:
        """Invoke Cohere client SDK or direct HTTP request via httpx."""
        if self._client is not None:
            if hasattr(self._client, "rerank"):
                response = self._client.rerank(
                    model=self._model_name,
                    query=query,
                    documents=documents,
                    top_n=top_n,
                )
                return list(getattr(response, "results", response))
            elif hasattr(self._client, "post"):
                headers = {
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": self._model_name,
                    "query": query,
                    "documents": documents,
                    "top_n": top_n,
                }
                response = self._client.post(
                    COHERE_API_URL, headers=headers, json=payload
                )
                response.raise_for_status()
                data = response.json()
                return list(data.get("results", []))

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model_name,
            "query": query,
            "documents": documents,
            "top_n": top_n,
        }

        if self._httpx_client is not None:
            resp = self._httpx_client.post(
                COHERE_API_URL, headers=headers, json=payload
            )
        else:
            with httpx.Client(timeout=10.0) as http_client:
                resp = http_client.post(COHERE_API_URL, headers=headers, json=payload)

        resp.raise_for_status()
        res_data = resp.json()
        return list(res_data.get("results", []))
