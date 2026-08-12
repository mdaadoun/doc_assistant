"""Unit tests for BM25 tokenizer and sparse index manager."""

import json

import pytest

from core.exceptions import RetrievalError
from models.chunk import ChunkDocument, ChunkMetadata
from retrieval.bm25_index import BM25IndexManager
from retrieval.bm25_tokenizer import tokenize, tokenize_corpus


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


def test_tokenize_lowercase_alphanumeric() -> None:
    """Verify tokenizer lowercases, strips punctuation, and removes stopwords."""
    assert tokenize("Hello, World! 123") == ["hello", "world", "123"]
    assert tokenize("") == []
    assert tokenize("---") == []


def test_tokenize_preserves_hyphenated_compounds() -> None:
    """Verify hyphenated compounds like FR-02 stay as single tokens."""
    assert tokenize("FR-02 fire-damage") == ["fr-02", "fire-damage"]
    assert tokenize("multi-word-compound") == ["multi-word-compound"]


def test_tokenize_removes_stopwords() -> None:
    """Verify common English stopwords are filtered out."""
    result = tokenize("the insurance is for a building")
    assert "the" not in result
    assert "is" not in result
    assert "for" not in result
    assert "a" not in result
    assert "insurance" in result
    assert "building" in result


def test_tokenize_corpus() -> None:
    """Verify corpus tokenization returns list of token lists."""
    corpus = tokenize_corpus(["One two.", "Three"])
    assert corpus == [["one", "two"], ["three"]]


def test_build_index_and_size(sample_chunks: list[ChunkDocument]) -> None:
    """Verify building index sets size and is_built flags."""
    manager = BM25IndexManager()
    assert manager.size == 0
    assert not manager.is_built

    count = manager.build(sample_chunks)
    assert count == 3
    assert manager.size == 3
    assert manager.is_built


def test_build_empty_corpus() -> None:
    """Verify building with empty corpus leaves index unbuilt."""
    manager = BM25IndexManager()
    assert manager.build([]) == 0
    assert not manager.is_built
    assert manager.size == 0


def test_search_returns_sparse_hits(sample_chunks: list[ChunkDocument]) -> None:
    """Verify BM25 search returns ranked sparse RetrievalResult hits."""
    manager = BM25IndexManager()
    manager.build(sample_chunks)

    results = manager.search("insurance coverage", top_k=2)
    assert len(results) == 2
    assert results[0].chunk_id == "chunk_0"
    assert results[0].retrieval_method == "sparse"
    assert results[0].relevance_score > 0.0
    assert results[0].file_name == "policy.pdf"
    assert results[0].page_number == 1
    assert results[1].chunk_id == "chunk_1"


def test_search_top_k_limit(sample_chunks: list[ChunkDocument]) -> None:
    """Verify top_k limits returned hit count."""
    manager = BM25IndexManager()
    manager.build(sample_chunks)

    results = manager.search("coverage benefits dental", top_k=1)
    assert len(results) == 1
    assert results[0].chunk_id == "chunk_1"


def test_search_empty_query(sample_chunks: list[ChunkDocument]) -> None:
    """Verify empty query returns empty result list."""
    manager = BM25IndexManager()
    manager.build(sample_chunks)
    assert manager.search("") == []
    assert manager.search("!!!") == []


def test_search_before_build_raises() -> None:
    """Verify searching an unbuilt index raises RetrievalError."""
    manager = BM25IndexManager()
    with pytest.raises(RetrievalError, match="BM25 index is empty"):
        manager.search("insurance")


def test_search_invalid_top_k(sample_chunks: list[ChunkDocument]) -> None:
    """Verify non-positive top_k raises RetrievalError."""
    manager = BM25IndexManager()
    manager.build(sample_chunks)
    with pytest.raises(RetrievalError, match="top_k must be a positive integer"):
        manager.search("insurance", top_k=0)


def test_save_and_load_roundtrip(
    sample_chunks: list[ChunkDocument], tmp_path: pytest.TempPathFactory
) -> None:
    """Verify save/load roundtrip preserves corpus and search behavior."""
    manager = BM25IndexManager()
    manager.build(sample_chunks)
    index_path = tmp_path / "bm25_index.json"

    saved = manager.save(index_path)
    assert saved == index_path
    assert index_path.exists()

    loaded = BM25IndexManager()
    count = loaded.load(index_path)
    assert count == 3
    assert loaded.size == 3
    assert loaded.is_built

    original_results = manager.search("insurance policy fire", top_k=2)
    loaded_results = loaded.search("insurance policy fire", top_k=2)
    assert [r.chunk_id for r in original_results] == [
        r.chunk_id for r in loaded_results
    ]
    assert [r.relevance_score for r in original_results] == [
        r.relevance_score for r in loaded_results
    ]


def test_save_empty_index(tmp_path: pytest.TempPathFactory) -> None:
    """Verify saving an empty index produces loadable empty state."""
    manager = BM25IndexManager()
    index_path = tmp_path / "empty_index.json"
    manager.save(index_path)

    loaded = BM25IndexManager()
    assert loaded.load(index_path) == 0
    assert not loaded.is_built


def test_load_missing_file_raises(tmp_path: pytest.TempPathFactory) -> None:
    """Verify loading a missing file raises RetrievalError."""
    manager = BM25IndexManager()
    with pytest.raises(RetrievalError, match="Failed to load BM25 index"):
        manager.load(tmp_path / "missing.json")


def test_load_invalid_version_raises(
    sample_chunks: list[ChunkDocument], tmp_path: pytest.TempPathFactory
) -> None:
    """Verify loading an unsupported index version raises RetrievalError."""
    manager = BM25IndexManager()
    manager.build(sample_chunks)
    index_path = tmp_path / "bad_version.json"
    manager.save(index_path)

    payload = json.loads(index_path.read_text(encoding="utf-8"))
    payload["version"] = 999
    index_path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = BM25IndexManager()
    with pytest.raises(RetrievalError, match="Unsupported BM25 index version"):
        loaded.load(index_path)


def test_clear_resets_state(sample_chunks: list[ChunkDocument]) -> None:
    """Verify clear resets index to empty state."""
    manager = BM25IndexManager()
    manager.build(sample_chunks)
    assert manager.is_built

    manager.clear()
    assert not manager.is_built
    assert manager.size == 0
    with pytest.raises(RetrievalError, match="BM25 index is empty"):
        manager.search("insurance")
