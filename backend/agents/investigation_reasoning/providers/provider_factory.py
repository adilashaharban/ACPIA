# -*- coding: utf-8 -*-
"""LLM Provider factory."""

from typing import Optional
from backend.agents.investigation_reasoning.providers.base_provider import ReasoningProvider
from backend.agents.investigation_reasoning.providers.gemini_provider import GeminiProvider
from backend.agents.investigation_reasoning.providers.openai_provider import OpenAIProvider
from backend.agents.investigation_reasoning.providers.claude_provider import ClaudeProvider
from backend.agents.investigation_reasoning.providers.ollama_provider import OllamaProvider

class ProviderFactory:
    """Instantiates configured LLM API provider wrappers."""
    
    @staticmethod
    def get_provider(provider_type: str, model_name: Optional[str] = None) -> ReasoningProvider:
        p_lower = provider_type.lower()
        if "gemini" in p_lower:
            return GeminiProvider(model_name or "gemini-1.5-pro")
        elif "openai" in p_lower:
            return OpenAIProvider(model_name or "gpt-4o")
        elif "claude" in p_lower:
            return ClaudeProvider(model_name or "claude-3-5-sonnet")
        elif "ollama" in p_lower:
            return OllamaProvider(model_name or "llama3")
        else:
            # Defaults to Gemini
            return GeminiProvider(model_name or "gemini-1.5-pro")
export_provider_factory = ProviderFactory
