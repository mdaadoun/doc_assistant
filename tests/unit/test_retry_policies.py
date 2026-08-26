"""Unit tests for Tenacity retry policies and external I/O resilience."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from clients.cohere_reranker import CohereRerankerAdapter
from clients.gemini_embedding import GeminiEmbeddingAdapter
from clients.openai_embedding import OpenAIEmbeddingAdapter
from core.exceptions import ConfigurationError
from core.retry import (
    create_async_retrying,
    create_sync_retrying,
    is_retryable_exception,
    retry_async_call,
    retry_sync_call,
)
from generation.engine import GroundedGenerator
from models.retrieval import RetrievalResult


class CustomStatusCodeError(Exception):
    """Custom exception with HTTP status_code attribute."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


def test_is_retryable_status_codes() -> None:
    """Verify standard retryable and non-retryable status codes."""
    assert is_retryable_exception(CustomStatusCodeError("Rate limited", 429)) is True
    assert is_retryable_exception(CustomStatusCodeError("Server error", 500)) is True
    assert is_retryable_exception(CustomStatusCodeError("Bad Gateway", 502)) is True
    assert is_retryable_exception(CustomStatusCodeError("Unavailable", 503)) is True
    assert is_retryable_exception(CustomStatusCodeError("Gateway Timeout", 504)) is True

    assert is_retryable_exception(CustomStatusCodeError("Bad Request", 400)) is False
    assert is_retryable_exception(CustomStatusCodeError("Unauthorized", 401)) is False
    assert is_retryable_exception(CustomStatusCodeError("Forbidden", 403)) is False
    assert is_retryable_exception(CustomStatusCodeError("Not Found", 404)) is False


def test_is_retryable_domain_and_standard_exceptions() -> None:
    """Verify domain ConfigurationError is never retried and stdlib network errors are retried."""
    assert is_retryable_exception(ConfigurationError("Config missing")) is False
    assert is_retryable_exception(TimeoutError("Connection timed out")) is True
    assert is_retryable_exception(ConnectionError("Connection reset by peer")) is True
    assert is_retryable_exception(ValueError("Invalid syntax")) is False


def test_is_retryable_httpx_errors() -> None:
    """Verify HTTPStatusError and httpx network errors."""
    req = httpx.Request("GET", "https://api.example.com")

    resp_429 = httpx.Response(429, request=req)
    resp_503 = httpx.Response(503, request=req)
    resp_401 = httpx.Response(401, request=req)

    assert (
        is_retryable_exception(
            httpx.HTTPStatusError("429", request=req, response=resp_429)
        )
        is True
    )
    assert (
        is_retryable_exception(
            httpx.HTTPStatusError("503", request=req, response=resp_503)
        )
        is True
    )
    assert (
        is_retryable_exception(
            httpx.HTTPStatusError("401", request=req, response=resp_401)
        )
        is False
    )

    assert is_retryable_exception(httpx.ConnectTimeout("Timeout", request=req)) is True
    assert (
        is_retryable_exception(httpx.NetworkError("Network down", request=req)) is True
    )


def test_sync_retry_success_on_first_try() -> None:
    """Verify synchronous function succeeds immediately on first invocation."""
    mock_fn = MagicMock(return_value="success")
    result = retry_sync_call(mock_fn, "arg1", kw="val")

    assert result == "success"
    assert mock_fn.call_count == 1
    mock_fn.assert_called_once_with("arg1", kw="val")


def test_sync_retry_transient_failure_recovery() -> None:
    """Verify synchronous retry recovers after transient rate limit failures."""
    mock_fn = MagicMock(
        side_effect=[
            CustomStatusCodeError("429 Too Many Requests", 429),
            CustomStatusCodeError("503 Service Unavailable", 503),
            "recovered",
        ]
    )

    result = retry_sync_call(
        mock_fn,
        max_attempts=4,
        min_wait=0.001,
        max_wait=0.005,
    )
    assert result == "recovered"
    assert mock_fn.call_count == 3


def test_sync_retry_exhaustion_raises() -> None:
    """Verify synchronous retry exhausts attempts and reraises last exception."""
    mock_fn = MagicMock(
        side_effect=CustomStatusCodeError("500 Internal Server Error", 500)
    )

    with pytest.raises(CustomStatusCodeError) as exc_info:
        retry_sync_call(
            mock_fn,
            max_attempts=3,
            min_wait=0.001,
            max_wait=0.005,
        )
    assert exc_info.value.status_code == 500
    assert mock_fn.call_count == 3


def test_sync_retry_non_retryable_fails_fast() -> None:
    """Verify non-retryable exception fails immediately without retrying."""
    mock_fn = MagicMock(side_effect=CustomStatusCodeError("401 Unauthorized", 401))

    with pytest.raises(CustomStatusCodeError) as exc_info:
        retry_sync_call(
            mock_fn,
            max_attempts=4,
            min_wait=0.001,
            max_wait=0.005,
        )
    assert exc_info.value.status_code == 401
    assert mock_fn.call_count == 1


@pytest.mark.asyncio
async def test_async_retry_success_and_transient_recovery() -> None:
    """Verify asynchronous retry recovers after transient failures."""
    mock_fn = AsyncMock(
        side_effect=[
            CustomStatusCodeError("429 Too Many Requests", 429),
            "async_recovered",
        ]
    )

    result = await retry_async_call(
        mock_fn,
        "query_param",
        max_attempts=3,
        min_wait=0.001,
        max_wait=0.005,
    )
    assert result == "async_recovered"
    assert mock_fn.call_count == 2


