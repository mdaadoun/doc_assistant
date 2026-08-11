"""Ingestion domain: PDF/DOCX/MD parsers, structural text chunking."""

from ingestion.base import BaseDocumentParser
from ingestion.docx_parser import DOCXParser
from ingestion.facade import IngestionFacade
from ingestion.markdown_parser import MarkdownParser
from ingestion.pdf_parser import PDFParser
from ingestion.recursive_chunker import RecursiveStructuralChunker
from ingestion.tracker import DifferentialTracker

__all__: list[str] = [
    "BaseDocumentParser",
    "DOCXParser",
    "DifferentialTracker",
    "IngestionFacade",
    "MarkdownParser",
    "PDFParser",
    "RecursiveStructuralChunker",
]
