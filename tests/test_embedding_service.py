"""Unit tests for Embedding Service."""

from __future__ import annotations

from unittest.mock import patch
from utils.embedding_service import SQLiteEmbeddingCache, get_embeddings


def test_sqlite_embedding_cache(tmp_path) -> None:
    """Tests SQLiteCache saving and reading logic."""
    db_file = tmp_path / "test_cache.db"
    cache = SQLiteEmbeddingCache(db_path=str(db_file))

    # Empty cache check
    assert cache.get("model_x", "test text") is None

    # Set cache
    embedding = [0.1, 0.2, 0.3]
    cache.set("model_x", "test text", embedding)

    # Retrieve cache
    cached = cache.get("model_x", "test text")
    assert cached == embedding


def test_get_embeddings_cached(tmp_path) -> None:
    """Verifies that get_embeddings reads from SQLite cache if available."""
    db_file = tmp_path / "test_cache.db"
    cache = SQLiteEmbeddingCache(db_path=str(db_file))
    cache.set("model_y", "hello", [1.0, 2.0])

    with patch("utils.embedding_service.CACHE_DB_PATH", str(db_file)):
        # By setting the db_file as the primary cache path, it should hit cache instantly
        embeddings = get_embeddings(["hello"], model_name="model_y")
        assert embeddings == [[1.0, 2.0]]
