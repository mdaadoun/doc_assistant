"""Unit tests for Qdrant vector store adapter."""

from unittest.mock import MagicMock

import pytest
from qdrant_client import QdrantClient
from qdrant_client.models import Distance

from core.exceptions import RetrievalError
from models.chunk import ChunkDocument, ChunkMetadata
from retrieval.vector_store import VectorStoreAdapter, _to_valid_uuid


@pytest.fixture
def memory_qdrant_client() -> QdrantClient:
    """Fixture providing in-memory Qdrant client."""
    return QdrantClient(location=":memory:")


@pytest.fixture
def sample_chunk() -> ChunkDocument:
    """Fixture providing sample ChunkDocument."""
    return ChunkDocument(
        chunk_id="doc_1_chunk_0",
        text="Helvetia doc assistant retrieval test.",
        file_name="policy.pdf",
        page_number=1,
        metadata=ChunkMetadata(
            source_format="pdf",
            chunk_index=0,
            total_chunks=1,
            char_count=37,
            token_count=8,
        ),
    )


def test_uuid_conversion() -> None:
    """Verify string to valid UUID conversion helper."""
    uuid_str = "550e8400-e29b-41d4-a716-446655440000"
    assert _to_valid_uuid(uuid_str) == uuid_str
    converted = _to_valid_uuid("doc_1_chunk_0")
    assert converted != "doc_1_chunk_0"
    assert len(converted) == 36


def test_adapter_init_defaults(memory_qdrant_client: QdrantClient) -> None:
    """Verify adapter initialization defaults and injected client binding."""
    adapter = VectorStoreAdapter(client=memory_qdrant_client)
    assert adapter.client == memory_qdrant_client
    assert adapter.vector_dim == 1536
    assert adapter.distance == Distance.COSINE


def test_adapter_init_failure() -> None:
    """Verify exception handling when QdrantClient fails during initialization."""
    mock_qdrant_cls = MagicMock(side_effect=RuntimeError("Connection refused"))
    with (
        pytest.raises(RetrievalError) as exc_info,
        pytest.MonkeyPatch.context() as mp,
    ):
        mp.setattr("retrieval.vector_store.QdrantClient", mock_qdrant_cls)
        VectorStoreAdapter(host="invalid_host", port=9999)
    assert "Failed to initialize Qdrant client" in exc_info.value.message


def test_ensure_and_exists_collection(memory_qdrant_client: QdrantClient) -> None:
    """Verify collection creation, existence checks, and recreation."""
    adapter = VectorStoreAdapter(
        client=memory_qdrant_client, collection_name="test_collection", vector_dim=1536
    )
    assert not adapter.collection_exists()

    res = adapter.ensure_collection()
    assert res is True
    assert adapter.collection_exists()

    # Ensure collection again (no-op)
    assert adapter.ensure_collection() is True

    # Recreate collection
    assert adapter.ensure_collection(recreate=True) is True
    assert adapter.collection_exists()


def test_upsert_and_count_chunks(
    memory_qdrant_client: QdrantClient, sample_chunk: ChunkDocument
) -> None:
    """Verify upserting chunks and fetching collection point count."""
    adapter = VectorStoreAdapter(
        client=memory_qdrant_client, collection_name="test_collection"
    )
    adapter.ensure_collection()

    embedding = [0.01] * 1536
    count = adapter.upsert_chunks(chunks=[sample_chunk], embeddings=[embedding])
    assert count == 1
    assert adapter.get_count() == 1


def test_upsert_mismatch_error(
    memory_qdrant_client: QdrantClient, sample_chunk: ChunkDocument
) -> None:
    """Verify RetrievalError raised when chunk count and embeddings count mismatch."""
    adapter = VectorStoreAdapter(
        client=memory_qdrant_client, collection_name="test_collection"
    )
    adapter.ensure_collection()

    with pytest.raises(RetrievalError) as exc_info:
        adapter.upsert_chunks(chunks=[sample_chunk], embeddings=[])
    assert "Mismatch between chunk count and embedding count" in exc_info.value.message


def test_search_vectors_and_filter(
    memory_qdrant_client: QdrantClient, sample_chunk: ChunkDocument
) -> None:
    """Verify dense vector search returning RetrievalResult objects."""
    adapter = VectorStoreAdapter(
        client=memory_qdrant_client, collection_name="test_collection"
    )
    adapter.ensure_collection()

    embedding = [0.05] * 1536
    adapter.upsert_chunks(chunks=[sample_chunk], embeddings=[embedding])

    # Search without filter
    results = adapter.search(query_vector=embedding, top_k=5)
    assert len(results) == 1
    assert results[0].chunk_id == sample_chunk.chunk_id
    assert results[0].text == sample_chunk.text
    assert results[0].file_name == sample_chunk.file_name
    assert results[0].retrieval_method == "dense"

    # Search with matching filter
    filtered_results = adapter.search(
        query_vector=embedding, top_k=5, filter_criteria={"file_name": "policy.pdf"}
    )
    assert len(filtered_results) == 1

    # Search with non-matching filter
    empty_results = adapter.search(
        query_vector=embedding, top_k=5, filter_criteria={"file_name": "other.pdf"}
    )
    assert len(empty_results) == 0


def test_delete_points_and_collection(
    memory_qdrant_client: QdrantClient, sample_chunk: ChunkDocument
) -> None:
    """Verify deleting points by ID and deleting collections."""
    adapter = VectorStoreAdapter(
        client=memory_qdrant_client, collection_name="test_collection"
    )
    adapter.ensure_collection()

    embedding = [0.02] * 1536
    adapter.upsert_chunks(chunks=[sample_chunk], embeddings=[embedding])
    assert adapter.get_count() == 1

    # Delete point
    assert adapter.delete_points(point_ids=[sample_chunk.chunk_id]) is True
    assert adapter.get_count() == 0

    # Delete empty point_ids sequence
    assert adapter.delete_points(point_ids=[]) is True

    # Delete collection
    assert adapter.delete_collection() is True
    assert not adapter.collection_exists()
    assert adapter.delete_collection() is False


def test_error_wrapping(memory_qdrant_client: QdrantClient) -> None:
    """Verify vector store errors are wrapped as RetrievalError."""
    adapter = VectorStoreAdapter(
        client=memory_qdrant_client, collection_name="non_existent"
    )

    with pytest.raises(RetrievalError):
        adapter.get_count()

    with pytest.raises(RetrievalError):
        adapter.search(query_vector=[0.1] * 1536)
