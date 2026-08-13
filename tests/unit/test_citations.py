"""Unit tests for citation extraction and validation logic."""

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
