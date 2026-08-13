"""Unit tests for the indexing orchestrator (embed → upsert → BM25)."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from qdrant_client import QdrantClient

from clients.mock_embedding import MockEmbeddingAdapter
from core.exceptions import RetrievalError
from models.chunk import ChunkDocument, ChunkMetadata
from retrieval.bm25_index import BM25IndexManager
from retrieval.indexing_orchestrator import IndexingOrchestrator, IndexingResult
from retrieval.vector_store import VectorStoreAdapter


def _make_chunk(
    chunk_id: str,
    text: str,
    file_name: str = "policy.pdf",
    page_number: int = 1,
) -> ChunkDocument:
    """Build a ChunkDocument fixture with minimal metadata."""
    return ChunkDocument(
        chunk_id=chunk_id,
        text=text,
        file_name=file_name,
        page_number=page_number,
        metadata=ChunkMetadata(
            source_format="pdf",
            chunk_index=0,
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


def _build_orchestrator(
    memory_qdrant_client: QdrantClient,
    dimension: int = 1536,
    bm25_index: BM25IndexManager | None = None,
) -> IndexingOrchestrator:
    """Construct orchestrator wired with mock embedding and in-memory Qdrant."""
    embedding = MockEmbeddingAdapter(dimension=dimension)
    vector_store = VectorStoreAdapter(
        client=memory_qdrant_client,
        collection_name="test_collection",
        vector_dim=dimension,
    )
    return IndexingOrchestrator(
        embedding_adapter=embedding,
        vector_store=vector_store,
        bm25_index=bm25_index,
    )


def test_index_empty_chunks_returns_empty_result(
    memory_qdrant_client: QdrantClient,
) -> None:
    """Verify indexing empty chunks is a no-op returning zero counts."""
    orchestrator = _build_orchestrator(memory_qdrant_client)
    result = orchestrator.index_chunks([])

    assert isinstance(result, IndexingResult)
    assert result.chunk_count == 0
    assert result.vector_count == 0
    assert result.bm25_count == 0
    assert result.collection_name == "test_collection"
    assert result.bm25_path is None


def test_index_chunks_embeds_upserts_and_builds_bm25(
    memory_qdrant_client: QdrantClient, sample_chunks: list[ChunkDocument]
) -> None:
    """Verify full indexing flow populates vectors and BM25 index."""
    orchestrator = _build_orchestrator(memory_qdrant_client)
    result = orchestrator.index_chunks(sample_chunks)

    assert result.chunk_count == 3
    assert result.vector_count == 3
    assert result.bm25_count == 3
    assert result.collection_name == "test_collection"

    # Vectors persisted in Qdrant
    assert orchestrator.vector_store.get_count() == 3

    # BM25 index built and searchable
    assert orchestrator.bm25_index.is_built
    hits = orchestrator.bm25_index.search("insurance coverage", top_k=2)
    assert len(hits) == 2
    assert hits[0].chunk_id == "chunk_0"


def test_index_chunks_saves_bm25_path(
    memory_qdrant_client: QdrantClient,
    sample_chunks: list[ChunkDocument],
    tmp_path: Path,
) -> None:
    """Verify BM25 index is persisted when bm25_path is provided."""
    orchestrator = _build_orchestrator(memory_qdrant_client)
    index_path = tmp_path / "bm25_index.json"

    result = orchestrator.index_chunks(sample_chunks, bm25_path=index_path)

    assert result.bm25_path == index_path
    assert index_path.exists()

    # Reload persisted index and confirm search parity
    loaded = BM25IndexManager()
    assert loaded.load(index_path) == 3
    assert loaded.search("insurance", top_k=1)[0].chunk_id == "chunk_0"


def test_index_chunks_collection_override(
    memory_qdrant_client: QdrantClient, sample_chunks: list[ChunkDocument]
) -> None:
    """Verify custom collection name is honored during indexing."""
    orchestrator = _build_orchestrator(memory_qdrant_client)
    result = orchestrator.index_chunks(
        sample_chunks, collection_name="custom_collection"
    )

    assert result.collection_name == "custom_collection"
    assert orchestrator.vector_store.get_count("custom_collection") == 3


def test_index_chunks_embedding_count_mismatch_raises(
    memory_qdrant_client: QdrantClient, sample_chunks: list[ChunkDocument]
) -> None:
    """Verify RetrievalError raised when embedding count mismatches chunk count."""
    mock_embedding = MagicMock()
    mock_embedding.embed_batch.return_value = [[0.1] * 1536]  # Only one vector

    vector_store = VectorStoreAdapter(
        client=memory_qdrant_client,
        collection_name="test_collection",
        vector_dim=1536,
    )
    orchestrator = IndexingOrchestrator(
        embedding_adapter=mock_embedding, vector_store=vector_store
    )

    with pytest.raises(RetrievalError, match="Embedding count mismatch"):
        orchestrator.index_chunks(sample_chunks)


def test_index_chunks_dimension_mismatch_raises(
    memory_qdrant_client: QdrantClient, sample_chunks: list[ChunkDocument]
) -> None:
    """Verify RetrievalError raised when embedding dimension mismatches store."""
    # Force a wrong-dimension embedding via a stub adapter
    stub_embedding = MagicMock()
    stub_embedding.embed_batch.return_value = [[0.1] * 64 for _ in sample_chunks]

    vector_store = VectorStoreAdapter(
        client=memory_qdrant_client,
        collection_name="test_collection",
        vector_dim=1536,
    )
    orchestrator = IndexingOrchestrator(
        embedding_adapter=stub_embedding, vector_store=vector_store
    )

    with pytest.raises(RetrievalError, match="Embedding dimension mismatch"):
        orchestrator.index_chunks(sample_chunks)
