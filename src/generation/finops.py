"""FinOps telemetry collection service for token usage, cost estimation, and latency."""

import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import structlog
import tiktoken

from models.chat import FinOpsMetadata

logger = structlog.get_logger(__name__)

# Standard model pricing in USD per 1,000 tokens: (prompt_rate_per_1k, completion_rate_per_1k)
MODEL_PRICING: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.00015, 0.0006),
    "gpt-4o": (0.0025, 0.01),
    "gpt-4-turbo": (0.01, 0.03),
    "gpt-3.5-turbo": (0.0005, 0.0015),
    "text-embedding-3-small": (0.00002, 0.0),
    "text-embedding-3-large": (0.00013, 0.0),
}
DEFAULT_MODEL_PRICING: tuple[float, float] = (0.00015, 0.0006)


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Count tokens in text string using tiktoken tokenizer with robust offline fallback."""
    if not text:
        return 0
    try:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except Exception:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        words = text.split()
        return max(1, int(len(words) * 1.3))


def calculate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: str = "gpt-4o-mini",
    is_cached: bool = False,
) -> float:
    """Calculate estimated USD cost based on token counts and model pricing."""
    if is_cached:
        return 0.0
    prompt_rate, completion_rate = MODEL_PRICING.get(
        model.lower(), DEFAULT_MODEL_PRICING
    )
    cost = (prompt_tokens / 1000.0 * prompt_rate) + (
        completion_tokens / 1000.0 * completion_rate
    )
    return round(cost, 6)


class FinOpsCollector:
    """Telemetry collector and cost calculator for LLM interactions."""

    def __init__(self, default_model: str = "gpt-4o-mini") -> None:
        """Initialize FinOpsCollector with default LLM model name."""
        self.default_model = default_model

    def count_tokens(self, text: str, model: str | None = None) -> int:
        """Count tokens for text given a target model."""
        target_model = model or self.default_model
        return count_tokens(text, target_model)

    def calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str | None = None,
        is_cached: bool = False,
    ) -> float:
        """Calculate estimated cost in USD for given token usage."""
        target_model = model or self.default_model
        return calculate_cost(prompt_tokens, completion_tokens, target_model, is_cached)

    def collect(
        self,
        prompt_text: str = "",
        completion_text: str = "",
        execution_time_seconds: float = 0.0,
        model: str | None = None,
        is_cached: bool = False,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
    ) -> FinOpsMetadata:
        """Construct FinOpsMetadata schema instance from text inputs or token counts."""
        target_model = model or self.default_model
        p_tokens = (
            prompt_tokens
            if prompt_tokens is not None
            else self.count_tokens(prompt_text, target_model)
        )
        c_tokens = (
            completion_tokens
            if completion_tokens is not None
            else self.count_tokens(completion_text, target_model)
        )
        total = p_tokens + c_tokens
        cost = self.calculate_cost(p_tokens, c_tokens, target_model, is_cached)
        exec_time = max(0.0, float(execution_time_seconds))

        return FinOpsMetadata(
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
            total_tokens=total,
            estimated_cost_usd=cost,
            execution_time_seconds=round(exec_time, 4),
            is_cached=is_cached,
        )

    @contextmanager
    def track_latency(self) -> Generator[dict[str, Any], None, None]:
        """Context manager measuring execution duration in seconds."""
        metrics: dict[str, Any] = {"elapsed_seconds": 0.0}
        start = time.perf_counter()
        try:
            yield metrics
        finally:
            metrics["elapsed_seconds"] = round(time.perf_counter() - start, 4)
