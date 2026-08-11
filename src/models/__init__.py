"""Domain schemas: Pydantic V2 frozen models, DTOs, and request/response payloads."""

from models.base import BaseDomainModel
from models.chat import ChatRequest, ChatResponse, Citation, FinOpsMetadata
from models.chunk import ChunkDocument, ChunkMetadata
from models.document import DocumentMetadata, PageMetadata, ParsedDocument, ParsedPage
from models.retrieval import DebugRetrievalResponse, RetrievalResult

__all__: list[str] = [
    "BaseDomainModel",
    "ChunkMetadata",
    "ChunkDocument",
    "DocumentMetadata",
    "PageMetadata",
    "ParsedPage",
    "ParsedDocument",
    "RetrievalResult",
    "DebugRetrievalResponse",
    "ChatRequest",
    "Citation",
    "FinOpsMetadata",
    "ChatResponse",
]
