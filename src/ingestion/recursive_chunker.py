"""Recursive structural text chunker for RAG document ingestion."""

import uuid
from collections.abc import Sequence

from core.exceptions import IngestionError
from models.chunk import ChunkDocument, ChunkMetadata
from models.document import ParsedDocument


class RecursiveStructuralChunker:
    """Recursive structural text chunker with page boundary preservation."""

    def __init__(
        self,
        max_tokens: int = 512,
        overlap_percentage: float = 0.10,
        separators: Sequence[str] | None = None,
    ) -> None:
        """Initialize chunker with token limit, overlap ratio, and separators."""
        if max_tokens <= 0:
            raise IngestionError(
                "max_tokens must be greater than 0",
                code="INVALID_CHUNKER_PARAM",
                details={"max_tokens": max_tokens},
            )
        if not (0.0 <= overlap_percentage < 1.0):
            raise IngestionError(
                "overlap_percentage must be between 0.0 and 1.0",
                code="INVALID_CHUNKER_PARAM",
                details={"overlap_percentage": overlap_percentage},
            )

        self.max_tokens = max_tokens
        self.overlap_percentage = overlap_percentage
        self.overlap_tokens = int(max_tokens * overlap_percentage)
        self.separators: list[str] = list(
            separators if separators is not None else ["\n\n", "\n", ". ", " ", ""]
        )

    def count_tokens(self, text: str) -> int:
        """Calculate token count with fallback for offline execution environments."""
        if not text:
            return 0
        try:
            import tiktoken

            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except Exception:
            words = text.split()
            word_est = max(1, int(len(words) * 1.3)) if words else 0
            char_est = max(1, (len(text) + 3) // 4)
            return max(word_est, char_est)

    def chunk_document(self, document: ParsedDocument) -> list[ChunkDocument]:
        """Chunk ParsedDocument while strictly preserving page boundaries."""
        try:
            raw_chunks: list[tuple[str, int]] = []
            for page in document.pages:
                page_text_chunks = self.chunk_page_text(page.text)
                for text_chunk in page_text_chunks:
                    raw_chunks.append((text_chunk, page.page_number))

            total_chunks = len(raw_chunks)
            chunks: list[ChunkDocument] = []
            for idx, (text_chunk, page_num) in enumerate(raw_chunks):
                token_count = self.count_tokens(text_chunk)
                unique_hash = uuid.uuid4().hex[:6]
                chunk_id = f"{document.file_name}_p{page_num}_c{idx}_{unique_hash}"
                meta = ChunkMetadata(
                    source_format=document.source_format,
                    chunk_index=idx,
                    total_chunks=max(1, total_chunks),
                    char_count=len(text_chunk),
                    token_count=token_count,
                )
                chunk_doc = ChunkDocument(
                    chunk_id=chunk_id,
                    text=text_chunk,
                    file_name=document.file_name,
                    page_number=page_num,
                    metadata=meta,
                )
                chunks.append(chunk_doc)
            return chunks
        except Exception as err:
            if isinstance(err, IngestionError):
                raise
            raise IngestionError(
                f"Failed to chunk document '{document.file_name}': {err}",
                details={"file_name": document.file_name},
            ) from err

    def chunk_page_text(self, text: str) -> list[str]:
        """Chunk a single page's text payload into structural blocks with overlap."""
        cleaned = text.strip()
        if not cleaned:
            return []
        if self.count_tokens(cleaned) <= self.max_tokens:
            return [cleaned]

        splits = self._recursive_split(cleaned, 0)
        return self._apply_overlap(splits)

    def _recursive_split(self, text: str, sep_idx: int) -> list[str]:
        """Recursively split text using separator priority hierarchy."""
        if self.count_tokens(text) <= self.max_tokens:
            return [text] if text.strip() else []

        if sep_idx >= len(self.separators):
            return self._hard_split(text)

        sep = self.separators[sep_idx]
        if sep == "":
            return self._hard_split(text)

        parts = text.split(sep)
        if len(parts) == 1:
            return self._recursive_split(text, sep_idx + 1)

        result: list[str] = []
        current: list[str] = []
        for part in parts:
            candidate = sep.join([*current, part]) if current else part
            if self.count_tokens(candidate) <= self.max_tokens:
                current.append(part)
            else:
                if current:
                    merged = sep.join(current)
                    if self.count_tokens(merged) <= self.max_tokens:
                        result.append(merged)
                    else:
                        result.extend(self._recursive_split(merged, sep_idx + 1))
                    current = []
                if self.count_tokens(part) <= self.max_tokens:
                    current.append(part)
                else:
                    result.extend(self._recursive_split(part, sep_idx + 1))

        if current:
            merged = sep.join(current)
            if self.count_tokens(merged) <= self.max_tokens:
                result.append(merged)
            else:
                result.extend(self._recursive_split(merged, sep_idx + 1))

        return [r for r in result if r.strip()]

    def _hard_split(self, text: str) -> list[str]:
        """Fallback slice for text blocks exceeding token limits without separators."""
        chunks: list[str] = []
        step = max(1, self.max_tokens * 3)
        for i in range(0, len(text), step):
            sub = text[i : i + step]
            if sub.strip():
                chunks.append(sub)
        return chunks

    def _apply_overlap(self, splits: list[str]) -> list[str]:
        """Prepend tail tokens from preceding split to enforce boundary overlap."""
        if not splits or self.overlap_tokens <= 0:
            return splits

        overlapped: list[str] = [splits[0]]
        for i in range(1, len(splits)):
            prev = splits[i - 1]
            curr = splits[i]
            prev_words = prev.split()
            overlap_words: list[str] = []
            for word in reversed(prev_words):
                candidate = " ".join([word, *overlap_words])
                if self.count_tokens(candidate) > self.overlap_tokens:
                    break
                overlap_words.insert(0, word)

            prefix = " ".join(overlap_words)
            if prefix and self.count_tokens(f"{prefix} {curr}") <= self.max_tokens:
                overlapped.append(f"{prefix} {curr}")
            else:
                overlapped.append(curr)

        return overlapped
