"""PDF document parser using PyMuPDF and pdfplumber with metadata extraction."""

from pathlib import Path
from typing import Any

import fitz
import pdfplumber

from core.exceptions import IngestionError
from ingestion.base import BaseDocumentParser
from models.document import DocumentMetadata, PageMetadata, ParsedDocument, ParsedPage


class PDFParser(BaseDocumentParser):
    """Parser for PDF files using PyMuPDF (default) or pdfplumber engine."""

    def __init__(self, engine: str = "pymupdf") -> None:
        if engine not in ("pymupdf", "pdfplumber"):
            raise IngestionError(
                f"Unsupported PDF engine: {engine}. Must be 'pymupdf' or 'pdfplumber'.",
                code="INVALID_PARSER_ENGINE",
            )
        self.engine = engine

    def parse(self, file_path: str | Path) -> ParsedDocument:
        """Parse PDF document and extract page-level text and metadata."""
        path = Path(file_path).resolve()
        if not path.exists() or not path.is_file():
            raise IngestionError(
                f"PDF file does not exist: {path}",
                code="FILE_NOT_FOUND",
                details={"file_path": str(path)},
            )
        if path.stat().st_size == 0:
            raise IngestionError(
                f"PDF file is empty (0 bytes): {path}",
                code="EMPTY_FILE",
                details={"file_path": str(path)},
            )

        if self.engine == "pdfplumber":
            return self._parse_pdfplumber(path)
        return self._parse_pymupdf(path)

    def _parse_pymupdf(self, path: Path) -> ParsedDocument:
        try:
            doc = fitz.open(path)
        except Exception as e:
            raise IngestionError(
                f"Failed to open PDF with PyMuPDF: {e}",
                code="PDF_PARSING_ERROR",
                details={"file_path": str(path), "engine": "pymupdf", "error": str(e)},
            ) from e

        try:
            raw_meta: dict[str, Any] = doc.metadata or {}
            doc_meta = DocumentMetadata(
                title=str(raw_meta.get("title")) if raw_meta.get("title") else None,
                author=str(raw_meta.get("author")) if raw_meta.get("author") else None,
                subject=str(raw_meta.get("subject")) if raw_meta.get("subject") else None,
                keywords=str(raw_meta.get("keywords")) if raw_meta.get("keywords") else None,
                creator=str(raw_meta.get("creator")) if raw_meta.get("creator") else None,
                producer=str(raw_meta.get("producer")) if raw_meta.get("producer") else None,
                creation_date=str(raw_meta.get("creationDate")) if raw_meta.get("creationDate") else None,
                mod_date=str(raw_meta.get("modDate")) if raw_meta.get("modDate") else None,
                total_pages=len(doc),
                file_size_bytes=path.stat().st_size,
            )

            pages: list[ParsedPage] = []
            for i in range(len(doc)):
                page = doc[i]
                text = page.get_text("text") or ""
                rect = page.rect
                images = page.get_images()
                table_count = 0
                if hasattr(page, "find_tables"):
                    try:
                        tables = page.find_tables()
                        table_count = len(tables.tables) if tables else 0
                    except Exception:
                        table_count = 0

                words = text.split()
                page_meta = PageMetadata(
                    page_number=i + 1,
                    width=float(rect.width),
                    height=float(rect.height),
                    rotation=int(getattr(page, "rotation", 0) or 0),
                    char_count=len(text),
                    word_count=len(words),
                    image_count=len(images),
                    table_count=table_count,
                )
                pages.append(
                    ParsedPage(page_number=i + 1, text=text, metadata=page_meta)
                )

            return ParsedDocument(
                file_name=path.name,
                file_path=str(path),
                source_format="pdf",
                doc_metadata=doc_meta,
                pages=pages,
            )
        except Exception as e:
            if isinstance(e, IngestionError):
                raise
            raise IngestionError(
                f"Error extracting PDF data with PyMuPDF: {e}",
                code="PDF_PARSING_ERROR",
                details={"file_path": str(path), "engine": "pymupdf", "error": str(e)},
            ) from e
        finally:
            doc.close()

    def _parse_pdfplumber(self, path: Path) -> ParsedDocument:
        try:
            with pdfplumber.open(path) as pdf:
                raw_meta: dict[str, Any] = pdf.metadata or {}
                doc_meta = DocumentMetadata(
                    title=str(raw_meta.get("Title")) if raw_meta.get("Title") else None,
                    author=str(raw_meta.get("Author")) if raw_meta.get("Author") else None,
                    subject=str(raw_meta.get("Subject")) if raw_meta.get("Subject") else None,
                    keywords=str(raw_meta.get("Keywords")) if raw_meta.get("Keywords") else None,
                    creator=str(raw_meta.get("Creator")) if raw_meta.get("Creator") else None,
                    producer=str(raw_meta.get("Producer")) if raw_meta.get("Producer") else None,
                    creation_date=str(raw_meta.get("CreationDate")) if raw_meta.get("CreationDate") else None,
                    mod_date=str(raw_meta.get("ModDate")) if raw_meta.get("ModDate") else None,
                    total_pages=len(pdf.pages),
                    file_size_bytes=path.stat().st_size,
                )

                pages: list[ParsedPage] = []
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    images = getattr(page, "images", [])
                    tables = page.extract_tables() or []
                    words = text.split()
                    page_meta = PageMetadata(
                        page_number=i + 1,
                        width=float(page.width),
                        height=float(page.height),
                        rotation=int(getattr(page, "rotation", 0) or 0),
                        char_count=len(text),
                        word_count=len(words),
                        image_count=len(images),
                        table_count=len(tables),
                    )
                    pages.append(
                        ParsedPage(page_number=i + 1, text=text, metadata=page_meta)
                    )

                return ParsedDocument(
                    file_name=path.name,
                    file_path=str(path),
                    source_format="pdf",
                    doc_metadata=doc_meta,
                    pages=pages,
                )
        except Exception as e:
            if isinstance(e, IngestionError):
                raise
            raise IngestionError(
                f"Failed to parse PDF with pdfplumber: {e}",
                code="PDF_PARSING_ERROR",
                details={"file_path": str(path), "engine": "pdfplumber", "error": str(e)},
            ) from e
