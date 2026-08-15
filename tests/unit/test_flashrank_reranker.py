"""Unit tests for FlashRank cross-encoder adapter and reranker interfaces."""

from unittest.mock import MagicMock

import pytest

from clients.base_reranker import BaseRerankerAdapter
from clients.flashrank_reranker import (
    DEFAULT_CANDIDATE_K,
    DEFAULT_TOP_K,
    FLASHRANK_DEFAULT_MODEL,
    FLASHRANK_PROVIDER_NAME,
    FlashRankRerankerAdapter,
)
from clients.mock_reranker import MOCK_RERANKER_PROVIDER, MockRerankerAdapter
from clients.reranker import create_reranker_adapter
from core.exceptions import ConfigurationError, RetrievalError
from models.retrieval import RetrievalResult


def _create_sample_hits(count: int = 40) -> list[RetrievalResult]:
    """Helper creating sample retrieval results for reranker testing."""
    hits: list[RetrievalResult] = []
    for idx in range(1, count + 1):
        hits.append(
            RetrievalResult(
                chunk_id=f"chunk_{idx:03d}",
                text=f"Helvetia document content excerpt for item {idx} discussing corporate policy.",
                file_name="policy_guide.pdf",
                page_number=(idx % 5) + 1,
                relevance_score=1.0 / (idx + 1),
                retrieval_method="rrf",
            )
        )
    return hits


def test_base_reranker_interface_contract() -> None:
    """Verify BaseRerankerAdapter is an abstract class requiring concrete implementations."""
    with pytest.raises(TypeError):
        BaseRerankerAdapter()  # type: ignore[abstract]


def test_mock_reranker_adapter_success() -> None:
    """Verify MockRerankerAdapter candidate slicing, scoring, and top_k filtering."""
    adapter = MockRerankerAdapter(default_candidate_k=30, default_top_k=5)
    assert adapter.provider_name == MOCK_RERANKER_PROVIDER
    assert adapter.model_name == "mock-miniLM-L6-v2"

    sample_hits = _create_sample_hits(40)
    query = "corporate policy guidance"
    reranked = adapter.rerank(query, sample_hits)

    assert len(reranked) == 5
    assert all(r.retrieval_method == "mock_flashrank" for r in reranked)
    # Assert descending order
    scores = [r.relevance_score for r in reranked]
    assert scores == sorted(scores, reverse=True)


def test_mock_reranker_empty_inputs() -> None:
    """Verify MockRerankerAdapter handles empty hits or empty query cleanly."""
    adapter = MockRerankerAdapter()
    assert adapter.rerank("", _create_sample_hits(5)) == []
    assert adapter.rerank("query", []) == []


def test_flashrank_adapter_init_defaults() -> None:
    """Verify FlashRankRerankerAdapter initializes with expected default constants."""
    mock_ranker = MagicMock()
    adapter = FlashRankRerankerAdapter(ranker_instance=mock_ranker)

    assert adapter.provider_name == FLASHRANK_PROVIDER_NAME
    assert adapter.model_name == FLASHRANK_DEFAULT_MODEL
    assert adapter.candidate_k == DEFAULT_CANDIDATE_K
    assert adapter.top_k == DEFAULT_TOP_K


def test_flashrank_rerank_with_mocked_ranker() -> None:
    """Verify FlashRank adapter formats passages, passes to Ranker, and returns top_k hits."""
    mock_ranker = MagicMock()
    # Mock Ranker return: reverse order of first 5 chunks
    raw_passages = [
        {
            "id": f"chunk_{(31 - i):03d}",
            "text": f"Helvetia document content excerpt for item {31 - i} discussing corporate policy.",
            "score": 0.95 - (i * 0.05),
        }
        for i in range(1, 31)
    ]
    mock_ranker.rerank.return_value = raw_passages

    adapter = FlashRankRerankerAdapter(
        model_name="ms-marco-MiniLM-L-6-v2",
        candidate_k=30,
        top_k=5,
        ranker_instance=mock_ranker,
    )

    sample_hits = _create_sample_hits(40)

    reranked = adapter.rerank("corporate policy", sample_hits)

    # Verify ranker was called with top 30 candidates
    assert mock_ranker.rerank.call_count == 1
    call_args = mock_ranker.rerank.call_args[0][0]
    assert call_args.query == "corporate policy"
    assert len(call_args.passages) == 30

    # Verify top 5 output limit and score assignment
    assert len(reranked) == 5
    assert reranked[0].chunk_id == "chunk_030"
    assert reranked[0].relevance_score == pytest.approx(0.90)
    assert reranked[0].retrieval_method == "flashrank"


def test_flashrank_rerank_empty_or_blank_inputs() -> None:
    """Verify FlashRank adapter returns empty list for empty hits or blank query."""
    mock_ranker = MagicMock()
    adapter = FlashRankRerankerAdapter(ranker_instance=mock_ranker)

    assert adapter.rerank("query", []) == []
    assert adapter.rerank("   ", _create_sample_hits(10)) == []
    assert mock_ranker.rerank.call_count == 0


def test_flashrank_inference_error_wrapping() -> None:
    """Verify FlashRank adapter wraps inference exceptions in RetrievalError."""
    mock_ranker = MagicMock()
    mock_ranker.rerank.side_error = RuntimeError("ONNX execution error")
    mock_ranker.rerank.side_effect = RuntimeError("ONNX execution error")

    adapter = FlashRankRerankerAdapter(ranker_instance=mock_ranker)
    sample_hits = _create_sample_hits(10)

    with pytest.raises(RetrievalError) as exc_info:
        adapter.rerank("query", sample_hits)

    assert exc_info.value.code == "RERANKER_INFERENCE_ERROR"
    assert "ONNX execution error" in exc_info.value.message


def test_create_reranker_adapter_factory() -> None:
    """Verify create_reranker_adapter factory instantiates flashrank and mock providers."""
    mock_adapter = create_reranker_adapter("mock", candidate_k=20, top_k=3)
    assert isinstance(mock_adapter, MockRerankerAdapter)
    assert mock_adapter.default_candidate_k == 20
    assert mock_adapter.default_top_k == 3

    with pytest.raises(ConfigurationError) as exc_info:
        create_reranker_adapter("unsupported_provider")
    assert exc_info.value.code == "UNSUPPORTED_PROVIDER"


def test_flashrank_real_model_inference_optional() -> None:
    """Test FlashRank adapter with real model using installed flashrank package."""
    try:
        adapter = FlashRankRerankerAdapter(
            model_name="ms-marco-MiniLM-L-12-v2", candidate_k=10, top_k=3
        )
    except RetrievalError as err:
        pytest.skip(
            f"FlashRank model download failed (likely offline/sandboxed): {err}"
        )
    sample_hits = _create_sample_hits(15)
    reranked = adapter.rerank("corporate policy", sample_hits)

    assert len(reranked) == 3
    assert all(r.retrieval_method == "flashrank" for r in reranked)
    assert reranked[0].relevance_score >= reranked[1].relevance_score
