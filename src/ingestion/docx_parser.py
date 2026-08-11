"""DOCX document parser using python-docx with structural metadata extraction."""

from pathlib import Path
from typing import Any

import docx
from docx.document import Document as DocxDocument
from docx.enum.section import WD_ORIENTATION
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from core.exceptions import IngestionError
from ingestion.base import BaseDocumentParser
from models.document import DocumentMetadata, PageMetadata, ParsedDocument, ParsedPage


class DOCXParser(BaseDocumentParser):
    """Parser for DOCX files using python-docx with structural metadata."""

    def parse(self, file_path: str | Path) -> ParsedDocument:
        """Parse DOCX file into structured document with pages and metadata."""
        path = Path(file_path).resolve()
        if not path.exists() or not path.is_file():
            raise IngestionError(
                f"DOCX file does not exist: {path}",
                code="FILE_NOT_FOUND",
                details={"file_path": str(path)},
            )
        if path.stat().st_size == 0:
            raise IngestionError(
                f"DOCX file is empty (0 bytes): {path}",
                code="EMPTY_FILE",
                details={"file_path": str(path)},
            )

        try:
            doc = docx.Document(str(path))
        except Exception as e:
            raise IngestionError(
                f"Failed to open DOCX file: {e}",
                code="DOCX_PARSING_ERROR",
                details={"file_path": str(path), "error": str(e)},
            ) from e

        try:
            return self._extract_parsed_document(path, doc)
        except Exception as e:
            if isinstance(e, IngestionError):
                raise
            raise IngestionError(
                f"Error extracting DOCX data: {e}",
                code="DOCX_PARSING_ERROR",
                details={"file_path": str(path), "error": str(e)},
            ) from e

    def _extract_parsed_document(self, path: Path, doc: DocxDocument) -> ParsedDocument:
        core: Any = doc.core_properties
        creator_val = getattr(core, "creator", None)
        doc_meta = DocumentMetadata(
            title=str(core.title) if core.title else None,
            author=str(core.author) if core.author else None,
            subject=str(core.subject) if core.subject else None,
            keywords=str(core.keywords) if core.keywords else None,
            creator=str(creator_val) if creator_val else None,
            producer=str(core.last_modified_by) if core.last_modified_by else None,
            creation_date=core.created.isoformat() if core.created else None,
            mod_date=core.modified.isoformat() if core.modified else None,
            total_pages=0,
            file_size_bytes=path.stat().st_size,
        )

        sec = doc.sections[0] if doc.sections else None
        def_width = (
            float(sec.page_width.pt) if sec and sec.page_width is not None else 612.0
        )
        def_height = (
            float(sec.page_height.pt) if sec and sec.page_height is not None else 792.0
        )
        def_rot = 90 if sec and sec.orientation == WD_ORIENTATION.LANDSCAPE else 0

        pages: list[ParsedPage] = []
        cur_text: list[str] = []
        cur_img = 0
        cur_tbl = 0

        def flush_page() -> None:
            nonlocal cur_text, cur_img, cur_tbl
            txt = "\n\n".join(cur_text).strip()
            words = txt.split()
            pg_num = len(pages) + 1
            meta = PageMetadata(
                page_number=pg_num,
                width=def_width,
                height=def_height,
                rotation=def_rot,
                char_count=len(txt),
                word_count=len(words),
                image_count=cur_img,
                table_count=cur_tbl,
            )
            pages.append(ParsedPage(page_number=pg_num, text=txt, metadata=meta))
            cur_text = []
            cur_img = 0
            cur_tbl = 0

        for child in doc.element.body:
            if isinstance(child, CT_P):
                p = Paragraph(child, doc)
                if self._has_page_break_before(p) and cur_text:
                    flush_page()

                cur_img += len(
                    p._element.xpath('.//*[local-name()="blip" or local-name()="pict"]')
                )
                formatted = self._format_paragraph(p)
                if formatted:
                    cur_text.append(formatted)

                if self._has_page_break_after(p) and cur_text:
                    flush_page()

            elif isinstance(child, CT_Tbl):
                tbl = Table(child, doc)
                cur_tbl += 1
                cur_img += len(
                    tbl._element.xpath(
                        './/*[local-name()="blip" or local-name()="pict"]'
                    )
                )
                tbl_txt = self._format_table(tbl)
                if tbl_txt:
                    cur_text.append(tbl_txt)

        if cur_text or not pages:
            flush_page()

        final_meta = doc_meta.model_copy(update={"total_pages": len(pages)})
        return ParsedDocument(
            file_name=path.name,
            file_path=str(path),
            source_format="docx",
            doc_metadata=final_meta,
            pages=pages,
        )

    def _has_page_break_before(self, p: Paragraph) -> bool:
        return bool(p.paragraph_format.page_break_before)

    def _has_page_break_after(self, p: Paragraph) -> bool:
        xml = p._element.xml
        return (
            'w:type="page"' in xml
            or "w:lastRenderedPageBreak" in xml
            or ("w:br" in xml and 'type="page"' in xml)
        )

    def _format_paragraph(self, p: Paragraph) -> str:
        text = p.text.strip()
        if not text:
            return ""
        style_name = p.style.name if p.style else ""
        if style_name.startswith("Heading"):
            try:
                level = int(style_name.replace("Heading", "").strip())
                prefix = "#" * max(1, min(level, 6))
                return f"{prefix} {text}"
            except ValueError:
                return f"# {text}"
        if style_name in ("Title", "Subtitle"):
            prefix = "#" if style_name == "Title" else "##"
            return f"{prefix} {text}"
        return text

    def _format_table(self, table: Table) -> str:
        rows_text: list[str] = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                rows_text.append(" | ".join(cells))
        return "\n".join(rows_text)
