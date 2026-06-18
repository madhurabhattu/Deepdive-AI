"""Embedding Service.

Provides local embeddings generation using Ollama (nomic-embed-text)
or local SentenceTransformers models with SQLite-based caching.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

from pathlib import Path

# Cache database path
CACHE_DB_PATH = str(
    Path(__file__).resolve().parent.parent / "data" / "embeddings_cache.db"
)


class SQLiteEmbeddingCache:
    """SQLite-backed cache for text embeddings."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = str(db_path) if db_path else CACHE_DB_PATH
        self._init_db()

    def _init_db(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS embedding_cache (
                    key TEXT PRIMARY KEY,
                    model_name TEXT,
                    text TEXT,
                    embedding TEXT
                )
                """
            )
            conn.commit()

    def get(self, model_name: str, text: str) -> list[float] | None:
        """Retrieves cached embedding if exists."""
        key = hashlib.sha256(f"{model_name}:{text}".encode("utf-8")).hexdigest()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT embedding FROM embedding_cache WHERE key = ?",
                    (key,),
                )
                row = cursor.fetchone()
                if row:
                    val: list[float] = json.loads(row[0])
                    return val
        except Exception as exc:
            logger.error("Error reading from embedding cache: %s", exc)
        return None

    def set(self, model_name: str, text: str, embedding: list[float]) -> None:
        """Caches embedding for the given text."""
        key = hashlib.sha256(f"{model_name}:{text}".encode("utf-8")).hexdigest()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO embedding_cache
                    (key, model_name, text, embedding) VALUES (?, ?, ?, ?)
                    """,
                    (key, model_name, text, json.dumps(embedding)),
                )
                conn.commit()
        except Exception as exc:
            logger.error("Error writing to embedding cache: %s", exc)


# Lazy-loaded sentence transformers models
_ST_MODELS: dict[str, Any] = {}


def _get_st_model(model_name: str) -> Any:
    """Lazy loads a local sentence-transformers model."""
    if model_name not in _ST_MODELS:
        try:
            from sentence_transformers import SentenceTransformer

            hf_name = (
                "all-MiniLM-L6-v2"
                if "all-MiniLM" in model_name
                else "BAAI/bge-small-en-v1.5"
            )
            logger.info("Loading local SentenceTransformer model: %s", hf_name)
            _ST_MODELS[model_name] = SentenceTransformer(hf_name)
        except ImportError as exc:
            logger.error("sentence-transformers is not installed: %s", exc)
            raise RuntimeError(
                "Local embedding fallback requires sentence-transformers. "
                "Run `pip install sentence-transformers`."
            ) from exc
    return _ST_MODELS[model_name]


def _embed_ollama_batch(
    texts: list[str], model_name: str, base_url: str
) -> list[list[float]]:
    """Calls Ollama server to generate embeddings in batch."""
    try:
        # Try new /api/embed endpoint
        payload = {"model": model_name, "input": texts}
        req = urllib.request.Request(
            f"{base_url}/api/embed",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            val: list[list[float]] = res["embeddings"]
            return val
    except Exception as exc:
        logger.warning(
            "Ollama /api/embed failed (%s). Falling back to item-by-item /api/embeddings",
            exc,
        )

    # Fallback to older /api/embeddings endpoint (sequential calls)
    embeddings = []
    for text in texts:
        payload = {"model": model_name, "prompt": text}
        req = urllib.request.Request(
            f"{base_url}/api/embeddings",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            embeddings.append(res["embedding"])
    return embeddings


def get_embeddings(
    texts: list[str],
    model_name: str = "nomic-embed-text",
    ollama_base_url: str = "http://localhost:11434",
) -> list[list[float]]:
    """Generates embeddings for a list of texts using the selected model.

    Utilizes SQLite caching and batches requests to save time and compute.

    Args:
        texts: List of strings to embed.
        model_name: Model name ('nomic-embed-text', 'all-MiniLM-L6-v2', or 'BGE-small').
        ollama_base_url: Connection URL for local Ollama server.

    Returns:
        List of embedding vectors (list of floats).
    """
    if not texts:
        return []

    cache = SQLiteEmbeddingCache()
    results: list[list[float] | None] = [None] * len(texts)
    uncached_indices: list[int] = []
    uncached_texts: list[str] = []

    # Check cache first
    for idx, text in enumerate(texts):
        cached = cache.get(model_name, text)
        if cached is not None:
            results[idx] = cached
        else:
            uncached_indices.append(idx)
            uncached_texts.append(text)

    if not uncached_texts:
        # All embeddings found in cache!
        return [r for r in results if r is not None]

    # Generate uncached embeddings
    computed_embeddings: list[list[float]] = []
    batch_size = 32

    # If Ollama embedding fails or server is unavailable, we fallback automatically to all-MiniLM-L6-v2
    actual_model = model_name
    use_ollama = model_name == "nomic-embed-text"

    if use_ollama:
        try:
            # Check connection first
            from utils.ai_client import is_ollama_available

            if not is_ollama_available():
                raise ConnectionError("Ollama server is not reachable")

            for i in range(0, len(uncached_texts), batch_size):
                batch = uncached_texts[i : i + batch_size]
                batch_embeddings = _embed_ollama_batch(
                    batch, model_name, ollama_base_url
                )
                computed_embeddings.extend(batch_embeddings)
        except Exception as exc:
            logger.warning(
                "Ollama embeddings generation failed: %s. "
                "Falling back to local 'all-MiniLM-L6-v2' via sentence-transformers.",
                exc,
            )
            actual_model = "all-MiniLM-L6-v2"
            use_ollama = False

    if not use_ollama:
        # Generate using SentenceTransformers
        st_model = _get_st_model(actual_model)
        embeddings_np = st_model.encode(
            uncached_texts, batch_size=batch_size, show_progress_bar=False
        )
        computed_embeddings = [emb.tolist() for emb in embeddings_np]

    # Save to cache and construct final results
    for idx, (orig_idx, text) in enumerate(
        zip(uncached_indices, uncached_texts)
    ):
        emb = computed_embeddings[idx]
        cache.set(actual_model, text, emb)
        results[orig_idx] = emb

    # Double check if any None is left (should not happen)
    final_results: list[list[float]] = []
    for r in results:
        if r is None:
            final_results.append([0.0] * 384)
        else:
            final_results.append(r)

    return final_results
