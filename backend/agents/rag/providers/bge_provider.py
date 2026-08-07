# -*- coding: utf-8 -*-
"""BGE embedding provider implementation."""

import hashlib
from typing import List
from backend.agents.rag.providers.base_provider import EmbeddingProvider

class BGEProvider(EmbeddingProvider):
    """Produces BGE mock high-dimensional vectors based on text hash seeds."""
    
    def __init__(self, model_name: str = "bge-large-en") -> None:
        self.model_name = model_name
        self.dimension = 768

    def get_embedding_dimension(self) -> int:
        return self.dimension

    def generate_embedding(self, text: str) -> List[float]:
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        import numpy as np
        seed = int(h[:8], 16)
        rng = np.random.default_rng(seed)
        vec = rng.uniform(-1.0, 1.0, self.dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self.generate_embedding(t) for t in texts]
export_bge_provider = BGEProvider
