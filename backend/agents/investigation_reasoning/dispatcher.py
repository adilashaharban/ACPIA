# -*- coding: utf-8 -*-
"""Provider dispatcher."""

from typing import Tuple, Dict, Any, Optional
from backend.agents.investigation_reasoning.providers.provider_factory import ProviderFactory

class Dispatcher:
    """Invokes target LLM providers using the instantiator factory."""
    
    @staticmethod
    def call_provider(
        provider_type: str,
        model_name: str,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, Dict[str, Any]]:
        """Dispatches prompting.
        
        Args:
            provider_type: Model provider ID.
            model_name: Specific model tag.
            prompt: Text prompt string.
            temperature: Randomness.
            max_tokens: Tokens limit.
            
        Returns:
            Tuple of (raw string response, provider metadata dict).
        """
        p = ProviderFactory.get_provider(provider_type, model_name)
        return p.generate(prompt, temperature, max_tokens)
export_dispatcher = Dispatcher
