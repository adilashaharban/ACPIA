# -*- coding: utf-8 -*-
"""Embedding generator factory."""

from typing import List, Optional
from backend.agents.rag.providers.base_provider import EmbeddingProvider
from backend.agents.rag.providers.sentence_transformer_provider import SentenceTransformerProvider
from backend.agents.rag.providers.bge_provider import BGEProvider
from backend.agents.rag.providers.e5_provider import E5Provider

class EmbeddingGenerator:
    """Instantiates embedding model connectors from configured identifiers."""
    
    def __init__(self, provider_type: str = "sentence_transformer") -> None:
        self.provider: EmbeddingProvider = self._resolve_provider(provider_type)

    def _resolve_provider(self, provider_type: str) -> EmbeddingProvider:
        p_lower = provider_type.lower()
        if "bge" in p_lower:
            return BGEProvider()
        elif "e5" in p_lower:
            return E5Provider()
        else:
            return SentenceTransformerProvider()

    def get_dimension(self) -> int:
        return self.provider.get_embedding_dimension()

    def generate(self, text: str) -> List[float]:
        return self.provider.generate_embedding(text)

    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        return self.provider.generate_embeddings(texts)
export_embedding_generator = EmbeddingGenerator
