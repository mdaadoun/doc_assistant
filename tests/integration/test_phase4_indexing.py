"""Phase 4 acceptance: Qdrant count == chunk count, BM25 returns hits."""

import pytest
from qdrant_client import QdrantClient

from clients.mock_embedding import MockEmbeddingAdapter
from models.chunk import ChunkDocument, ChunkMetadata
from retrieval.bm25_index import BM25IndexManager
from retrieval.bm25_tokenizer import tokenize
from retrieval.indexing_orchestrator import IndexingOrchestrator
from retrieval.vector_store import VectorStoreAdapter

_SAMPLE_QUERIES = [
    "insurance coverage",
    "claims refunds",
    "employee benefits",
]


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
            token_count=len(tokenize(text)),
        ),
    )


@pytest.fixture()
def sample_chunks() -> list[ChunkDocument]:
    """Fixture providing a small corpus of chunk documents."""
    return [
        _make_chunk(
            "chunk_0",
            "Helvetia insurance policy covers fire damage to buildings.",
            file_name="policy.pdf",
        ),
        _make_chunk(
            "chunk_1",
            "Employee health benefits include dental and vision coverage.",
            file_name="benefits.docx",
        ),
        _make_chunk(
            "chunk_2",
            "The claims department processes refunds within thirty days.",
            file_name="claims.md",
        ),
        _make_chunk(
            "chunk_3",
            "All fire-damage claims require FR-02 documentation form.",
            file_name="claims.md",
            page_number=2,
        ),
    ]


@pytest.fixture()
def orchestrator() -> IndexingOrchestrator:
    """Construct orchestrator wired with mock embedding and in-memory Qdrant."""
    client = QdrantClient(location=":memory:")
    store = VectorStoreAdapter(
        client=client,
        collection_name="phase4_acceptance",
        vector_dim=64,
    )
    return IndexingOrchestrator(
        embedding_adapter=MockEmbeddingAdapter(dimension=64),
        vector_store=store,
    )


def test_qdrant_count_matches_chunk_count(
    orchestrator: IndexingOrchestrator,
    sample_chunks: list[ChunkDocument],
) -> None:
    """Verify Qdrant collection point count matches indexed chunk count."""
    result = orchestrator.index_chunks(sample_chunks)
    qdrant_count = orchestrator.vector_store.get_count()
    assert qdrant_count == result.chunk_count, (
        f"Qdrant has {qdrant_count} points but "
        f"{result.chunk_count} chunks were indexed"
    )
    assert qdrant_count == len(sample_chunks)


def test_bm25_returns_results_for_sample_queries(
    orchestrator: IndexingOrchestrator,
    sample_chunks: list[ChunkDocument],
) -> None:
    """Verify BM25 returns non-empty results for representative queries."""
    orchestrator.index_chunks(sample_chunks)
    for query in _SAMPLE_QUERIES:
        hits = orchestrator.bm25_index.search(query, top_k=3)
        assert len(hits) > 0, (
            f"BM25 returned no results for query: '{query}'"
        )
        assert all(h.relevance_score > 0.0 for h in hits)
        assert all(h.retrieval_method == "sparse" for h in hits)


def test_bm25_and_vector_counts_match(
    orchestrator: IndexingOrchestrator,
    sample_chunks: list[ChunkDocument],
) -> None:
    """Verify BM25 index size and vector count are equal after indexing."""
    result = orchestrator.index_chunks(sample_chunks)
    assert result.vector_count == result.bm25_count
    assert result.vector_count == len(sample_chunks)


def test_upsert_batching_produces_correct_total(
    sample_chunks: list[ChunkDocument],
) -> None:
    """Verify batched upsert with batch_size=2 produces correct total count."""
    client = QdrantClient(location=":memory:")
    store = VectorStoreAdapter(
        client=client,
        collection_name="batch_test",
        vector_dim=64,
    )
    orch = IndexingOrchestrator(
        embedding_adapter=MockEmbeddingAdapter(dimension=64),
        vector_store=store,
        batch_size=2,
    )
    result = orch.index_chunks(sample_chunks)
    assert result.vector_count == len(sample_chunks)
    assert store.get_count() == len(sample_chunks)
