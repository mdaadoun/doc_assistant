"""Chat domain models for request, response, citation, and FinOps telemetry."""

from pydantic import Field

from models.base import BaseDomainModel


class ChatRequest(BaseDomainModel):
    """User assistant query request schema."""

    query: str = Field(..., min_length=1, description="User query prompt")
    conversation_id: str = Field(..., min_length=1, description="Unique conversation session ID")
    top_k: int = Field(default=5, ge=1, description="Top K context chunks to retrieve")


class Citation(BaseDomainModel):
    """Source reference supporting generated assistant answer."""

    file_name: str = Field(..., description="Source document file name")
    page_number: int = Field(..., ge=1, description="1-indexed source page number")
    chunk_id: str = Field(..., description="Cited chunk identifier")
    excerpt: str = Field(..., description="Relevant text snippet cited")
    relevance_score: float = Field(..., description="Relevance score of cited chunk")


class FinOpsMetadata(BaseDomainModel):
    """Telemetry and cost tracking metrics per interaction."""

    prompt_tokens: int = Field(..., ge=0, description="Prompt token count")
    completion_tokens: int = Field(..., ge=0, description="Completion token count")
    total_tokens: int = Field(..., ge=0, description="Total token count")
    estimated_cost_usd: float = Field(..., ge=0.0, description="Estimated USD cost")
    execution_time_seconds: float = Field(..., ge=0.0, description="Latency in seconds")
    is_cached: bool = Field(default=False, description="Cache hit indicator")


class ChatResponse(BaseDomainModel):
    """Assistant completion response schema with grounded citations."""

    answer: str = Field(..., description="Generated answer text")
    citations: list[Citation] = Field(default_factory=list, description="Supporting citations")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    grounded: bool = Field(..., description="Context grounding indicator")
    latency_ms: int = Field(..., ge=0, description="Total latency in milliseconds")
    finops: FinOpsMetadata = Field(..., description="Token and cost telemetry")
