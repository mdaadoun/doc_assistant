"""Unit tests for SHA-256 cache key generation logic."""

from unittest.mock import patch

import pytest

from cache.key_generator import compute_cache_key
from core.exceptions import CacheError


def test_compute_cache_key_deterministic() -> None:
    """Verify identical inputs produce exact same 64-char SHA-256 key."""
    key1 = compute_cache_key(
        input_text="What is the remote work policy?",
        prompt="SYSTEM PROMPT: Be helpful.",
        model="gpt-4o-mini",
    )
    key2 = compute_cache_key(
        input_text="What is the remote work policy?",
        prompt="SYSTEM PROMPT: Be helpful.",
        model="gpt-4o-mini",
    )
    assert len(key1) == 64
    assert key1 == key2


def test_compute_cache_key_differs_on_input_or_prompt_or_model() -> None:
    """Verify changes to any key component results in distinct SHA-256 key."""
    base_key = compute_cache_key(
        input_text="Query A", prompt="Prompt X", model="gpt-4o-mini"
    )

    diff_input = compute_cache_key(
        input_text="Query B", prompt="Prompt X", model="gpt-4o-mini"
    )
    diff_prompt = compute_cache_key(
        input_text="Query A", prompt="Prompt Y", model="gpt-4o-mini"
    )
    diff_model = compute_cache_key(
        input_text="Query A", prompt="Prompt X", model="gpt-4o"
    )

    assert base_key != diff_input
    assert base_key != diff_prompt
    assert base_key != diff_model


def test_compute_cache_key_normalizes_whitespace_and_case() -> None:
    """Verify input trimming and model lowercase normalization."""
    k1 = compute_cache_key("  hello world  ", " prompt ", "GPT-4O-MINI")
    k2 = compute_cache_key("hello world", "prompt", "gpt-4o-mini")
    assert k1 == k2


def test_compute_cache_key_extra_params_ordering_invariance() -> None:
    """Verify extra parameter key ordering does not alter generated key."""
    p1 = {"temperature": 0.0, "top_k": 5}
    p2 = {"top_k": 5, "temperature": 0.0}

    k1 = compute_cache_key("Query", "Prompt", "gpt-4o-mini", extra_params=p1)
    k2 = compute_cache_key("Query", "Prompt", "gpt-4o-mini", extra_params=p2)
    assert k1 == k2


def test_compute_cache_key_unicode_characters() -> None:
    """Verify UTF-8 characters are handled seamlessly without corruption."""
    k = compute_cache_key(
        input_text="Was sind die Geschäftsbedingungen für Zürich?",
        prompt="Richtlinien für Helvetia Consulting 🇨🇭",
        model="gpt-4o-mini",
    )
    assert len(k) == 64


def test_compute_cache_key_serialization_failure_raises_cache_error() -> None:
    """Verify serialization failures are wrapped in CacheError."""
    with patch("json.dumps", side_effect=TypeError("Cannot serialize")):
        with pytest.raises(CacheError) as exc_info:
            compute_cache_key("query", "prompt", "model")
        assert exc_info.value.code == "CACHE_KEY_ERROR"
