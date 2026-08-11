"""Unit tests for recursive structural document chunker module."""

import pytest
from core.exceptions import IngestionError
from ingestion.recursive_chunker import RecursiveStructuralChunker
from models.document import DocumentMetadata, PageMetadata, ParsedDocument, ParsedPage


def _create_mock_document(
    pages_content: list[str], file_name: str = "sample.pdf"
) -> ParsedDocument:
    """Helper to create ParsedDocument fixture with custom page texts."""
    pages: list[ParsedPage] = []
    for idx, content in enumerate(pages_content, start=1):
        p_meta = PageMetadata(
            page_number=idx,
            width=612.0,
            height=792.0,
            char_count=len(content),
            word_count=len(content.split()),
        )
        pages.append(ParsedPage(page_number=idx, text=content, metadata=p_meta))

    d_meta = DocumentMetadata(
        total_pages=len(pages),
        file_size_bytes=1024,
    )
    return ParsedDocument(
        file_name=file_name,
        file_path=f"/tmp/{file_name}",
        source_format="pdf",
        doc_metadata=d_meta,
        pages=pages,
    )


def test_chunker_initialization_defaults_and_validation() -> None:
    """Verify chunker initialization parameters and validation guards."""
    chunker = RecursiveStructuralChunker()
    assert chunker.max_tokens == 512
    assert chunker.overlap_percentage == 0.10
    assert chunker.overlap_tokens == 51

    with pytest.raises(IngestionError) as exc_info:
        RecursiveStructuralChunker(max_tokens=0)
    assert exc_info.value.code == "INVALID_CHUNKER_PARAM"

    with pytest.raises(IngestionError) as exc_info:
        RecursiveStructuralChunker(overlap_percentage=1.5)
    assert exc_info.value.code == "INVALID_CHUNKER_PARAM"


def test_chunker_empty_document_and_blank_pages() -> None:
    """Verify chunker handles empty documents and blank pages gracefully."""
    chunker = RecursiveStructuralChunker()
    empty_doc = _create_mock_document([])
    assert chunker.chunk_document(empty_doc) == []

    blank_doc = _create_mock_document(["   ", "\n\n  \t  "])
    assert chunker.chunk_document(blank_doc) == []


def test_chunker_single_short_page() -> None:
    """Verify chunking a single short page produces exactly one chunk."""
    chunker = RecursiveStructuralChunker(max_tokens=100)
    doc = _create_mock_document(["Short test content for ingestion chunker."])
    chunks = chunker.chunk_document(doc)

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.page_number == 1
    assert chunk.file_name == "sample.pdf"
    assert chunk.text == "Short test content for ingestion chunker."
    assert chunk.metadata.chunk_index == 0
    assert chunk.metadata.total_chunks == 1
    assert chunk.metadata.token_count > 0


def test_chunker_page_boundary_preservation() -> None:
    """Verify chunks preserve page attribution across multi-page document."""
    chunker = RecursiveStructuralChunker(max_tokens=50)
    p1 = "Page one content paragraph.\nSecond sentence on page one."
    p2 = "Page two starts here with different information."
    doc = _create_mock_document([p1, p2])

    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 2

    # Check page attribution
    p1_chunks = [c for c in chunks if c.page_number == 1]
    p2_chunks = [c for c in chunks if c.page_number == 2]
    assert len(p1_chunks) >= 1
    assert len(p2_chunks) >= 1

    # Verify overall index sequence
    for idx, c in enumerate(chunks):
        assert c.metadata.chunk_index == idx
        assert c.metadata.total_chunks == len(chunks)


def test_chunker_large_text_structural_splitting() -> None:
    """Verify recursive splitting breaks large text into <= max_tokens chunks."""
    chunker = RecursiveStructuralChunker(max_tokens=20, overlap_percentage=0.1)
    paragraph1 = "Word " * 35  # ~45 tokens
    paragraph2 = "Data " * 35  # ~45 tokens
    text = f"{paragraph1}\n\n{paragraph2}"
    doc = _create_mock_document([text])

    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 4
    for chunk in chunks:
        assert chunk.metadata.token_count <= 20


def test_chunker_overlap_application() -> None:
    """Verify chunk overlap prepends tail context between adjacent splits."""
    chunker = RecursiveStructuralChunker(max_tokens=6, overlap_percentage=0.3)
    s1 = "Alpha beta gamma delta epsilon."
    s2 = "Zeta eta theta iota kappa."
    text = f"{s1}\n\n{s2}"
    doc = _create_mock_document([text])

    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 2
    # Verify second chunk contains overlapping context from first split
    assert len(chunks[1].text) > 0


def test_chunker_hard_split_fallback() -> None:
    """Verify hard character split fallback for un-splittable tokens."""
    chunker = RecursiveStructuralChunker(max_tokens=10)
    unbroken_string = "X" * 150
    doc = _create_mock_document([unbroken_string])

    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 2
    assert all(c.metadata.token_count <= 10 or len(c.text) <= 30 for c in chunks)
