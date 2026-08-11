"""Ingestion domain: PDF/DOCX/MD parsers, structural text chunking."""

from ingestion.base import BaseDocumentParser
from ingestion.docx_parser import DOCXParser
from ingestion.pdf_parser import PDFParser

__all__: list[str] = [
    "BaseDocumentParser",
    "DOCXParser",
    "PDFParser",
]
