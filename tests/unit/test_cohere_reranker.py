"""Unit tests for Cohere cross-encoder reranker adapter."""

from unittest.mock import MagicMock

import httpx
import pytest

from clients.cohere_reranker import (
    COHERE_DEFAULT_MODEL,
    COHERE_PROVIDER_NAME,
    DEFAULT_CANDIDATE_K,
    DEFAULT_TOP_K,
    CohereRerankerAdapter,
)
from clients.reranker import create_reranker_adapter
from core.exceptions import ConfigurationError, RetrievalError
from models.retrieval import RetrievalResult


def _create_sample_hits(count: int = 35) -> list[RetrievalResult]:
    """Helper creating sample retrieval results for Cohere reranker testing."""
    hits: list[RetrievalResult] = []
    for idx in range(1, count + 1):
        hits.append(
            RetrievalResult(
                chunk_id=f"chunk_{idx:03d}",
                text=f"Helvetia document content excerpt for item {idx} regarding policy guidelines.",
                file_name="policy.pdf",
                page_number=(idx % 4) + 1,
                relevance_score=1.0 / (idx + 1),
                retrieval_method="rrf",
            )
        )
    return hits


def test_cohere_adapter_init_defaults() -> None:
    """Verify CohereRerankerAdapter initializes with expected defaults when key is provided."""
    adapter = CohereRerankerAdapter(api_key="test-cohere-key")

    assert adapter.provider_name == COHERE_PROVIDER_NAME
    assert adapter.model_name == COHERE_DEFAULT_MODEL
    assert adapter.candidate_k == DEFAULT_CANDIDATE_K
    assert adapter.top_k == DEFAULT_TOP_K


def test_cohere_adapter_missing_api_key_raises() -> None:
    """Verify initialization without API key raises ConfigurationError."""
    with pytest.raises(ConfigurationError) as exc_info:
        CohereRerankerAdapter(api_key="")

    assert exc_info.value.code == "MISSING_API_KEY"


def test_cohere_rerank_with_mock_sdk_client() -> None:
    """Verify reranking using mocked Cohere SDK client."""
    mock_client = MagicMock()

    class MockItem:
        def __init__(self, index: int, score: float) -> None:
            self.index = index
            self.relevance_score = score

    class MockResponse:
        def __init__(self) -> None:
            self.results = [MockItem(2, 0.95), MockItem(0, 0.85)]

    mock_client.rerank.return_value = MockResponse()

    adapter = CohereRerankerAdapter(
        api_key="test-key", candidate_k=20, top_k=2, client=mock_client
    )
    sample_hits = _create_sample_hits(30)
    results = adapter.rerank("policy guidelines", sample_hits)

    assert mock_client.rerank.call_count == 1
    call_kwargs = mock_client.rerank.call_args[1]
    assert call_kwargs["model"] == COHERE_DEFAULT_MODEL
    assert call_kwargs["query"] == "policy guidelines"
    assert len(call_kwargs["documents"]) == 20
    assert call_kwargs["top_n"] == 2

    assert len(results) == 2
    assert results[0].chunk_id == "chunk_003"
    assert results[0].relevance_score == pytest.approx(0.95)
    assert results[0].retrieval_method == COHERE_PROVIDER_NAME
    assert results[1].chunk_id == "chunk_001"
    assert results[1].relevance_score == pytest.approx(0.85)


def test_cohere_rerank_with_httpx_mock_client() -> None:
    """Verify reranking using mocked HTTP client."""
    mock_httpx = MagicMock(spec=httpx.Client)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {
        "results": [
            {"index": 1, "relevance_score": 0.91},
            {"index": 0, "relevance_score": 0.72},
        ]
    }
    mock_httpx.post.return_value = mock_response

    adapter = CohereRerankerAdapter(
        api_key="test-key", candidate_k=10, top_k=2, httpx_client=mock_httpx
    )
    sample_hits = _create_sample_hits(15)
    results = adapter.rerank("corporate guidelines", sample_hits)

    assert mock_httpx.post.call_count == 1
    assert len(results) == 2
    assert results[0].chunk_id == "chunk_002"
    assert results[0].relevance_score == pytest.approx(0.91)


def test_cohere_rerank_empty_or_blank_inputs() -> None:
    """Verify empty hits or blank query return empty list without calling API."""
    mock_client = MagicMock()
    adapter = CohereRerankerAdapter(api_key="test-key", client=mock_client)

    assert adapter.rerank("query", []) == []
    assert adapter.rerank("   ", _create_sample_hits(5)) == []
    assert mock_client.rerank.call_count == 0


def test_cohere_api_error_handling() -> None:
    """Verify Cohere API errors are wrapped in RetrievalError."""
    mock_client = MagicMock()
    mock_client.rerank.side_effect = RuntimeError("Cohere API rate limit exceeded")

    adapter = CohereRerankerAdapter(api_key="test-key", client=mock_client)
    sample_hits = _create_sample_hits(5)

    with pytest.raises(RetrievalError) as exc_info:
        adapter.rerank("query", sample_hits)

    assert exc_info.value.code == "RERANKER_INFERENCE_ERROR"
    assert "Cohere API rate limit exceeded" in exc_info.value.message


def test_create_cohere_reranker_via_factory() -> None:
    """Verify create_reranker_adapter factory instantiates Cohere adapter."""
    mock_client = MagicMock()
    adapter = create_reranker_adapter(
        provider="cohere",
        model_name="rerank-v3.5",
        candidate_k=25,
        top_k=4,
        client=mock_client,
    )
    assert isinstance(adapter, CohereRerankerAdapter)
    assert adapter.model_name == "rerank-v3.5"
    assert adapter.candidate_k == 25
    assert adapter.top_k == 4
