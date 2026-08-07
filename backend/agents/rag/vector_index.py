# -*- coding: utf-8 -*-
"""Vector search index manager."""

from typing import List, Tuple
from backend.agents.rag.repositories.base_repository import RAGRepository
from backend.agents.rag.schema import RetrievalChunk

class VectorIndex:
    """Manages dense vector storage updates and search delegates."""
    
    def __init__(self, repository: RAGRepository) -> None:
        self.repository = repository

    def add_chunks(self, chunks: List[RetrievalChunk]) -> None:
        self.repository.add_chunks(chunks)

    def delete_chunks(self, chunk_ids: List[str]) -> None:
        self.repository.delete_chunks(chunk_ids)

    def clear(self) -> None:
        self.repository.clear_index()

    def search(self, query_vector: List[float], top_k: int) -> List[Tuple[RetrievalChunk, float]]:
        return self.repository.search(query_vector, top_k)
export_vector_index = VectorIndex
