"""Retrieval engine domain: hybrid vector/BM25 search, RRF fusion, re-ranker."""

from retrieval.bm25_index import BM25IndexManager
from retrieval.bm25_tokenizer import tokenize, tokenize_corpus
from retrieval.debug_retrieval import DebugRetrievalBuilder
from retrieval.dense_search import DENSE_TOP_K_DEFAULT, DenseSearchService
from retrieval.indexing_orchestrator import IndexingOrchestrator, IndexingResult
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
    "DebugRetrievalBuilder",
    "DENSE_TOP_K_DEFAULT",
    "DenseSearchService",
    "IndexingOrchestrator",
    "IndexingResult",
    "RRF_K_DEFAULT",
    "RRF_METHOD",
    "RRF_TOP_K_DEFAULT",
    "RRFusionService",
    "SPARSE_TOP_K_DEFAULT",
    "SparseSearchService",
    "VectorStoreAdapter",
    "tokenize",
    "tokenize_corpus",
]
