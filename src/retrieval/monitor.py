"""RetrievalMonitor benchmark runner evaluating hybrid retrieval, ranking, and guardrails."""

import time
from collections.abc import Callable
from pathlib import Path

import structlog

from core.eval_dataset import load_eval_dataset_from_jsonl
from core.exceptions import EvaluationError
from models.evaluation import (
    EvalDataset,
    EvalDatasetItem,
    RetrievalBenchmarkReport,
    RetrievalMetricThresholds,
    RetrievalQueryResult,
)
from models.retrieval import RetrievalResult
from retrieval.confidence_guard import ConfidenceGuard
from retrieval.dense_search import DenseSearchService
from retrieval.metrics import (
    compute_latency_statistics,
    compute_precision_at_k,
    compute_recall_at_k,
    match_retrieved_chunks,
)
from retrieval.report_formatter import (
    format_retrieval_markdown_report,
    write_retrieval_markdown_report,
)
from retrieval.reranker_service import RerankerService
from retrieval.rrf_fusion import RRFusionService
from retrieval.sparse_search import SparseSearchService

logger = structlog.get_logger(__name__)

RetrieverCallable = Callable[[str, int], list[RetrievalResult]]


class RetrievalMonitor:
    """Benchmark runner orchestrating offline retrieval quality & latency evaluation."""

    def __init__(
        self,
        dense_search: DenseSearchService | None = None,
        sparse_search: SparseSearchService | None = None,
        rrf_fusion: RRFusionService | None = None,
        reranker: RerankerService | None = None,
        confidence_guard: ConfidenceGuard | None = None,
        retriever_fn: RetrieverCallable | None = None,
        thresholds: RetrievalMetricThresholds | None = None,
    ) -> None:
        """Initialize benchmark monitor with pipeline services or custom retriever function."""
        self.dense_search = dense_search
        self.sparse_search = sparse_search
        self.rrf_fusion = rrf_fusion
        self.reranker = reranker
        self.confidence_guard = confidence_guard or ConfidenceGuard()
        self.retriever_fn = retriever_fn
        self.thresholds = thresholds or RetrievalMetricThresholds()

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Execute candidate retrieval pipeline for a single query."""
        if self.retriever_fn is not None:
            return self.retriever_fn(query, top_k)

        if self.dense_search and self.sparse_search and self.rrf_fusion:
            dense_hits = self.dense_search.search(query)
            sparse_hits = self.sparse_search.search(query)
            fused = self.rrf_fusion.fuse(dense_hits=dense_hits, sparse_hits=sparse_hits)
            if self.reranker:
                return self.reranker.rerank(query=query, hits=fused, top_k=top_k)
            return list(fused[:top_k])

        raise EvaluationError(
            message="RetrievalMonitor lacks search services or retriever_fn to execute retrieval.",
            code="RETRIEVER_UNCONFIGURED",
        )

    def evaluate_item(
        self,
        item: EvalDatasetItem,
        top_k: int = 5,
    ) -> RetrievalQueryResult:
        """Evaluate retrieval performance and guardrail behavior for a single dataset item."""
        start_t = time.perf_counter()
        try:
            hits = self.retrieve(item.query, top_k=top_k)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            decision = self.confidence_guard.evaluate(hits)

            retrieved_cids = [h.chunk_id for h in hits[:top_k]]
            gt_cids = [c.chunk_id for c in item.ground_truth_citations]
            matched_cids = match_retrieved_chunks(hits[:top_k], item)

            is_correctly_refused = (
                not decision.passed if item.is_out_of_corpus else decision.passed
            )

            reciprocal_rank = 0.0
            for rank, hit in enumerate(hits[:top_k], start=1):
                if hit.chunk_id in matched_cids:
                    reciprocal_rank = 1.0 / float(rank)
                    break

            precision_val = (
                compute_precision_at_k(
                    matched_cids, gt_cids, k=top_k, normalize_by_min_gt=True
                )
                if not item.is_out_of_corpus
                else 0.0
            )
            recall_val = (
                compute_recall_at_k(matched_cids, gt_cids, k=top_k)
                if not item.is_out_of_corpus
                else 1.0
            )

            return RetrievalQueryResult(
                query_id=item.query_id,
                query=item.query,
                category=item.category,
                is_out_of_corpus=item.is_out_of_corpus,
                retrieved_chunk_ids=retrieved_cids,
                ground_truth_chunk_ids=gt_cids,
                top_k=top_k,
                precision_at_k=precision_val,
                recall_at_k=recall_val,
                reciprocal_rank=reciprocal_rank,
                hit_at_k=len(matched_cids) > 0,
                passed_confidence_guard=decision.passed,
                top_score=decision.top_score,
                is_correctly_refused=is_correctly_refused,
                latency_ms=round(elapsed_ms, 3),
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            logger.error("query_eval_failed", query_id=item.query_id, error=str(exc))
            return RetrievalQueryResult(
                query_id=item.query_id,
                query=item.query,
                category=item.category,
                is_out_of_corpus=item.is_out_of_corpus,
                top_k=top_k,
                latency_ms=round(elapsed_ms, 3),
                error=str(exc),
            )

    def run_benchmark(
        self,
        dataset: EvalDataset | None = None,
        dataset_path: Path | str | None = None,
        top_k: int = 5,
    ) -> RetrievalBenchmarkReport:
        """Run full benchmark suite against evaluation dataset and aggregate quality metrics."""
        target_dataset = (
            dataset
            if dataset is not None
            else load_eval_dataset_from_jsonl(dataset_path)
        )
        if not target_dataset.items:
            raise EvaluationError(
                message="Cannot run benchmark on empty evaluation dataset.",
                code="EMPTY_EVAL_DATASET",
            )

        results = [
            self.evaluate_item(item, top_k=top_k) for item in target_dataset.items
        ]
        in_c = [r for r in results if not r.is_out_of_corpus]
        out_c = [r for r in results if r.is_out_of_corpus]

        in_n = len(in_c)
        out_n = len(out_c)

        mean_prec = sum(r.precision_at_k for r in in_c) / in_n if in_n > 0 else 0.0
        mean_rec = sum(r.recall_at_k for r in in_c) / in_n if in_n > 0 else 0.0
        mrr = sum(r.reciprocal_rank for r in in_c) / in_n if in_n > 0 else 0.0
        hit_rate = sum(1 for r in in_c if r.hit_at_k) / in_n if in_n > 0 else 0.0
        honesty = (
            sum(1 for r in out_c if r.is_correctly_refused) / out_n
            if out_n > 0
            else 1.0
        )

        lat_stats = compute_latency_statistics([r.latency_ms for r in results])
        prec_pass = mean_prec >= self.thresholds.min_precision_at_5
        hon_pass = honesty >= self.thresholds.min_honesty_filter_precision
        lat_pass = lat_stats["p95_ms"] <= self.thresholds.max_p95_latency_ms

        return RetrievalBenchmarkReport(
            total_queries=len(results),
            in_corpus_queries=in_n,
            out_of_corpus_queries=out_n,
            mean_precision_at_k=round(mean_prec, 4),
            mean_recall_at_k=round(mean_rec, 4),
            mrr=round(mrr, 4),
            hit_rate_at_k=round(hit_rate, 4),
            honesty_filter_precision=round(honesty, 4),
            latency_p50_ms=lat_stats["p50_ms"],
            latency_p90_ms=lat_stats["p90_ms"],
            latency_p95_ms=lat_stats["p95_ms"],
            latency_p99_ms=lat_stats["p99_ms"],
            latency_mean_ms=lat_stats["mean_ms"],
            latency_max_ms=lat_stats["max_ms"],
            thresholds=self.thresholds,
            precision_threshold_passed=prec_pass,
            honesty_threshold_passed=hon_pass,
            latency_threshold_passed=lat_pass,
            all_passed=prec_pass and hon_pass and lat_pass,
            query_results=results,
        )

    def generate_report(
        self,
        report: RetrievalBenchmarkReport,
        output_path: Path | str | None = None,
    ) -> str:
        """Render Markdown benchmark report and optionally write to filesystem."""
        if output_path is not None:
            write_retrieval_markdown_report(report, output_path)
        return format_retrieval_markdown_report(report)
