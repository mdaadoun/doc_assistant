"""Pure retrieval benchmark metric computations and statistical aggregations."""

import math
from collections.abc import Sequence

from models.evaluation import EvalDatasetItem
from models.retrieval import RetrievalResult


def compute_precision_at_k(
    retrieved_ids: Sequence[str],
    ground_truth_ids: Sequence[str],
    k: int = 5,
) -> float:
    """Compute Precision@k: fraction of top-k retrieved chunks present in ground truth."""
    if k <= 0 or not retrieved_ids:
        return 0.0
    top_k_retrieved = list(retrieved_ids[:k])
    gt_set = set(ground_truth_ids)
    if not gt_set:
        return 0.0
    matched_count = sum(1 for cid in top_k_retrieved if cid in gt_set)
    return float(matched_count) / float(k)


def compute_recall_at_k(
    retrieved_ids: Sequence[str],
    ground_truth_ids: Sequence[str],
    k: int = 5,
) -> float:
    """Compute Recall@k: fraction of ground-truth chunks retrieved in top-k."""
    gt_set = set(ground_truth_ids)
    if not gt_set:
        return 1.0 if not retrieved_ids else 0.0
    if k <= 0 or not retrieved_ids:
        return 0.0
    top_k_retrieved = list(retrieved_ids[:k])
    matched_count = sum(1 for cid in top_k_retrieved if cid in gt_set)
    return float(matched_count) / float(len(gt_set))


def compute_reciprocal_rank(
    retrieved_ids: Sequence[str],
    ground_truth_ids: Sequence[str],
    k: int = 5,
) -> float:
    """Compute Reciprocal Rank (1/rank) of first relevant chunk within top-k."""
    if k <= 0 or not retrieved_ids:
        return 0.0
    gt_set = set(ground_truth_ids)
    if not gt_set:
        return 0.0
    for rank, cid in enumerate(retrieved_ids[:k], start=1):
        if cid in gt_set:
            return 1.0 / float(rank)
    return 0.0


def compute_hit_at_k(
    retrieved_ids: Sequence[str],
    ground_truth_ids: Sequence[str],
    k: int = 5,
) -> bool:
    """Return True if at least one ground-truth chunk is present in top-k hits."""
    if k <= 0 or not retrieved_ids:
        return False
    gt_set = set(ground_truth_ids)
    if not gt_set:
        return False
    return any(cid in gt_set for cid in retrieved_ids[:k])


def match_retrieved_chunks(
    retrieved_hits: Sequence[RetrievalResult],
    item: EvalDatasetItem,
) -> list[str]:
    """Match retrieved hits against ground-truth citations by chunk ID or file+page."""
    matched_cids: list[str] = []
    for hit in retrieved_hits:
        for gt in item.ground_truth_citations:
            if hit.chunk_id == gt.chunk_id or (
                hit.file_name == gt.file_name and hit.page_number == gt.page_number
            ):
                matched_cids.append(hit.chunk_id)
                break
    return matched_cids


def compute_percentile(values: Sequence[float], percentile: float) -> float:
    """Compute linear interpolated percentile (0.0 to 100.0) from numeric values."""
    if not values:
        return 0.0
    sorted_v = sorted(float(v) for v in values)
    n = len(sorted_v)
    if n == 1:
        return sorted_v[0]
    clamped_p = max(0.0, min(100.0, float(percentile)))
    rank = (clamped_p / 100.0) * (n - 1)
    low_idx = int(math.floor(rank))
    high_idx = min(low_idx + 1, n - 1)
    weight = rank - low_idx
    interpolated = sorted_v[low_idx] * (1.0 - weight) + sorted_v[high_idx] * weight
    return float(interpolated)


def compute_latency_statistics(latencies: Sequence[float]) -> dict[str, float]:
    """Compute p50, p90, p95, p99, mean, and max latency statistics in ms."""
    if not latencies:
        return {
            "p50_ms": 0.0,
            "p90_ms": 0.0,
            "p95_ms": 0.0,
            "p99_ms": 0.0,
            "mean_ms": 0.0,
            "max_ms": 0.0,
        }
    clean = [max(0.0, float(x)) for x in latencies]
    return {
        "p50_ms": round(compute_percentile(clean, 50.0), 3),
        "p90_ms": round(compute_percentile(clean, 90.0), 3),
        "p95_ms": round(compute_percentile(clean, 95.0), 3),
        "p99_ms": round(compute_percentile(clean, 99.0), 3),
        "mean_ms": round(sum(clean) / len(clean), 3),
        "max_ms": round(max(clean), 3),
    }
