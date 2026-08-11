"""Unit tests for PDF document parser and page metadata extraction."""

from pathlib import Path

import fitz
import pytest

from core.exceptions import IngestionError
from ingestion.pdf_parser import PDFParser
from models.document import ParsedDocument


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a temporary 2-page PDF file with text and metadata."""
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()

    # Page 1
    page1 = doc.new_page(width=595, height=842)
    page1.insert_text((50, 100), "Helvetia Consulting Enterprise SLA Document")
    page1.insert_text((50, 150), "Page one content with sample text.")

    # Page 2
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text((50, 100), "Security Policy section and guidelines.")

    doc.set_metadata(
        {
            "title": "Enterprise SLA 2025",
            "author": "Helvetia Team",
            "subject": "Corporate SLA Policy",
        }
    )
    doc.save(pdf_path)
    doc.close()
    return pdf_path


def test_pdf_parser_init_unsupported_engine() -> None:
    """Verify initialization fails for invalid parser engine."""
    with pytest.raises(IngestionError) as exc_info:
        PDFParser(engine="invalid_engine")
    assert exc_info.value.code == "INVALID_PARSER_ENGINE"


def test_pdf_parser_pymupdf_success(sample_pdf: Path) -> None:
    """Verify PyMuPDF engine extracts pages, text, and metadata accurately."""
    parser = PDFParser(engine="pymupdf")
    parsed: ParsedDocument = parser.parse(sample_pdf)

    assert parsed.file_name == "sample.pdf"
    assert parsed.source_format == "pdf"
    assert parsed.doc_metadata.total_pages == 2
    assert parsed.doc_metadata.title == "Enterprise SLA 2025"
    assert parsed.doc_metadata.author == "Helvetia Team"
    assert len(parsed.pages) == 2

    # Page 1 checks
    p1 = parsed.pages[0]
    assert p1.page_number == 1
    assert "Helvetia Consulting" in p1.text
    assert p1.metadata.width == 595.0
    assert p1.metadata.height == 842.0
    assert p1.metadata.word_count > 0

    # Page 2 checks
    p2 = parsed.pages[1]
    assert p2.page_number == 2
    assert "Security Policy" in p2.text


def test_pdf_parser_pdfplumber_success(sample_pdf: Path) -> None:
    """Verify pdfplumber engine extracts pages, text, and metadata accurately."""
    parser = PDFParser(engine="pdfplumber")
    parsed: ParsedDocument = parser.parse(sample_pdf)

    assert parsed.file_name == "sample.pdf"
    assert parsed.source_format == "pdf"
    assert parsed.doc_metadata.total_pages == 2
    assert len(parsed.pages) == 2

    p1 = parsed.pages[0]
    assert p1.page_number == 1
    assert "Helvetia" in p1.text
    assert p1.metadata.width == 595.0


def test_pdf_parser_nonexistent_file(tmp_path: Path) -> None:
    """Verify IngestionError is raised for non-existent file path."""
    parser = PDFParser()
    missing_file = tmp_path / "missing.pdf"
    with pytest.raises(IngestionError) as exc_info:
        parser.parse(missing_file)
    assert exc_info.value.code == "FILE_NOT_FOUND"


def test_pdf_parser_empty_file(tmp_path: Path) -> None:
    """Verify IngestionError is raised for empty 0-byte PDF file."""
    empty_file = tmp_path / "empty.pdf"
    empty_file.write_bytes(b"")
    parser = PDFParser()
    with pytest.raises(IngestionError) as exc_info:
        parser.parse(empty_file)
    assert exc_info.value.code == "EMPTY_FILE"


def test_pdf_parser_corrupt_file(tmp_path: Path) -> None:
    """Verify IngestionError is raised for corrupted invalid PDF content."""
    corrupt_file = tmp_path / "corrupt.pdf"
    corrupt_file.write_bytes(b"This is not a valid PDF header content")
    parser = PDFParser()
    with pytest.raises(IngestionError) as exc_info:
        parser.parse(corrupt_file)
    assert exc_info.value.code == "PDF_PARSING_ERROR"
