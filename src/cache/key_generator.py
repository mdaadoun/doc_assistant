"""Deterministic SHA-256 cache key generation for query, prompt, and model."""

import hashlib
import json
from typing import Any

from core.exceptions import CacheError


def compute_cache_key(
    input_text: str,
    prompt: str,
    model: str,
    extra_params: dict[str, Any] | None = None,
) -> str:
    """Generate deterministic 64-character SHA-256 hex digest for cache indexing.

    Args:
        input_text: Normalized user input query or raw prompt string.
        prompt: System prompt template, grounding context, or instructions.
        model: Target generation model identifier (e.g., 'gpt-4o-mini').
        extra_params: Optional additional parameters (e.g. temperature, top_k).

    Returns:
        64-character SHA-256 hexadecimal digest string.

    Raises:
        CacheError: If serialization or hashing encounters an unexpected failure.
    """
    try:
        canonical_payload: dict[str, Any] = {
            "input": input_text.strip(),
            "model": model.strip().lower(),
            "prompt": prompt.strip(),
        }

        if extra_params:
            # Sort keys for deterministic JSON serialization
            canonical_payload["extra"] = {
                k: extra_params[k] for k in sorted(extra_params.keys())
            }

        serialized = json.dumps(
            canonical_payload,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    except Exception as err:
        raise CacheError(
            f"Failed to generate cache key: {err}",
            code="CACHE_KEY_ERROR",
            details={
                "input_preview": input_text[:50],
                "model": model,
            },
        ) from err
