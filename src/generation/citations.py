"""Citation extraction and validation logic for inline document references."""

import re
from collections.abc import Sequence
from typing import Any

import structlog
from pydantic import Field

from core.exceptions import GenerationError
from models.base import BaseDomainModel
from models.chat import Citation

logger = structlog.get_logger(__name__)

CITATION_REGEX = re.compile(
    r"\[Doc:\s*([^|\]]+?)\s*\|\s*Page:\s*(\d+)\s*\]", re.IGNORECASE
)


class RawCitation(BaseDomainModel):
    """Raw parsed inline citation tag from text."""

    file_name: str = Field(..., description="Parsed file name")
    page_number: int = Field(..., ge=1, description="Parsed 1-indexed page number")


class CitationValidationResult(BaseDomainModel):
    """Validation report payload comparing extracted citations against context."""

    is_valid: bool = Field(..., description="True if all citations are grounded")
    citation_accuracy: float = Field(
        ..., ge=0.0, le=1.0, description="Ratio of valid to total citations"
    )
    valid_citations: list[Citation] = Field(
        default_factory=list, description="Successfully matched citations"
    )
    invalid_citations: list[RawCitation] = Field(
        default_factory=list, description="Citations missing from context"
    )


class CitationExtractor:
    """Extractor for parsing inline citation tags from LLM completions."""

    @staticmethod
    def extract_raw(text: str) -> list[RawCitation]:
        """Extract raw inline document and page citation targets from text."""
        matches = CITATION_REGEX.findall(text)
        citations: list[RawCitation] = []
        seen: set[tuple[str, int]] = set()

        for doc_name, page_str in matches:
            file_name = doc_name.strip()
            try:
                page_num = int(page_str.strip())
            except ValueError:
                continue

            key = (file_name.lower(), page_num)
            if key not in seen and page_num >= 1:
                seen.add(key)
                citations.append(RawCitation(file_name=file_name, page_number=page_num))

        return citations

    @staticmethod
    def _extract_context_meta(ctx: Any) -> tuple[str, int, str, str, float]:
        """Extract normalized file_name, page_number, chunk_id, excerpt, and score."""
        if isinstance(ctx, dict):
            file_name = str(ctx.get("file_name") or ctx.get("source_file") or "")
            raw_page = (
                ctx.get("page_number")
                if ctx.get("page_number") is not None
                else ctx.get("page", 1)
            )
            try:
                page_num = int(raw_page) if raw_page is not None else 1
            except (ValueError, TypeError):
                page_num = 1
            chunk_id = str(
                ctx.get("chunk_id") or ctx.get("id") or f"{file_name}_p{page_num}"
            )
            excerpt = str(
                ctx.get("excerpt") or ctx.get("text") or ctx.get("content") or ""
            )
            try:
                score = float(ctx.get("relevance_score") or ctx.get("score") or 1.0)
            except (ValueError, TypeError):
                score = 1.0
        else:
            file_name = str(getattr(ctx, "file_name", getattr(ctx, "source_file", "")))
            raw_page = getattr(ctx, "page_number", getattr(ctx, "page", 1))
            try:
                page_num = int(raw_page) if raw_page is not None else 1
            except (ValueError, TypeError):
                page_num = 1
            chunk_id = str(
                getattr(
                    ctx,
                    "chunk_id",
                    getattr(ctx, "id", f"{file_name}_p{page_num}"),
                )
            )
            excerpt = str(
                getattr(
                    ctx,
                    "excerpt",
                    getattr(ctx, "text", getattr(ctx, "content", "")),
                )
            )
            try:
                score = float(
                    getattr(ctx, "relevance_score", getattr(ctx, "score", 1.0))
                )
            except (ValueError, TypeError):
                score = 1.0

        return file_name.strip(), page_num, chunk_id, excerpt, score

    @classmethod
    def extract_citations(cls, text: str, contexts: Sequence[Any]) -> list[Citation]:
        """Extract inline citations from text and resolve against context blocks."""
        raw_list = cls.extract_raw(text)
        resolved: list[Citation] = []

        for raw in raw_list:
            for ctx in contexts:
                f_name, p_num, c_id, excerpt, score = cls._extract_context_meta(ctx)
                if f_name.lower() == raw.file_name.lower() and p_num == raw.page_number:
                    resolved.append(
                        Citation(
                            file_name=f_name,
                            page_number=p_num,
                            chunk_id=c_id,
                            excerpt=excerpt,
                            relevance_score=score,
                        )
                    )
                    break

        return resolved


