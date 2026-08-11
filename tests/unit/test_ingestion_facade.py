"""Unit tests for IngestionFacade format dispatcher and fail-fast validation."""

from pathlib import Path

import pytest

from core.exceptions import IngestionError
from ingestion.base import BaseDocumentParser
from ingestion.facade import IngestionFacade
from models.document import DocumentMetadata, PageMetadata, ParsedDocument, ParsedPage


class DummyParser(BaseDocumentParser):
    """Dummy parser for testing custom parser registration."""

    def parse(self, file_path: str | Path) -> ParsedDocument:
        path = Path(file_path)
        return ParsedDocument(
            file_name=path.name,
            file_path=str(path),
            source_format="txt",
            doc_metadata=DocumentMetadata(
                title="Dummy Document",
                total_pages=1,
                file_size_bytes=path.stat().st_size if path.exists() else 0,
            ),
            pages=[
                ParsedPage(
                    page_number=1,
                    text="Dummy document text content for unit test validation.",
                    metadata=PageMetadata(
                        page_number=1,
                        width=612.0,
                        height=792.0,
                        char_count=52,
                        word_count=8,
                    ),
                )
            ],
        )


@pytest.fixture
def sample_md_file(tmp_path: Path) -> Path:
    """Create sample Markdown file for facade ingestion testing."""
    file_path = tmp_path / "sample.md"
    file_path.write_text(
        "# Heading 1\n\nThis is sample markdown text for ingestion facade testing."
    )
    return file_path


def test_facade_init_defaults() -> None:
    """Verify default initialization registers standard parsers and chunker."""
    facade = IngestionFacade()
    supported = facade.supported_formats()
    assert supported == ["docx", "markdown", "md", "pdf"]
    assert facade.max_file_size_bytes is None


def test_register_and_unregister_parser() -> None:
    """Verify registration and unregistration of custom format parsers."""
    facade = IngestionFacade()
    dummy = DummyParser()

    facade.register_parser("txt", dummy)
    assert "txt" in facade.supported_formats()
    assert facade.get_parser("txt") is dummy

    facade.unregister_parser(".TXT")
    assert "txt" not in facade.supported_formats()


def test_register_empty_extension_error() -> None:
    """Verify error raised when registering empty extension string."""
    facade = IngestionFacade()
    with pytest.raises(IngestionError) as exc_info:
        facade.register_parser("  ", DummyParser())
    assert exc_info.value.code == "INVALID_EXTENSION"


def test_validate_file_nonexistent(tmp_path: Path) -> None:
    """Verify fail-fast validation fails for non-existent file path."""
    facade = IngestionFacade()
    non_existent = tmp_path / "missing.md"
    with pytest.raises(IngestionError) as exc_info:
        facade.validate_file(non_existent)
    assert exc_info.value.code == "FILE_NOT_FOUND"


def test_validate_file_directory(tmp_path: Path) -> None:
    """Verify fail-fast validation fails when path targets a directory."""
    facade = IngestionFacade()
    with pytest.raises(IngestionError) as exc_info:
        facade.validate_file(tmp_path)
    assert exc_info.value.code == "INVALID_FILE"


def test_validate_file_empty(tmp_path: Path) -> None:
    """Verify fail-fast validation fails for 0-byte empty file."""
    facade = IngestionFacade()
    empty_file = tmp_path / "empty.md"
    empty_file.write_text("")
    with pytest.raises(IngestionError) as exc_info:
        facade.validate_file(empty_file)
    assert exc_info.value.code == "EMPTY_FILE"


def test_validate_file_too_large(tmp_path: Path) -> None:
    """Verify fail-fast validation fails when file exceeds max size limit."""
    facade = IngestionFacade(max_file_size_bytes=10)
    file_path = tmp_path / "large.md"
    file_path.write_text("Content exceeds 10 bytes limit")
    with pytest.raises(IngestionError) as exc_info:
        facade.validate_file(file_path)
    assert exc_info.value.code == "FILE_TOO_LARGE"


def test_validate_file_unsupported_format(tmp_path: Path) -> None:
    """Verify fail-fast validation fails for unregistered file extensions."""
    facade = IngestionFacade()
    unsupported_file = tmp_path / "file.xyz"
    unsupported_file.write_text("some content")
    with pytest.raises(IngestionError) as exc_info:
        facade.validate_file(unsupported_file)
    assert exc_info.value.code == "UNSUPPORTED_FORMAT"


def test_parse_and_ingest_markdown(sample_md_file: Path) -> None:
    """Verify end-to-end document parsing and chunk ingestion for Markdown file."""
    facade = IngestionFacade()

    parsed_doc = facade.parse_document(sample_md_file)
    assert parsed_doc.file_name == "sample.md"
    assert parsed_doc.source_format == "md"

    chunks = facade.ingest_document(sample_md_file)
    assert len(chunks) > 0
    assert chunks[0].chunk_id is not None
    assert "ingestion facade testing" in chunks[0].text


def test_ingest_batch(tmp_path: Path) -> None:
    """Verify batch ingestion of multiple document files."""
    facade = IngestionFacade()
    doc1 = tmp_path / "doc1.md"
    doc1.write_text("# Doc 1\n\nContent for first batch document.")
    doc2 = tmp_path / "doc2.md"
    doc2.write_text("# Doc 2\n\nContent for second batch document.")

    chunks = facade.ingest_batch([doc1, doc2])
    assert len(chunks) >= 2


def test_format_override(tmp_path: Path) -> None:
    """Verify format override dispatches correctly despite non-standard filename."""
    facade = IngestionFacade()
    custom_name = tmp_path / "doc_without_extension"
    custom_name.write_text("# Title\n\nText content.")

    parsed_doc = facade.parse_document(custom_name, format_override="md")
    assert parsed_doc.source_format == "md"
