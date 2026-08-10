"""Chunk domain models for document ingestion and indexing."""

from pydantic import Field

from models.base import BaseDomainModel


class ChunkMetadata(BaseDomainModel):
    """Metadata describing document chunk metrics and format."""

    source_format: str = Field(..., description="Source format extension e.g. pdf, docx, md")
    chunk_index: int = Field(..., ge=0, description="0-indexed position in document")
    total_chunks: int = Field(..., gt=0, description="Total chunks in document")
    char_count: int = Field(..., ge=0, description="Character count in chunk")
    token_count: int = Field(..., ge=0, description="Token count in chunk")


class ChunkDocument(BaseDomainModel):
    """Document chunk schema with text payload and metadata."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    text: str = Field(..., description="Chunk text content")
    file_name: str = Field(..., description="Source document file name")
    page_number: int = Field(..., ge=1, description="1-indexed source page number")
    metadata: ChunkMetadata = Field(..., description="Chunk metadata metrics")
