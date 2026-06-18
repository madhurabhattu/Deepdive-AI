"""Unit tests for RAG Pipeline."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from utils.document_chunker import DocumentChunk
from utils.rag_pipeline import stream_rag_answer


def test_stream_rag_answer() -> None:
    """Verifies that stream_rag_answer embeds the query, searches index, and streams the answer."""
    # Mock vector store and chunk
    mock_store = MagicMock()
    chunk = DocumentChunk(
        chunk_id="c1",
        text="Target document content snippet.",
        metadata={"filename": "doc.pdf", "page_number": 5, "chunk_id": "c1"},
    )
    mock_store.search.return_value = [(chunk, 0.95)]

    # Mock embedding retrieval and stream chat response
    with patch("utils.rag_pipeline.get_embeddings", return_value=[[0.1, 0.2]]):
        with patch("utils.rag_pipeline.stream_chat", return_value=iter(["Generated", " answer", " text."])):
            generator = stream_rag_answer(
                question="What is the snippet?",
                vector_store=mock_store,
                embedding_model="nomic-embed-text",
                llm_model="llama3",
                provider="ollama",
            )

            items = list(generator)

            # Verify token generation
            tokens = [item["content"] for item in items if item["type"] == "token"]
            assert "".join(tokens) == "Generated answer text."

            # Verify citations are produced at the end
            sources = [
                item["content"] for item in items if item["type"] == "sources"
            ][0]
            assert len(sources) == 1
            assert sources[0]["filename"] == "doc.pdf"
            assert sources[0]["page_number"] == 5
            assert sources[0]["text"] == "Target document content snippet."
            assert sources[0]["score"] == 0.95
