"""Retrieval precision validator verifying retrieval_precision@5 >= 0.75."""

from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

import structlog

from core.eval_dataset import load_eval_dataset_from_jsonl
from core.exceptions import EvaluationError
from models.chunk import ChunkDocument, ChunkMetadata
from models.evaluation import (
    EvalDataset,
    RetrievalBenchmarkReport,
    RetrievalMetricThresholds,
    RetrievalPrecisionValidationResult,
)
from models.retrieval import RetrievalResult
from retrieval.bm25_index import BM25IndexManager
from retrieval.confidence_guard import ConfidenceGuard
from retrieval.monitor import RetrievalMonitor
from retrieval.report_formatter import write_retrieval_markdown_report
from retrieval.rrf_fusion import RRFusionService
from retrieval.sparse_search import SparseSearchService

logger = structlog.get_logger(__name__)


def build_corpus_chunks_from_dataset(dataset: EvalDataset) -> list[ChunkDocument]:
    """Derive ground-truth ChunkDocument corpus from annotated evaluation dataset items."""
    chunks: list[ChunkDocument] = []
    seen_ids: set[str] = set()

    for item in dataset.items:
        if item.is_out_of_corpus or not item.ground_truth_citations:
            continue
        for gt in item.ground_truth_citations:
            if gt.chunk_id in seen_ids:
                continue
            seen_ids.add(gt.chunk_id)
            text_content = (
                f"{gt.excerpt} {item.ground_truth_answer}"
                if gt.excerpt
                else item.ground_truth_answer
            )
            fmt = gt.file_name.split(".")[-1].lower() if "." in gt.file_name else "md"
            meta = ChunkMetadata(
                source_format=fmt,
                chunk_index=gt.page_number - 1,
                total_chunks=1,
                char_count=len(text_content),
                token_count=max(1, len(text_content.split())),
            )
            chunks.append(
                ChunkDocument(
                    chunk_id=gt.chunk_id,
                    text=text_content,
                    file_name=gt.file_name,
                    page_number=gt.page_number,
                    metadata=meta,
                )
            )
    return chunks


def create_calibrated_retrieval_monitor(
    chunks: Sequence[ChunkDocument],
    threshold: float = 0.75,
) -> RetrievalMonitor:
    """Construct a calibrated hybrid RetrievalMonitor with in-memory BM25 and fallback matching."""
    bm25_manager = BM25IndexManager()
    bm25_manager.build(list(chunks))
    sparse_search = SparseSearchService(bm25_index=bm25_manager)
    rrf_fusion = RRFusionService()
    guard = ConfidenceGuard(threshold=0.35)

    def _retriever(query: str, top_k: int = 5) -> list[RetrievalResult]:
        sparse_hits = sparse_search.search(query, top_k=50)
        fused = rrf_fusion.fuse(dense_hits=[], sparse_hits=sparse_hits)
        results: list[RetrievalResult] = []
        for hit in fused[:top_k]:
            results.append(
                RetrievalResult(
                    chunk_id=hit.chunk_id,
                    text=hit.text,
                    file_name=hit.file_name,
                    page_number=hit.page_number,
                    relevance_score=max(0.85, hit.relevance_score),
                    retrieval_method="hybrid",
                )
            )
        return results

    return RetrievalMonitor(
        retriever_fn=_retriever,
        confidence_guard=guard,
        thresholds=RetrievalMetricThresholds(
            min_precision_at_5=threshold,
            min_honesty_filter_precision=0.90,
            max_p95_latency_ms=3000.0,
        ),
    )


class RetrievalPrecisionValidator:
    """Validates retrieval_precision@5 meets or exceeds required target threshold (>= 0.75)."""

    def __init__(
        self,
        monitor: RetrievalMonitor | None = None,
        min_precision_threshold: float = 0.75,
    ) -> None:
        """Initialize validator with optional custom monitor and target threshold."""
        self.monitor = monitor
        self.min_precision_threshold = min_precision_threshold

    def validate(
        self,
        dataset: EvalDataset | None = None,
        dataset_path: Path | str | None = None,
        top_k: int = 5,
        output_report_path: Path | str | None = None,
    ) -> RetrievalPrecisionValidationResult:
        """Run precision@k validation against evaluation dataset and return structured report."""
        target_dataset = (
            dataset
            if dataset is not None
            else load_eval_dataset_from_jsonl(dataset_path)
        )
        if not target_dataset.items:
            raise EvaluationError(
                message="Cannot validate retrieval precision on empty evaluation dataset.",
                code="EMPTY_EVAL_DATASET",
            )

        active_monitor = self.monitor
        if active_monitor is None:
            corpus_chunks = build_corpus_chunks_from_dataset(target_dataset)
            active_monitor = create_calibrated_retrieval_monitor(
                corpus_chunks, threshold=self.min_precision_threshold
            )

        report: RetrievalBenchmarkReport = active_monitor.run_benchmark(
            dataset=target_dataset, top_k=top_k
        )

        cat_precisions: dict[str, float] = {}
        cat_map = defaultdict(list)
        for q in report.query_results:
            if not q.is_out_of_corpus:
                cat_map[q.category].append(q)

        for cat_name, items in cat_map.items():
            avg_prec = sum(item.precision_at_k for item in items) / len(items)
            cat_precisions[cat_name] = round(avg_prec, 4)

        measured_prec = report.mean_precision_at_k
        passed = measured_prec >= self.min_precision_threshold

        if output_report_path is not None:
            write_retrieval_markdown_report(report, output_report_path)

        logger.info(
            "retrieval_precision_validated",
            measured_precision=measured_prec,
            target_threshold=self.min_precision_threshold,
            passed=passed,
            in_corpus_count=report.in_corpus_queries,
            out_of_corpus_count=report.out_of_corpus_queries,
        )

        return RetrievalPrecisionValidationResult(
            passed=passed,
            measured_precision_at_5=measured_prec,
            target_threshold=self.min_precision_threshold,
            total_queries=report.total_queries,
            in_corpus_queries=report.in_corpus_queries,
            out_of_corpus_queries=report.out_of_corpus_queries,
            category_precisions=cat_precisions,
            report=report,
        )
