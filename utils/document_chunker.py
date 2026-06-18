"""Document Chunker Utility.

Provides recursive character text splitting and metadata management for document chunks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentChunk:
    """Represents a chunk of a document with its metadata."""

    chunk_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


class RecursiveTextSplitter:
    """Splits text recursively by character separators.

    Maintains chunk size and chunk overlap constraints.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: list[str] | None = None,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]

    def split_text(self, text: str) -> list[str]:
        """Splits the input text recursively using separators."""
        return self._split(text, self.separators)

    def _split(self, text: str, separators: list[str]) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        if not separators:
            # If no separators left, split character by character
            return [
                text[i : i + self.chunk_size]
                for i in range(
                    0, len(text), self.chunk_size - self.chunk_overlap
                )
            ]

        separator = separators[0]
        if separator == "":
            splits = list(text)
        else:
            splits = text.split(separator)

        chunks = []
        current_chunk: list[str] = []
        current_len = 0

        for split in splits:
            if len(split) > self.chunk_size:
                # If a single split is larger than chunk_size, recursively split it
                if current_chunk:
                    chunks.append(separator.join(current_chunk))
                    current_chunk = []
                    current_len = 0

                sub_splits = self._split(split, separators[1:])
                chunks.extend(sub_splits)
            else:
                added_len = len(split) + (len(separator) if current_chunk else 0)

                if current_len + added_len > self.chunk_size:
                    if current_chunk:
                        chunks.append(separator.join(current_chunk))

                    # Retain overlap from end of current_chunk
                    overlap_chunk: list[str] = []
                    overlap_len = 0
                    for prev_split in reversed(current_chunk):
                        prev_added = len(prev_split) + (
                            len(separator) if overlap_chunk else 0
                        )
                        if overlap_len + prev_added <= self.chunk_overlap:
                            overlap_chunk.insert(0, prev_split)
                            overlap_len += prev_added
                        else:
                            break

                    current_chunk = overlap_chunk
                    current_len = overlap_len

                current_chunk.append(split)
                current_len += len(split) + (
                    len(separator) if len(current_chunk) > 1 else 0
                )

        if current_chunk:
            chunks.append(separator.join(current_chunk))

        return chunks


def chunk_document_pages(
    pages: list[dict[str, Any]],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[DocumentChunk]:
    """Chunks a list of page dicts and returns a list of DocumentChunks.

    Args:
        pages: List of dicts containing page text and metadata.
        chunk_size: Target size of each chunk in characters.
        chunk_overlap: Target overlap between chunks in characters.

    Returns:
        List of DocumentChunk objects.
    """
    splitter = RecursiveTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = []

    for page in pages:
        filename = page["filename"]
        page_num = page["page_number"]
        text = page["text"]

        page_splits = splitter.split_text(text)
        for idx, split in enumerate(page_splits):
            chunk_id = f"{filename}_p{page_num}_c{idx}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    text=split,
                    metadata={
                        "filename": filename,
                        "page_number": page_num,
                        "chunk_id": chunk_id,
                    },
                )
            )

    return chunks
