# -*- coding: utf-8 -*-
"""Unit tests for ProviderFactory and LLM providers."""

from backend.agents.investigation_reasoning.providers.provider_factory import ProviderFactory

def test_providers() -> None:
    """Verifies that all model provider subclasses instantiate and execute health checks."""
    for p_type in ["gemini", "openai", "claude", "ollama"]:
        p = ProviderFactory.get_provider(p_type)
        assert p.health_check()
        raw_res, raw_meta = p.generate("Query", 0.0, 100)
        assert "findings" in raw_res
        assert raw_meta["provider"] == p_type
