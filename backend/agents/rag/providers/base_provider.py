# -*- coding: utf-8 -*-
"""Embedding provider base interface."""

from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    """Abstract interface for generating text chunk vector embeddings."""
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Returns target vector floats count."""
        pass

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """Calculates embeddings vector."""
        pass

    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Calculates batch vectors."""
        pass
export_base_provider = EmbeddingProvider
