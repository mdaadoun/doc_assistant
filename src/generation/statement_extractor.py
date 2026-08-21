"""Atomic statement and claim extraction logic for RAGAS evaluation."""

import re
from typing import Final

from generation.citations import CITATION_REGEX

# Known abbreviations that should not trigger sentence boundaries
ABBREVIATIONS: Final[set[str]] = {
    "e.g.",
    "i.e.",
    "etc.",
    "vs.",
    "dr.",
    "mr.",
    "mrs.",
    "ms.",
    "prof.",
    "approx.",
    "no.",
    "p.",
    "pp.",
    "fig.",
    "inc.",
    "ltd.",
    "corp.",
    "v1.0",
    "v1.5",
    "v2.0",
    "semver",
    "sec.",
    "art.",
}

# Regex to safely detect sentence termination while preserving numbers & abbreviations
SENTENCE_SPLIT_REGEX = re.compile(
    r"(?<=[.!?;\n])\s+(?=[A-Z0-9\"'(\[])|"
    r"(?<=[a-zA-Z0-9])\.\s+(?=[A-Z0-9\"'(\[])|"
    r"\n{1,}"
)

# Standardized refusal string
NO_CONTEXT_REFUSAL_CLEAN = (
    "i cannot answer this question based on the available documentation."
)


class StatementExtractor:
    """Extracts discrete atomic propositions and factual claims from answer texts."""

    @classmethod
    def clean_text_for_extraction(cls, text: str) -> str:
        """Remove inline citations and normalize whitespace while preserving content."""
        if not text:
            return ""
        # Strip inline citations like [Doc: file.pdf | Page: 1]
        cleaned = CITATION_REGEX.sub("", text)
        # Normalize double whitespace and strip
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        return cleaned.strip()

    @classmethod
    def extract_statements(cls, text: str) -> list[str]:
        """Extract atomic statement strings from generated or ground-truth answer text."""
        if not text or not text.strip():
            return []

        cleaned_text = cls.clean_text_for_extraction(text)
        if not cleaned_text:
            return []

        # Check for standardized refusal
        if NO_CONTEXT_REFUSAL_CLEAN in cleaned_text.lower():
            return [
                "I cannot answer this question based on the available documentation."
            ]

        # Split into raw sentences
        raw_chunks = SENTENCE_SPLIT_REGEX.split(cleaned_text)
        statements: list[str] = []

        for chunk in raw_chunks:
            chunk_clean = chunk.strip()
            if not chunk_clean:
                continue

            # Strip leading list markers like "1. ", "- ", "* "
            chunk_clean = re.sub(r"^(\d+[\.\)]|\-|\*)\s*", "", chunk_clean).strip()
            if len(chunk_clean) < 3:
                continue

            # Avoid splitting on known abbreviations if dangling
            lower_chunk = chunk_clean.lower()
            if any(lower_chunk == ab for ab in ABBREVIATIONS):
                continue

            # Ensure proper punctuation termination
            if not chunk_clean.endswith((".", "!", "?", ";")):
                chunk_clean = f"{chunk_clean}."

            statements.append(chunk_clean)

        return statements if statements else [f"{cleaned_text}."]
