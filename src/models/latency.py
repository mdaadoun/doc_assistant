"""Domain models for latency benchmarking, percentile statistics, and SLA validation."""

from datetime import datetime, timezone

from pydantic import Field

from models.base import BaseDomainModel


def _get_utc_timestamp() -> str:
    """Generate ISO timestamp in UTC."""
    return datetime.now(timezone.utc).isoformat()


class LatencyStageBreakdown(BaseDomainModel):
    """Execution latency breakdown by pipeline processing stage in milliseconds."""

    retrieval_latency_ms: float = Field(
        default=0.0, ge=0.0, description="Dense/sparse hybrid retrieval latency"
    )
    rerank_latency_ms: float = Field(
        default=0.0, ge=0.0, description="Cross-encoder re-ranking latency"
    )
    guard_latency_ms: float = Field(
        default=0.0, ge=0.0, description="Confidence guard evaluation latency"
    )
    generation_latency_ms: float = Field(
        default=0.0, ge=0.0, description="LLM text generation / streaming latency"
    )
    total_latency_ms: float = Field(
        default=0.0, ge=0.0, description="Total wall-clock pipeline latency"
    )


class LatencyQueryBenchmark(BaseDomainModel):
    """Per-query latency benchmark record with execution duration and category."""

    query_id: str = Field(..., description="Unique query identifier")
    query: str = Field(..., description="Executed user question")
    category: str = Field(default="general", description="Evaluation category")
    is_out_of_corpus: bool = Field(
        default=False, description="Whether query was an out-of-corpus refusal test"
    )
    latency_ms: float = Field(
        ..., ge=0.0, description="Total execution latency in milliseconds"
    )
    stage_breakdown: LatencyStageBreakdown | None = Field(
        default=None, description="Optional granular stage breakdown"
    )
    status: str = Field(default="OK", description="Execution status e.g. OK or ERROR")
    error_message: str | None = Field(
        default=None, description="Error details if query execution failed"
    )


class LatencyPercentileMetrics(BaseDomainModel):
    """Statistical summary of query latencies across percentiles in milliseconds."""

    p50_ms: float = Field(..., ge=0.0, description="50th percentile (median) latency")
    p90_ms: float = Field(..., ge=0.0, description="90th percentile latency")
    p95_ms: float = Field(..., ge=0.0, description="95th percentile latency")
    p99_ms: float = Field(..., ge=0.0, description="99th percentile latency")
    mean_ms: float = Field(..., ge=0.0, description="Arithmetic mean latency")
    min_ms: float = Field(..., ge=0.0, description="Minimum latency observed")
    max_ms: float = Field(..., ge=0.0, description="Maximum latency observed")
    std_dev_ms: float = Field(
        default=0.0, ge=0.0, description="Standard deviation of latencies"
    )


class LatencyMetricThresholds(BaseDomainModel):
    """Target SLA latency thresholds for automated quality gating."""

    max_p95_latency_ms: float = Field(
        default=3000.0,
        ge=0.0,
        description="Target maximum p95 latency in ms (SLA <= 3000ms)",
    )
    max_mean_latency_ms: float = Field(
        default=1500.0,
        ge=0.0,
        description="Target maximum mean latency in ms",
    )
    max_p99_latency_ms: float = Field(
        default=5000.0,
        ge=0.0,
        description="Target maximum p99 latency in ms",
    )


class LatencyValidationResult(BaseDomainModel):
    """Aggregate latency benchmark evaluation result for Phase 10.6."""

    passed: bool = Field(
        ..., description="True if measured p95 latency satisfies target threshold"
    )
    measured_p95_latency_ms: float = Field(
        ..., ge=0.0, description="Measured 95th percentile latency in ms"
    )
    target_threshold_ms: float = Field(
        default=3000.0, ge=0.0, description="Target maximum p95 threshold in ms"
    )
    total_queries: int = Field(..., ge=0, description="Total benchmark queries timed")
    in_corpus_queries: int = Field(..., ge=0, description="Total in-corpus queries")
    out_of_corpus_queries: int = Field(
        ..., ge=0, description="Total out-of-corpus queries"
    )
    percentiles: LatencyPercentileMetrics = Field(
        ..., description="Aggregate latency percentiles and summary statistics"
    )
    thresholds: LatencyMetricThresholds = Field(
        default_factory=LatencyMetricThresholds,
        description="Target SLA threshold configuration",
    )
    category_p95_latencies: dict[str, float] = Field(
        default_factory=dict, description="P95 latency breakdown by query category"
    )
    query_benchmarks: list[LatencyQueryBenchmark] = Field(
        default_factory=list, description="Per-query detailed benchmark records"
    )
    timestamp: str = Field(
        default_factory=_get_utc_timestamp,
        description="Benchmark execution timestamp (ISO format)",
    )
