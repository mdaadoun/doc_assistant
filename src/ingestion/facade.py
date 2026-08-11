"""Ingestion facade orchestrating format dispatching and fail-fast file validation."""

from pathlib import Path
from typing import Sequence

from core.exceptions import IngestionError
from ingestion.base import BaseDocumentParser
from ingestion.docx_parser import DOCXParser
from ingestion.markdown_parser import MarkdownParser
from ingestion.pdf_parser import PDFParser
from ingestion.recursive_chunker import RecursiveStructuralChunker
from models.chunk import ChunkDocument
from models.document import ParsedDocument


class IngestionFacade:
    """Facade orchestrating format dispatching, fail-fast validation, parsing, and chunking."""

    def __init__(
        self,
        parsers: dict[str, BaseDocumentParser] | None = None,
        chunker: RecursiveStructuralChunker | None = None,
        max_file_size_bytes: int | None = None,
    ) -> None:
        """Initialize ingestion facade with format parsers, chunker, and size limits."""
        self._parsers: dict[str, BaseDocumentParser] = {}
        if parsers is not None:
            for ext, parser in parsers.items():
                self.register_parser(ext, parser)
        else:
            self.register_parser("pdf", PDFParser())
            self.register_parser("docx", DOCXParser())
            self.register_parser("md", MarkdownParser())
            self.register_parser("markdown", MarkdownParser())

        self.chunker = chunker or RecursiveStructuralChunker()
        self.max_file_size_bytes = max_file_size_bytes

    def register_parser(self, extension: str, parser: BaseDocumentParser) -> None:
        """Register a format parser for a file extension."""
        ext = extension.strip().lstrip(".").lower()
        if not ext:
            raise IngestionError("Extension cannot be empty", code="INVALID_EXTENSION")
        self._parsers[ext] = parser

    def unregister_parser(self, extension: str) -> None:
        """Unregister a format parser for a file extension."""
        ext = extension.strip().lstrip(".").lower()
        if ext in self._parsers:
            del self._parsers[ext]

    def supported_formats(self) -> list[str]:
        """Return sorted list of supported file extensions."""
        return sorted(self._parsers.keys())

    def get_parser(self, extension: str) -> BaseDocumentParser:
        """Retrieve registered parser for an extension."""
        ext = extension.strip().lstrip(".").lower()
        if ext not in self._parsers:
            raise IngestionError(
                f"Unsupported format extension: {ext}",
                code="UNSUPPORTED_FORMAT",
                details={"extension": ext, "supported": self.supported_formats()},
            )
        return self._parsers[ext]

    def validate_file(
        self, file_path: str | Path, format_override: str | None = None
    ) -> Path:
        """Perform fail-fast validation on target document file."""
        path = Path(file_path).resolve()
        if not path.exists():
            raise IngestionError(
                f"Document file does not exist: {path}",
                code="FILE_NOT_FOUND",
                details={"file_path": str(path)},
            )
        if not path.is_file():
            raise IngestionError(
                f"Target path is not a file: {path}",
                code="INVALID_FILE",
                details={"file_path": str(path)},
            )

        file_size = path.stat().st_size
        if file_size == 0:
            raise IngestionError(
                f"Document file is empty (0 bytes): {path}",
                code="EMPTY_FILE",
                details={"file_path": str(path)},
            )

        if (
            self.max_file_size_bytes is not None
            and file_size > self.max_file_size_bytes
        ):
            raise IngestionError(
                f"File size ({file_size} bytes) exceeds limit ({self.max_file_size_bytes} bytes): {path}",
                code="FILE_TOO_LARGE",
                details={
                    "file_path": str(path),
                    "file_size": file_size,
                    "max_size": self.max_file_size_bytes,
                },
            )

        ext = format_override or path.suffix
        ext_clean = ext.strip().lstrip(".").lower()
        if not ext_clean or ext_clean not in self._parsers:
            raise IngestionError(
                f"Unsupported document format extension: '{ext_clean}'",
                code="UNSUPPORTED_FORMAT",
                details={"extension": ext_clean, "supported": self.supported_formats()},
            )

        return path

    def parse_document(
        self, file_path: str | Path, format_override: str | None = None
    ) -> ParsedDocument:
        """Validate and parse a document file into ParsedDocument structure."""
        validated_path = self.validate_file(file_path, format_override=format_override)
        ext = format_override or validated_path.suffix
        parser = self.get_parser(ext)
        return parser.parse(validated_path)

    def ingest_document(
        self, file_path: str | Path, format_override: str | None = None
    ) -> list[ChunkDocument]:
        """Validate, parse, and chunk a document into ChunkDocument list."""
        parsed_doc = self.parse_document(file_path, format_override=format_override)
        return self.chunker.chunk_document(parsed_doc)

    def ingest_batch(
        self,
        file_paths: Sequence[str | Path],
        format_override: str | None = None,
    ) -> list[ChunkDocument]:
        """Validate, parse, and chunk multiple document files into flattened list."""
        chunks: list[ChunkDocument] = []
        for path in file_paths:
            doc_chunks = self.ingest_document(path, format_override=format_override)
            chunks.extend(doc_chunks)
        return chunks
