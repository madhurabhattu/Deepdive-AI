"""Unit tests for Document Chunker."""

from __future__ import annotations

from utils.document_chunker import (
    DocumentChunk,
    RecursiveTextSplitter,
    chunk_document_pages,
)


def test_recursive_text_splitter_basic() -> None:
    """Tests basic splitting with size and overlap constraints."""
    splitter = RecursiveTextSplitter(chunk_size=50, chunk_overlap=10)
    text = "This is a long piece of text that should be split recursively."
    chunks = splitter.split_text(text)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 50


def test_chunk_document_pages() -> None:
    """Tests mapping pages to DocumentChunk objects with metadata."""
    pages = [
        {"filename": "doc.pdf", "page_number": 1, "text": "Hello world from page one."},
        {"filename": "doc.pdf", "page_number": 2, "text": "This is page two content."},
    ]
    chunks = chunk_document_pages(pages, chunk_size=30, chunk_overlap=5)
    assert len(chunks) >= 2
    assert isinstance(chunks[0], DocumentChunk)
    assert chunks[0].metadata["filename"] == "doc.pdf"
    assert chunks[0].metadata["page_number"] == 1
    assert chunks[0].chunk_id == "doc.pdf_p1_c0"
