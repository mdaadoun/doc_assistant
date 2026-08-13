"""Unit tests for RerankerService primary/fallback strategy pattern implementation."""

from unittest.mock import MagicMock

import pytest

from clients.mock_reranker import MockRerankerAdapter
from core.exceptions import RetrievalError
from models.retrieval import DebugRetrievalResponse, RetrievalResult
from retrieval.debug_retrieval import DebugRetrievalBuilder
from retrieval.reranker_service import RerankerService


def _create_sample_hits(count: int = 10, method: str = "rrf") -> list[RetrievalResult]:
    """Helper constructing sample retrieval hits for reranker testing."""
    return [
        RetrievalResult(
            chunk_id=f"chunk_{idx:03d}",
            text=f"Helvetia policy document sample section {idx}.",
            file_name="policy.pdf",
            page_number=1,
            relevance_score=1.0 / (idx + 1),
            retrieval_method=method,
        )
        for idx in range(1, count + 1)
    ]


def test_reranker_service_primary_success() -> None:
    """Verify primary reranker adapter success flow without triggering fallback."""
    primary = MagicMock()
    primary.provider_name = "mock_primary"
    primary.rerank.return_value = _create_sample_hits(3)

    fallback = MagicMock()
    fallback.provider_name = "mock_fallback"

    service = RerankerService(
        primary_adapter=primary,
        fallback_adapter=fallback,
        candidate_k=20,
        top_k=3,
    )
    sample_hits = _create_sample_hits(10)
    results = service.rerank("policy details", sample_hits)

    assert len(results) == 3
    primary.rerank.assert_called_once_with(
        query="policy details", hits=sample_hits, candidate_k=20, top_k=3
    )
    fallback.rerank.assert_not_called()


def test_reranker_service_primary_failure_fallback_success() -> None:
    """Verify fallback strategy execution when primary adapter raises an exception."""
    primary = MagicMock()
    primary.provider_name = "mock_primary"
    primary.rerank.side_effect = RuntimeError("Primary ONNX model failure")

    fallback_hits = _create_sample_hits(4, method="mock_fallback")

    fallback = MagicMock()
    fallback.provider_name = "mock_fallback"
    fallback.rerank.return_value = fallback_hits

    service = RerankerService(
        primary_adapter=primary,
        fallback_adapter=fallback,
        auto_fallback=True,
    )
    sample_hits = _create_sample_hits(10)
    results = service.rerank("insurance claim", sample_hits)

    assert len(results) == 4
    assert all(r.retrieval_method == "mock_fallback" for r in results)
    primary.rerank.assert_called_once()
    fallback.rerank.assert_called_once()


def test_reranker_service_both_failed_raises_retrieval_error() -> None:
    """Verify RetrievalError is raised when both primary and fallback adapters fail."""
    primary = MagicMock()
    primary.provider_name = "mock_primary"
    primary.rerank.side_effect = RuntimeError("Primary model error")

    fallback = MagicMock()
    fallback.provider_name = "mock_fallback"
    fallback.rerank.side_effect = ValueError("Fallback API HTTP timeout")

    service = RerankerService(
        primary_adapter=primary,
        fallback_adapter=fallback,
        auto_fallback=True,
    )
    sample_hits = _create_sample_hits(5)

    with pytest.raises(RetrievalError) as exc_info:
        service.rerank("query string", sample_hits)

    assert exc_info.value.code == "RERANK_ALL_FAILED"
    assert "Both primary and fallback rerankers failed" in str(exc_info.value)


def test_reranker_service_auto_fallback_disabled() -> None:
    """Verify primary failure immediately raises RetrievalError when auto_fallback is False."""
    primary = MagicMock()
    primary.provider_name = "mock_primary"
    primary.rerank.side_effect = RuntimeError("Primary failure")

    fallback = MagicMock()
    fallback.provider_name = "mock_fallback"

    service = RerankerService(
        primary_adapter=primary,
        fallback_adapter=fallback,
        auto_fallback=False,
    )
    sample_hits = _create_sample_hits(5)

    with pytest.raises(RetrievalError) as exc_info:
        service.rerank("query string", sample_hits)

    assert exc_info.value.code == "RERANK_PRIMARY_FAILED"
    fallback.rerank.assert_not_called()


def test_reranker_service_empty_or_blank_inputs() -> None:
    """Verify empty query or empty hits payload returns empty result without adapter invocation."""
    primary = MagicMock()
    fallback = MagicMock()
    service = RerankerService(primary_adapter=primary, fallback_adapter=fallback)

    assert service.rerank("", _create_sample_hits(5)) == []
    assert service.rerank("   ", _create_sample_hits(5)) == []
    assert service.rerank("valid query", []) == []

    primary.rerank.assert_not_called()
    fallback.rerank.assert_not_called()


def test_reranker_service_default_init_with_mock_adapters() -> None:
    """Verify default initialization produces functional service using fallback mock adapters."""
    primary_mock = MockRerankerAdapter()
    fallback_mock = MockRerankerAdapter()
    service = RerankerService(
        primary_adapter=primary_mock, fallback_adapter=fallback_mock
    )

    sample_hits = _create_sample_hits(10)
    reranked = service.rerank("policy document query", sample_hits, top_k=3)

    assert len(reranked) == 3


def test_debug_retrieval_builder_with_reranker_service() -> None:
    """Verify DebugRetrievalBuilder populates final_reranked when RerankerService is provided."""
    dense_search = MagicMock()
    dense_hits = _create_sample_hits(2)
    dense_search.search.return_value = dense_hits

    sparse_search = MagicMock()
    sparse_hits = _create_sample_hits(2)
    sparse_search.search.return_value = sparse_hits

    rrf_fusion = MagicMock()
    fused_hits = _create_sample_hits(2)
    rrf_fusion.fuse.return_value = fused_hits

    reranker_service = MagicMock()
    final_hits = _create_sample_hits(1)
    reranker_service.rerank.return_value = final_hits

    builder = DebugRetrievalBuilder(
        dense_search=dense_search,
        sparse_search=sparse_search,
        rrf_fusion=rrf_fusion,
        reranker=reranker_service,
    )

    response = builder.build("coverage details", rerank_top_k=1)
    assert isinstance(response, DebugRetrievalResponse)
    assert response.final_reranked == final_hits
    reranker_service.rerank.assert_called_once_with(
        "coverage details", fused_hits, top_k=1
    )
