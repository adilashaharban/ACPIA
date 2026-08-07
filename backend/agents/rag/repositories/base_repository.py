# -*- coding: utf-8 -*-
"""RAG repository base interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from backend.agents.rag.schema import RetrievalChunk

class RAGRepository(ABC):
    """Abstract interface for storing and loading indexed text chunks."""
    
    @abstractmethod
    def build_index(self) -> None:
        """Initializes index templates."""
        pass

    @abstractmethod
    def add_chunks(self, chunks: List[RetrievalChunk]) -> None:
        """Appends chunks to index storage."""
        pass

    @abstractmethod
    def delete_chunks(self, chunk_ids: List[str]) -> None:
        """Deletes target chunks from index."""
        pass

    @abstractmethod
    def search(self, query_vector: List[float], top_k: int) -> List[Tuple[RetrievalChunk, float]]:
        """Dense similarity vector search."""
        pass

    @abstractmethod
    def rebuild(self) -> None:
        """Re-indexes chunk entries."""
        pass

    @abstractmethod
    def optimize(self) -> None:
        """Optimizes index speed structures."""
        pass

    @abstractmethod
    def save_chunks(self, chunks: List[RetrievalChunk]) -> None:
        """Saves chunks."""
        pass

    @abstractmethod
    def load_chunks(self) -> List[RetrievalChunk]:
        """Loads all chunks."""
        pass

    @abstractmethod
    def clear_index(self) -> None:
        """Purges index."""
        pass

    @abstractmethod
    def get_chunk(self, chunk_id: str) -> Optional[RetrievalChunk]:
        """Retrieves a single chunk by ID."""
        pass

    @abstractmethod
    def exists(self, chunk_id: str) -> bool:
        """Verifies if chunk exists."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Returns total indexed chunks count."""
        pass
export_base_repository = RAGRepository