@pytest.mark.asyncio
async def test_async_retry_exhaustion_and_non_retryable() -> None:
    """Verify async retry handles attempt exhaustion and fast-failing."""
    mock_fn_exhaust = AsyncMock(
        side_effect=CustomStatusCodeError("502 Bad Gateway", 502)
    )

    with pytest.raises(CustomStatusCodeError):
        await retry_async_call(
            mock_fn_exhaust,
            max_attempts=3,
            min_wait=0.001,
            max_wait=0.005,
        )
    assert mock_fn_exhaust.call_count == 3

    mock_fn_fast_fail = AsyncMock(side_effect=ConfigurationError("Invalid API key"))
    with pytest.raises(ConfigurationError):
        await retry_async_call(
            mock_fn_fast_fail,
            max_attempts=4,
            min_wait=0.001,
            max_wait=0.005,
        )
    assert mock_fn_fast_fail.call_count == 1


def test_openai_embedding_retry_integration() -> None:
    """Verify OpenAIEmbeddingAdapter retries on transient errors and succeeds."""
    mock_client = MagicMock()
    mock_item = MagicMock()
    mock_item.index = 0
    mock_item.embedding = [0.1] * 1536

    mock_resp = MagicMock()
    mock_resp.data = [mock_item]

    mock_client.embeddings.create.side_effect = [
        CustomStatusCodeError("429 rate limited", 429),
        mock_resp,
    ]

    adapter = OpenAIEmbeddingAdapter(
        api_key="test-key",
        client=mock_client,
    )

    # Override settings for fast testing
    res = adapter.embed_text("test retry embedding")
    assert len(res) == 1536
    assert mock_client.embeddings.create.call_count == 2


def test_gemini_embedding_retry_integration() -> None:
    """Verify GeminiEmbeddingAdapter retries on transient 503 and succeeds."""
    mock_client = MagicMock()
    mock_emb = MagicMock()
    mock_emb.values = [0.2] * 768

    mock_resp = MagicMock()
    mock_resp.embeddings = [mock_emb]

    mock_client.models.embed_content.side_effect = [
        CustomStatusCodeError("503 backend unavailable", 503),
        mock_resp,
    ]

    adapter = GeminiEmbeddingAdapter(
        api_key="gemini-key",
        client=mock_client,
    )

    res = adapter.embed_text("gemini retry")
    assert len(res) == 768
    assert mock_client.models.embed_content.call_count == 2


def test_cohere_reranker_retry_integration() -> None:
    """Verify CohereRerankerAdapter retries on transient network errors."""
    mock_client = MagicMock()

    class MockItem:
        def __init__(self, index: int, score: float) -> None:
            self.index = index
            self.relevance_score = score

    class MockResponse:
        def __init__(self) -> None:
            self.results = [MockItem(0, 0.9)]

    mock_client.rerank.side_effect = [
        CustomStatusCodeError("502 Bad Gateway", 502),
        MockResponse(),
    ]

    adapter = CohereRerankerAdapter(
        api_key="cohere-key",
        client=mock_client,
    )

    sample_hit = RetrievalResult(
        chunk_id="c1",
        text="text content",
        file_name="doc.pdf",
        page_number=1,
        relevance_score=0.5,
        retrieval_method="dense",
    )

    results = adapter.rerank("test query", [sample_hit])
    assert len(results) == 1
    assert results[0].relevance_score == pytest.approx(0.9)
    assert mock_client.rerank.call_count == 2


@pytest.mark.asyncio
async def test_grounded_generator_retry_integration() -> None:
    """Verify GroundedGenerator retries on 429 during stream creation."""
    mock_client = MagicMock()

    class MockChoiceDelta:
        def __init__(self, content: str | None) -> None:
            self.content = content

    class MockChoice:
        def __init__(self, content: str | None) -> None:
            self.delta = MockChoiceDelta(content)

    class MockChunk:
        def __init__(self, content: str | None) -> None:
            self.choices = [MockChoice(content)]

    async def mock_stream_iter() -> AsyncGenerator[MockChunk, None]:
        yield MockChunk("Grounded response")

    mock_client.chat.completions.create = AsyncMock(
        side_effect=[
            CustomStatusCodeError("429 rate limit exceeded", 429),
            mock_stream_iter(),
        ]
    )

    gen = GroundedGenerator(client=mock_client)
    contexts = [{"file_name": "doc.pdf", "page_number": 1, "text": "content"}]

    tokens: list[str] = []
    async for tok in gen.generate_stream("What is the policy?", contexts):
        tokens.append(tok)

    assert "".join(tokens) == "Grounded response"
    assert mock_client.chat.completions.create.call_count == 2


def test_create_sync_and_async_retrying_instances() -> None:
    """Verify create_sync_retrying and create_async_retrying build configured Tenacity objects."""
    sync_retry = create_sync_retrying(max_attempts=5, min_wait=0.1, max_wait=2.0)
    assert sync_retry.stop is not None
    assert sync_retry.wait is not None

    async_retry = create_async_retrying(max_attempts=3, min_wait=0.2, max_wait=1.0)
    assert async_retry.stop is not None
    assert async_retry.wait is not None
