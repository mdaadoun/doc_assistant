"""Parsed document domain models for document ingestion pipeline."""

from pydantic import Field

from models.base import BaseDomainModel


class PageMetadata(BaseDomainModel):
    """Page-level metadata metrics and dimensions."""

    page_number: int = Field(..., ge=1, description="1-indexed page number")
    width: float = Field(..., ge=0.0, description="Page width in points")
    height: float = Field(..., ge=0.0, description="Page height in points")
    rotation: int = Field(default=0, description="Page rotation angle in degrees")
    char_count: int = Field(..., ge=0, description="Character count on page")
    word_count: int = Field(..., ge=0, description="Word count on page")
    image_count: int = Field(default=0, ge=0, description="Image count on page")
    table_count: int = Field(default=0, ge=0, description="Table count on page")


class ParsedPage(BaseDomainModel):
    """Extracted single page payload and metadata."""

    page_number: int = Field(..., ge=1, description="1-indexed page number")
    text: str = Field(..., description="Extracted text content from page")
    metadata: PageMetadata = Field(..., description="Page-level metadata")


class DocumentMetadata(BaseDomainModel):
    """Document-level metadata header."""

    title: str | None = Field(default=None, description="Document title")
    author: str | None = Field(default=None, description="Document author")
    subject: str | None = Field(default=None, description="Document subject")
    keywords: str | None = Field(default=None, description="Document keywords")
    creator: str | None = Field(default=None, description="Document creator app")
    producer: str | None = Field(default=None, description="PDF producer engine")
    creation_date: str | None = Field(
        default=None, description="Creation timestamp string"
    )
    mod_date: str | None = Field(
        default=None, description="Modification timestamp string"
    )
    total_pages: int = Field(..., ge=0, description="Total pages in document")
    file_size_bytes: int = Field(..., ge=0, description="File size in bytes")


class ParsedDocument(BaseDomainModel):
    """Structured document representation extracted by parsers."""

    file_name: str = Field(..., description="Source file name")
    file_path: str = Field(..., description="Source file path")
    source_format: str = Field(
        ..., description="Source document format extension e.g. pdf"
    )
    doc_metadata: DocumentMetadata = Field(..., description="Global document metadata")
    pages: list[ParsedPage] = Field(..., description="List of extracted pages")
