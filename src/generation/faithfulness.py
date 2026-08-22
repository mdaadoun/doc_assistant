"""RAGAS Faithfulness evaluation engine verifying statement context alignment."""

import re
from collections.abc import Sequence
from typing import Any, Final

import structlog

from generation.engine import NO_CONTEXT_REFUSAL
from generation.statement_extractor import (
    NO_CONTEXT_REFUSAL_CLEAN,
    StatementExtractor,
)
from models.faithfulness import (
    FaithfulnessQueryResult,
    StatementVerification,
)

logger = structlog.get_logger(__name__)

STOPWORDS: Final[set[str]] = {
    "the",
    "and",
    "is",
    "in",
    "to",
    "of",
    "for",
    "with",
    "a",
    "an",
    "on",
    "that",
    "this",
    "by",
    "from",
    "at",
    "as",
    "be",
    "are",
    "was",
    "were",
    "or",
    "it",
    "its",
    "all",
    "any",
    "can",
    "may",
    "will",
    "shall",
    "must",
    "under",
    "over",
    "such",
    "than",
    "then",
    "into",
    "their",
    "they",
    "them",
    "which",
    "who",
    "when",
    "what",
    "where",
    "why",
    "how",
}

TOKEN_SPLIT_REGEX = re.compile(r"[\w']+|[0-9]+(?:\.[0-9]+)?%?|\$[0-9,]+")


def _extract_context_passages(
    contexts: Sequence[str | dict[str, Any] | Any],
) -> list[tuple[str, str]]:
    """Extract list of (chunk_id, normalized_text) pairs from heterogeneous context inputs."""
    passages: list[tuple[str, str]] = []
    for idx, ctx in enumerate(contexts):
        if isinstance(ctx, str):
            passages.append((f"ctx-{idx + 1}", ctx.lower()))
        elif isinstance(ctx, dict):
            cid = str(
                ctx.get("chunk_id")
                or ctx.get("id")
                or f"{ctx.get('file_name', 'doc')}_p{ctx.get('page_number', 1)}"
            )
            text = str(
                ctx.get("text") or ctx.get("content") or ctx.get("excerpt") or ""
            )
            passages.append((cid, text.lower()))
        else:
            cid = str(getattr(ctx, "chunk_id", getattr(ctx, "id", f"chunk_{idx + 1}")))
            text = str(
                getattr(
                    ctx, "text", getattr(ctx, "content", getattr(ctx, "excerpt", ""))
                )
            )
            passages.append((cid, text.lower()))
    return passages


def _stem(token: str) -> str:
    """Compute base root prefix for stemming inflections (e.g. written/writing)."""
    t = token.lower().strip(".,!?;:\"'()[]")
    for suffix in ("ing", "tion", "ment", "ance", "ence", "ed", "es", "s", "al", "ly"):
        if t.endswith(suffix) and len(t) - len(suffix) >= 3:
            return t[: -len(suffix)]
    return t


def _extract_keywords(text: str) -> list[str]:
    """Extract alphanumeric keywords and numeric tokens from text excluding stopwords."""
    raw_tokens = TOKEN_SPLIT_REGEX.findall(text.lower())
    return [
        t for t in raw_tokens if (len(t) >= 2 or t.isdigit()) and t not in STOPWORDS
    ]