class CitationValidator:
    """Validator verifying whether extracted inline citations exist in context."""

    @classmethod
    def verify_document_presence(
        cls, file_name: str, page_number: int, contexts: Sequence[Any]
    ) -> bool:
        """Check if target document and page exist within retrieved context blocks."""
        target_doc = file_name.strip().lower()
        for ctx in contexts:
            f_name, p_num, _, _, _ = CitationExtractor._extract_context_meta(ctx)
            if f_name.lower() == target_doc and p_num == page_number:
                return True
        return False

    @classmethod
    def verify_grounding(cls, text: str, contexts: Sequence[Any]) -> bool:
        """Check whether all inline citations in completion text exist in context."""
        res = cls.validate(text, contexts)
        return res.is_valid

    @classmethod
    def filter_invalid_citations(
        cls, text: str, contexts: Sequence[Any]
    ) -> tuple[str, list[Citation]]:
        """Filter out ungrounded citation tags from text and return valid citations."""
        res = cls.validate(text, contexts)
        if res.is_valid:
            return text, res.valid_citations

        invalid_map = {
            (inv.file_name.lower(), inv.page_number) for inv in res.invalid_citations
        }

        def _replacer(match: re.Match[str]) -> str:
            doc_name = match.group(1).strip()
            try:
                p_num = int(match.group(2).strip())
            except ValueError:
                return match.group(0)
            if (doc_name.lower(), p_num) in invalid_map:
                return ""
            return match.group(0)

        cleaned_text = CITATION_REGEX.sub(_replacer, text)
        cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text).strip()
        return cleaned_text, res.valid_citations

    @classmethod
    def validate(
        cls,
        text_or_citations: str | Sequence[Citation],
        contexts: Sequence[Any],
        strict: bool = False,
    ) -> CitationValidationResult:
        """Validate inline citations against context list, optionally raising on failure."""
        if isinstance(text_or_citations, str):
            raw_citations = CitationExtractor.extract_raw(text_or_citations)
        else:
            raw_citations = [
                RawCitation(file_name=c.file_name, page_number=c.page_number)
                for c in text_or_citations
            ]

        if not raw_citations:
            return CitationValidationResult(
                is_valid=True,
                citation_accuracy=1.0,
                valid_citations=[],
                invalid_citations=[],
            )

        context_metas = [
            CitationExtractor._extract_context_meta(ctx) for ctx in contexts
        ]

        valid: list[Citation] = []
        invalid: list[RawCitation] = []

        for raw in raw_citations:
            matched = False
            for f_name, p_num, c_id, excerpt, score in context_metas:
                if f_name.lower() == raw.file_name.lower() and p_num == raw.page_number:
                    valid.append(
                        Citation(
                            file_name=f_name,
                            page_number=p_num,
                            chunk_id=c_id,
                            excerpt=excerpt,
                            relevance_score=score,
                        )
                    )
                    matched = True
                    break
            if not matched:
                invalid.append(raw)

        total = len(raw_citations)
        accuracy = len(valid) / total if total > 0 else 1.0
        is_valid = len(invalid) == 0

        result = CitationValidationResult(
            is_valid=is_valid,
            citation_accuracy=round(accuracy, 4),
            valid_citations=valid,
            invalid_citations=invalid,
        )

        if strict and not is_valid:
            logger.warning(
                "Citation validation failed in strict mode",
                invalid_count=len(invalid),
                accuracy=accuracy,
            )
            raise GenerationError(
                f"Citation validation failed: {len(invalid)} ungrounded citation(s) detected",
                code="CITATION_VALIDATION_ERROR",
                details={
                    "invalid_citations": [inv.model_dump() for inv in invalid],
                    "citation_accuracy": result.citation_accuracy,
                },
            )

        return result
