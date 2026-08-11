"""Base document parser abstract interface."""

from abc import ABC, abstractmethod
from pathlib import Path

from models.document import ParsedDocument


class BaseDocumentParser(ABC):
    """Abstract base class for format-specific document parsers."""

    @abstractmethod
    def parse(self, file_path: str | Path) -> ParsedDocument:
        """Parse source document file and extract structured ParsedDocument."""
        ...
