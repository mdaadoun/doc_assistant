"""Domain models for RAGAS faithfulness framework and context-to-answer alignment."""

from datetime import datetime, timezone

from pydantic import Field

from models.base import BaseDomainModel


def _get_utc_timestamp() -> str:
    """Generate ISO timestamp in UTC."""
    return datetime.now(timezone.utc).isoformat()


class StatementVerification(BaseDomainModel):
    """Factual statement verification result against retrieved context passages."""

    statement: str = Field(..., description="Extracted atomic claim or statement")
    is_faithful: bool = Field(
        ..., description="True if statement is verified and supported by context"
    )
    reason: str = Field(
        default="", description="Verification rationale or support explanation"
    )
    supporting_chunk_id: str | None = Field(
        default=None, description="Chunk ID of supporting context passage if matched"
    )
    matched_keywords: list[str] = Field(
        default_factory=list, description="Key entity and fact tokens matched in context"
    )


class FaithfulnessQueryResult(BaseDomainModel):
    """Per-query faithfulness evaluation record under the RAGAS framework."""

    query_id: str = Field(..., description="Evaluation query identifier")
    query: str = Field(..., description="Executed user question")
    generated_answer: str = Field(..., description="Generated or evaluated answer text")
    contexts: list[str] = Field(
        default_factory=list, description="Context strings used for grounding"
    )
    statements: list[str] = Field(
        default_factory=list, description="List of discrete statements evaluated"
    )
    verifications: list[StatementVerification] = Field(
        default_factory=list, description="Detailed per-statement verification records"
    )
    verified_statements_count: int = Field(
        default=0, ge=0, description="Count of statements supported by context"
    )
    total_statements_count: int = Field(
        default=0, ge=0, description="Total statements extracted from answer"
    )
    faithfulness_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Faithfulness score (supported statements / total statements)",
    )
    is_faithful: bool = Field(
        default=False, description="True if score meets or exceeds minimum threshold"
    )
    is_out_of_corpus: bool = Field(
        default=False, description="Whether query was an out-of-corpus refusal test"
    )
    is_refusal: bool = Field(
        default=False, description="True if response was a valid grounded refusal"
    )
    category: str = Field(default="general", description="Evaluation domain category")


class FaithfulnessMetricThresholds(BaseDomainModel):
    """Configurable quality threshold targets for RAGAS faithfulness."""

    min_faithfulness_score: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Target minimum mean faithfulness score (>= 0.85)",
    )
    min_honesty_filter_precision: float = Field(
        default=0.90,
        ge=0.0,
        le=1.0,
        description="Target minimum honesty precision for out-of-corpus queries",
    )


class FaithfulnessValidationResult(BaseDomainModel):
    """Domain model capturing aggregate RAGAS faithfulness validation outcomes."""

    passed: bool = Field(
        ..., description="True if mean faithfulness meets or exceeds threshold"
    )
    mean_faithfulness_score: float = Field(
        ..., ge=0.0, le=1.0, description="Measured mean faithfulness score"
    )
    target_threshold: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Target minimum faithfulness threshold",
    )
    total_queries: int = Field(..., ge=0, description="Total queries evaluated")
    in_corpus_queries: int = Field(..., ge=0, description="Total in-corpus queries")
    out_of_corpus_queries: int = Field(
        ..., ge=0, description="Total out-of-corpus queries"
    )
    category_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Mean faithfulness score breakdown by category",
    )
    query_results: list[FaithfulnessQueryResult] = Field(
        default_factory=list, description="Per-query detailed evaluation records"
    )
    timestamp: str = Field(
        default_factory=_get_utc_timestamp,
        description="Validation execution timestamp (ISO format)",
    )
