"""Unit tests for Markdown document parser and frontmatter extraction."""

from pathlib import Path

import pytest

from core.exceptions import IngestionError
from ingestion.markdown_parser import MarkdownParser
from models.document import ParsedDocument


@pytest.fixture
def sample_md_with_frontmatter(tmp_path: Path) -> Path:
    """Create temporary Markdown file with YAML frontmatter, headers, tables, and page breaks."""
    md_path = tmp_path / "sample.md"
    content = """---
title: Corporate AI Strategy
author: AI Engineering Team
subject: System Architecture
keywords:
  - RAG
  - Vector Database
  - Markdown
creation_date: "2026-08-11"
---

# Corporate AI Strategy Overview

This document defines the high-level design of the corporate RAG assistant.

![Architecture Diagram](https://example.com/diag.png)

| Layer | Component |
| --- | --- |
| Parser | MarkdownParser |
| Model | Pydantic V2 |

<!-- pagebreak -->

# Page 2: Implementation Details

Detailed technical documentation for frontmatter extraction and sectioning.
"""
    md_path.write_text(content, encoding="utf-8")
    return md_path


@pytest.fixture
def sample_md_without_frontmatter(tmp_path: Path) -> Path:
    """Create temporary Markdown file without YAML frontmatter."""
    md_path = tmp_path / "no_fm.md"
    content = """# Fallback Title From Header

Standard markdown content without any frontmatter block.
"""
    md_path.write_text(content, encoding="utf-8")
    return md_path


def test_markdown_parser_success_with_frontmatter(
    sample_md_with_frontmatter: Path,
) -> None:
    """Verify MarkdownParser extracts frontmatter, tables, images, and handles page breaks."""
    parser = MarkdownParser()
    parsed: ParsedDocument = parser.parse(sample_md_with_frontmatter)

    assert parsed.file_name == "sample.md"
    assert parsed.source_format == "md"
    assert parsed.doc_metadata.title == "Corporate AI Strategy"
    assert parsed.doc_metadata.author == "AI Engineering Team"
    assert parsed.doc_metadata.subject == "System Architecture"
    assert parsed.doc_metadata.keywords == "RAG, Vector Database, Markdown"
    assert parsed.doc_metadata.total_pages == 2
    assert len(parsed.pages) == 2

    # Page 1 checks
    p1 = parsed.pages[0]
    assert p1.page_number == 1
    assert "Corporate AI Strategy Overview" in p1.text
    assert p1.metadata.image_count == 1
    assert p1.metadata.table_count == 1
    assert p1.metadata.word_count > 0

    # Page 2 checks
    p2 = parsed.pages[1]
    assert p2.page_number == 2
    assert "Page 2: Implementation Details" in p2.text


def test_markdown_parser_without_frontmatter(
    sample_md_without_frontmatter: Path,
) -> None:
    """Verify MarkdownParser extracts title from first level-1 heading when frontmatter is absent."""
    parser = MarkdownParser()
    parsed: ParsedDocument = parser.parse(sample_md_without_frontmatter)

    assert parsed.doc_metadata.title == "Fallback Title From Header"
    assert parsed.doc_metadata.author is None
    assert parsed.doc_metadata.total_pages == 1
    assert len(parsed.pages) == 1
    assert "Standard markdown content" in parsed.pages[0].text


def test_markdown_parser_nonexistent_file(tmp_path: Path) -> None:
    """Verify IngestionError is raised for non-existent Markdown file path."""
    parser = MarkdownParser()
    missing_file = tmp_path / "missing.md"
    with pytest.raises(IngestionError) as exc_info:
        parser.parse(missing_file)
    assert exc_info.value.code == "FILE_NOT_FOUND"


def test_markdown_parser_empty_file(tmp_path: Path) -> None:
    """Verify IngestionError is raised for empty 0-byte Markdown file."""
    empty_file = tmp_path / "empty.md"
    empty_file.write_bytes(b"")
    parser = MarkdownParser()
    with pytest.raises(IngestionError) as exc_info:
        parser.parse(empty_file)
    assert exc_info.value.code == "EMPTY_FILE"


def test_markdown_parser_invalid_frontmatter(tmp_path: Path) -> None:
    """Verify IngestionError is raised for malformed invalid YAML frontmatter."""
    corrupt_file = tmp_path / "invalid_fm.md"
    corrupt_file.write_text(
        "---\ntitle: [invalid yaml\n---\nBody text", encoding="utf-8"
    )
    parser = MarkdownParser()
    with pytest.raises(IngestionError) as exc_info:
        parser.parse(corrupt_file)
    assert exc_info.value.code == "MARKDOWN_PARSING_ERROR"
