"""Vector Store Utility.

Provides a FAISS-based vector database for similarity search of document chunks,
falling back to a pure-numpy implementation if FAISS is not installed.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from utils.document_chunker import DocumentChunk

try:
    import faiss  # type: ignore[import-untyped]

    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False


class FAISSVectorStore:
    """FAISS-based local vector store with a pure-numpy fallback."""

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension
        self.chunks: list[DocumentChunk] = []
        self._index: Any = None
        self._vectors: list[np.ndarray] = []

        if HAS_FAISS:
            # Flat Inner Product index (uses Cosine Similarity if vectors are normalized)
            self._index = faiss.IndexFlatIP(dimension)
        else:
            self._index = None

    def create_index(
        self, chunks: list[DocumentChunk], embeddings: list[list[float]]
    ) -> None:
        """Initializes a new vector index with chunks and their embeddings.

        Normalizes vectors for Cosine Similarity.
        """
        self.chunks = chunks
        if not embeddings:
            return

        self.dimension = len(embeddings[0])
        v_np = np.array(embeddings, dtype=np.float32)

        # Normalize rows to unit length for Inner Product = Cosine Similarity
        norms = np.linalg.norm(v_np, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        v_np = v_np / norms

        if HAS_FAISS:
            self._index = faiss.IndexFlatIP(self.dimension)
            self._index.add(v_np)
        else:
            self._vectors = [row for row in v_np]

    def save_index(self, dir_path: str | Path) -> None:
        """Saves the index and metadata to a directory."""
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)

        # Save metadata and chunks
        with open(path / "chunks.pkl", "wb") as f:
            pickle.dump(self.chunks, f)

        # Save index file or raw vectors
        if HAS_FAISS and self._index is not None:
            faiss.write_index(self._index, str(path / "index.faiss"))
        else:
            with open(path / "vectors.pkl", "wb") as f:
                pickle.dump((self._vectors, self.dimension), f)

    def load_index(self, dir_path: str | Path) -> None:
        """Loads the index and metadata from a directory."""
        path = Path(dir_path)
        chunks_path = path / "chunks.pkl"
        if not chunks_path.exists():
            raise FileNotFoundError(f"Chunks file not found at {chunks_path}")

        with open(chunks_path, "rb") as f:
            self.chunks = pickle.load(f)

        faiss_path = path / "index.faiss"
        if HAS_FAISS and faiss_path.exists():
            self._index = faiss.read_index(str(faiss_path))
            self.dimension = self._index.d
        else:
            vectors_path = path / "vectors.pkl"
            if vectors_path.exists():
                with open(vectors_path, "rb") as f:
                    self._vectors, self.dimension = pickle.load(f)
            else:
                raise FileNotFoundError(
                    "No valid index.faiss or vectors.pkl found."
                )

    def search(
        self, query_embedding: list[float], k: int = 4
    ) -> list[tuple[DocumentChunk, float]]:
        """Searches for top-k similar chunks to the query embedding.

        Returns:
            List of tuples (DocumentChunk, score).
        """
        if not self.chunks:
            return []

        q_np = np.array([query_embedding], dtype=np.float32)
        q_norm = np.linalg.norm(q_np)
        if q_norm > 0:
            q_np = q_np / q_norm

        k = min(k, len(self.chunks))

        if HAS_FAISS and self._index is not None:
            scores, indices = self._index.search(q_np, k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self.chunks):
                    continue
                results.append((self.chunks[idx], float(score)))
            return results
        else:
            # Pure-numpy Cosine Similarity search fallback
            q_vec = q_np[0]
            scores_list = []
            for idx, vec in enumerate(self._vectors):
                score = float(np.dot(vec, q_vec))
                scores_list.append((score, idx))

            scores_list.sort(key=lambda x: x[0], reverse=True)
            results = []
            for score, idx in scores_list[:k]:
                results.append((self.chunks[idx], score))
            return results
