# -*- coding: utf-8 -*-
"""FAISS vector search repository implementation."""

import numpy as np
from typing import List, Optional, Tuple, Dict
from backend.agents.rag.repositories.base_repository import RAGRepository
from backend.agents.rag.schema import RetrievalChunk

class FAISSRepository(RAGRepository):
    """Uses a numpy cosine similarity matrix to mock FAISS dense vector operations."""
    
    def __init__(self) -> None:
        self._chunks: Dict[str, RetrievalChunk] = {}
        # Maps chunk ID to mock vector
        self._vectors: Dict[str, np.ndarray] = {}

    def build_index(self) -> None:
        pass

    def add_chunks(self, chunks: List[RetrievalChunk]) -> None:
        for chunk in chunks:
            self._chunks[chunk.chunk_id] = chunk
            # Mock high dimensional float vector
            dim = chunk.embedding.embedding_dimension
            self._vectors[chunk.chunk_id] = np.random.randn(dim)

    def delete_chunks(self, chunk_ids: List[str]) -> None:
        for cid in chunk_ids:
            self._chunks.pop(cid, None)
            self._vectors.pop(cid, None)

    def search(self, query_vector: List[float], top_k: int) -> List[Tuple[RetrievalChunk, float]]:
        if not self._chunks or not query_vector:
            return []
            
        q_arr = np.array(query_vector)
        q_norm = np.linalg.norm(q_arr)
        if q_norm == 0:
            q_norm = 1e-9
            
        results = []
        for cid, chunk in self._chunks.items():
            vec = self._vectors.get(cid)
            if vec is not None:
                v_norm = np.linalg.norm(vec)
                if v_norm == 0:
                    v_norm = 1e-9
                # Cosine similarity
                sim = float(np.dot(q_arr, vec) / (q_norm * v_norm))
                results.append((chunk, sim))
                
        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def rebuild(self) -> None:
        pass

    def optimize(self) -> None:
        pass

    def save_chunks(self, chunks: List[RetrievalChunk]) -> None:
        self.add_chunks(chunks)

    def load_chunks(self) -> List[RetrievalChunk]:
        return list(self._chunks.values())

    def clear_index(self) -> None:
        self._chunks.clear()
        self._vectors.clear()

    def get_chunk(self, chunk_id: str) -> Optional[RetrievalChunk]:
        return self._chunks.get(chunk_id)

    def exists(self, chunk_id: str) -> bool:
        return chunk_id in self._chunks

    def count(self) -> int:
        return len(self._chunks)
export_faiss_repository = FAISSRepository
