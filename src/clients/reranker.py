"""Reranker adapter factory and default provider loader."""

from typing import Any

from clients.base_reranker import BaseRerankerAdapter
from clients.cohere_reranker import CohereRerankerAdapter
from clients.flashrank_reranker import FlashRankRerankerAdapter
from clients.mock_reranker import MockRerankerAdapter
from core.exceptions import ConfigurationError


def create_reranker_adapter(
    provider: str = "flashrank",
    model_name: str | None = None,
    candidate_k: int = 30,
    top_k: int = 5,
    **kwargs: Any,
) -> BaseRerankerAdapter:
    """Instantiate a reranker adapter for the given provider."""
    prov = provider.lower().strip()
    if prov == "flashrank":
        model = model_name or "ms-marco-MiniLM-L-6-v2"
        return FlashRankRerankerAdapter(
            model_name=model, candidate_k=candidate_k, top_k=top_k, **kwargs
        )
    elif prov == "cohere":
        model = model_name or "rerank-v3.5"
        return CohereRerankerAdapter(
            model_name=model, candidate_k=candidate_k, top_k=top_k, **kwargs
        )
    elif prov == "mock":
        model = model_name or "mock-miniLM-L6-v2"
        return MockRerankerAdapter(
            model_name=model, default_candidate_k=candidate_k, default_top_k=top_k
        )
    else:
        raise ConfigurationError(
            f"Unsupported reranker provider: {provider}",
            code="UNSUPPORTED_PROVIDER",
            details={"provider": provider},
        )
