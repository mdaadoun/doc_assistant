"""Domain models for honesty filter precision validation and refusal classification."""

from datetime import datetime, timezone

from pydantic import Field

from models.base import BaseDomainModel


def _get_utc_timestamp() -> str:
    """Generate ISO timestamp in UTC."""
    return datetime.now(timezone.utc).isoformat()


class HonestyQueryClassification(BaseDomainModel):
    """Classification record evaluating query refusal behavior against ground truth."""

    query_id: str = Field(..., description="Unique query identifier")
    query: str = Field(..., description="Executed user question")
    category: str = Field(default="general", description="Evaluation category")
    is_out_of_corpus: bool = Field(
        default=False, description="True if query is outside corporate documentation"
    )
    expected_refusal: bool = Field(
        default=False, description="True if refusal is expected behavior"
    )
    system_refused: bool = Field(
        default=False, description="True if system gated or emitted refusal"
    )
    is_correctly_classified: bool = Field(
        default=False, description="True if system decision matches ground truth"
    )
    confidence_score: float = Field(
        default=0.0, ge=0.0, description="Highest relevance score observed"
    )
    relevance_threshold: float = Field(
        default=0.35, ge=0.0, le=1.0, description="Confidence threshold cutoff"
    )
    refusal_reason: str = Field(
        default="", description="Reason for refusal or acceptance"
    )
    generated_answer: str | None = Field(
        default=None, description="Generated response text if evaluated"
    )


class HonestyConfusionMatrix(BaseDomainModel):
    """Confusion matrix capturing refusal vs acceptance outcomes."""

    true_refusals: int = Field(
        default=0, ge=0, description="Out-of-corpus queries correctly refused"
    )
    false_acceptances: int = Field(
        default=0, ge=0, description="Out-of-corpus queries incorrectly accepted"
    )
    true_acceptances: int = Field(
        default=0, ge=0, description="In-corpus queries correctly accepted"
    )
    false_refusals: int = Field(
        default=0, ge=0, description="In-corpus queries incorrectly refused"
    )


class HonestyMetricThresholds(BaseDomainModel):
    """Configurable quality threshold targets for honesty filter precision."""

    min_honesty_filter_precision: float = Field(
        default=0.90,
        ge=0.0,
        le=1.0,
        description="Target minimum honesty filter precision (>= 0.90)",
    )
    max_false_refusal_rate: float = Field(
        default=0.10,
        ge=0.0,
        le=1.0,
        description="Maximum allowable false refusal rate for in-corpus queries",
    )


class HonestyValidationResult(BaseDomainModel):
    """Domain model capturing aggregate honesty filter precision validation outcomes."""

    passed: bool = Field(
        ..., description="True if honesty precision meets or exceeds threshold"
    )
    measured_honesty_precision: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Measured honesty filter precision (TR / (TR + FA))",
    )
    target_threshold: float = Field(
        default=0.90,
        ge=0.0,
        le=1.0,
        description="Target minimum honesty precision threshold",
    )
    total_queries: int = Field(..., ge=0, description="Total queries evaluated")
    in_corpus_queries: int = Field(..., ge=0, description="Total in-corpus queries")
    out_of_corpus_queries: int = Field(
        ..., ge=0, description="Total out-of-corpus queries"
    )
    true_refusals: int = Field(
        default=0, ge=0, description="Count of correctly refused out-of-corpus queries"
    )
    false_acceptances: int = Field(
        default=0, ge=0, description="Count of hallucinated out-of-corpus acceptances"
    )
    true_acceptances: int = Field(
        default=0, ge=0, description="Count of correctly accepted in-corpus queries"
    )
    false_refusals: int = Field(
        default=0, ge=0, description="Count of falsely refused in-corpus queries"
    )
    out_of_corpus_refusal_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Rate of refusal on out-of-corpus items",
    )
    in_corpus_pass_rate: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Rate of acceptance on in-corpus items"
    )
    false_refusal_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Rate of false refusals on in-corpus items",
    )
    confusion_matrix: HonestyConfusionMatrix = Field(
        ..., description="Detailed confusion matrix for refusal gating"
    )
    category_metrics: dict[str, float] = Field(
        default_factory=dict,
        description="Refusal precision or accuracy breakdown by category",
    )
    query_classifications: list[HonestyQueryClassification] = Field(
        default_factory=list, description="Detailed per-query classification records"
    )
    timestamp: str = Field(
        default_factory=_get_utc_timestamp,
        description="Validation execution timestamp (ISO format)",
    )
