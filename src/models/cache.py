"""Domain models for SHA-256 response caching and cache statistics."""

import time
from typing import Any

from pydantic import Field

from models.base import BaseDomainModel
from models.chat import Citation


class CacheEntry(BaseDomainModel):
    """Cached assistant response payload keyed on SHA-256 digest."""

    key: str = Field(
        ..., min_length=64, max_length=64, description="64-character SHA-256 hex digest"
    )
    input_text: str = Field(..., description="Normalized user input query")
    prompt: str = Field(..., description="Full prompt text / system prompt template")
    model: str = Field(..., description="Generation model identifier")
    response: str = Field(..., description="Cached response text")
    created_at: float = Field(
        ..., ge=0.0, description="Epoch timestamp of cache entry creation"
    )
    ttl_seconds: int | None = Field(
        default=None, ge=1, description="Time-to-live expiration in seconds"
    )
    citations: list[Citation] = Field(
        default_factory=list, description="Retrieved source citations"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Execution and finops metadata"
    )

    def is_expired(self, current_time: float | None = None) -> bool:
        """Evaluate if cache entry has exceeded its time-to-live."""
        if self.ttl_seconds is None:
            return False
        now = current_time if current_time is not None else time.time()
        return (now - self.created_at) > self.ttl_seconds


class CacheStats(BaseDomainModel):
    """Telemetry and performance statistics for cache operations."""

    hits: int = Field(default=0, ge=0, description="Total cache hit count")
    misses: int = Field(default=0, ge=0, description="Total cache miss count")
    evictions: int = Field(default=0, ge=0, description="Total evicted entries count")
    entries_count: int = Field(
        default=0, ge=0, description="Current number of stored entries"
    )
    hit_rate: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Ratio of hits to total lookups"
    )
