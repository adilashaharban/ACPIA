# -*- coding: utf-8 -*-
"""SentenceTransformer embedding provider implementation."""

import hashlib
from typing import List
from backend.agents.rag.providers.base_provider import EmbeddingProvider

class SentenceTransformerProvider(EmbeddingProvider):
    """Produces mock high-dimensional vectors based on text hash seeds."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.dimension = 384

    def get_embedding_dimension(self) -> int:
        return self.dimension

    def generate_embedding(self, text: str) -> List[float]:
        # Hash text to generate seed
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        # Seed generator to yield deterministic outputs
        import numpy as np
        seed = int(h[:8], 16)
        rng = np.random.default_rng(seed)
        vec = rng.uniform(-1.0, 1.0, self.dimension)
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self.generate_embedding(t) for t in texts]
export_st_provider = SentenceTransformerProvider