class RAGASFaithfulnessEvaluator:
    """Evaluates context-to-answer faithfulness under the RAGAS framework."""

    @classmethod
    def verify_statement(
        cls,
        statement: str,
        contexts: Sequence[str | dict[str, Any] | Any],
        is_out_of_corpus: bool = False,
    ) -> StatementVerification:
        """Verify if a discrete factual statement is supported by retrieved context passages."""
        stmt_lower = statement.lower().strip()

        if (
            NO_CONTEXT_REFUSAL_CLEAN in stmt_lower
            or NO_CONTEXT_REFUSAL.lower() in stmt_lower
        ):
            is_faithful = is_out_of_corpus or not contexts
            return StatementVerification(
                statement=statement,
                is_faithful=is_faithful,
                reason=(
                    "Valid grounded refusal for ungrounded/out-of-corpus query"
                    if is_faithful
                    else "Unprompted refusal when factual context is present"
                ),
                supporting_chunk_id=None,
                matched_keywords=["refusal"] if is_faithful else [],
            )

        passages = _extract_context_passages(contexts)
        if not passages:
            return StatementVerification(
                statement=statement,
                is_faithful=False,
                reason="No context passages provided for verification",
                supporting_chunk_id=None,
                matched_keywords=[],
            )

        keywords = _extract_keywords(statement)
        if not keywords:
            return StatementVerification(
                statement=statement,
                is_faithful=True,
                reason="Statement contains no substantive factual claims",
                supporting_chunk_id=passages[0][0] if passages else None,
                matched_keywords=[],
            )

        best_chunk_id: str | None = None
        best_matched: list[str] = []
        best_overlap_ratio = 0.0

        for chunk_id, passage_text in passages:
            passage_words = set(_extract_keywords(passage_text))
            passage_stems = {_stem(w) for w in passage_words}

            matched: list[str] = []
            for kw in keywords:
                kw_stem = _stem(kw)
                if (
                    kw in passage_text
                    or kw in passage_words
                    or kw_stem in passage_stems
                ):
                    matched.append(kw)

            overlap_ratio = len(matched) / len(keywords) if keywords else 1.0
            if overlap_ratio > best_overlap_ratio:
                best_overlap_ratio = overlap_ratio
                best_chunk_id = chunk_id
                best_matched = matched

        is_faithful = best_overlap_ratio >= 0.40 or (
            len(best_matched) >= 3 and best_overlap_ratio >= 0.30
        )
        reason = (
            f"Supported with {best_overlap_ratio:.1%} keyword overlap in chunk {best_chunk_id}"
            if is_faithful
            else f"Unsupported (only {best_overlap_ratio:.1%} overlap in context)"
        )

        return StatementVerification(
            statement=statement,
            is_faithful=is_faithful,
            reason=reason,
            supporting_chunk_id=best_chunk_id if is_faithful else None,
            matched_keywords=best_matched,
        )

    @classmethod
    def evaluate_answer(
        cls,
        query: str,
        answer: str,
        contexts: Sequence[str | dict[str, Any] | Any],
        is_out_of_corpus: bool = False,
        query_id: str = "eval",
        category: str = "general",
        min_threshold: float = 0.85,
    ) -> FaithfulnessQueryResult:
        """Evaluate full answer faithfulness by decomposing into statements and verifying."""
        statements = StatementExtractor.extract_statements(answer)
        raw_contexts = [text for _, text in _extract_context_passages(contexts)]

        if not statements:
            score = 1.0 if is_out_of_corpus else 0.0
            return FaithfulnessQueryResult(
                query_id=query_id,
                query=query,
                generated_answer=answer,
                contexts=raw_contexts,
                faithfulness_score=score,
                is_faithful=(score >= min_threshold),
                is_out_of_corpus=is_out_of_corpus,
                is_refusal=is_out_of_corpus,
                category=category,
            )

        verifications = [
            cls.verify_statement(
                statement=s, contexts=contexts, is_out_of_corpus=is_out_of_corpus
            )
            for s in statements
        ]
        verified_count = sum(1 for v in verifications if v.is_faithful)
        total_count = len(statements)
        score = float(verified_count) / float(total_count) if total_count > 0 else 0.0
        is_refusal = (
            NO_CONTEXT_REFUSAL_CLEAN in answer.lower()
            or NO_CONTEXT_REFUSAL.lower() in answer.lower()
        )

        return FaithfulnessQueryResult(
            query_id=query_id,
            query=query,
            generated_answer=answer,
            contexts=raw_contexts,
            statements=statements,
            verifications=verifications,
            verified_statements_count=verified_count,
            total_statements_count=total_count,
            faithfulness_score=round(score, 4),
            is_faithful=(score >= min_threshold),
            is_out_of_corpus=is_out_of_corpus,
            is_refusal=is_refusal,
            category=category,
        )
