"""Unit tests for citation extraction and validation logic."""

import pytest

from core.exceptions import GenerationError
from generation.citations import (
    CITATION_REGEX,
    CitationExtractor,
    CitationValidationResult,
    CitationValidator,
    RawCitation,
)
from models.chat import Citation


def test_citation_regex_matching() -> None:
    """Verify CITATION_REGEX accurately identifies valid inline citation tags."""
    sample = "Helvetia achieved record growth [Doc: annual_report_2025.pdf | Page: 14] in Q3."
    matches = CITATION_REGEX.findall(sample)
    assert len(matches) == 1
    assert matches[0] == ("annual_report_2025.pdf", "14")


def test_raw_citation_extraction() -> None:
    """Verify CitationExtractor.extract_raw parses tags with spacing and deduplication."""
    text = (
        "According to policy [Doc: policy.pdf | Page: 3], claims are processed within 24h. "
        "Further details in [Doc: policy.pdf | Page: 3] and [doc: appendix.docx | page: 12]."
    )
    raws = CitationExtractor.extract_raw(text)
    assert len(raws) == 2
    assert raws[0] == RawCitation(file_name="policy.pdf", page_number=3)
    assert raws[1] == RawCitation(file_name="appendix.docx", page_number=12)


def test_extract_citations_with_context() -> None:
    """Verify CitationExtractor.extract_citations maps raw tags to context metadata."""
    text = "Revenue grew by 15% [Doc: financials.pdf | Page: 5]."
    contexts = [
        {
            "file_name": "financials.pdf",
            "page_number": 5,
            "chunk_id": "chunk_fin_5",
            "excerpt": "Revenue grew by 15% year over year.",
            "relevance_score": 0.95,
        }
    ]
    citations = CitationExtractor.extract_citations(text, contexts)
    assert len(citations) == 1
    assert citations[0].file_name == "financials.pdf"
    assert citations[0].page_number == 5
    assert citations[0].chunk_id == "chunk_fin_5"
    assert citations[0].excerpt == "Revenue grew by 15% year over year."
    assert citations[0].relevance_score == 0.95


def test_validator_all_valid() -> None:
    """Verify CitationValidator reports 100% accuracy when all citations match context."""
    text = "Facts from [Doc: doc_a.pdf | Page: 1] and [Doc: doc_b.pdf | Page: 2]."
    contexts = [
        {"file_name": "doc_a.pdf", "page_number": 1, "chunk_id": "c1", "excerpt": "a"},
        {"file_name": "doc_b.pdf", "page_number": 2, "chunk_id": "c2", "excerpt": "b"},
    ]
    res = CitationValidator.validate(text, contexts)
    assert isinstance(res, CitationValidationResult)
    assert res.is_valid is True
    assert res.citation_accuracy == 1.0
    assert len(res.valid_citations) == 2
    assert len(res.invalid_citations) == 0


def test_validator_partial_invalid() -> None:
    """Verify CitationValidator detects hallucinated/unmatched citations."""
    text = "Valid [Doc: real.pdf | Page: 1] and Fake [Doc: fake.pdf | Page: 99]."
    contexts = [
        {"file_name": "real.pdf", "page_number": 1, "chunk_id": "c1", "excerpt": "real"}
    ]
    res = CitationValidator.validate(text, contexts)
    assert res.is_valid is False
    assert res.citation_accuracy == 0.5
    assert len(res.valid_citations) == 1
    assert len(res.invalid_citations) == 1
    assert res.invalid_citations[0].file_name == "fake.pdf"
    assert res.invalid_citations[0].page_number == 99


def test_validator_no_citations() -> None:
    """Verify CitationValidator handles text with no citations gracefully."""
    text = "I cannot answer this question based on the available documentation."
    res = CitationValidator.validate(text, contexts=[])
    assert res.is_valid is True
    assert res.citation_accuracy == 1.0
    assert len(res.valid_citations) == 0
    assert len(res.invalid_citations) == 0


def test_validator_citation_object_input() -> None:
    """Verify CitationValidator accepts Sequence[Citation] as input."""
    citations = [
        Citation(
            file_name="real.pdf",
            page_number=1,
            chunk_id="c1",
            excerpt="ex",
            relevance_score=0.9,
        )
    ]
    contexts = [
        {"file_name": "real.pdf", "page_number": 1, "chunk_id": "c1", "excerpt": "ex"}
    ]
    res = CitationValidator.validate(citations, contexts)
    assert res.is_valid is True
    assert res.citation_accuracy == 1.0
    assert len(res.valid_citations) == 1


def test_verify_document_presence() -> None:
    """Verify verify_document_presence accurately checks context document matches."""
    contexts = [
        {"file_name": "report_2025.pdf", "page_number": 4, "chunk_id": "c4"}
    ]
    assert CitationValidator.verify_document_presence("report_2025.pdf", 4, contexts) is True
    assert CitationValidator.verify_document_presence("REPORT_2025.PDF", 4, contexts) is True
    assert CitationValidator.verify_document_presence("report_2025.pdf", 99, contexts) is False
    assert CitationValidator.verify_document_presence("missing.pdf", 4, contexts) is False


def test_verify_grounding() -> None:
    """Verify verify_grounding returns boolean grounding status."""
    contexts = [
        {"file_name": "doc1.pdf", "page_number": 1, "chunk_id": "c1"}
    ]
    valid_text = "Good text [Doc: doc1.pdf | Page: 1]."
    invalid_text = "Bad text [Doc: doc2.pdf | Page: 2]."
    assert CitationValidator.verify_grounding(valid_text, contexts) is True
    assert CitationValidator.verify_grounding(invalid_text, contexts) is False


def test_filter_invalid_citations() -> None:
    """Verify filter_invalid_citations removes hallucinated tags from text."""
    contexts = [
        {"file_name": "real.pdf", "page_number": 1, "chunk_id": "c1"}
    ]
    text = "Fact A [Doc: real.pdf | Page: 1] and Fact B [Doc: fake.pdf | Page: 2]."
    cleaned_text, valid_cites = CitationValidator.filter_invalid_citations(text, contexts)
    assert "[Doc: fake.pdf | Page: 2]" not in cleaned_text
    assert "[Doc: real.pdf | Page: 1]" in cleaned_text
    assert len(valid_cites) == 1
    assert valid_cites[0].file_name == "real.pdf"


def test_validate_strict_mode_raises() -> None:
    """Verify validate with strict=True raises GenerationError on invalid citations."""
    contexts = [
        {"file_name": "real.pdf", "page_number": 1, "chunk_id": "c1"}
    ]
    invalid_text = "Invalid claim [Doc: fake.pdf | Page: 99]."
    with pytest.raises(GenerationError) as exc_info:
        CitationValidator.validate(invalid_text, contexts, strict=True)

    assert "Citation validation failed" in exc_info.value.message
    assert exc_info.value.code == "CITATION_VALIDATION_ERROR"
    assert "invalid_citations" in exc_info.value.details
