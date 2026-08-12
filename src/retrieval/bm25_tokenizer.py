"""BM25 tokenizer: lowercase word tokenization with stopword removal."""

import re
from collections.abc import Sequence

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")

_STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "but", "by",
    "for", "if", "in", "into", "is", "it", "no", "not", "of",
    "on", "or", "such", "that", "the", "their", "then", "there",
    "these", "they", "this", "to", "was", "will", "with",
})


def tokenize(text: str) -> list[str]:
    """Tokenize text preserving hyphenated compounds, removing stopwords."""
    tokens = _TOKEN_PATTERN.findall(text.lower())
    return [t for t in tokens if t not in _STOPWORDS]


def tokenize_corpus(texts: Sequence[str]) -> list[list[str]]:
    """Tokenize a sequence of texts into a tokenized corpus."""
    return [tokenize(text) for text in texts]
