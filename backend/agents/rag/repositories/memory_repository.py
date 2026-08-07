# -*- coding: utf-8 -*-
"""In-memory RAG repository implementation."""

from typing import List, Optional, Tuple, Dict
from backend.agents.rag.repositories.base_repository import RAGRepository
from backend.agents.rag.schema import RetrievalChunk

class MemoryRepository(RAGRepository):
    """Stores text chunks inside thread-safe local dictionaries."""
    
    def __init__(self) -> None:
        self._chunks: Dict[str, RetrievalChunk] = {}

    def build_index(self) -> None:
        pass

    def add_chunks(self, chunks: List[RetrievalChunk]) -> None:
        for chunk in chunks:
            self._chunks[chunk.chunk_id] = chunk

    def delete_chunks(self, chunk_ids: List[str]) -> None:
        for cid in chunk_ids:
            self._chunks.pop(cid, None)

    def search(self, query_vector: List[float], top_k: int) -> List[Tuple[RetrievalChunk, float]]:
        # Mock cosine similarity return (all 0.90 similarity)
        res = []
        for c in list(self._chunks.values())[:top_k]:
            res.append((c, 0.90))
        return res

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

    def get_chunk(self, chunk_id: str) -> Optional[RetrievalChunk]:
        return self._chunks.get(chunk_id)

    def exists(self, chunk_id: str) -> bool:
        return chunk_id in self._chunks

    def count(self) -> int:
        return len(self._chunks)
export_memory_repository = MemoryRepository
