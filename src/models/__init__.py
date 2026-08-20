"""Domain schemas: Pydantic V2 frozen models, DTOs, and request/response payloads."""

from models.base import BaseDomainModel
from models.chat import (
    ChatRequest,
    ChatResponse,
    Citation,
    FinOpsMetadata,
    SSEDonePayload,
    SSEErrorPayload,
    SSEMetaDataPayload,
    SSETokenPayload,
)
from models.chunk import ChunkDocument, ChunkMetadata
from models.differential import (
    DifferentialDelta,
    DifferentialResult,
    FileState,
    StateManifest,
)
from models.document import DocumentMetadata, PageMetadata, ParsedDocument, ParsedPage
from models.evaluation import (
    EvalDataset,
    EvalDatasetItem,
    EvalGroundTruthCitation,
    RetrievalBenchmarkReport,
    RetrievalMetricThresholds,
    RetrievalPrecisionValidationResult,
    RetrievalQueryResult,
)
from models.retrieval import DebugRetrievalHit, DebugRetrievalResponse, RetrievalResult

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
    "DebugRetrievalHit",
    "ChatRequest",
    "Citation",
    "FinOpsMetadata",
    "ChatResponse",
    "SSEMetaDataPayload",
    "SSETokenPayload",
    "SSEDonePayload",
    "SSEErrorPayload",
    "FileState",
    "StateManifest",
    "DifferentialDelta",
    "DifferentialResult",
    "EvalGroundTruthCitation",
    "EvalDatasetItem",
    "EvalDataset",
    "RetrievalQueryResult",
    "RetrievalMetricThresholds",
    "RetrievalBenchmarkReport",
    "RetrievalPrecisionValidationResult",
]
