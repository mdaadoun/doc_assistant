"""Unit tests for OpenAI, Gemini, and Mock embedding client adapters."""

from unittest.mock import MagicMock

import pytest

from clients.embedding import EmbeddingClientAdapter
from clients.gemini_embedding import GeminiEmbeddingAdapter
from clients.mock_embedding import MockEmbeddingAdapter
from clients.openai_embedding import OpenAIEmbeddingAdapter
from core.exceptions import ConfigurationError, RetrievalError


def test_mock_embedding_adapter_basic() -> None:
    """Verify MockEmbeddingAdapter generates deterministic 1536d normalized vectors."""
    adapter = MockEmbeddingAdapter(model_name="mock-test", dimension=1536)
    assert adapter.dimension == 1536
    assert adapter.model_name == "mock-test"

    vec = adapter.embed_text("Helvetia insurance documentation")
    assert len(vec) == 1536
    assert isinstance(vec[0], float)

    # Test determinism
    vec_again = adapter.embed_text("Helvetia insurance documentation")
    assert vec == vec_again

    # Test batch embedding
    texts = ["doc 1", "doc 2", "doc 3"]
    batch_vecs = adapter.embed_batch(texts)
    assert len(batch_vecs) == 3
    assert len(batch_vecs[0]) == 1536


def test_mock_embedding_adapter_empty_and_batching() -> None:
    """Verify MockEmbeddingAdapter handles empty sequences and custom batching."""
    adapter = MockEmbeddingAdapter(dimension=512)
    assert adapter.embed_batch([]) == []

    texts = [f"text chunk {i}" for i in range(10)]
    results = adapter.embed_batch(texts, batch_size=3)
    assert len(results) == 10
    assert all(len(v) == 512 for v in results)


def test_openai_adapter_missing_key_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify OpenAIEmbeddingAdapter raises ConfigurationError when key missing."""
    monkeypatch.setenv("OPENAI_API_KEY", "")
    with pytest.raises(ConfigurationError, match="OpenAI API key is missing"):
        OpenAIEmbeddingAdapter(api_key="")


def test_openai_adapter_mocked_client() -> None:
    """Verify OpenAIEmbeddingAdapter processes responses using injected mock client."""
    mock_client = MagicMock()
    mock_item_0 = MagicMock()
    mock_item_0.index = 0
    mock_item_0.embedding = [0.1] * 1536

    mock_item_1 = MagicMock()
    mock_item_1.index = 1
    mock_item_1.embedding = [0.2] * 1536

    mock_response = MagicMock()
    mock_response.data = [
        mock_item_1,
        mock_item_0,
    ]  # Unsorted order to test index sorting
    mock_client.embeddings.create.return_value = mock_response

    adapter = OpenAIEmbeddingAdapter(
        model_name="text-embedding-3-small",
        api_key="sk-dummy-key",
        client=mock_client,
    )

    assert adapter.dimension == 1536
    assert adapter.model_name == "text-embedding-3-small"

    results = adapter.embed_batch(["hello", "world"])
    assert len(results) == 2
    assert results[0] == [0.1] * 1536
    assert results[1] == [0.2] * 1536
    mock_client.embeddings.create.assert_called_once()


def test_openai_adapter_error_wrapping() -> None:
    """Verify OpenAIEmbeddingAdapter wraps client API exceptions into RetrievalError."""
    mock_client = MagicMock()
    mock_client.embeddings.create.side_effect = RuntimeError("API Rate Limit Exceeded")

    adapter = OpenAIEmbeddingAdapter(
        model_name="text-embedding-3-small",
        api_key="sk-dummy-key",
        client=mock_client,
    )

    with pytest.raises(RetrievalError, match="OpenAI embedding generation failed"):
        adapter.embed_text("test sentence")


def test_gemini_adapter_missing_key_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify GeminiEmbeddingAdapter raises ConfigurationError when key missing."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with pytest.raises(ConfigurationError, match="Gemini API key is missing"):
        GeminiEmbeddingAdapter(api_key="")


def test_gemini_adapter_mocked_client() -> None:
    """Verify GeminiEmbeddingAdapter generates vectors via injected mock client."""
    mock_client = MagicMock()
    mock_emb_0 = MagicMock()
    mock_emb_0.values = [0.5] * 768

    mock_response = MagicMock()
    mock_response.embeddings = [mock_emb_0]
    mock_client.models.embed_content.return_value = mock_response

    adapter = GeminiEmbeddingAdapter(
        model_name="text-embedding-004",
        api_key="gemini-dummy-key",
        dimension=768,
        client=mock_client,
    )

    assert adapter.dimension == 768
    vec = adapter.embed_text("Gemini text embedding")
    assert len(vec) == 768
    assert vec == [0.5] * 768


def test_facade_provider_selection_mock() -> None:
    """Verify EmbeddingClientAdapter selects mock provider correctly."""
    adapter = EmbeddingClientAdapter(provider="mock", dimension=1536)
    assert adapter.provider == "mock"
    assert adapter.dimension == 1536
    vec = adapter.embed_text("Facade test")
    assert len(vec) == 1536


def test_facade_provider_auto_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify EmbeddingClientAdapter auto falls back to mock when keys missing."""
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    adapter = EmbeddingClientAdapter(provider="auto")
    assert adapter.provider == "mock"


def test_facade_unsupported_provider_raises_error() -> None:
    """Verify EmbeddingClientAdapter raises ConfigurationError on invalid provider."""
    with pytest.raises(ConfigurationError, match="Unsupported embedding provider"):
        EmbeddingClientAdapter(provider="invalid_provider")
