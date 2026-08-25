"""Markdown parser with YAML frontmatter and structural metadata extraction."""

import re
from pathlib import Path
from typing import Any

import yaml  # type: ignore

from core.exceptions import IngestionError
from ingestion.base import BaseDocumentParser
from models.document import DocumentMetadata, PageMetadata, ParsedDocument, ParsedPage

PAGE_BREAK_PATTERN = re.compile(r"(?i)<!--\s*page_?break\s*-->|\\pagebreak|\\newpage")
IMAGE_PATTERN = re.compile(r"!\[.*?\]\(.*?\)|<img\s+[^>]*>", re.IGNORECASE)
HEADER_TITLE_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)


class MarkdownParser(BaseDocumentParser):
    """Parser for Markdown (.md) documents with YAML frontmatter extraction."""

    def parse(self, file_path: str | Path) -> ParsedDocument:
        """Parse Markdown file into structured document with pages and metadata."""
        path = Path(file_path).resolve()
        if not path.exists() or not path.is_file():
            raise IngestionError(
                f"Markdown file does not exist: {path}",
                code="FILE_NOT_FOUND",
                details={"file_path": str(path)},
            )
        if path.stat().st_size == 0:
            raise IngestionError(
                f"Markdown file is empty (0 bytes): {path}",
                code="EMPTY_FILE",
                details={"file_path": str(path)},
            )

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            raise IngestionError(
                f"Failed to read Markdown file: {e}",
                code="MARKDOWN_PARSING_ERROR",
                details={"file_path": str(path), "error": str(e)},
            ) from e

        try:
            frontmatter, body = self._extract_frontmatter(content, path)
            return self._build_parsed_document(path, frontmatter, body)
        except Exception as e:
            if isinstance(e, IngestionError):
                raise
            raise IngestionError(
                f"Error parsing Markdown data: {e}",
                code="MARKDOWN_PARSING_ERROR",
                details={"file_path": str(path), "error": str(e)},
            ) from e

    def _extract_frontmatter(
        self, content: str, path: Path
    ) -> tuple[dict[str, Any], str]:
        """Extract YAML frontmatter block and remaining Markdown body."""
        if not content.startswith("---"):
            return {}, content.strip()

        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content.strip()

        fm_str = parts[1].strip()
        body = parts[2].strip()

        if not fm_str:
            return {}, body

        try:
            parsed_fm = yaml.safe_load(fm_str)
            if not isinstance(parsed_fm, dict):
                return {}, body
            return parsed_fm, body
        except Exception as e:
            raise IngestionError(
                f"Invalid YAML frontmatter format: {e}",
                code="MARKDOWN_PARSING_ERROR",
                details={"file_path": str(path), "error": str(e)},
            ) from e

    def _build_parsed_document(
        self, path: Path, fm: dict[str, Any], body: str
    ) -> ParsedDocument:
        """Construct ParsedDocument with page metadata and document metadata."""
        title = self._get_str(fm, "title")
        if not title:
            match = HEADER_TITLE_PATTERN.search(body)
            if match:
                title = match.group(1).strip()

        keywords = fm.get("keywords")
        keywords_str: str | None
        if isinstance(keywords, list):
            keywords_str = ", ".join(str(k) for k in keywords)
        else:
            keywords_str = self._get_str(fm, "keywords")

        doc_meta = DocumentMetadata(
            title=title,
            author=self._get_str(fm, "author"),
            subject=self._get_str(fm, "subject"),
            keywords=keywords_str,
            creator=self._get_str(fm, "creator"),
            producer=self._get_str(fm, "producer"),
            creation_date=self._get_str(fm, "creation_date")
            or self._get_str(fm, "date"),
            mod_date=self._get_str(fm, "mod_date"),
            total_pages=0,
            file_size_bytes=path.stat().st_size,
        )

        raw_pages = PAGE_BREAK_PATTERN.split(body) if body else [""]
        pages: list[ParsedPage] = []

        for idx, page_text in enumerate(raw_pages, start=1):
            txt = page_text.strip()
            words = txt.split()
            img_count = len(IMAGE_PATTERN.findall(txt))
            tbl_count = self._count_tables(txt)

            page_meta = PageMetadata(
                page_number=idx,
                width=612.0,
                height=792.0,
                rotation=0,
                char_count=len(txt),
                word_count=len(words),
                image_count=img_count,
                table_count=tbl_count,
            )
            pages.append(ParsedPage(page_number=idx, text=txt, metadata=page_meta))

        doc_meta_final = doc_meta.model_copy(update={"total_pages": len(pages)})

        return ParsedDocument(
            file_name=path.name,
            file_path=str(path),
            source_format="md",
            doc_metadata=doc_meta_final,
            pages=pages,
        )

    def _count_tables(self, text: str) -> int:
        """Count Markdown formatted table blocks in text."""
        lines = text.splitlines()
        table_count = 0
        in_table = False
        for line in lines:
            stripped = line.strip()
            if (
                stripped.startswith("|")
                and stripped.endswith("|")
                and len(stripped) > 2
            ):
                if not in_table:
                    in_table = True
                    table_count += 1
            else:
                in_table = False
        return table_count

    def _get_str(self, fm: dict[str, Any], key: str) -> str | None:
        """Safely extract non-empty string value from dictionary key."""
        val = fm.get(key)
        if val is not None:
            s_val = str(val).strip()
            return s_val if s_val else None
        return None
