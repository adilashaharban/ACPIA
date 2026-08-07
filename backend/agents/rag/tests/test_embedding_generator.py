# -*- coding: utf-8 -*-
"""Unit tests for EmbeddingGenerator and providers."""

from backend.agents.rag.embedding_generator import EmbeddingGenerator

def test_embedding_providers() -> None:
    """Verifies dimension outputs and generation parameters for model types."""
    st = EmbeddingGenerator("sentence_transformer")
    assert st.get_dimension() == 384
    v1 = st.generate("Hello world")
    assert len(v1) == 384
    
    bge = EmbeddingGenerator("bge")
    assert bge.get_dimension() == 768
    v2 = bge.generate("Hello world")
    assert len(v2) == 768
    
    e5 = EmbeddingGenerator("e5")
    assert e5.get_dimension() == 1024
    v3 = e5.generate("Hello world")
    assert len(v3) == 1024
