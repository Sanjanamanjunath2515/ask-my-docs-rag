"""
FAISS vector store for semantic similarity search.
"""

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import faiss
import numpy as np

from utils.text_splitter import TextChunk

INDEX_DIR = Path("data/faiss_index")


@dataclass
class SearchResult:
    """A retrieved chunk with similarity score."""

    chunk: TextChunk
    score: float
    rank: int


class FAISSVectorStore:
    """In-memory FAISS index with chunk metadata."""

    def __init__(self):
        self.index: Optional[faiss.IndexFlatIP] = None
        self.chunks: List[TextChunk] = []
        self.dimension: int = 0

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        """L2-normalize for cosine similarity via inner product."""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        return vectors / norms

    def build(self, embeddings: np.ndarray, chunks: List[TextChunk]) -> None:
        """
        Build FAISS index from embeddings and associated chunks.

        Args:
            embeddings: (n, dim) float32 array
            chunks: Metadata aligned with embedding rows
        """
        if len(chunks) == 0 or embeddings.shape[0] == 0:
            raise ValueError("Cannot build index with no chunks.")

        if embeddings.shape[0] != len(chunks):
            raise ValueError("Embeddings count must match chunks count.")

        self.dimension = embeddings.shape[1]
        normalized = self._normalize(embeddings.astype(np.float32))

        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(normalized)
        self.chunks = chunks

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[SearchResult]:
        """
        Retrieve top-k most similar chunks.

        Args:
            query_embedding: 1D or 2D embedding vector
            top_k: Number of results to return
        """
        if self.index is None or not self.chunks:
            return []

        query = query_embedding.astype(np.float32)
        if query.ndim == 1:
            query = query.reshape(1, -1)
        query = self._normalize(query)

        k = min(top_k, len(self.chunks))
        scores, indices = self.index.search(query, k)

        results: List[SearchResult] = []
        for rank, (idx, score) in enumerate(zip(indices[0], scores[0])):
            if idx < 0:
                continue
            results.append(
                SearchResult(
                    chunk=self.chunks[idx],
                    score=float(score),
                    rank=rank + 1,
                )
            )
        return results

    def save(self, path: Optional[Path] = None) -> None:
        """Persist index and chunks to disk."""
        path = path or INDEX_DIR
        path.mkdir(parents=True, exist_ok=True)

        if self.index is not None:
            faiss.write_index(self.index, str(path / "index.faiss"))
        with open(path / "chunks.pkl", "wb") as f:
            pickle.dump(self.chunks, f)
        with open(path / "meta.pkl", "wb") as f:
            pickle.dump({"dimension": self.dimension}, f)

    def load(self, path: Optional[Path] = None) -> bool:
        """Load index from disk. Returns True if successful."""
        path = path or INDEX_DIR
        index_file = path / "index.faiss"
        chunks_file = path / "chunks.pkl"

        if not index_file.exists() or not chunks_file.exists():
            return False

        try:
            self.index = faiss.read_index(str(index_file))
            with open(chunks_file, "rb") as f:
                self.chunks = pickle.load(f)
            meta_file = path / "meta.pkl"
            if meta_file.exists():
                with open(meta_file, "rb") as f:
                    meta = pickle.load(f)
                    self.dimension = meta.get("dimension", 0)
            return True
        except Exception:
            return False

    @property
    def is_ready(self) -> bool:
        return self.index is not None and len(self.chunks) > 0

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)
