"""Unit tests for dense vector search service (feature 5.1, top-50 Qdrant)."""

from unittest.mock import MagicMock

import pytest
from qdrant_client import QdrantClient

from clients.mock_embedding import MockEmbeddingAdapter
from core.exceptions import RetrievalError
from models.chunk import ChunkDocument, ChunkMetadata
from retrieval.dense_search import DENSE_TOP_K_DEFAULT, DenseSearchService
from retrieval.vector_store import VectorStoreAdapter


def _make_chunk(
    chunk_id: str,
    text: str,
    file_name: str = "policy.pdf",
    page_number: int = 1,
    chunk_index: int = 0,
) -> ChunkDocument:
    """Build a ChunkDocument fixture with minimal metadata."""
    return ChunkDocument(
        chunk_id=chunk_id,
        text=text,
        file_name=file_name,
        page_number=page_number,
        metadata=ChunkMetadata(
            source_format="pdf",
            chunk_index=chunk_index,
            total_chunks=1,
            char_count=len(text),
            token_count=8,
        ),
    )


@pytest.fixture
def memory_qdrant_client() -> QdrantClient:
    """Fixture providing in-memory Qdrant client."""
    return QdrantClient(location=":memory:")


@pytest.fixture
def sample_chunks() -> list[ChunkDocument]:
    """Fixture providing a small corpus of chunk documents."""
    return [
        _make_chunk("chunk_0", "Helvetia insurance policy covers fire damage."),
        _make_chunk("chunk_1", "Employee health benefits include dental coverage."),
        _make_chunk("chunk_2", "The claims department processes refunds within thirty days."),
    ]


def _build_service(
    memory_qdrant_client: QdrantClient,
    dimension: int = 1536,
    top_k: int = DENSE_TOP_K_DEFAULT,
) -> DenseSearchService:
    """Construct dense search service with mock embedding and in-memory Qdrant."""
    embedding = MockEmbeddingAdapter(dimension=dimension)
    vector_store = VectorStoreAdapter(
        client=memory_qdrant_client,
        collection_name="test_collection",
        vector_dim=dimension,
    )
    return DenseSearchService(
        embedding_adapter=embedding,
        vector_store=vector_store,
        top_k=top_k,
    )


def test_default_top_k_constant() -> None:
    """Verify feature requirement default is top 50."""
    assert DENSE_TOP_K_DEFAULT == 50


def test_init_defaults_and_clamping(
    memory_qdrant_client: QdrantClient,
) -> None:
    """Verify top_k defaults to 50 and clamps non-positive values to 1."""
    service = _build_service(memory_qdrant_client)
    assert service.top_k == 50

    service = _build_service(memory_qdrant_client, top_k=0)
    assert service.top_k == 1

    service = _build_service(memory_qdrant_client, top_k=-5)
    assert service.top_k == 1


def test_search_returns_dense_hits_top_k(
    memory_qdrant_client: QdrantClient, sample_chunks: list[ChunkDocument]
) -> None:
    """Verify dense search returns top-k hits with dense retrieval method."""
    service = _build_service(memory_qdrant_client, top_k=2)
    service.vector_store.ensure_collection()

    embeddings = [
        service.embedding_adapter.embed_text(c.text) for c in sample_chunks
    ]
    service.vector_store.upsert_chunks(chunks=sample_chunks, embeddings=embeddings)

    results = service.search("insurance coverage")
    assert len(results) == 2
    assert results[0].retrieval_method == "dense"
    assert results[0].chunk_id in {c.chunk_id for c in sample_chunks}
    assert isinstance(results[0].relevance_score, float)


def test_search_returns_up_to_top_50(
    memory_qdrant_client: QdrantClient,
) -> None:
    """Verify search requests top 50 from Qdrant when configurable limit is absent."""
    chunks = [_make_chunk(f"c_{i}", f"document chunk number {i}") for i in range(60)]
    service = _build_service(memory_qdrant_client)
    service.vector_store.ensure_collection()

    embeddings = [service.embedding_adapter.embed_text(c.text) for c in chunks]
    service.vector_store.upsert_chunks(chunks=chunks, embeddings=embeddings)

    hits = service.search("document chunk")
    assert len(hits) <= 50


def test_search_empty_query_raises(
    memory_qdrant_client: QdrantClient,
) -> None:
    """Verify empty or whitespace-only query raises RetrievalError."""
    service = _build_service(memory_qdrant_client)
    with pytest.raises(RetrievalError, match="non-empty"):
        service.search("")
    with pytest.raises(RetrievalError, match="non-empty"):
        service.search("   ")


def test_search_collection_missing_raises(
    memory_qdrant_client: QdrantClient,
) -> None:
    """Verify searching a non-existent collection raises RetrievalError."""
    service = _build_service(memory_qdrant_client)
    with pytest.raises(RetrievalError, match="does not exist"):
        service.search("insurance")


def test_search_dimension_mismatch_raises(
    memory_qdrant_client: QdrantClient,
) -> None:
    """Verify query embedding dimension mismatch raises RetrievalError."""
    service = _build_service(memory_qdrant_client, dimension=1536)
    service.vector_store.ensure_collection()

    stub_embedding = MagicMock()
    stub_embedding.embed_text.return_value = [0.1] * 64
    service.embedding_adapter = stub_embedding

    with pytest.raises(RetrievalError, match="dimension mismatches"):
        service.search("insurance")


def test_search_embedding_failure_wrapped(
    memory_qdrant_client: QdrantClient,
) -> None:
    """Verify embedding exceptions are wrapped as RetrievalError."""
    service = _build_service(memory_qdrant_client)
    service.vector_store.ensure_collection()

    stub_embedding = MagicMock()
    stub_embedding.embed_text.side_effect = RuntimeError("provider down")
    service.embedding_adapter = stub_embedding

    with pytest.raises(RetrievalError, match="Failed to embed"):
        service.search("insurance")


def test_search_passes_filter_criteria(
    memory_qdrant_client: QdrantClient, sample_chunks: list[ChunkDocument]
) -> None:
    """Verify filter criteria are forwarded to the vector store search."""
    service = _build_service(memory_qdrant_client)
    service.vector_store.ensure_collection()

    embeddings = [
        service.embedding_adapter.embed_text(c.text) for c in sample_chunks
    ]
    service.vector_store.upsert_chunks(chunks=sample_chunks, embeddings=embeddings)

    filtered = service.search(
        "insurance", filter_criteria={"file_name": "policy.pdf"}
    )
    assert all(r.file_name == "policy.pdf" for r in filtered)
    assert len(filtered) >= 1


def test_search_returns_custom_collection_hits(
    memory_qdrant_client: QdrantClient, sample_chunks: list[ChunkDocument]
) -> None:
    """Verify custom collection name is honored during dense search."""
    service = _build_service(memory_qdrant_client)
    service.vector_store.ensure_collection("custom_collection")

    embeddings = [
        service.embedding_adapter.embed_text(c.text) for c in sample_chunks
    ]
    service.vector_store.upsert_chunks(
        chunks=sample_chunks,
        embeddings=embeddings,
        collection_name="custom_collection",
    )

    results = service.search("insurance", collection_name="custom_collection")
    assert len(results) == 3
    ids = {r.chunk_id for r in results}
    assert ids == {"chunk_0", "chunk_1", "chunk_2"}
    assert all(r.retrieval_method == "dense" for r in results)


