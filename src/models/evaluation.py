"""Evaluation domain models for RAG benchmarking and dataset validation."""

from datetime import datetime, timezone

from pydantic import Field

from models.base import BaseDomainModel


class EvalGroundTruthCitation(BaseDomainModel):
    """Ground-truth citation reference with source document attribution."""

    file_name: str = Field(..., description="Source document file name")
    page_number: int = Field(default=1, ge=1, description="1-indexed page number")
    chunk_id: str = Field(..., description="Target ground-truth chunk ID")
    excerpt: str = Field(default="", description="Relevant reference excerpt")


class EvalDatasetItem(BaseDomainModel):
    """Annotated evaluation query-answer record for RAG evaluation."""

    query_id: str = Field(..., description="Unique query identifier")
    query: str = Field(..., min_length=1, description="Evaluation user query")
    ground_truth_answer: str = Field(
        ..., min_length=1, description="Expected ground-truth response"
    )
    ground_truth_citations: list[EvalGroundTruthCitation] = Field(
        default_factory=list, description="Supporting ground-truth citations"
    )
    is_out_of_corpus: bool = Field(
        default=False,
        description="Whether query is out-of-corpus expecting refusal",
    )
    category: str = Field(
        default="general",
        description="Domain category e.g. hr_policy, sla, legal, out_of_corpus",
    )


class EvalDataset(BaseDomainModel):
    """Collection container for validated evaluation dataset records."""

    items: list[EvalDatasetItem] = Field(
        default_factory=list, description="List of evaluation dataset items"
    )
    version: str = Field(
        default="1.0.0", description="Dataset schema and content version"
    )

    @property
    def total_queries(self) -> int:
        """Return total count of queries in dataset."""
        return len(self.items)

    @property
    def out_of_corpus_count(self) -> int:
        """Return count of out-of-corpus queries in dataset."""
        return sum(1 for item in self.items if item.is_out_of_corpus)

    @property
    def in_corpus_count(self) -> int:
        """Return count of in-corpus queries in dataset."""
        return sum(1 for item in self.items if not item.is_out_of_corpus)


class RetrievalQueryResult(BaseDomainModel):
    """Per-query benchmark execution outcome with metrics and attribution."""

    query_id: str = Field(..., description="Query identifier from eval dataset")
    query: str = Field(..., description="Executed query string")
    category: str = Field(default="general", description="Evaluation category")
    is_out_of_corpus: bool = Field(
        default=False, description="Whether query was out-of-corpus"
    )
    retrieved_chunk_ids: list[str] = Field(
        default_factory=list, description="Chunk IDs of top-k retrieved candidates"
    )
    ground_truth_chunk_ids: list[str] = Field(
        default_factory=list, description="Chunk IDs from ground-truth citations"
    )
    top_k: int = Field(default=5, ge=1, description="Number of candidates evaluated")
    precision_at_k: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Precision@k metric score"
    )
    recall_at_k: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Recall@k metric score"
    )
    reciprocal_rank: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Reciprocal rank (1/rank)"
    )
    hit_at_k: bool = Field(
        default=False, description="True if at least 1 ground truth chunk was retrieved"
    )
    passed_confidence_guard: bool = Field(
        default=False, description="Whether top hit score satisfied confidence cutoff"
    )
    top_score: float = Field(
        default=0.0, description="Highest relevance score among retrieved hits"
    )
    is_correctly_refused: bool = Field(
        default=False,
        description="Whether refusal behavior correctly matched ground truth",
    )
    latency_ms: float = Field(
        default=0.0, ge=0.0, description="Retrieval pipeline execution latency in ms"
    )
    error: str | None = Field(
        default=None, description="Error message if query execution failed"
    )


class RetrievalMetricThresholds(BaseDomainModel):
    """Configurable quality threshold targets for retrieval benchmarking."""

    min_precision_at_5: float = Field(
        default=0.75, ge=0.0, le=1.0, description="Target minimum precision@5"
    )
    min_honesty_filter_precision: float = Field(
        default=0.90, ge=0.0, le=1.0, description="Target minimum honesty precision"
    )
    max_p95_latency_ms: float = Field(
        default=3000.0, ge=0.0, description="Target maximum p95 latency in ms"
    )


def _get_utc_timestamp() -> str:
    """Generate ISO timestamp in UTC."""
    return datetime.now(timezone.utc).isoformat()


class RetrievalBenchmarkReport(BaseDomainModel):
    """Aggregate benchmark report summary for retrieval and guardrail evaluation."""

    total_queries: int = Field(
        ..., ge=0, description="Total benchmark queries evaluated"
    )
    in_corpus_queries: int = Field(..., ge=0, description="Total in-corpus queries")
    out_of_corpus_queries: int = Field(
        ..., ge=0, description="Total out-of-corpus queries"
    )
    mean_precision_at_k: float = Field(
        ..., ge=0.0, le=1.0, description="Mean Precision@k across in-corpus queries"
    )
    mean_recall_at_k: float = Field(
        ..., ge=0.0, le=1.0, description="Mean Recall@k across in-corpus queries"
    )
    mrr: float = Field(
        ..., ge=0.0, le=1.0, description="Mean Reciprocal Rank across in-corpus queries"
    )
    hit_rate_at_k: float = Field(
        ..., ge=0.0, le=1.0, description="Hit rate (queries with >=1 hit) in-corpus"
    )
    honesty_filter_precision: float = Field(
        ..., ge=0.0, le=1.0, description="Correct refusal rate on out-of-corpus queries"
    )
    latency_p50_ms: float = Field(
        ..., ge=0.0, description="Median retrieval latency ms"
    )
    latency_p90_ms: float = Field(..., ge=0.0, description="90th percentile latency ms")
    latency_p95_ms: float = Field(..., ge=0.0, description="95th percentile latency ms")
    latency_p99_ms: float = Field(..., ge=0.0, description="99th percentile latency ms")
    latency_mean_ms: float = Field(..., ge=0.0, description="Mean retrieval latency ms")
    latency_max_ms: float = Field(..., ge=0.0, description="Max retrieval latency ms")
    thresholds: RetrievalMetricThresholds = Field(
        default_factory=RetrievalMetricThresholds,
        description="Target benchmark quality thresholds",
    )
    precision_threshold_passed: bool = Field(
        ..., description="True if mean_precision_at_k meets threshold"
    )
    honesty_threshold_passed: bool = Field(
        ..., description="True if honesty_filter_precision meets threshold"
    )
    latency_threshold_passed: bool = Field(
        ..., description="True if latency_p95_ms meets threshold"
    )
    all_passed: bool = Field(
        ..., description="True if all benchmark quality thresholds are satisfied"
    )
    query_results: list[RetrievalQueryResult] = Field(
        default_factory=list, description="Per-query detailed evaluation records"
    )
    timestamp: str = Field(
        default_factory=_get_utc_timestamp,
        description="Benchmark execution timestamp (ISO format)",
    )
