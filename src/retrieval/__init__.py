"""Retrieval engine domain: hybrid vector/BM25 search, RRF fusion, re-ranker."""

from clients.base_reranker import BaseRerankerAdapter
from clients.flashrank_reranker import FlashRankRerankerAdapter
from clients.mock_reranker import MockRerankerAdapter
from clients.reranker import create_reranker_adapter
from retrieval.bm25_index import BM25IndexManager
from retrieval.bm25_tokenizer import tokenize, tokenize_corpus
from retrieval.confidence_guard import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_REFUSAL_RESPONSE,
    ConfidenceGuard,
)
from retrieval.debug_retrieval import DebugRetrievalBuilder
from retrieval.dense_search import DENSE_TOP_K_DEFAULT, DenseSearchService
from retrieval.indexing_orchestrator import IndexingOrchestrator, IndexingResult
from retrieval.metrics import (
    compute_hit_at_k,
    compute_label_match_ratio_at_k,
    compute_latency_statistics,
    compute_percentile,
    compute_precision_at_k,
    compute_recall_at_k,
    compute_reciprocal_rank,
    match_retrieved_chunks,
)
from retrieval.monitor import RetrievalMonitor
from retrieval.precision_validator import (
    RetrievalPrecisionValidator,
    build_corpus_chunks_from_dataset,
    create_calibrated_retrieval_monitor,
)
from retrieval.report_formatter import (
    format_retrieval_markdown_report,
    write_retrieval_markdown_report,
)
from retrieval.reranker_service import RerankerService
from retrieval.rrf_fusion import (
    RRF_K_DEFAULT,
    RRF_METHOD,
    RRF_TOP_K_DEFAULT,
    RRFusionService,
)
from retrieval.sparse_search import SPARSE_TOP_K_DEFAULT, SparseSearchService
from retrieval.vector_store import VectorStoreAdapter

__all__: list[str] = [
    "BM25IndexManager",
    "BaseRerankerAdapter",
    "ConfidenceGuard",
    "DEFAULT_CONFIDENCE_THRESHOLD",
    "DEFAULT_REFUSAL_RESPONSE",
    "DENSE_TOP_K_DEFAULT",
    "DebugRetrievalBuilder",
    "DenseSearchService",
    "FlashRankRerankerAdapter",
    "IndexingOrchestrator",
    "IndexingResult",
    "MockRerankerAdapter",
    "RRF_K_DEFAULT",
    "RRF_METHOD",
    "RRF_TOP_K_DEFAULT",
    "RRFusionService",
    "RerankerService",
    "RetrievalMonitor",
    "RetrievalPrecisionValidator",
    "SPARSE_TOP_K_DEFAULT",
    "SparseSearchService",
    "VectorStoreAdapter",
    "build_corpus_chunks_from_dataset",
    "compute_hit_at_k",
    "compute_label_match_ratio_at_k",
    "compute_latency_statistics",
    "compute_percentile",
    "compute_precision_at_k",
    "compute_recall_at_k",
    "compute_reciprocal_rank",
    "create_calibrated_retrieval_monitor",
    "create_reranker_adapter",
    "format_retrieval_markdown_report",
    "match_retrieved_chunks",
    "tokenize",
    "tokenize_corpus",
    "write_retrieval_markdown_report",
]
