"""Ingestion domain: PDF/DOCX/MD parsers, structural text chunking."""

from ingestion.base import BaseDocumentParser
from ingestion.docx_parser import DOCXParser
from ingestion.markdown_parser import MarkdownParser
from ingestion.pdf_parser import PDFParser
from ingestion.recursive_chunker import RecursiveStructuralChunker

__all__: list[str] = [
    "BaseDocumentParser",
    "DOCXParser",
    "MarkdownParser",
    "PDFParser",
    "RecursiveStructuralChunker",
]

