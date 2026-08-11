"""BM25 tokenizer: lowercase alphanumeric word tokenization."""

import re
from collections.abc import Sequence

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alphanumeric word tokens."""
    return _TOKEN_PATTERN.findall(text.lower())


def tokenize_corpus(texts: Sequence[str]) -> list[list[str]]:
    """Tokenize a sequence of texts into a tokenized corpus."""
    return [tokenize(text) for text in texts]
