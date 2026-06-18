"""Unit tests for Vector Store."""

from __future__ import annotations

from utils.document_chunker import DocumentChunk
from utils.vector_store import FAISSVectorStore


def test_vector_store_search_and_io(tmp_path) -> None:
    """Tests index creation, similarity search, saving, and loading on the vector store."""
    store = FAISSVectorStore(dimension=3)

    chunks = [
        DocumentChunk(
            chunk_id="c1",
            text="apples",
            metadata={"filename": "a.pdf", "page_number": 1, "chunk_id": "c1"},
        ),
        DocumentChunk(
            chunk_id="c2",
            text="bananas",
            metadata={"filename": "b.pdf", "page_number": 2, "chunk_id": "c2"},
        ),
    ]
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    store.create_index(chunks, embeddings)

    # Test similarity search
    query = [1.0, 0.0, 0.0]
    results = store.search(query, k=1)

    assert len(results) == 1
    assert results[0][0].text == "apples"
    assert results[0][1] > 0.9  # close to 1.0 similarity

    # Save index
    dir_path = tmp_path / "index_dir"
    store.save_index(str(dir_path))

    # Load index into new store
    new_store = FAISSVectorStore(dimension=3)
    new_store.load_index(str(dir_path))

    assert len(new_store.chunks) == 2
    assert new_store.chunks[0].text == "apples"

    results = new_store.search(query, k=1)
    assert results[0][0].text == "apples"
