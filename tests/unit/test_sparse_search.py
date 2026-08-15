"""Unit tests for sparse BM25 search service (feature 5.2, top-50 BM25)."""

import pytest

from core.exceptions import RetrievalError
from models.chunk import ChunkDocument, ChunkMetadata
from retrieval.bm25_index import BM25IndexManager
from retrieval.bm25_tokenizer import tokenize
from retrieval.sparse_search import SPARSE_TOP_K_DEFAULT, SparseSearchService


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


@pytest.fixture
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
    ]


def _build_service(
    chunks: list[ChunkDocument] | None = None,
    top_k: int = SPARSE_TOP_K_DEFAULT,
) -> SparseSearchService:
    """Construct sparse search service with optional pre-built BM25 index."""
    bm25_index = BM25IndexManager()
    if chunks is not None:
        bm25_index.build(chunks)
    return SparseSearchService(bm25_index=bm25_index, top_k=top_k)


def test_default_top_k_constant() -> None:
    """Verify feature requirement default is top 50."""
    assert SPARSE_TOP_K_DEFAULT == 50


def test_init_defaults_and_clamping() -> None:
    """Verify top_k defaults to 50 and clamps non-positive values to 1."""
    service = _build_service()
    assert service.top_k == 50

    service = _build_service(top_k=0)
    assert service.top_k == 1

    service = _build_service(top_k=-5)
    assert service.top_k == 1


def test_search_returns_sparse_hits_top_k(sample_chunks: list[ChunkDocument]) -> None:
    """Verify sparse search returns top-k hits with sparse retrieval method."""
    service = _build_service(chunks=sample_chunks, top_k=2)

    results = service.search("insurance coverage")
    assert len(results) == 2
    assert results[0].retrieval_method == "sparse"
    assert results[0].chunk_id in {c.chunk_id for c in sample_chunks}
    assert isinstance(results[0].relevance_score, float)
    assert results[0].file_name == "policy.pdf"
    assert results[0].page_number == 1


def test_search_returns_up_to_top_50() -> None:
    """Verify search returns at most 50 hits from BM25 index."""
    chunks = [_make_chunk(f"c_{i}", f"document chunk number {i}") for i in range(60)]
    service = _build_service(chunks=chunks)

    hits = service.search("document chunk")
    assert len(hits) <= 50


def test_search_empty_query_raises(sample_chunks: list[ChunkDocument]) -> None:
    """Verify empty or whitespace-only query raises RetrievalError."""
    service = _build_service(chunks=sample_chunks)
    with pytest.raises(RetrievalError, match="non-empty"):
        service.search("")
    with pytest.raises(RetrievalError, match="non-empty"):
        service.search("   ")


def test_search_unbuilt_index_raises() -> None:
    """Verify searching an unbuilt index raises RetrievalError."""
    service = _build_service()
    with pytest.raises(RetrievalError, match="BM25 index is empty"):
        service.search("insurance")


def test_search_custom_top_k_overrides_default(
    sample_chunks: list[ChunkDocument],
) -> None:
    """Verify per-call top_k overrides configured default."""
    service = _build_service(chunks=sample_chunks, top_k=50)

    results = service.search("coverage benefits dental", top_k=1)
    assert len(results) == 1
    assert results[0].chunk_id == "chunk_1"


def test_search_returns_custom_top_k_hits(
    sample_chunks: list[ChunkDocument],
) -> None:
    """Verify custom top_k returns exactly that many hits when available."""
    service = _build_service(chunks=sample_chunks, top_k=3)

    results = service.search("insurance benefits claims")
    assert len(results) == 3
    ids = {r.chunk_id for r in results}
    assert ids == {"chunk_0", "chunk_1", "chunk_2"}
    assert all(r.retrieval_method == "sparse" for r in results)
